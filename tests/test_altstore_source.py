import copy
import importlib.util
import plistlib
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "platform/ios/scripts/altstore_source.py"
SPEC = importlib.util.spec_from_file_location("altstore_source", SCRIPT)
source_tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(source_tool)


class AltStoreSourceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.ipa = Path(self.directory.name) / "app.ipa"
        self.info = {
            "CFBundleIdentifier": "com.example.app",
            "CFBundleExecutable": "App",
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleVersion": "1",
            "MinimumOSVersion": "15.0",
        }
        self.write_ipa()
        self.metadata = source_tool.inspect_ipa(self.ipa)
        self.source = {
            "name": "Test", "news": [], "featuredApps": ["com.example.app"],
            "apps": [{
                "name": "App", "bundleIdentifier": "com.example.app",
                "developerName": "Test", "localizedDescription": "Test app",
                "iconURL": "https://example.com/icon.png",
                "appPermissions": {"entitlements": [], "privacy": {}},
                "versions": [{
                    **{key: self.metadata[key] for key in
                       ("version", "buildVersion", "minOSVersion", "size", "sha256")},
                    "date": "2026-08-05", "downloadURL": "https://example.com/app.ipa",
                }],
            }],
        }
        self.release = {
            "isDraft": False, "isPrerelease": False,
            "publishedAt": "2026-09-13T12:00:00Z", "body": "Changes",
            "assets": [{"name": "Applesauce-iOS-unsigned.ipa",
                        "url": "https://example.com/app.ipa", "size": self.metadata["size"]}],
        }

    def write_ipa(self, signed=False, profile=False):
        command = struct.pack("<4I", 0x1D, 16, 48, 0) if signed else b""
        executable = struct.pack("<8I", 0xFEEDFACF, 0x0100000C, 0, 2,
                                 int(signed), len(command), 0, 0) + command
        with zipfile.ZipFile(self.ipa, "w") as archive:
            archive.writestr("Payload/App.app/Info.plist", plistlib.dumps(self.info))
            archive.writestr("Payload/App.app/App", executable)
            if profile:
                archive.writestr("Payload/App.app/embedded.mobileprovision", b"profile")

    def test_valid_source_matches_actual_archive(self):
        source_tool.validate_source(self.source)
        source_tool.check_ipa(self.source, self.metadata)

    def test_rejects_wrong_size_checksum_version_and_minimum_os(self):
        for key, value in (("size", 1), ("sha256", "0" * 64),
                           ("buildVersion", "99"), ("minOSVersion", "17.4")):
            with self.subTest(key=key):
                invalid = copy.deepcopy(self.source)
                invalid["apps"][0]["versions"][0][key] = value
                with self.assertRaises(ValueError):
                    source_tool.check_ipa(invalid, self.metadata)

    def test_rejects_wrong_bundle_and_permissions(self):
        for key, value in (("bundleIdentifier", "com.example.other"),
                           ("appPermissions", {"entitlements": ["get-task-allow"], "privacy": {}})):
            with self.subTest(key=key):
                invalid = copy.deepcopy(self.source)
                invalid["apps"][0][key] = value
                with self.assertRaises(ValueError):
                    source_tool.check_ipa(invalid, self.metadata)

    def test_rejects_trollstore_and_personal_signing_material(self):
        for options in ({"signed": True}, {"profile": True}):
            with self.subTest(options=options):
                self.write_ipa(**options)
                with self.assertRaises(ValueError):
                    source_tool.inspect_ipa(self.ipa)

    def test_collects_privacy_permissions(self):
        self.info["NSMicrophoneUsageDescription"] = "Record audio"
        self.write_ipa()
        metadata = source_tool.inspect_ipa(self.ipa)
        self.assertEqual(metadata["appPermissions"]["privacy"],
                         {"NSMicrophoneUsageDescription": "Record audio"})

    def test_rejects_truncated_load_commands(self):
        with self.assertRaises(ValueError):
            source_tool.require_unsigned(struct.pack("<8I", 0xFEEDFACF, 0x0100000C,
                                                       0, 2, 1, 16, 0, 0))

    def test_rejects_duplicates_and_unordered_versions(self):
        invalid = copy.deepcopy(self.source)
        invalid["apps"].append(copy.deepcopy(invalid["apps"][0]))
        with self.assertRaises(ValueError):
            source_tool.validate_source(invalid)
        for version in ("1.0.0", "2.0.0"):
            invalid = copy.deepcopy(self.source)
            newer = dict(invalid["apps"][0]["versions"][0], version=version)
            invalid["apps"][0]["versions"].append(newer)
            with self.assertRaises(ValueError):
                source_tool.validate_source(invalid)

    def test_update_prepends_and_preserves_history(self):
        metadata = dict(self.metadata, version="1.1.0")
        result = source_tool.update_source(self.source, metadata, self.release)
        self.assertEqual([item["version"] for item in result["apps"][0]["versions"]],
                         ["1.1.0", "1.0.0"])
        self.assertEqual(len(self.source["apps"][0]["versions"]), 1)

    def test_republishing_is_idempotent(self):
        result = source_tool.update_source(self.source, self.metadata, self.release)
        self.assertEqual(source_tool.update_source(result, self.metadata, self.release), result)

    def test_changed_binary_requires_new_build(self):
        with self.assertRaisesRegex(ValueError, "new version or build"):
            source_tool.update_source(self.source, dict(self.metadata, sha256="0" * 64), self.release)

    def test_rejects_release_downgrade(self):
        with self.assertRaisesRegex(ValueError, "older release"):
            source_tool.update_source(self.source, dict(self.metadata, version="0.9.0"), self.release)

    def test_rejects_draft_prerelease_and_asset_mismatch(self):
        for key in ("isDraft", "isPrerelease"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                source_tool.update_source(self.source, self.metadata, dict(self.release, **{key: True}))
        self.release["assets"][0]["size"] += 1
        with self.assertRaises(ValueError):
            source_tool.update_source(self.source, self.metadata, self.release)

    def test_rejects_release_checksum_mismatch(self):
        self.release["assets"][0]["digest"] = "sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            source_tool.update_source(self.source, self.metadata, self.release)


if __name__ == "__main__":
    unittest.main()
