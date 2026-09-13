# Applesauce — Install, JIT And Troubleshooting Guide

Applesauce is a native iOS app that plays supported 32-bit iPhone games on modern devices, through high-level emulation and the Dynarmic CPU backend.

The emulation is not this project's work. Applesauce ships two emulator cores — [HyperHLE](https://github.com/HyperHLE/HyperHLE) v1.0.6, a fork of touchHLE with broader game compatibility, and [touchHLE](https://github.com/touchHLE/touchHLE) 0.2.3 upstream — and adds the iOS app around them: the interface, the build system and the packaging. Applesauce is an unaffiliated fork, is not endorsed by either project, and includes no games or Apple software.

## At A Glance

| Item | Current status |
| --- | --- |
| App version | 0.4.1 |
| Emulator cores | HyperHLE v1.0.6 and touchHLE 0.2.3, switchable per game |
| Minimum target | iOS 15.0 |
| Tested environment | iPhone 16 Pro running iOS 27 beta 4 (24A5390f) |
| CPU backend | Dynarmic |
| JIT | Required whenever the app starts as a new process |
| Games | Not included; decrypted 32-bit IPAs are required |

The app currently provides:

- An Apple-style SwiftUI game library.
- IPA importing with the guest app's title and icon.
- A per-game core picker, plus a default core in Settings.
- Persistent settings and per-game save folders.
- Guest-aware portrait and landscape launch handling.
- A red in-game exit control that returns to the library.
- A StikDebug JIT shortcut.
- An optional FPS counter under **Settings → Advanced → Developer Tools**.

## Upgrading From touchHLE For iOS

This project was called *touchHLE for iOS* up to 0.3.0. 0.4.0 renames it to Applesauce and changes the bundle identifier, so it installs **alongside** the old app rather than replacing it, and starts with an empty library.

To move your games across:

1. Open the iOS Files app and go to **On My iPhone**.
2. Find the old app's folder. It is named *HyperHLE* if you had 0.2.0 or 0.3.0, or *touchHLE* if you had 0.1.0.
3. Copy `touchHLE_apps` into the **Applesauce** folder for your games.
4. Copy `touchHLE_sandbox` too for your saves, and `touchHLE_options.txt` if you customized game options. Back up any existing Applesauce saves before merging or replacing folders.
5. Check that your games and saves work in Applesauce before deleting the old app.

App-wide settings and per-game core selections are stored in the old app's preferences; set those again in Applesauce. Copying game files alone does not transfer saves or core selections.

## Screenshots

<table>
  <tr>
    <td><img src="Screenshots/library-games.png" alt="Applesauce library with imported game cards" width="260"></td>
    <td><img src="Screenshots/library-empty.png" alt="Empty Applesauce game library" width="260"></td>
  </tr>
  <tr>
    <td><img src="Screenshots/settings.png" alt="Applesauce settings screen" width="260"></td>
    <td><img src="Screenshots/about.png" alt="Applesauce about screen" width="260"></td>
  </tr>
</table>

Imported titles shown in screenshots are not all compatibility claims.

## Device And Game Testing

Applesauce has been personally tested on an **iPhone 16 Pro running iOS 27 beta 4** (build 24A5390f). Its deployment target is iOS 15.0, and it is intended to work on other iPhones and iOS versions, but those combinations have not all been verified yet.

**iOS 15 and 16 are entirely untested here.** That support is back-ported from [nerivalaitis](https://github.com/nerivalaitis)' work, which was tested on iOS 15; the developer of this project has no device older than an iPhone 16 Pro. Below iOS 16 the app also drives rotation through the device orientation rather than `requestGeometryUpdate`, so landscape behaviour is the most likely thing to differ there.

Confirmed on that device, on the HyperHLE core, with the exact app versions tested:

- Flappy Bird 1.1.0 — including at 2x, 3x and 4x resolution scale.
- Touch & Go 1.1 — at all resolution settings.
- Tony Hawk's Pro Skater 2 1.2.1.
- Wolfenstein RPG 1.1.1.
- Mirror's Edge 1.4.72.
- The Sims Medieval 1.0.1 — playable, but names cannot be entered (see Current Limitations).

The [touchHLE compatibility database](https://appdb.touchhle.org/) uses a star-rating system for specific app versions. Higher-rated entries are the best place to begin, but a high rating is not a guarantee that the same version has already been tested through Applesauce.

The Sims Medieval now reaches gameplay, which was the original goal of this project. It began after the developer gave his sister a new iPhone 17 Pro Max and discovered that the copy of The Sims Medieval she had legitimately purchased years ago could no longer be installed. Future compatibility work will focus on identifying and fixing the first missing emulator subsystem rather than changing the library UI.

## Current Limitations

- JIT is required. There is no no-JIT ARM interpreter.
- **The Sims Medieval:** no keyboard appears for naming your Sim or your kingdom, so those names cannot be entered. The game is playable past those screens; the confirm control sits near the top-right corner of the screen rather than where it is drawn.
- Games that render through an offscreen texture gain no extra detail from resolution scaling. The scale hack enlarges renderbuffers but not textures, so it is applied only where it is safe to do so.
- The touchHLE compatibility database describes touchHLE generally, not guaranteed behaviour through this app.
- Some games run under one core and not the other. If a game fails, switch its core and try again.
- Device and iOS-version coverage is still limited.
- Some games need emulator-side compatibility work even when the app itself is functioning.
- This is an early test build, not an App Store release.

## Acknowledgements

Applesauce exists because of the work of the [touchHLE contributors](https://github.com/touchHLE/touchHLE/graphs/contributors) and of [HyperHLE](https://github.com/HyperHLE/HyperHLE). The emulators are their projects; this one adds the native iOS app and iOS-specific integration fixes.

Thanks to [nerivalaitis](https://github.com/nerivalaitis) for the iOS 15 back-port, the TrollStore packaging and the guest memory-allocation fallback that makes older devices work.

Thanks also to Reddit user [u/WorriedEquipment2241](https://www.reddit.com/user/WorriedEquipment2241/) for publicly demonstrating a separate touchHLE iOS experiment on a jailbroken device. That demonstration helped show that the idea was viable and highlighted an important reality: compatibility still differs game by game. Applesauce does not claim to contain that unreleased port's source code.

## Which Build Do I Want?

JIT is what decides this, not the app itself:

| Your iOS | Download | How JIT gets enabled |
| --- | --- | --- |
| 17.4 or newer | `Applesauce-iOS-unsigned.ipa` | Sideload, then StikDebug's bolt button in the app |
| 15.0–17.0, TrollStore installed | `Applesauce-iOS-trollstore.ipa` | TrollStore's **Enable JIT**, before each session |
| 15.0–17.0, TrollStore, **A11 or older** | `Applesauce-iOS-trollstore-permanent-jit.ipa` | Already on, and stays on |
| 17.0.1–17.3 | — | Neither TrollStore nor StikDebug reaches these; AltJIT with a computer is the only route |

The TrollStore builds carry `com.apple.developer.kernel.extended-virtual-addressing` and `com.apple.developer.kernel.increased-memory-limit`. The emulator maps the guest address space as one flat 4GiB region, which older hardware cannot do without them, and a free Apple account cannot sign them — which is why those builds are TrollStore-only rather than a sideloading option.

**The permanent-JIT build crashes on launch on A12 and newer** (iPhone XS/XR onwards): iOS 15 bans `dynamic-codesigning` there. Use the ordinary TrollStore build on those devices.

## Install The Unsigned IPA

The public IPA must remain unsigned. It contains no Apple ID, certificate, provisioning profile, development team, device identifier, games, or saves. Your chosen install method signs it locally with your own Apple account. (The TrollStore IPAs are ad-hoc "fakesigned" so they can carry the entitlements above — they contain no personal signing material either.)

### Option A: AltStore Classic

This is the simplest public installation route.

1. Install [AltStore Classic](https://altstore.io/) and complete its normal AltServer setup.
2. Open **Sources → +** in AltStore and paste the [Applesauce source](https://raw.githubusercontent.com/johnny901901901/Applesauce/ios-host/distribution/altstore-source.json) URL below.
3. Open the source and choose **Applesauce**, rather than either superseded touchHLE listing.
4. Let AltStore sign and install it with your Apple account. Future published updates appear in AltStore.
5. Complete the [JIT setup](#enable-jit) before starting a game.

```text
https://raw.githubusercontent.com/johnny901901901/Applesauce/ios-host/distribution/altstore-source.json
```

The source uses the ordinary unsigned IPA, not either TrollStore build. Adding it does not enable JIT or change Apple's signing limits. It is an AltStore **Classic** source, not an AltStore PAL listing.

Manual installation still works: download `Applesauce-iOS-unsigned.ipa` from [GitHub Releases](https://github.com/johnny901901901/Applesauce/releases), then choose it in **My Apps → +**.

With a free Apple account, Apple limits Personal Team profiles to seven days and three installed apps per device. AltStore can refresh apps before they expire while it can reach AltServer. See [Apple's Personal Team limits](https://developer.apple.com/help/account/basics/about-your-developer-account) and [AltStore's refresh explanation](https://faq.altstore.io/altstore-classic/your-altstore).

A paid Apple Developer Program account provides longer-lived development signing and avoids the free Personal Team's weekly reprovisioning limit. It does **not** remove the JIT requirement.

### Option B: Build And Install With Xcode

This works with either a free Personal Team or a paid developer account.

1. Complete the [source prerequisites](#build-from-source).
2. Build the Debug Rust library:

   ```sh
   sh platform/ios/scripts/build-rust.sh aarch64-apple-ios Debug
   ```

3. Open `platform/ios/TouchHLEHost.xcodeproj`.
4. Select the **TouchHLEHost** target.
5. Under **Signing & Capabilities**, choose your own team.
6. Change the bundle identifier if Xcode says `io.github.johnny901901901.applesauce` is unavailable.
7. Select your iPhone and press **Run**.
8. Follow any Developer Mode or trust prompts shown by Xcode and the iPhone.
9. Complete the [JIT setup](#enable-jit) before starting a game.

Never commit or upload Xcode's signed app, provisioning profile, certificate, team ID, or `xcuserdata`.

## Enable JIT

Dynarmic requires executable memory, so installing the app is not enough by itself. JIT must be enabled again whenever Applesauce starts as a new process. JIT normally remains available until the app is force-quit or removed from memory.

### StikDebug And LocalDevVPN

The in-app bolt button uses StikDebug's URL scheme and its bundled `universal.js` script.

1. Install the current [StikDebug release](https://github.com/StephenDev0/StikDebug).
2. Create a pairing file by following the [AltStore JIT pairing guide](https://faq.altstore.io/altstore-classic/enabling-jit).
3. Import that pairing file into StikDebug.
4. Install and connect [LocalDevVPN](https://apps.apple.com/app/localdevvpn/id6755608044), or another loopback VPN supported by your StikDebug version.
5. Keep the iPhone awake, unlocked, connected to Wi-Fi, and connected to the loopback VPN.
6. Open Applesauce to the library and tap the **bolt** button.
7. Allow StikDebug to enable JIT for Applesauce, then return to the app and start the game.

The initial pairing setup needs a Mac or PC. After that, StikDebug is designed to enable JIT on-device. StikDebug currently supports iOS 17.4 and newer, with additional caveats for newer beta versions; check its own compatibility notes before troubleshooting Applesauce.

Treat the pairing file as private device material. Never upload or attach it to an issue.

### TrollStore

On iOS 15.0–17.0 with TrollStore installed, use one of the `-trollstore` IPAs above. Install it in TrollStore, then use TrollStore's **Enable JIT** on Applesauce before starting a game; it has to be redone whenever the app starts as a new process. The bolt button does not appear in these builds, because StikDebug cannot help below iOS 17.4.

On A11 and older devices the permanent-JIT build skips all of that — JIT is granted by the `dynamic-codesigning` entitlement and never has to be re-enabled. The app detects this and hides the JIT prompts entirely.

### AltJIT

AltStore users can instead follow the official [AltJIT instructions](https://faq.altstore.io/altstore-classic/altjit). In AltStore, long-press Applesauce under **My Apps** and choose **Enable JIT**. Current iOS versions may require extra Mac-side setup, and the device may need to remain connected until JIT has been enabled.

Installing through AltStore, SideStore, Sideloadly, or Xcode does not automatically provide JIT.

## Import Games

1. Open Applesauce and tap **Import Game**.
2. Select a decrypted 32-bit `.ipa` from Files.
3. The app imports the IPA, reads its app name and icon, and adds it to the library.
4. Check the [touchHLE compatibility database](https://appdb.touchhle.org/) for the exact app version before testing.
5. Enable JIT, then tap the game card.

Only use software you obtained legally. This project does not provide game downloads, decrypted executables, encryption keys, or instructions for bypassing copy protection.

Removing a title from the library removes the imported IPA but deliberately keeps its save folder.

## Saves And Backups

Guest files are stored inside the app container:

```text
Documents/touchHLE_sandbox/<guest-bundle-id>
```

That folder keeps its upstream name because both emulator cores read it by name.

Progress therefore survives returning to the library and normal app restarts. Deleting Applesauce from the device can delete the entire app container, including saves.

To back up saves:

1. Open the iOS Files app.
2. Browse to **On My iPhone → Applesauce**.
3. Copy the `touchHLE_sandbox` folder somewhere safe.

Do not publish saves with a release or attach them to bug reports without checking their contents.

## Troubleshooting

### The game stays on “Starting game…” or crashes immediately

- Re-enable JIT after every fresh Applesauce process.
- Confirm LocalDevVPN is connected and StikDebug has the correct pairing file.
- Confirm the imported IPA is decrypted, 32-bit, and the exact version listed in the compatibility database.
- Switch the game to the other core and try again.
- Retry with the app's default settings.

### StikDebug reports a tunnel or connection error

- Wake and unlock the iPhone.
- Confirm Wi-Fi and LocalDevVPN are connected.
- Reconnect LocalDevVPN, then retry.
- Replace the pairing file if the device was restored, updated, or re-paired.
- Check the current [StikDebug troubleshooting notes](https://github.com/StephenDev0/StikDebug).

### There is audio and touch input but the picture is blank or stretched

- Confirm you are on 0.2.0 or newer; it contains the iOS OpenGL ES presentation and landscape orientation fixes.
- Return to the library and start the game in its declared orientation.
- Record the exact game version, device, iOS version, and whether portrait titles render correctly.

### Touch does not respond in a landscape game

This was a bug in 0.1.0 and is fixed in 0.2.0 — update before investigating further. Each game is also locked to its launch orientation, because older games often assume a fixed screen layout, so if a game launched in the wrong orientation, return to the library, hold the phone the way you want, and launch again.

### The app no longer opens

If it was signed with a free Apple account, refresh or reinstall it before the seven-day profile expires. Reinstalling the app can risk the app container, so back up saves first.

## Logs

Runtime output is written to:

```text
Documents/touchhle-host.log
```

The log is visible under **On My iPhone → Applesauce** because file sharing is enabled. Before sharing it, check it for game names, local paths, or other personal data.

A useful issue report includes:

- iPhone model and iOS version.
- Applesauce version and install method.
- Which core the game was set to.
- Whether JIT was confirmed enabled.
- Exact guest app title and version, but not the IPA itself.
- Reproduction steps.
- The relevant log excerpt.

Never attach games, saves, pairing files, certificates, provisioning profiles, signed IPAs, or device backups.

## Build From Source

### Prerequisites

- macOS with Xcode 26 or newer and its command-line tools.
- Stable Rust installed through [rustup](https://rustup.rs/).
- CMake and Ninja.
- Python 3 for packaging and release validation.
- Boost headers.

Homebrew can install the non-Xcode dependencies:

```sh
brew install cmake ninja boost python
rustup target add aarch64-apple-ios
rustup target add aarch64-apple-ios-sim
```

The scripts look for Boost under `vendor/boost` by default. To use Homebrew's headers:

```sh
export TOUCHHLE_BOOST_ROOT="$(brew --prefix boost)/include"
```

If Xcode is installed somewhere other than `/Applications/Xcode.app`:

```sh
export DEVELOPER_DIR="/Applications/Xcode-beta.app/Contents/Developer"
```

### Unsigned Release Build

```sh
sh platform/ios/scripts/build-host.sh iphoneos Release
sh platform/ios/scripts/package-ipa.sh
```

The outputs are:

```text
build/host-iphoneos/Build/Products/Release-iphoneos/Applesauce.app
dist/Applesauce-iOS-unsigned.ipa
dist/Applesauce-iOS-unsigned.ipa.sha256
```

The packaging script refuses to package a signed app.

### TrollStore Builds

Same app, different entitlements, applied by fakesigning with `ldid`
(`brew install ldid`):

```sh
sh platform/ios/scripts/package-ipa.sh --trollstore
sh platform/ios/scripts/package-ipa.sh --trollstore-permanent-jit
```

Verify each with the matching flag:

```sh
sh platform/ios/scripts/verify-ipa.sh
sh platform/ios/scripts/verify-ipa.sh --trollstore dist/Applesauce-iOS-trollstore.ipa
sh platform/ios/scripts/verify-ipa.sh --trollstore-permanent-jit dist/Applesauce-iOS-trollstore-permanent-jit.ipa
```

`codesign` cannot tell these three apart — ldid writes a CodeDirectory with an
empty CMS blob, which it reports as "no signature" exactly like a genuinely
unsigned app. So the check reads the embedded entitlements back with `ldid -e`
instead: the plain IPA must have none, and the permanent-JIT entitlement must
appear in exactly one of them.

### Changing The Deployment Target

Cargo does not treat `IPHONEOS_DEPLOYMENT_TARGET` as a build input, so changing
it leaves already-built objects — including the C++ ones from Dynarmic — at the
old minimum. `build-rust.sh` keeps a stamp and starts that target triple over
when it changes, and both it and `embed-cores.sh` refuse to ship a core whose
`minos` does not match the app's. A core built for a newer iOS than the app
claims will not load at all on the devices the app says it supports.

### Simulator Build

```sh
sh platform/ios/scripts/build-host.sh iphonesimulator Debug
```

Dynarmic and JIT behavior differs between a simulator and a physical iPhone, so final gameplay testing must happen on a device.

## Upstream Relationship

Applesauce is published as a GitHub fork so the original history, contributors, and licenses remain visible. It is not an official touchHLE or HyperHLE release, and neither project is affiliated with it.

## License And Credits

The emulator source is licensed under MPL-2.0, while binary distribution is covered by GPL-3.0-or-later due to dependency licensing. The repository's existing license files, copyright headers and attribution are preserved unchanged.

Credit the touchHLE contributors, HyperHLE, Dynarmic, SDL, StikDebug, LocalDevVPN, and the other dependencies listed by touchHLE. Applesauce is not affiliated with Apple.
