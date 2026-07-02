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
- local Chatterbox TTS Docker endpoint smoke-tested on `http://127.0.0.1:9011`
- Codex visible-event JSONL listener smoke-tested against Chatterbox from PowerShell/stdin
- VS Code/Codex extension voice wrapper configured through `chatgpt.cliExecutable`
- Codex Desktop voice monitor for `~/.codex/sessions` installed as a hidden Startup launcher
- local Chatterbox playback through native Windows WAV output

This means selected text correction, overlay launch and dictation can be useful on Windows while keeping shared application logic independent from the operating system.

## Not Yet Supported

The following Windows integrations are not implemented yet:

- screenshot region capture
- system audio loopback capture
- translated virtual microphone output

Audio support needs a separate design because the Linux implementation currently relies on PulseAudio-compatible tools such as `pactl`, `parec` and `pacat`. Windows will need a different backend, likely based on WASAPI for capture and an explicit virtual audio device strategy for microphone output.

Local Chatterbox TTS is smoke-tested on Windows through the Docker HTTP endpoint at `http://127.0.0.1:9011`. The Codex visible-event JSONL listener, the VS Code/Codex wrapper command, and the standalone Codex Desktop session monitor have also been validated. The shared service API, platform notes, and VRAM measurements are documented in [Chatterbox TTS Voice Output](chatterbox-tts-voice-output.md).

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

## Local Chatterbox TTS

Status: working experimental GPU TTS path for Codex Desktop, the VS Code/Codex extension wrapper, and OpenClaw HTTP integrations.

The retained local TTS backend is Chatterbox es-ES. Earlier Piper/Kokoro/Qwen/NeuTTS experiment paths were cleaned from the active project; keep this section as the Windows source of truth for local voice output.

### Service Lifecycle

Windows runs the service through Docker Desktop:

```powershell
cd C:\Dev\Active\so_intelligence_tools
poetry run so-intelligence-tools ensure-chatterbox-tts-server
poetry run so-intelligence-tools status-chatterbox-tts-server
Invoke-RestMethod http://127.0.0.1:9011/health
```

Stop it when the GPU should be free:

```powershell
poetry run so-intelligence-tools stop-chatterbox-tts-server
```

The container publishes only on localhost by default:

```text
http://127.0.0.1:9011
```

The service exposes:

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | readiness, loaded model and available voices |
| `GET /metrics` | request counts, per-voice counters, synthesis time, RTF and VRAM observations |
| `POST /v1/audio/speech` | generate `audio/wav` from text and a selected voice |

### Voices

Generate a direct WAV for manual listening:

```powershell
$body = @{ text = "Hola, esta es la voz femenina local para Codex en Windows."; voice = "female" } | ConvertTo-Json
Invoke-WebRequest `
  -Uri "http://127.0.0.1:9011/v1/audio/speech" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body `
  -OutFile "$env:TEMP\chatterbox-female.wav"
```

Supported request voices:

| Voice | Aliases | Notes |
| --- | --- | --- |
| `female` | `mujer`, `default` | User-selected Common Voice female Spanish clone: `cv_female_es_ref_01 / warm`. |
| `male` | `hombre` | Built-in Chatterbox es-ES conditioning. |

The female reference file is packaged in:

```text
docker\chatterbox-tts\voices\common_voice_female_es_ref_01_row_410.wav
```

Per-request tuning fields such as `exaggeration`, `cfg_weight` and `temperature` are accepted by the service, but they are not reliable emotion controls yet. In Windows tests, neutral/expressive/emphatic labels sounded too similar to treat them as validated emotion support.

### VS Code/Codex Extension

Smoke-test the Codex visible-event listener directly:

```powershell
'{"type":"item.completed","item":{"type":"agent_message","text":"Prueba visible de Codex con Chatterbox en Windows."}}' |
  poetry run so-intelligence-tools listen-codex-visible-events `
    --base-url http://127.0.0.1:9011 `
    --voice female `
    --detail standard
```

The VS Code/Codex extension hook is configured in the current user's settings:

```json
{
  "chatgpt.cliExecutable": "C:\\Dev\\Active\\so_intelligence_tools\\scripts\\codex-tts-wrapper.cmd"
}
```

That command is a Windows launcher for `scripts\codex-tts-wrapper.py`. It resolves the newest installed OpenAI ChatGPT/Codex extension CLI, proxies `app-server` output back to the extension, and sends visible Codex JSONL events to Chatterbox. It was validated on Windows with a Codex-like app-server event: Chatterbox metrics moved from `0` to `1` successful female request and the generated WAV played through native Windows audio.

The standalone Codex Desktop app also starts an app-server internally, but no `chatgpt.cliExecutable`-style override was found for that app. Treat the validated hook as the VS Code/Codex extension integration path.

### Codex Desktop Session Monitor

For the standalone Codex Desktop app, use the session monitor. Codex Desktop writes task lifecycle events, lightweight tool progress events, and visible assistant messages to JSONL transcripts under `%USERPROFILE%\.codex\sessions`; the monitor tails those files and speaks task boundaries, tool starts/completions, plus new visible `agent_message` entries:

```powershell
poetry run so-intelligence-tools listen-codex-desktop-session-events `
  --voice female `
  --base-url http://127.0.0.1:9011 `
  --detail standard
```

Install the hidden Startup launcher:

```powershell
poetry run so-intelligence-tools install-windows-codex-desktop-tts-startup
```

The launcher installed on this machine is:

```text
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\so-intelligence-tools-codex-desktop-tts.vbs
```

The background log is:

```text
%LOCALAPPDATA%\so_intelligence_tools\logs\so-intelligence-tools-codex-desktop-tts.log
```

Each spoken Codex Desktop segment writes a JSON latency metric to that log. Use `message_to_playback_start_seconds` for the user-perceived delay from message display to audio start, and `synthesis_seconds` to isolate Chatterbox generation time.

### Codex Desktop Speech Semantics

The monitor uses the following event priorities:

| Event | Spoken behavior |
| --- | --- |
| `task_started` | Speak `Inicio de tarea.` immediately, clear stale queued/prefetched speech, and stop current WAV playback when Windows allows it. |
| `response_item.function_call` | Speak lightweight tool progress such as `Ejecutando comando.` or `Preparando cambios de archivos.` |
| `response_item.function_call_output` | Speak `Herramienta terminada.` |
| `patch_apply_*`, `web_search_*` | Speak bounded progress, never raw tool output. |
| visible `agent_message` | Read cleaned assistant text according to the selected detail level. |
| `task_complete` without `last_agent_message` | Speak `Fin de tarea.` immediately and clear stale queued/prefetched speech. |
| `task_complete` with `last_agent_message` | Clear stale queued/prefetched speech, speak `Fin de tarea.`, then read the cleaned final message. |

Hidden reasoning, token counts and raw tool outputs are intentionally ignored.

The monitor overlaps synthesis and playback:

- one worker synthesizes the next segment with Chatterbox;
- one worker plays ready WAV segments in order;
- while one WAV is playing, the next segment can already be synthesized;
- the ready-audio buffer is capped to two segments;
- task boundaries clear both queued text and prefetched audio;
- tool-progress notices such as repeated `Ejecutando comando.` are soft feedback, so a later visible assistant message drops older pending/prefetched tool-progress audio and plays next.

The hidden Startup monitor reads these persistent defaults from the project `.env`:

```text
LOCAL_TTS_BASE_URL=http://127.0.0.1:9011
LOCAL_TTS_VOICE=female
CODEX_VOICE_DETAIL=standard
CODEX_VOICE_MAX_SEGMENT_CHARS=500
```

Reading levels:

- `minimal`: only task start/end markers.
- `actions`: task start/end markers plus lightweight tool progress, without assistant message text.
- `standard`: task start/end plus visible assistant messages.
- `no-code`: like `standard`, but drops fenced code blocks.
- `full`: preserves more visible text detail.

Wrapper session controls still apply to VS Code/Codex extension sessions:

```powershell
poetry run so-intelligence-tools codex-voice-sessions
poetry run so-intelligence-tools codex-voice-voice female --base-url http://127.0.0.1:9011
poetry run so-intelligence-tools codex-voice-detail actions
poetry run so-intelligence-tools codex-voice-off
poetry run so-intelligence-tools codex-voice-on
```

### Latency And Performance Evidence

Measured on the current Windows workstation with an NVIDIA RTX 3070 on 2026-07-02.

| Scenario | Result | Notes |
| --- | ---: | --- |
| First deployed female smoke request | `17.336s` wall | Warm female clone path includes conditioning/startup cost. |
| Male smoke request | `5.962s` wall | Same deployed service, shorter request. |
| Service average after smoke | RTF about `2.63` | From `/metrics` after male/female smoke. |
| Direct current PyTorch Chatterbox spike | `11.42s` synth / `8.96s` audio, RTF `1.27` | Direct process, `cfg_weight=0.25`. |
| HTTP service spike | `12.64s` synth / `9.00s` audio, RTF `1.40` | Same model path via HTTP service. |
| Long text one-shot | `56.92s` | Too slow for interactive Codex speech. |
| Long text chunked | first chunk ready in `5.56s` | Supports chunking/pipeline strategy. |
| Codex Desktop monitor smoke | last RTF about `1.8282` | Session-monitor-shaped event, female voice. |
| Whisper + Chatterbox coexistence short request | `11.028s` wall, `10.836s` synth, `5.20s` audio, RTF `2.084` | Whisper stayed running; Qwen embeddings unloaded. |

Optimization attempts that are currently not recommended:

| Attempt | Outcome |
| --- | --- |
| Chatterbox `bf16` in current runtime | Failed because of speaker-conditioning dtype mismatch. |
| `rsxdalv/chatterbox` faster branch | Not drop-in compatible with the es-ES loader during the spike. |
| `onnx-community/chatterbox-multilingual-ONNX` | Ran with CUDAExecutionProvider but measured around `15.6s` for the medium prompt and did not emit a stop token before the max-token cap in the simple script. |
| Qwen3-TTS FlashAttention / bitsandbytes | Worked in later retries but was slower than Chatterbox for this use case; not chosen for low-latency Codex/OpenClaw voice. |

Current conclusion: Chatterbox is the retained quality path, but perceived latency depends on chunking, queue policy and pre-synthesis rather than raw model speed alone.

### VRAM And Coexistence Conditions

Measured state on the current Windows RTX 3070:

| State | VRAM used | Notes |
| --- | ---: | --- |
| Windows/WDDM floor, no local AI model loaded | about `1074 MiB` | Desktop compositor, browser/Codex/Docker overhead. |
| Qwen embeddings resident, Whisper and Chatterbox stopped | about `3522 MiB` | `qwen3-embedding:0.6b` inside the embedding Ollama container. |
| Whisper resident, Chatterbox stopped, Qwen embeddings resident | about `5762 MiB` | Faster-Whisper Docker service at `127.0.0.1:9000`. |
| Chatterbox resident, Whisper stopped, Qwen embeddings unloaded | about `4335 MiB` | Chatterbox es-ES service only. |
| Chatterbox and Whisper resident, Qwen embeddings unloaded | about `6567 MiB` | Both audio services fit with modest headroom. |
| Chatterbox synthesis while Whisper was resident | about `6890 MiB` after request | Short female request left about `1129 MiB` free. |

Whisper and Chatterbox can run together on this 8 GiB RTX 3070 if Qwen embeddings is unloaded first. Keeping Chatterbox, Whisper and Qwen embeddings all resident is not recommended.

Qwen embeddings is used by Memanto/Moorcheh semantic memory, not by TTS or Whisper:

```powershell
docker exec qwen3-embedding-0-6b-ollama-gpu ollama ps
docker exec qwen3-embedding-0-6b-ollama-gpu ollama stop qwen3-embedding:0.6b
```

Prefer this order when GPU headroom is needed:

1. Unload `qwen3-embedding:0.6b`.
2. Keep Whisper and Chatterbox warm together if both are needed.
3. Stop Chatterbox when voice output is not needed.
4. Stop Whisper only when ASR/dictation is not needed.

### LAN Access From Another Computer

The current Docker compose bindings publish Whisper and Chatterbox only to localhost:

```text
127.0.0.1:9000 -> Whisper
127.0.0.1:9011 -> Chatterbox
```

Another laptop on the same Wi-Fi cannot use these endpoints until the compose port bindings are changed to `0.0.0.0` or the host LAN IP and Windows Firewall allows inbound traffic. Do not expose these endpoints beyond the trusted local network; neither service is documented here as internet-facing or authenticated.

### Troubleshooting

Check the TTS service:

```powershell
poetry run so-intelligence-tools status-chatterbox-tts-server
Invoke-RestMethod http://127.0.0.1:9011/health
Invoke-RestMethod http://127.0.0.1:9011/metrics
```

Check the Codex Desktop monitor:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -like '*listen-codex-desktop-session-events*' } |
  Select-Object ProcessId,ParentProcessId,CommandLine

Get-Content -Tail 40 "$env:LOCALAPPDATA\so_intelligence_tools\logs\so-intelligence-tools-codex-desktop-tts.log"
```

If Windows shows a Windows Script Host popup about a truncated Startup path, do not relaunch the `.vbs` through an unquoted `wscript.exe` path. Prefer the Python background launcher directly:

```powershell
cd C:\Dev\Active\so_intelligence_tools
.venv\Scripts\python.exe -m so_intelligence_tools.infrastructure.windows_background_launcher codex-desktop-tts
```

Stop Chatterbox when the GPU should be free:

```powershell
poetry run so-intelligence-tools stop-chatterbox-tts-server
```
