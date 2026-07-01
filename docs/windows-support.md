# Windows Support

Windows support started with text-focused desktop adapters and now includes the main overlay launcher plus local push-to-talk dictation.

## Current Status

Implemented in the first Windows adapter slice:

- clipboard read/write through Win32 APIs
- keyboard copy/paste automation through Win32 APIs
- selected text discovery through a clipboard roundtrip
- corrected text insertion through clipboard + paste
- best-effort notification feedback
- platform-aware runtime selection for selected text correction
- selected text correction shortcut listener through native Win32 `RegisterHotKey`
- local push-to-talk dictation listener through a press-and-hold keyboard hook
- microphone capture through PortAudio / `sounddevice`
- local ASR runtime warm-up/check for dictation
- faster-whisper HTTP dictation backend backed by a warm Docker server
- Electron overlay launcher with Windows single-instance toggle behavior
- independent Electron settings window with persisted shortcut rows in Electron user data
- independent Electron translator shell launched from the main overlay `Traducir audio` card
- application icon applied to Electron windows and the desktop shortcut
- hidden user-level Startup launcher for the local inference API
- hidden user-level Startup launcher for the shortcut listener
- hidden user-level Startup launcher for the dictation listener

This means selected text correction, overlay launch and dictation can be useful on Windows while keeping shared application logic independent from the operating system.

## Not Yet Supported

The following Windows integrations are not implemented yet:

- screenshot region capture
- system audio loopback capture
- translated virtual microphone output
- Piper/Codex voice-output playback through the Linux `scripts/codex-tts-wrapper.py` path

Audio support needs a separate design because the Linux implementation currently relies on PulseAudio-compatible tools such as `pactl`, `parec` and `pacat`. Windows will need a different backend, likely based on WASAPI for capture and an explicit virtual audio device strategy for microphone output.

Local Piper TTS voice output is also Linux-validated only at the moment. The Docker HTTP service may be portable, but Windows still needs validation for audio playback, Docker Desktop behavior, the VS Code Codex wrapper path and per-window session-state storage. The Linux setup is documented in [Piper TTS Voice Output](piper-tts-voice-output.md).

The current research plan is documented in [Windows Audio Routing Research](windows-audio-routing.md). The recommended first Windows audio slice is WASAPI loopback for system audio capture plus an installed virtual audio cable driver, such as VB-CABLE, for translated virtual microphone output.

## Practical Notes

The first Windows text adapters use normal `Ctrl+C` and `Ctrl+V` automation against the focused application. Some applications, elevated windows, secure desktops or focus transitions may block that automation. When replacement cannot complete, the existing selected text correction flow can still preserve the corrected text on the clipboard as a fallback.

If no text is selected, the Windows selection adapter tries `Ctrl+A` and then copies again. In normal text inputs this selects the whole focused field before correction. In larger editors it may select the whole document, depending on how that application handles `Ctrl+A`.

## Main Overlay Shortcut

The current Windows overlay shortcut is:

```text
Ctrl + Alt + A
```

This shortcut launches the Electron app. Electron keeps a single app instance, so pressing the shortcut again toggles the existing overlay instead of spawning unlimited windows.

The launcher, settings and translator shell are separate Electron windows. The main launcher window is sized to the visible overlay panel rather than to a large transparent desktop canvas, so it should not intercept clicks meant for the settings window.

The overlay settings UI also shows `Ctrl + Alt + A` for `Abrir overlay`. Those desktop settings are stored in Electron `desktop-settings.json`; they are visible configuration state, but OS-level listeners still use their own Windows or Linux registration paths.

The desktop shortcut is installed on the redirected Windows Desktop at:

```text
D:\Users\Armando\Desktop\so_intelligence_tools Overlay.lnk
```

It uses the project icon at:

```text
C:\Dev\Active\so_intelligence_tools\assets\branding\app-icon.ico
```

## Selected Text Correction Shortcut

The default Windows shortcut is:

```text
Ctrl + Alt + C
```

To inspect effective Windows shortcuts and their configuration source:

```powershell
poetry run so-intelligence-tools show-shortcuts --platform windows
```

Run the listener manually for the current session:

```powershell
cd C:\Dev\Active\so_intelligence_tools
poetry run so-intelligence-tools listen-shortcuts
```

Install the listener in the current user's Windows Startup folder:

```powershell
cd C:\Dev\Active\so_intelligence_tools
poetry run so-intelligence-tools install-windows-shortcut-listener-startup
```

Install the local inference API in the same Startup folder:

```powershell
cd C:\Dev\Active\so_intelligence_tools
poetry run so-intelligence-tools install-windows-api-startup
```

After installing the Startup entries, either sign out and back in or run the API and listener manually once for the current session.

The Startup installers write user-level hidden `.vbs` launchers and do not require administrator privileges. The API and listener still run after login, but they should not leave black Python terminal windows open on the desktop.

Background logs are appended here:

```text
%LOCALAPPDATA%\so_intelligence_tools\logs\so-intelligence-tools-api.log
%LOCALAPPDATA%\so_intelligence_tools\logs\so-intelligence-tools-shortcuts.log
%LOCALAPPDATA%\so_intelligence_tools\logs\so-intelligence-tools-dictation.log
```

If the shortcut stops responding, check Task Manager for the Python processes or inspect those logs before reinstalling the Startup entries.

The listener expects the local inference API and Ollama to be available. A working local
configuration should point `OLLAMA_MODEL` at an installed model, for example
`gemma4-e2b-longctx:latest` on this Windows machine.

For a warmer shortcut experience, enable API startup warm-up and use a longer Ollama keep-alive:

```env
OLLAMA_KEEP_ALIVE=24h
OLLAMA_WARMUP_ON_STARTUP=true
```

Ollama itself should also be configured to start at login. The standard Ollama Windows installer normally creates an `Ollama.lnk` entry in the user's Startup folder.

## Push-To-Talk Dictation

The default Windows dictation shortcut is:

```text
Ctrl + Shift + Space
```

Run the dictation listener manually for the current session:

```powershell
cd C:\Dev\Active\so_intelligence_tools
poetry run so-intelligence-tools listen-dictation-shortcut
```

Install the dictation listener in the current user's Windows Startup folder:

```powershell
cd C:\Dev\Active\so_intelligence_tools
poetry run so-intelligence-tools install-windows-dictation-startup
```

Dictation uses a warm OpenAI-compatible faster-whisper HTTP server. Ollama currently remains the runtime for local text correction, not ASR.

The reproducible Docker setup is documented in [Faster-Whisper Docker Server](whisper-docker.md).

Faster-whisper HTTP:

```env
PUSH_TO_TALK_DICTATION_RUNTIME=faster_whisper_http
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_BASE_URL=http://127.0.0.1:9000
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_MODEL=whisper-1
PUSH_TO_TALK_DICTATION_LANGUAGE=es-ES
```

The dictation listener checks the ASR runtime before listening for the shortcut, so startup fails clearly in logs if the server is unavailable.

To select a specific Windows microphone input, set `PUSH_TO_TALK_DICTATION_MICROPHONE_SOURCE` to a `sounddevice` input device index or device name.

Windows uses `WINDOWS_PUSH_TO_TALK_DICTATION_SHORTCUT`. It currently defaults to `Ctrl + Shift + Space` to avoid the `Ctrl + Space` operating-system shortcut collision. Linux keeps `PUSH_TO_TALK_DICTATION_SHORTCUT`.

Linux dictation setup, service management, `Ctrl + Space` desktop cleanup, and CPU benchmark notes live in [Linux Whisper Dictation](linux-whisper-dictation.md). Do not use the Windows Startup commands for Linux service installation.

Windows buffers recognized final segments while the shortcut is held and inserts the resulting text once after the shortcut is released. This avoids typing into Word or other applications while modifier keys are still physically pressed.

The runner also starts microphone capture before opening the ASR stream and replays that short buffered audio once the stream is ready. On release it keeps capture alive for `PUSH_TO_TALK_DICTATION_POST_ROLL_SECONDS` so final syllables are less likely to be cut off.

Current Windows validation status: working with `faster_whisper_http` and the local Docker `large-v3-turbo` server.
