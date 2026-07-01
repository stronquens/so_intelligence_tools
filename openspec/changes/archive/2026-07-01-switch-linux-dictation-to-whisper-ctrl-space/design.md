## Context

The current code already routes dictation through `faster_whisper_http` and starts `docker/whisper-server` from the Linux service installer. This change originally moved Linux defaults from `Ctrl + Alt + Space` to `Ctrl + Space`, but `change-dictation-shortcut-to-ctrl-shift-space` now supersedes the active default with `Ctrl + Shift + Space` because `Ctrl + Space` collides with OS search/input-method shortcuts.

## Goals / Non-Goals

**Goals:**

- Move Linux push-to-talk dictation off the old `Ctrl + Alt + Space` shortcut.
- Keep faster-whisper HTTP as the active runtime.
- Clear known native Ubuntu `Ctrl + Space` hotkeys during install without failing on systems that do not expose those schemas.
- Update docs/tests so the Linux and Windows shortcut story is consistent.

**Non-Goals:**

- Do not reintroduce Nemotron runtime code.
- Do not remove the Nemotron backup documentation.
- Do not add a graphical shortcut editor in this change.

## Decisions

- Change `PUSH_TO_TALK_DICTATION_SHORTCUT` away from the old `<ctrl>+<alt>+<space>` default.
- Add best-effort GNOME/IBus conflict cleanup to `LocalApiUserServiceInstaller`.
- Keep cleanup non-fatal when `gsettings` or the relevant schema/key is missing.
- Preserve user overrides: if a user sets a different shortcut in `.env`, the listener uses it.

## Risks / Trade-offs

- Clearing IBus hotkeys changes a desktop preference. This is intentional for the requested machine setup, but users who rely on IBus activation may need to choose another IBus shortcut.
- Global key capture still depends on the Linux/X11 listener limitations.
