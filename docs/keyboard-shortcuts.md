# Keyboard Shortcuts

Status: Working reference for OS-level shortcuts.

Use this page when you need to know which key combination launches each feature and which setting controls it.

## Inspect Effective Shortcuts

The quickest source of truth is the CLI. It reads the current `.env` through `ToolRunnerSettings`.

```bash
poetry run so-intelligence-tools show-shortcuts
```

Filter by platform:

```bash
poetry run so-intelligence-tools show-shortcuts --platform linux
poetry run so-intelligence-tools show-shortcuts --platform windows
poetry run so-intelligence-tools show-shortcuts --platform desktop
```

If you change `.env`, restart any already-running listener or service before expecting the new shortcut to take effect.

## Linux / GNOME

| Feature | Default | Setting | Mechanism |
| --- | --- | --- | --- |
| Selected text correction | `<Primary><Alt>c` | `GNOME_SELECTED_TEXT_CORRECTION_BINDING` | GNOME custom shortcut |
| System audio translation | `<Primary><Alt>y` | `GNOME_SYSTEM_AUDIO_TRANSLATION_BINDING` | GNOME custom shortcut |
| Voice translation virtual microphone | `<Primary><Alt>u` | `GNOME_VOICE_TRANSLATION_BINDING` | GNOME custom shortcut |
| Push-to-talk dictation | `<ctrl>+<shift>+<space>` | `PUSH_TO_TALK_DICTATION_SHORTCUT` | Press-and-hold listener service |

Linux currently uses two shortcut syntaxes because GNOME custom shortcuts and Python press-and-hold listeners expect different formats.

The Linux dictation shortcut intentionally uses `Ctrl + Shift + Space` instead of the older `Ctrl + Space`. The Linux installer performs best-effort cleanup for known old `Ctrl + Space` conflicts in IBus/GNOME settings and Ulauncher, but desktop shell shortcuts cannot always be suppressed by the listener itself.

## Windows

| Feature | Default | Setting | Mechanism |
| --- | --- | --- | --- |
| Open overlay | `Ctrl + Alt + A` | Windows shell shortcut | Electron desktop launcher |
| Selected text correction | `<ctrl>+<alt>+c` | `WINDOWS_SELECTED_TEXT_CORRECTION_SHORTCUT` | Windows global shortcut listener |
| Push-to-talk dictation | `<ctrl>+<shift>+<space>` | `WINDOWS_PUSH_TO_TALK_DICTATION_SHORTCUT` | Press-and-hold listener |

`Ctrl+Alt+A` launches the Electron app; the app single-instance handler toggles the existing overlay when it is already running. `Ctrl+Shift+Space` is used by the Windows project dictation listener to avoid common `Ctrl+Space` operating-system shortcut collisions.

## Desktop Overlay Settings

The Electron overlay has its own `desktop-settings.json` stored in Electron user data. Those entries are visible/editable in the overlay settings UI, but not every entry is currently registered as an OS-level global shortcut.

| Feature | Default | Source | Status |
| --- | --- | --- | --- |
| Open overlay | `Ctrl + Alt + A` | `desktop-settings.json` | UI setting; Windows launcher shortcut |
| Selected text correction | `Ctrl + Alt + C` | `desktop-settings.json` | UI setting; OS listener uses platform `.env` |
| Screenshot OCR | `Ctrl + Alt + O` | `desktop-settings.json` | Planned |
| System audio translation | `Ctrl + Alt + T` | `desktop-settings.json` | UI setting; Linux OS shortcut uses `.env` |
| Voice translation virtual microphone | `Ctrl + Alt + M` | `desktop-settings.json` | UI setting; Linux OS shortcut uses `.env` |
| Push-to-talk dictation | `Ctrl + Shift + Space` | `desktop-settings.json` | Planned/UI setting; OS listener uses platform `.env` |
| Assistant | `Sin asignar` | `desktop-settings.json` | Planned; `Ctrl + Alt + A` is reserved for the overlay |
| Summary | `Ctrl + Alt + R` | `desktop-settings.json` | Planned |
| Intelligent capture | `Ctrl + Alt + I` | `desktop-settings.json` | Planned |

For operational shortcuts, prefer the `.env` variables listed above and verify with `show-shortcuts`.
