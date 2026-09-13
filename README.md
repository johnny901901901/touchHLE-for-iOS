<p align="center">
  <img src="branding/banner.png" alt="Applesauce — A playful emulator for iOS" width="760">
</p>

# Applesauce

**A playful emulator for iOS.** It plays supported 32-bit iPhone games on modern
iPhones — **no jailbreak required**, though JIT is. It installs and runs on
iPadOS too, but every game runs as an iPhone guest for now: the core's iPad
device families are not yet reachable from the app.

Applesauce is an **unaffiliated fork**. The emulation is entirely the work of
[touchHLE](https://github.com/touchHLE/touchHLE) and its fork
[HyperHLE](https://github.com/HyperHLE/HyperHLE); this project is the iOS app
built around them — the interface, the build system and the packaging. Neither
project is connected to Applesauce or endorses it, so please report problems
here rather than to them. No games or Apple software are included.

**One app, two emulator cores.** They support different sets of games, so both
ship inside the app and you choose which one runs each game:

| Core | Version | |
| --- | --- | --- |
| **HyperHLE** | [v1.0.6](https://github.com/HyperHLE/HyperHLE) | Runs more games, including The Sims Medieval |
| **touchHLE** | 0.2.3 | The original emulator |

Neither is strictly better. Set the default in Settings, or touch and hold a game
in your library to give that game its own core.

| | |
| --- | --- |
| Latest build | 0.4.1 |
| Emulator cores | HyperHLE v1.0.6 and touchHLE 0.2.3, switchable per game |
| Minimum iOS | 15.0 |
| Tested on | iPhone 16 Pro, iOS 27 beta 4 (24A5390f) |
| JIT | Required each time the app starts as a new process |
| Games | Not included — bring your own decrypted 32-bit IPA |

## Install With AltStore Classic

In AltStore Classic, open **Sources → +** and paste the
[Applesauce source](https://raw.githubusercontent.com/johnny901901901/Applesauce/ios-host/distribution/altstore-source.json) URL:

```text
https://raw.githubusercontent.com/johnny901901901/Applesauce/ios-host/distribution/altstore-source.json
```

Install **Applesauce** from the source. Future releases appear in AltStore,
so you can update without downloading each IPA manually. Normal signing,
refresh and JIT requirements still apply. This source is for **AltStore Classic**;
the TrollStore builds remain separate downloads.

**[Installation and JIT setup](platform/ios/README.md#install-the-unsigned-ipa)**

## Which build do I want?

JIT is the thing that decides this, not the app. Pick the row that matches your
device:

| Your iOS | Download | How JIT gets enabled |
| --- | --- | --- |
| 17.4 or newer | `Applesauce-iOS-unsigned.ipa` | Sideload with AltStore, then StikDebug's bolt button in the app |
| 15.0–17.0, TrollStore installed | `Applesauce-iOS-trollstore.ipa` | TrollStore's **Enable JIT**, before each session |
| 15.0–17.0, TrollStore, **A11 or older** (iPhone X / 8 and earlier) | `Applesauce-iOS-trollstore-permanent-jit.ipa` | Already on, and stays on |
| 17.0.1–17.3 | — | Neither TrollStore nor StikDebug reaches these. AltJIT with a computer attached is the only route |

**The permanent-JIT build crashes on launch on A12 and newer** (iPhone XS/XR
onwards) — iOS 15 bans the entitlement it carries. Use the ordinary TrollStore
build there.

**iOS 15 and 16 have not been tested by this project's developer**, who has one
iPhone on iOS 27. That support is back-ported from
[nerivalaitis](https://github.com/nerivalaitis)' work, which was tested on iOS
15. Below iOS 16 the app also has to drive rotation a different way, so if a
landscape game misbehaves there, that is the first thing to say in a report.

## Upgrading from touchHLE for iOS

This project was called *touchHLE for iOS* up to 0.3.0. 0.4.0 renames it to
Applesauce and changes the bundle identifier, so it installs **alongside** the
old app instead of replacing it, with an empty game library.

To bring your games across, open Files and go to *On My iPhone*. The old app's
folder is named after whichever version you have — *HyperHLE* for 0.2.0 and
0.3.0, *touchHLE* for 0.1.0. Copy both `touchHLE_apps` (games) and
`touchHLE_sandbox` (saves) into the *Applesauce* folder. Copy
`touchHLE_options.txt` too if you customized game options. Check that your games
and saves work in Applesauce before deleting the old app.
App-wide settings and per-game core selections are stored in the old app's
preferences and must be set again. Do not replace an existing Applesauce saves
folder without backing it up first.

## Screenshots

| Library | Settings | About |
| --- | --- | --- |
| ![Game library](platform/ios/Screenshots/library-games.png) | ![Settings](platform/ios/Screenshots/settings.png) | ![About](platform/ios/Screenshots/about.png) |

Games shown are not included and must be supplied by you.

## Install

Download the IPA for your device from the
[latest release](https://github.com/johnny901901901/Applesauce/releases) — see
[Which build do I want?](#which-build-do-i-want) above.

`Applesauce-iOS-unsigned.ipa` is sideloaded with AltStore Classic, or built and
signed yourself in Xcode; enable JIT with
[StikDebug](https://github.com/StephenDev0/StikDebug) + LocalDevVPN, or AltJIT.
The two `-trollstore` IPAs are installed by TrollStore, which grants the memory
entitlements older devices need and, on the ordinary one, the **Enable JIT**
option.

**[Full install, JIT, import and troubleshooting guide →](platform/ios/README.md)**

A free Apple account works, with Apple's usual seven-day signing limit. A paid
developer account signs for longer but does not remove the JIT requirement.

## What works

Tested on the **HyperHLE** core, on an iPhone 16 Pro running iOS 27 beta 4
(build 24A5390f). Exact app versions matter — the same game can behave very
differently between releases, and between the two cores:

| Game | Version | Status |
| --- | --- | --- |
| Flappy Bird | 1.1.0 | Playable, including at 2x–4x resolution scale |
| Touch & Go | 1.1 | Playable at all resolution settings |
| Tony Hawk's Pro Skater 2 | 1.2.1 | Playable |
| Wolfenstein RPG | 1.1.1 | Playable |
| Mirror's Edge | 1.4.72 | Playable |
| The Sims Medieval | 1.0.1 | Playable, but see below |

Only one device has been tested, and only on an iOS **beta**. No shipping iOS
release has been verified yet, so reports from stable iOS 17.4+ are especially
useful — and reports from iOS 15 and 16, which nobody here can test at all, more
so.

## Known issues

- **The Sims Medieval:** no keyboard appears when naming your Sim or your kingdom,
  so those names cannot be entered. The game is still playable past those screens —
  the confirm control sits near the top-right corner rather than where it is drawn.
- JIT is required; there is no interpreter fallback.
- Games rendering through an offscreen texture gain no extra detail from resolution
  scaling, which is applied only where it is safe to do so.
- A high rating in the [compatibility database](https://appdb.touchhle.org/)
  describes touchHLE generally and does not guarantee behaviour through this app.
- Some games run under one core and not the other. Call of Duty: Zombies has been
  reported working under touchHLE 0.2.3 but not under HyperHLE. If a game fails,
  switch its core and try again before reporting it.

## Reporting a game

[Open an issue](https://github.com/johnny901901901/Applesauce/issues/new/choose) using
the compatibility report form. Please include the exact app version, your iPhone
model and iOS version, whether JIT was enabled, the Applesauce version, and a log
excerpt (`touchHLE_log.txt`, reachable in Files under *On My iPhone → Applesauce*).

**Do not post IPA files or links to them, pairing files, signing certificates,
provisioning profiles or device backups.**

## Building

See [platform/ios/README.md](platform/ios/README.md#build-from-source). In short:

```sh
git clone --recurse-submodules https://github.com/johnny901901901/Applesauce.git
cd Applesauce
sh platform/ios/scripts/build-sdl-shared.sh iphoneos
sh platform/ios/scripts/build-host.sh iphoneos Release
```

To produce the release IPAs (the TrollStore ones need `brew install ldid`):

```sh
sh platform/ios/scripts/package-ipa.sh
sh platform/ios/scripts/package-ipa.sh --trollstore
sh platform/ios/scripts/package-ipa.sh --trollstore-permanent-jit
```

That builds an app carrying the HyperHLE core alone. For the touchHLE core as
well, check out [`johnny901901901/touchHLE`](https://github.com/johnny901901901/touchHLE)
at branch `ios-core-dylib` beside it and point the build at it:

```sh
TOUCHHLE_CORE_REPO=../touchHLE sh platform/ios/scripts/build-host.sh iphoneos Release
```

The app ships whichever cores were built; the picker appears only when there is
more than one.

`vendor/dynarmic` points at a fork carrying the changes needed to run the arm64 JIT
inside a signed iOS app (MAP_JIT / W^X handling), so the `--recurse-submodules` part
matters.

Core file and folder names (`touchHLE_apps`, `touchHLE_options.txt`,
`touchHLE_log.txt`) keep their upstream spelling on purpose: both cores read them
by name, and renaming them would break every existing library.

## Credits

- [touchHLE](https://github.com/touchHLE/touchHLE) — the original emulator, and the
  work this rests on entirely.
- [HyperHLE](https://github.com/HyperHLE/HyperHLE) — the compatibility fork used as
  this build's default core.
- [nerivalaitis](https://github.com/nerivalaitis) — the iOS 15 back-port, TrollStore
  packaging and the guest memory-allocation fallback that makes older devices work.
- [u/WorriedEquipment2241](https://www.reddit.com/user/WorriedEquipment2241/) for
  publicly demonstrating a separate touchHLE iOS experiment on a jailbroken device,
  which helped show the direction was worth pursuing.

Licensed under MPL-2.0, subject to the existing third-party licence requirements.
Upstream copyright headers and the licence are unchanged. touchHLE and HyperHLE are
the names of those projects and are used here only to identify them.
