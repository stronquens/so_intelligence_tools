# Chatterbox TTS Voice Output

Status: experimental GPU-backed Spanish voice output for Codex and OpenClaw.

This service wraps `ResembleAI/Chatterbox-Multilingual-es-es` behind a local HTTP API. It keeps the model warm while voice output is enabled, exposes health and metrics endpoints, and can be stopped to release GPU memory.

Platform status:

| Area | Linux | Windows |
| --- | --- | --- |
| Docker Chatterbox service | Supported path | Smoke-tested with Docker Desktop |
| `POST /v1/audio/speech` endpoint | Supported path | Smoke-tested |
| Local playback via `speak-text` | Uses Linux audio tools unless configured otherwise | Uses native Windows WAV playback |
| Codex JSONL listener | Supported path | Smoke-tested from PowerShell/stdin |
| VS Code/Codex wrapper | Linux path documented below | Validated with `scripts/codex-tts-wrapper.cmd` |
| Standalone Codex Desktop app | Use app-server wrapper where available | Validated through `~/.codex/sessions` monitor |

The current default voice is the user-selected female clone:

```text
chatterbox-es-es female clone / cv_female_es_ref_01 / warm
```

## Start Or Stop

### Linux

Start the warm service:

```bash
so-ai ensure-chatterbox-tts-server
```

Check whether it is ready:

```bash
so-ai status-chatterbox-tts-server
curl http://127.0.0.1:9011/health
```

Stop it to release VRAM:

```bash
so-ai stop-chatterbox-tts-server
```

The service lives in `docker/chatterbox-tts` and publishes only to localhost:

```text
http://127.0.0.1:9011
```

### Windows

From this repository:

```powershell
poetry run so-intelligence-tools ensure-chatterbox-tts-server
poetry run so-intelligence-tools status-chatterbox-tts-server
Invoke-RestMethod http://127.0.0.1:9011/health
```

Stop it to release VRAM:

```powershell
poetry run so-intelligence-tools stop-chatterbox-tts-server
```

## Voices

`POST /v1/audio/speech` accepts a `voice` parameter:

| Voice | Alias | Notes |
| --- | --- | --- |
| `female` | `mujer`, `default` | Selected Common Voice female Spanish clone, warm preset. |
| `male` | `hombre` | Built-in Chatterbox es-ES conditioning. |

The female preset uses the packaged reference clip at:

```text
docker/chatterbox-tts/voices/common_voice_female_es_ref_01_row_410.wav
```

Runtime tuning fields are also accepted per request:

```json
{
  "text": "Hola, esta es una prueba.",
  "voice": "female",
  "exaggeration": 0.65,
  "cfg_weight": 0.35,
  "temperature": 0.75
}
```

These fields are useful for timbre and prosody experiments, but they are not validated as reliable emotion tags. Earlier testing showed that simple `neutral`, `expressive`, and `emphatic` labels sounded too similar.

## API

Generate WAV audio:

```bash
curl -o female.wav \
  -H "Content-Type: application/json" \
  -d '{"text":"Hola, soy la voz femenina local para Codex.","voice":"female"}' \
  http://127.0.0.1:9011/v1/audio/speech
```

Generate the male voice:

```bash
curl -o male.wav \
  -H "Content-Type: application/json" \
  -d '{"text":"Hola, soy la voz masculina local para Codex.","voice":"male"}' \
  http://127.0.0.1:9011/v1/audio/speech
```

Inspect readiness and loaded presets:

```bash
curl http://127.0.0.1:9011/health
```

Inspect service metrics:

```bash
curl http://127.0.0.1:9011/metrics
```

The metrics payload includes total requests, failures, per-voice counters, last synthesis time, last audio duration, last realtime factor, average realtime factor, and current NVIDIA VRAM usage when `nvidia-smi` is available.

## Codex Integration

### Linux

The existing local TTS client can point at Chatterbox by changing the base URL and voice:

```bash
so-ai speak-text \
  --base-url http://127.0.0.1:9011 \
  --voice female \
  --text "Hola, voy a leer los eventos visibles de Codex."
```

For Codex visible-event reading:

```bash
codex exec --json "resume el estado del repo" \
  | so-ai listen-codex-visible-events \
      --base-url http://127.0.0.1:9011 \
      --voice female
```

For the Codex IDE extension on Linux, the integration point is the same wrapper pattern used by the earlier TTS work. The installed OpenAI Codex extension uses the Codex CLI app-server; until the extension exposes a dedicated voice-output hook, configure the local wrapper that proxies the bundled CLI and tees app-server events to the TTS listener:

```json
{
  "chatgpt.cliExecutable": "/home/sciling/Escritorio/so_intelligence_tools/scripts/codex-tts-wrapper.py"
}
```

Before opening a Codex thread, make sure Chatterbox is running:

```bash
so-ai ensure-chatterbox-tts-server
so-ai codex-voice-voice female --base-url http://127.0.0.1:9011
```

For a running Codex app or VS Code wrapper session, select the Chatterbox voice per window:

```bash
so-ai codex-voice-voice female --base-url http://127.0.0.1:9011
```

Switch back to the male Chatterbox preset:

```bash
so-ai codex-voice-voice male --base-url http://127.0.0.1:9011
```

Stopping the container disables GPU voice output without changing normal Codex text output:

```bash
so-ai stop-chatterbox-tts-server
```

### Windows

Windows can use the HTTP service directly and can route VS Code/Codex extension app-server events through the Windows wrapper command:

```json
{
  "chatgpt.cliExecutable": "C:\\Dev\\Active\\so_intelligence_tools\\scripts\\codex-tts-wrapper.cmd"
}
```

This is configured in the current user's VS Code settings at:

```text
%APPDATA%\Code\User\settings.json
```

The wrapper resolves the newest installed OpenAI ChatGPT/Codex extension CLI under `%USERPROFILE%\.vscode\extensions\openai.chatgpt-*\bin\windows-x86_64\codex.exe`, proxies `app-server` stdout back to the extension, and tees visible JSONL events to `listen-codex-visible-events`.

Generate a WAV:

```powershell
$body = @{ text = "Hola, esta es una prueba de Chatterbox en Windows."; voice = "female" } | ConvertTo-Json
Invoke-WebRequest `
  -Uri "http://127.0.0.1:9011/v1/audio/speech" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body `
  -OutFile "$env:TEMP\chatterbox-female.wav"
```

Smoke-test the Codex visible-event listener shape directly:

```powershell
'{"type":"item.completed","item":{"type":"agent_message","text":"Prueba visible de Codex con voz femenina."}}' |
  poetry run so-intelligence-tools listen-codex-visible-events `
    --base-url http://127.0.0.1:9011 `
    --voice female `
    --detail standard
```

Windows native WAV playback is available through Python `winsound`, so `LOCAL_TTS_PLAYBACK_COMMAND` is no longer required for the default local speaker output.

Windows validation on 2026-07-02 confirmed both paths:

- The JSONL listener sends a visible Codex event to the Chatterbox endpoint from PowerShell.
- The wrapper command `scripts\codex-tts-wrapper.cmd app-server --stdio` launches through the Windows wrapper path, starts the listener, sends a visible Codex-like event to Chatterbox, and plays the generated WAV through Windows audio.

The standalone Codex Desktop app uses its own packaged app-server startup. No local `chatgpt.cliExecutable`-style override was found in the Codex Desktop app settings or logs, so this Windows hook is currently for the VS Code/Codex extension path.

For the standalone Codex Desktop app on Windows, use the session monitor instead. Codex Desktop writes visible assistant messages to JSONL files under:

```text
%USERPROFILE%\.codex\sessions
```

Run the monitor manually:

```powershell
poetry run so-intelligence-tools listen-codex-desktop-session-events `
  --voice female `
  --base-url http://127.0.0.1:9011 `
  --detail standard
```

Install it as a hidden Windows Startup launcher:

```powershell
poetry run so-intelligence-tools install-windows-codex-desktop-tts-startup
```

This monitor tails new session JSONL lines, reads task lifecycle events, visible `agent_message` events, and lightweight Desktop tool progress markers such as `function_call`, `function_call_output`, `patch_apply_*`, and `web_search_*`. It skips hidden reasoning and raw tool outputs, then sends the cleaned text to Chatterbox. It starts at the end of existing session files, so it should not read old history when launched.

Codex Desktop task lifecycle events always have priority:

- `task_started` speaks `Inicio de tarea.` immediately and clears stale queued speech from earlier turns.
- `task_complete` without a final message speaks `Fin de tarea.` immediately, clears pending assistant-message speech, and stops current Windows WAV playback when possible.
- `task_complete` with `last_agent_message` clears stale queued speech, speaks `Fin de tarea.`, and then reads that final message.
- If an older segment was still synthesizing when a lifecycle event arrived, its audio is discarded before playback.

The monitor emits one JSON latency metric per spoken segment in the Windows background log. The key field for perceived latency is `message_to_playback_start_seconds`, measured from the Codex Desktop JSONL message timestamp to the moment local WAV playback starts. `synthesis_seconds` separates Chatterbox generation time from monitor/polling overhead.

Codex Desktop playback uses a small two-stage pipeline:

- one worker synthesizes the next segment with Chatterbox;
- a second worker plays ready WAV segments in order;
- while the current segment is playing, the next segment can be synthesized ahead of time;
- the ready-audio buffer is bounded to two segments so stale speech does not build up indefinitely;
- when a visible assistant message arrives, older pending or prefetched tool-progress segments are dropped so repeated `Ejecutando comando.` notices do not delay real content;
- priority events such as `task_started` and `task_complete` still clear queued and prefetched audio before speaking the new task boundary.

Example fields:

```json
{
  "event": "codex_desktop_tts_latency",
  "message_to_playback_start_seconds": 20.85,
  "message_to_queue_seconds": 0.09,
  "synthesis_seconds": 20.76,
  "playback_seconds": 6.60,
  "phase": "commentary",
  "status": "spoken"
}
```

The Startup launcher reads persistent defaults from the project `.env`:

```text
LOCAL_TTS_BASE_URL=http://127.0.0.1:9011
LOCAL_TTS_VOICE=female
CODEX_VOICE_DETAIL=standard
CODEX_VOICE_MAX_SEGMENT_CHARS=500
```

For Codex Desktop, supported spoken detail values are:

- `minimal`: read only `Inicio de tarea.` and `Fin de tarea.`.
- `actions`: read task boundaries and lightweight tool progress, but skip assistant message text.
- `standard`: read task lifecycle plus visible assistant messages, with URLs shortened and code blocks summarized rather than read literally.
- `no-code`: drop fenced code blocks from speech.
- `full`: preserve code-block summaries and full URLs.

Current Windows Codex Desktop queue policy:

| Case | Behavior |
| --- | --- |
| New task starts | Clear stale queued/prefetched speech, stop current playback when possible, speak `Inicio de tarea.`. |
| Task completes with no final text | Clear stale queued/prefetched speech and speak `Fin de tarea.`. |
| Task completes with `last_agent_message` | Clear stale queued/prefetched speech, speak `Fin de tarea.`, then read the cleaned final message. |
| Tool calls repeat before a visible message | Treat tool-progress speech as soft feedback; pending/prefetched older tool notices are skipped once a visible assistant message arrives. |
| Playback is ongoing while more text arrives | Synthesize the next segment while the current WAV plays, preserve order, and cap prefetched audio to two segments. |
| Hidden reasoning or raw tool output arrives | Ignore it. |

For a running wrapper session, use the same per-session controls:

```powershell
poetry run so-intelligence-tools codex-voice-sessions
poetry run so-intelligence-tools codex-voice-voice female --base-url http://127.0.0.1:9011
poetry run so-intelligence-tools codex-voice-detail actions
poetry run so-intelligence-tools codex-voice-off
poetry run so-intelligence-tools codex-voice-on
```

### Windows Performance Notes

Measured on the current Windows RTX 3070 workstation on 2026-07-02.

| Scenario | Result | Notes |
| --- | ---: | --- |
| First deployed female smoke request | `17.336s` wall | Female clone conditioning/startup path. |
| Male smoke request | `5.962s` wall | Same deployed service, shorter request. |
| Average service RTF after smoke | about `2.63` | From `/metrics`. |
| Direct PyTorch Chatterbox spike | `11.42s` synth / `8.96s` audio, RTF `1.27` | Direct process, `cfg_weight=0.25`. |
| HTTP service spike | `12.64s` synth / `9.00s` audio, RTF `1.40` | Same model through the service endpoint. |
| Long text one-shot | `56.92s` wall | Too slow for interactive Codex voice. |
| Long text chunked | first chunk ready in `5.56s` | Supports chunking and pipeline strategy. |
| Codex Desktop session monitor smoke | last RTF about `1.8282` | Female voice, Desktop-shaped JSONL event. |
| Whisper + Chatterbox short request | `11.028s` wall, `10.836s` synth, `5.20s` audio, RTF `2.084` | Whisper stayed resident; Qwen embeddings unloaded. |

Optimization attempts that are not currently recommended for the retained Windows path:

| Attempt | Result |
| --- | --- |
| Naive current-runtime `bf16` | Failed due speaker-conditioning dtype mismatch. |
| `rsxdalv/chatterbox` faster branch | Not drop-in compatible with the es-ES loader during the spike. |
| `onnx-community/chatterbox-multilingual-ONNX` | Ran on CUDA but measured about `15.6s` for the medium prompt and did not stop cleanly before the max-token cap in the simple script. |
| Qwen3-TTS FlashAttention / bitsandbytes | Later retries worked, but FlashAttention/BNB paths were slower than Chatterbox for this low-latency voice use case. |

Current conclusion: Chatterbox is the retained natural Spanish voice path, but low perceived latency depends on shorter chunks, pre-synthesis during playback, and skipping obsolete tool-progress speech.

## OpenClaw Integration

OpenClaw can use the same localhost HTTP endpoint from the host on either Linux or Windows:

```text
base_url = http://127.0.0.1:9011
voice = female
```

For a direct smoke test from any integration script, send `text` and `voice` to `/v1/audio/speech` and treat the response body as `audio/wav`.

If OpenClaw runs inside another container, route to the host according to that environment's Docker networking setup instead of using `127.0.0.1` inside the container.

## GPU Notes

Chatterbox es-ES is the retained TTS backend after removing earlier Piper/Kokoro/Qwen/NeuTTS experiment paths. On the current RTX 3070 benchmark, model load used roughly 3.3 GiB additional VRAM and generation peaked around 3.8 to 4.0 GiB above baseline.

Windows RTX 3070 measurements on 2026-07-02:

| State | VRAM used | Notes |
| --- | ---: | --- |
| Windows/WDDM floor, no local AI model loaded | about 1074 MiB | Desktop compositor, browsers, Codex, Docker Desktop, OpenClaw tray, wallpaper/process overhead. |
| Qwen embeddings model loaded | about 3522 MiB | `qwen3-embedding:0.6b` inside the Memanto embedding Ollama container. Not a TTS or Whisper model. |
| Whisper loaded, TTS stopped, Qwen embeddings loaded | about 5762 MiB | Faster-Whisper Docker service at `http://127.0.0.1:9000`. |
| Chatterbox loaded, Whisper stopped, Qwen embeddings unloaded | about 4335 MiB | Chatterbox es-ES service only. |
| Chatterbox and Whisper both idle, Qwen embeddings unloaded | about 6567 MiB | Both audio services fit with about 1452 MiB free. |
| Chatterbox synthesis while Whisper was loaded | about 6890 MiB after request | Short female request completed with about 1129 MiB free. |

Whisper and Chatterbox can be up at the same time on this 8 GiB RTX 3070 when the Qwen embeddings model is unloaded, but the margin is modest. Keeping Whisper, Chatterbox, and Qwen embeddings all resident is not recommended.

The Qwen embedding model is used by Memanto/Moorcheh for semantic memory search and new memory embeddings. It lives outside this repository in `C:\Dev\Active\memanto_local`, served by Docker Ollama on `127.0.0.1:11435`; it is unrelated to TTS generation and ASR transcription.

Inspect whether the embedding model is resident:

```powershell
docker exec qwen3-embedding-0-6b-ollama-gpu ollama ps
```

Unload it when you need GPU headroom for audio services:

```powershell
docker exec qwen3-embedding-0-6b-ollama-gpu ollama stop qwen3-embedding:0.6b
```

Memanto can load it again when semantic memory operations need embeddings. If VRAM is tight, unload Qwen embeddings first, then decide whether Whisper and Chatterbox both need to stay warm.

This service is designed to be started and stopped explicitly:

```bash
so-ai ensure-chatterbox-tts-server
so-ai stop-chatterbox-tts-server
```

That lifecycle mirrors the Whisper container workflow: warm when needed, stopped when the GPU should be free.

## Configuration

The installer creates `docker/chatterbox-tts/.env` from `.env.example` if it does not exist. Key settings:

```env
CHATTERBOX_TTS_PORT=9011
CHATTERBOX_TTS_DEVICE=cuda
CHATTERBOX_TTS_DEFAULT_VOICE=female
CHATTERBOX_TTS_FEMALE_REFERENCE=/app/voices/common_voice_female_es_ref_01_row_410.wav
```

Change preset defaults there, then restart:

```bash
so-ai stop-chatterbox-tts-server
so-ai ensure-chatterbox-tts-server
```

## Troubleshooting

If the service is not ready:

```bash
docker logs chatterbox-tts --tail 120
curl http://127.0.0.1:9011/health
```

If Docker reports GPU errors, verify that Docker can see the NVIDIA runtime:

```bash
docker run --rm --gpus all nvidia/cuda:12.6.3-base-ubuntu24.04 nvidia-smi
```

If synthesis is too slow or VRAM is tight, stop other local GPU services such as Whisper before testing Chatterbox, then restart them afterwards.
