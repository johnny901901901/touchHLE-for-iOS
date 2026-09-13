#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO=$(CDPATH= cd -- "$ROOT/../.." && pwd)

# What the IPA is expected to carry. The three release IPAs differ only in
# their entitlements, and `codesign` cannot tell them apart: ldid writes a
# CodeDirectory with an empty CMS blob, which codesign reports as "no
# signature" exactly like a genuinely unsigned app. So the entitlements
# themselves are what gets checked, read back with ldid.
EXPECT=unsigned
IPA=

while [ $# -gt 0 ]; do
    case "$1" in
        --trollstore)
            EXPECT=trollstore
            ;;
        --trollstore-permanent-jit)
            EXPECT=permanent
            ;;
        -h|--help)
            echo "Usage: $0 [--trollstore | --trollstore-permanent-jit] [file.ipa]"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            exit 2
            ;;
        *)
            IPA=$1
            ;;
    esac
    shift
done

[ -n "$IPA" ] || IPA="$REPO/dist/Applesauce-iOS-unsigned.ipa"

case "$IPA" in
    /*) ;;
    *) IPA="$PWD/$IPA" ;;
esac

if [ ! -f "$IPA" ]; then
    echo "IPA not found: $IPA" >&2
    exit 1
fi

STAGE=$(mktemp -d "${TMPDIR:-/tmp}/applesauce-verify.XXXXXX")
trap 'rm -rf "$STAGE"' EXIT HUP INT TERM

unzip -tq "$IPA" >/dev/null
unzip -q "$IPA" -d "$STAGE"

APP="$STAGE/Payload/Applesauce.app"
if [ ! -d "$APP" ]; then
    echo "Payload/Applesauce.app is missing." >&2
    exit 1
fi

# Check embedded cores too: signing the host and signing its libraries are
# separate build steps, so an unsigned host alone is not enough.
find "$APP" -type f -print | while IFS= read -r binary; do
    file "$binary" | grep -q 'Mach-O' || continue
    team=$(codesign -dvvv "$binary" 2>&1 | awk -F= '/^TeamIdentifier=/ { print $2 }')
    if [ -n "$team" ] && [ "$team" != 'not set' ]; then
        echo "A binary is signed with a developer identity. Refusing release validation." >&2
        exit 1
    fi
done

if ! command -v ldid >/dev/null 2>&1; then
    echo "This check needs ldid to read the embedded entitlements (brew install ldid)." >&2
    exit 1
fi

ENTITLEMENTS=$(ldid -e "$APP/Applesauce" 2>/dev/null || true)

require_entitlement() {
    if ! printf '%s' "$ENTITLEMENTS" | python3 -c \
        'import plistlib, sys; sys.exit(0 if plistlib.loads(sys.stdin.buffer.read()).get(sys.argv[1]) is True else 1)' "$1"; then
        echo "Expected the $1 entitlement to be true." >&2
        exit 1
    fi
}

refuse_entitlement() {
    if printf '%s' "$ENTITLEMENTS" | grep -q "<key>$1</key>"; then
        echo "The $1 entitlement is present and must not be." >&2
        exit 1
    fi
}

case "$EXPECT" in
    unsigned)
        # Anything at all here means this is one of the TrollStore builds, which
        # must never be published as the plain sideloading IPA: AltStore and
        # Xcode replace the signature, and the memory entitlements cannot be
        # signed by a free Apple account.
        if [ -n "$ENTITLEMENTS" ]; then
            echo "This IPA carries entitlements, so it is not the unsigned build." >&2
            echo "Verify it with --trollstore or --trollstore-permanent-jit." >&2
            exit 1
        fi
        ;;
    trollstore|permanent)
        require_entitlement get-task-allow
        require_entitlement com.apple.developer.kernel.extended-virtual-addressing
        require_entitlement com.apple.developer.kernel.increased-memory-limit
        if [ "$EXPECT" = permanent ]; then
            require_entitlement dynamic-codesigning
        else
            # Shipping this in the general TrollStore build would crash the app
            # on launch for every A12 and newer device.
            refuse_entitlement dynamic-codesigning
        fi
        ;;
esac

# Personal signing material is unacceptable in either mode: ldid signs the
# executable in place and creates none of this.
if [ -e "$APP/embedded.mobileprovision" ] || [ -d "$APP/_CodeSignature" ]; then
    echo "Signing material was found inside the app." >&2
    exit 1
fi

if grep -R -a -l '/Users/' "$APP" >/dev/null 2>&1; then
    echo "A local macOS user path was found inside the app." >&2
    exit 1
fi

if find "$APP" -type f \( \
    -name '*.ipa' -o \
    -name '*.mobileprovision' -o \
    -name '*.mobiledevicepairing' -o \
    -name '*.p12' -o \
    -name '*.cer' \
\) -print | grep -q .; then
    echo "Private or nested package material was found inside the app." >&2
    exit 1
fi

INFO="$APP/Info.plist"
BUNDLE_ID=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$INFO")
VERSION=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$INFO")
BUILD=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$INFO")

if [ "$BUNDLE_ID" != "io.github.johnny901901901.applesauce" ]; then
    echo "Unexpected bundle identifier: $BUNDLE_ID" >&2
    exit 1
fi

file "$APP/Applesauce" | grep -q 'arm64'

echo "Verified $EXPECT IPA"
echo "Bundle: $BUNDLE_ID"
echo "Version: $VERSION ($BUILD)"
echo "Size: $(stat -f '%z' "$IPA") bytes"
shasum -a 256 "$IPA"
