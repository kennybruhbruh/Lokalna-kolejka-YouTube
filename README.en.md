[Polski](README.md) | **English**

# YouTube Local Queue

A YouTube tweak that creates a local video queue. It also works in LiveContainer and in IPAs with an injected dylib.

## Features

- Add videos to the local queue from the context menu (the "Add to queue" action)
- Automatically move on to the next video when the current one ends
- Background playback without waking the screen
- Support for the "next" button on the lock screen and in Control Center
- Queue management: view, reorder, remove
- Settings inside the YouTube settings (the "Local Queue" section)

## How it works

The tweak does not use Cydia Substrate. It relies entirely on method swizzling in the Objective-C runtime, so it can be loaded in environments without a jailbreak.

### Adding to the queue

The tweak replaces the handler of the native "Add to queue" action (formerly "Play next in queue"), extracts the video identifier from the tapped item and stores it in the local queue. Action names are matched against a list of titles in many languages.

### Auto advance

The tweak hooks into YouTube's native autonav/autoplay mechanism:

1. Hooks on `nextEndpointForAutonav`, `nextEndpointForAutoplay`, `autonavEndpoint` and `autoplayEndpoint` return the next video from the queue instead of recommendations.
2. Hooks on `playNext`, `playAutonav` and `playAutoplay` take the item off the queue when moving on.
3. The native transition also works in the background, without waking the screen.
4. Seeking to the end of a video advances the queue as well.

## Building

The YouTube headers are required in the `Headers/YouTubeHeader` directory (the PoomSmart/YouTubeHeader repository). The workflows in `.github/workflows` download them automatically.

```bash
make package THEOS_PACKAGE_SCHEME=rootless
```

## Usage

1. Build the dylib or download it from the GitHub Actions artifacts.
2. Load it in LiveContainer (Tweaks folder) or inject it into an IPA.
3. You will find the settings under YouTube Settings → Local Queue.

## Settings

- **Auto advance**: plays the next item from the queue when a video ends
- **Show Play Next button** / **Show Queue button**: buttons in the player overlay
- **Open Local Queue**: view and manage the queue
- **Clear Local Queue**: removes all items

## Changelog

### 0.0.3
- Fix: "Add to queue" opened the YouTube Premium ad, because newer YouTube renamed the native action.
- Fix: crash when changing settings, caused by a wrong signature of the `sendActionsForControlEvents:` hook.
- The `setHidden:` and `setRelatedVideosVisible:` hooks are installed only once, and only when the class implements the method itself.
- Fix: with auto advance enabled, the current video was replayed instead of the next one from the queue (stale ID of the "taken" item).
- Fix: a double transition (native autonav + our own navigation) could skip a queue item.
- Fix: adding to the queue from some places (e.g. a channel's "Videos" tab) failed or added the video you were currently watching. The video ID is now read from the menu's own data, and when that is not possible the tweak no longer adds the current video blindly.
- New: the "Diagnostics" option in the settings copies the menu data to the clipboard when the video cannot be determined.
- The dylib is built for arm64 only, with the install name `@rpath/YTLocalQueue.dylib` (better compatibility with the injectors in Feather/FlareStore).
- Interface translated to Polish.
- New: translation system. The strings live in `Localization/*.strings` and are embedded into the dylib at build time; anyone can add their own language (see TRANSLATING.md). Polish is the first translation.

## Known issues

- Moving on to the next video may not work in every scenario.
- End-of-video detection can be unreliable in some cases.

## License

MIT
