# Design

## View Split

`App.vue` becomes a small view selector:

- default view: overlay launcher
- `?view=translator`: existing realtime translator UI

The old translator markup moves to `TranslatorView.vue` so the new overlay can be implemented without deleting the existing realtime translation capability.

## Overlay Layout

The overlay view renders a fixed 1280x720 scene matching the provided reference:

- faux desktop wallpaper and top/bottom bars
- background document window
- centered glass launcher panel
- right glass settings panel
- eight launcher actions
- shortcut editor rows
- startup and always-visible toggles

## Styling Approach

The mockup relies on translucent dark glass panels over a desktop background. The implementation uses CSS backdrop filters, layered backgrounds, subtle borders, and controlled fixed dimensions. Icons come from `@lucide/vue`; no new package is required.

## Risks

- Exact pixel parity with the source image is limited by available fonts, OS rendering, and the fact that this is a real Vue layout rather than a flat image.
- Backdrop blur requires browser/Electron support. The implementation keeps solid translucent fallback colors.
