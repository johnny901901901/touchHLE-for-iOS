#!/usr/bin/env python3
"""Validate an AltStore Classic source against an unsigned release IPA."""

import argparse
import copy
import datetime
import hashlib
import json
import plistlib
import re
import struct
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit


def require(condition, message):
    if not condition:
        raise ValueError(message)


def https_url(value):
    require(isinstance(value, str), "URL must be a string")
    parsed = urlsplit(value)
    require(parsed.scheme == "https" and parsed.hostname and not parsed.username,
            f"Expected a public HTTPS URL: {value}")


def version_tuple(value):
    require(isinstance(value, str) and re.fullmatch(r"\d+(?:\.\d+)*", value),
            f"Invalid numeric version: {value}")
    parts = tuple(int(part) for part in value.split("."))
    return parts + (0,) * max(0, 3 - len(parts))


def validate_source(source):
    require(isinstance(source.get("name"), str) and source["name"], "Source name is missing")
    require(isinstance(source.get("apps"), list) and source["apps"], "Source has no apps")
    require(isinstance(source.get("news"), list), "Source news must be an array")
    bundle_ids = set()
    for app in source["apps"]:
        for key in ("name", "bundleIdentifier", "developerName", "localizedDescription"):
            require(isinstance(app.get(key), str) and app[key], f"Missing app {key}")
        bundle_id = app["bundleIdentifier"]
        require(bundle_id not in bundle_ids, f"Duplicate app: {bundle_id}")
        bundle_ids.add(bundle_id)
        https_url(app["iconURL"])
        for screenshot in app.get("screenshots", []):
            https_url(screenshot if isinstance(screenshot, str) else screenshot["imageURL"])
        permissions = app.get("appPermissions", {})
        require(isinstance(permissions.get("entitlements"), list), "Entitlements must be an array")
        require(all(isinstance(item, str) for item in permissions["entitlements"]),
                "Entitlements must contain names")
        require(isinstance(permissions.get("privacy"), dict), "Privacy must be a dictionary")
        require(isinstance(app.get("versions"), list) and app["versions"], "App has no versions")
        seen_versions = set()
        previous = None
        for version in app["versions"]:
            identity = (version["version"], version["buildVersion"])
            order = tuple(version_tuple(item) for item in identity)
            require(identity not in seen_versions, f"Duplicate version: {identity}")
            require(previous is None or order < previous, "Versions must be newest first")
            previous = order
            seen_versions.add(identity)
            datetime.datetime.fromisoformat(version["date"].replace("Z", "+00:00"))
            https_url(version["downloadURL"])
            require(type(version.get("size")) is int and version["size"] > 0,
                    "IPA size must be a positive byte count")
            require(re.fullmatch(r"[0-9a-f]{64}", version.get("sha256", "")),
                    "IPA SHA-256 must have 64 lowercase hex digits")
            version_tuple(version["minOSVersion"])
    require(set(source.get("featuredApps", [])) <= bundle_ids, "Featured app is not in source")
    news_ids = [item["identifier"] for item in source["news"]]
    require(len(news_ids) == len(set(news_ids)), "Duplicate news identifier")


def require_unsigned(executable):
    # Release IPAs strip the host signature. Reject signed/TrollStore hosts so
    # their privileged entitlements cannot accidentally enter the Classic feed.
    require(len(executable) >= 32, "Truncated executable")
    magic, cpu, _, _, count, command_size, _, _ = struct.unpack_from("<8I", executable)
    require(magic == 0xFEEDFACF and cpu == 0x0100000C, "Expected an arm64 Mach-O host")
    limit = 32 + command_size
    require(limit <= len(executable), "Truncated load commands")
    offset = 32
    for _ in range(count):
        require(offset + 8 <= limit, "Truncated load command")
        command, size = struct.unpack_from("<2I", executable, offset)
        require(size >= 8 and size % 8 == 0 and offset + size <= limit,
                "Invalid load command size")
        require(command != 0x1D, "Use the unsigned IPA, not a signed or TrollStore build")
        offset += size
    require(offset == limit, "Invalid load command count")


def inspect_ipa(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate archive entries")
        require(not any(name.endswith((".mobileprovision", ".p12", ".mobiledevicepairing"))
                        for name in names), "Private signing or pairing material in IPA")
        infos = [name for name in names if re.fullmatch(r"Payload/[^/]+\.app/Info\.plist", name)]
        require(len(infos) == 1, "Expected exactly one app in Payload")
        info = plistlib.loads(archive.read(infos[0]))
        app_root = infos[0].rsplit("/", 1)[0]
        executable_name = info["CFBundleExecutable"]
        require(isinstance(executable_name, str) and "/" not in executable_name,
                "Invalid executable name")
        require_unsigned(archive.read(f"{app_root}/{executable_name}"))
        require(not any(".appex/" in name for name in names),
                "App extensions need their permissions added before distribution")
        privacy = {key: value for key, value in info.items() if "UsageDescription" in key}
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "bundleIdentifier": info["CFBundleIdentifier"],
        "version": info["CFBundleShortVersionString"],
        "buildVersion": info["CFBundleVersion"],
        "minOSVersion": info["MinimumOSVersion"],
        "size": path.stat().st_size,
        "sha256": digest.hexdigest(),
        "appPermissions": {"entitlements": [], "privacy": privacy},
    }


def app_for(source, bundle_id):
    matches = [app for app in source["apps"] if app["bundleIdentifier"] == bundle_id]
    require(len(matches) == 1, f"Source does not contain {bundle_id}")
    return matches[0]


def check_ipa(source, metadata):
    app = app_for(source, metadata["bundleIdentifier"])
    version = next((version for version in app["versions"]
                    if (version["version"], version["buildVersion"])
                    == (metadata["version"], metadata["buildVersion"])), None)
    require(version is not None, "IPA version/build is absent from source")
    for key in ("version", "buildVersion", "minOSVersion", "size", "sha256"):
        require(version[key] == metadata[key], f"Source {key} does not match IPA")
    require(app["appPermissions"] == metadata["appPermissions"],
            "Source permissions do not match IPA")


def update_source(source, metadata, release):
    require(not release.get("isDraft") and not release.get("isPrerelease"),
            "Only published, non-prerelease builds enter the Classic feed")
    asset = next((asset for asset in release["assets"]
                  if asset["name"] == "Applesauce-iOS-unsigned.ipa"), None)
    require(asset is not None, "Release has no unsigned IPA")
    require(asset["size"] == metadata["size"], "Release asset size differs from IPA")
    if asset.get("digest"):
        require(asset["digest"] == f"sha256:{metadata['sha256']}", "Release checksum differs from IPA")
    result = copy.deepcopy(source)
    app = app_for(result, metadata["bundleIdentifier"])
    newest = app["versions"][0]
    new_order = (version_tuple(metadata["version"]), version_tuple(metadata["buildVersion"]))
    old_order = (version_tuple(newest["version"]), version_tuple(newest["buildVersion"]))
    require(new_order >= old_order, "Refusing to replace the latest version with an older release")
    entry = {key: metadata[key] for key in
             ("version", "buildVersion", "minOSVersion", "size", "sha256")}
    entry.update(date=release["publishedAt"], downloadURL=asset["url"],
                 localizedDescription=release.get("body", ""))
    if new_order == old_order:
        require(newest["sha256"] == metadata["sha256"],
                "A changed binary needs a new version or build number")
    app["versions"] = [entry] + [item for item in app["versions"]
                                 if (item["version"], item["buildVersion"])
                                 != (metadata["version"], metadata["buildVersion"])]
    app["appPermissions"] = metadata["appPermissions"]
    validate_source(result)
    check_ipa(result, metadata)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--ipa", type=Path)
    parser.add_argument("--release-json", type=Path, help="Metadata from gh release view")
    args = parser.parse_args()
    source = json.loads(args.source.read_text())
    validate_source(source)
    if args.release_json:
        require(args.ipa is not None, "Updating requires --ipa")
    if args.ipa:
        metadata = inspect_ipa(args.ipa)
        if args.release_json:
            source = update_source(source, metadata, json.loads(args.release_json.read_text()))
            with tempfile.NamedTemporaryFile(mode="w", dir=args.source.parent,
                                             delete=False, encoding="utf-8") as handle:
                temporary = Path(handle.name)
                json.dump(source, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            temporary.replace(args.source)
        else:
            check_ipa(source, metadata)
    print("AltStore source validated" + (" against IPA" if args.ipa else ""))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile) as error:
        sys.exit(f"error: {error}")
