# Applesauce 0.4.1

This update improves the library, game-session cleanup and AltStore Classic
distribution. It keeps the same bundle identifier as 0.4.0, so it updates an
existing Applesauce installation and retains its library and saves.

## Install and update with AltStore Classic

In AltStore Classic, open **Sources → +** and add:

```text
https://raw.githubusercontent.com/johnny901901901/Applesauce/ios-host/distribution/altstore-source.json
```

Choose **Applesauce** from the source. Future releases appear in AltStore;
you do not have to download a new IPA manually each time. Signing, refresh and
JIT requirements still apply. The source does not enable JIT automatically.

[Full installation and JIT guide](https://github.com/johnny901901901/Applesauce/blob/ios-host/platform/ios/README.md)

## Fixes

- Importing copies files away from the main UI thread and coordinates access
  with Files providers such as iCloud Drive. A failed copy is cleaned up before
  it can appear as a partially imported game.
- Repeated taps cannot queue overlapping game launches. Library reloads are
  also suppressed while a game or import is active.
- Malformed game metadata that causes the HyperHLE parser to panic is caught
  at the native bridge. The library uses this parser regardless of the chosen
  gameplay core and falls back to a filename when metadata is unreadable.
- The FPS timer no longer retains the game-controls screen after exiting.
- The exit button respects the screen's safe area, and returning to the
  library uses the iOS 15 orientation fallback too.
- A core that fails to load all required entry points releases its library
  handle instead of leaking a new reference on every retry.
- Building a second core copies only that core, avoiding accidental overwrite
  of a newer core with a stale file from another checkout.
- Release verification now checks embedded libraries for personal signatures
  and checks that required TrollStore entitlements are actually enabled.
- Migration instructions include saves and correctly explain which settings
  need to be reselected.

The AltStore source is checked against the unsigned IPA's version, build,
minimum iOS, size, checksum and permissions. A release workflow updates the
source for future published releases; prereleases and TrollStore packages are
excluded from that automatic update.

## Downloads

- **Applesauce-iOS-unsigned.ipa:** AltStore Classic and other ordinary sideloaders.
- **Applesauce-iOS-trollstore.ipa:** the existing TrollStore route for supported
  older iOS devices, with JIT enabled through TrollStore.
- **Applesauce-iOS-trollstore-permanent-jit.ipa:** A11 and older only. Do not
  install this variant on A12 or newer devices.

The emulator versions remain HyperHLE v1.0.6 and touchHLE 0.2.3. This release
does not claim additional game compatibility or fix the known Sims Medieval
keyboard/input issues. The existing gameplay reports are from earlier builds;
fresh device regression testing of 0.4.1 is still needed.

No games are included. Full credit for emulation belongs to
[touchHLE](https://github.com/touchHLE/touchHLE) and
[HyperHLE](https://github.com/HyperHLE/HyperHLE). Applesauce is an independent,
unofficial port.
