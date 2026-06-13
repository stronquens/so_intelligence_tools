# Windows Support

Windows support is starting with text-focused desktop adapters.

## Current Status

Implemented in the first Windows adapter slice:

- clipboard read/write through Win32 APIs
- keyboard copy/paste automation through Win32 APIs
- selected text discovery through a clipboard roundtrip
- corrected text insertion through clipboard + paste
- best-effort notification feedback
- platform-aware runtime selection for selected text correction
- selected text correction shortcut listener through native Win32 `RegisterHotKey`
- user-level Startup launcher for the local inference API
- user-level Startup launcher for the shortcut listener

This means the shared selected text correction use case can be composed with Windows adapters while keeping the application logic independent from the operating system.

## Not Yet Supported

The following Windows integrations are not implemented yet:

- screenshot region capture
- push-to-talk microphone capture
- system audio loopback capture
- translated virtual microphone output

Audio support needs a separate design because the Linux implementation currently relies on PulseAudio-compatible tools such as `pactl`, `parec` and `pacat`. Windows will need a different backend, likely based on WASAPI for capture and an explicit virtual audio device strategy for microphone output.

## Practical Notes

The first Windows text adapters use normal `Ctrl+C` and `Ctrl+V` automation against the focused application. Some applications, elevated windows, secure desktops or focus transitions may block that automation. When replacement cannot complete, the existing selected text correction flow can still preserve the corrected text on the clipboard as a fallback.

If no text is selected, the Windows selection adapter tries `Ctrl+A` and then copies again. In normal text inputs this selects the whole focused field before correction. In larger editors it may select the whole document, depending on how that application handles `Ctrl+A`.

## Selected Text Correction Shortcut

The default Windows shortcut is:

```text
Ctrl + Alt + C
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

The Startup installers write user-level `.cmd` launchers and do not require administrator privileges.

The listener expects the local inference API and Ollama to be available. A working local
configuration should point `OLLAMA_MODEL` at an installed model, for example
`gemma4-e2b-longctx:latest` on this Windows machine.

For a warmer shortcut experience, enable API startup warm-up and use a longer Ollama keep-alive:

```env
OLLAMA_KEEP_ALIVE=24h
OLLAMA_WARMUP_ON_STARTUP=true
```

Ollama itself should also be configured to start at login. The standard Ollama Windows installer normally creates an `Ollama.lnk` entry in the user's Startup folder.
