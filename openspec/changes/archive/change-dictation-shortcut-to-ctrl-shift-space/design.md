## Context

The current working tree moved Linux dictation from the older `Ctrl + Alt + Space` default to `Ctrl + Space` and added best-effort IBus cleanup for that conflict. User testing shows `Ctrl + Space` is still a poor default because it can activate accidentally while typing and collides with an operating-system search/input-method shortcut.

Repository history does not show a prior `Ctrl + Shift + Space` implementation. Earlier defaults were `Ctrl + Alt + Space` for Linux/Nemotron-era dictation, `Ctrl + Shift + D` in a legacy desktop setting migration path, and `Ctrl + Space` in the current Whisper/Windows path.

## Goals / Non-Goals

**Goals:**

- Make `Ctrl + Shift + Space` the default push-to-talk dictation shortcut for Linux and Windows.
- Keep the shortcut configurable through existing environment variables.
- Make the press-and-hold listener parse and match `Shift` reliably.
- Keep docs, shortcut map output, desktop defaults, and legacy settings migration aligned.

**Non-Goals:**

- Rework shortcut registration architecture.
- Change selected-text correction shortcuts or other tool bindings.
- Remove the ability for users to override dictation shortcuts in `.env`.

## Decisions

- Use `Ctrl + Shift + Space` rather than returning to `Ctrl + Alt + Space`. `Ctrl + Shift + Space` directly addresses the current collision while preserving the user's requested muscle memory around `Ctrl + Space`; `Ctrl + Alt + Space` was the previous Linux default but is not the requested target.
- Update both Linux and Windows dictation defaults. The issue was reported from the current setup, and the product docs currently present `Ctrl + Space` as the shared default, so a split default would make the docs and overlay harder to reason about.
- Add explicit `Shift` support to `_parse_shortcut` and `_normalize_key`. The listener currently handles `ctrl`, `alt`, and `space` directly; relying on raw key names like `shift_l` would make the new shortcut unreliable.
- Change desktop settings migration so legacy `Ctrl + Space`, `Ctrl + Shift + D`, and `Ctrl + Alt + Space` dictation values move to `Ctrl + Shift + Space` when they still match known defaults.
- Leave IBus `Ctrl + Space` cleanup code in place only if already present, but stop documenting it as required for the active dictation default. Removing it can be handled separately if desired.

## Risks / Trade-offs

- Persisted user settings may intentionally keep `Ctrl + Space` if the value is no longer recognized as a legacy default. Mitigation: migrate known old defaults and keep `.env` as the source for OS listeners.
- `Ctrl + Shift + Space` may conflict with some applications. Mitigation: keep both platform shortcut env vars configurable and document the setting names.
- Active systemd/user services need a restart to pick up the new `.env` or code defaults. Mitigation: document restarting/reinstalling the dictation listener as part of validation notes.
