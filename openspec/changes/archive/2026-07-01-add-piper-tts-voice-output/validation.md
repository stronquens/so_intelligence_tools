# Validation

Date: 2026-07-01.
Host: local Linux workstation, CPU-only.

## Commands Run

```bash
poetry run pytest tests/test_local_tts_client.py tests/test_codex_voice_events.py tests/test_user_services.py
poetry run python -m py_compile src/so_intelligence_tools/local_tts/*.py src/so_intelligence_tools/cli/main.py src/so_intelligence_tools/infrastructure/user_services.py docker/piper-tts/server.py
poetry run python -m py_compile scripts/codex-tts-wrapper.py docker/piper-tts/server.py src/so_intelligence_tools/local_tts/*.py
poetry run pytest tests/test_codex_voice_control.py tests/test_codex_voice_events.py tests/test_local_tts_client.py tests/test_user_services.py
poetry run pytest tests/test_codex_voice_events.py tests/test_codex_voice_control.py tests/test_local_tts_client.py tests/test_user_services.py
poetry run pytest tests/test_codex_voice_control.py tests/test_local_tts_client.py tests/test_codex_voice_events.py tests/test_user_services.py
scripts/codex-tts-wrapper.py --version
timeout 10 scripts/codex-tts-wrapper.py app-server --help
STATE_DIR=$(mktemp -d) && export SO_AI_CODEX_TTS_STATE_DIR="$STATE_DIR" && poetry run python - <<PY
import os
from so_intelligence_tools.local_tts.codex_voice_control import register_session
register_session(pid=$$, cwd=os.getcwd(), args=['app-server'])
PY
poetry run so-intelligence-tools codex-voice-sessions
poetry run so-intelligence-tools codex-voice-off
poetry run so-intelligence-tools codex-voice-on
poetry run so-intelligence-tools codex-voice-detail full
poetry run so-intelligence-tools codex-voice-voice female
rm -rf "$STATE_DIR"
docker compose -f docker/piper-tts/compose.yaml up -d --build
poetry run so-intelligence-tools ensure-piper-tts-server
curl -fsS http://127.0.0.1:9010/health
poetry run so-intelligence-tools speak-text --voice female --text 'Prueba de voz femenina configurada en el mismo contenedor.'
curl -fsS -X POST http://127.0.0.1:9010/v1/audio/speech -H 'content-type: application/json' -d '{"text":"hola"}' -o /tmp/so-ai-piper-smoke.wav
file /tmp/so-ai-piper-smoke.wav
python - <<'PY'
import wave
with wave.open("/tmp/so-ai-piper-smoke.wav", "rb") as wav_file:
    assert wav_file.getnframes() > 0
PY
rm -f /tmp/so-ai-piper-smoke.wav
poetry run so-intelligence-tools speak-text --text 'Hola, ya está activada la voz local de Piper para leer mensajes visibles de Codex.'
printf '%s\n' '{"type":"item.completed","item":{"type":"agent_message","text":"Este es un mensaje visible de Codex leído desde el listener JSONL."}}' | poetry run so-intelligence-tools listen-codex-visible-events
printf '%s\n' '{"type":"item.started","item":{"type":"command_execution","command":"cat secret.txt"}}' '{"type":"item.completed","item":{"type":"command_execution","command":"cat secret.txt","output":"contenido privado","exit_code":0}}' '{"type":"item.completed","item":{"type":"agent_message","text":"Mensaje visible leído después de una herramienta."}}' | poetry run so-intelligence-tools listen-codex-visible-events
poetry run so-intelligence-tools stop-piper-tts-server
poetry run so-intelligence-tools status-piper-tts-server
poetry run so-intelligence-tools speak-text --text 'Esto no debería sonar porque el contenedor está parado.'
poetry run so-intelligence-tools ensure-piper-tts-server
poetry run so-intelligence-tools status-piper-tts-server
poetry run openspec validate add-piper-tts-voice-output --strict
```

## Results

- Piper TTS Docker service starts successfully and reports `ready`.
- `/health` returns the configured Spanish Piper voice: `es/es_ES/davefx/medium/es_ES-davefx-medium.onnx`.
- `/v1/audio/speech` returns valid non-empty WAV PCM: mono, 16-bit, 22050 Hz.
- A playback bug was found and fixed: the Piper wrapper was calling `PiperVoice.synthesize()` without consuming its generated chunks, which produced a 44-byte WAV header with zero frames. It now calls `PiperVoice.synthesize_wav()` and rejects empty audio.
- `speak-text` returns `spoken` when the service is running.
- `listen-codex-visible-events` accepts Codex JSONL `item.completed` events with visible `agent_message` text and sends them to speech.
- `listen-codex-visible-events` reads the full visible cycle by default: assistant deltas/messages plus safe lifecycle summaries for command/tool start and completion.
- Command/tool payloads remain filtered: the JSONL smoke test included a command and output payload, but the spoken text was limited to lifecycle summaries and visible assistant text.
- Markdown speech normalization announces fenced code blocks by language without reading their contents, shortens raw URLs and Markdown link URLs to their final path segment, and treats completed newline-delimited lines as speech-ready boundaries.
- Full-cycle voice mode announces `Fin de tarea.` when `turn/completed` arrives.
- Codex voice detail modes are supported: `minimal`, `actions`, `standard`, `no-code`, and `full`.
- The event listener now consumes events asynchronously and clears pending queued message speech when turn completion arrives, so `Fin de tarea.` is spoken next after the currently playing segment finishes.
- The default Codex voice detail mode is `actions`, so it speaks task start/end and tool/function/command lifecycle without reading full assistant messages.
- Piper can load multiple voice aliases in one container through `PIPER_TTS_VOICES_JSON`; `/health` reports `default`, `male`, and `female` on this workstation after configuring `female` as `es_AR/daniela/high`.
- `speak-text --voice female` returns `spoken`, and per-window commands can set `codex-voice-detail full` and `codex-voice-voice female` on a live session.
- `scripts/codex-tts-wrapper.py` resolves the installed OpenAI Codex extension's bundled CLI, proxies `app-server` stdout back to the IDE, and tees app-server JSONL events to the local TTS listener.
- The wrapper returns the bundled Codex CLI version and preserves `codex app-server --help` output.
- The wrapper registers per-instance voice sessions, and `codex-voice-off`, `codex-voice-on`, `codex-voice-toggle`, and `codex-voice-sessions` can control the active session for the current working directory without stopping Piper globally.
- Stopping the Piper container makes `status-piper-tts-server` return `disabled`, and `speak-text` returns `disabled` without blocking or failing.
- The service was restarted after the off-switch validation and left `ready`.
- Unit tests passed: 42 passed.

## Privacy And Hook Boundary

The implementation filters hidden reasoning item types and command/tool internals before speech. It supports visible Codex CLI JSONL events and app-server-style `item/agentMessage/delta` notifications. The official Codex lifecycle hook model does not provide a documented streaming hook for every visible assistant message, so the documented integration path is a JSONL/event-source bridge for visible events. A `--final-only` listener mode keeps the reduced behavior available when full-cycle narration is too noisy.

## Retained Evidence

- `docs/piper-tts-voice-output.md` documents operation and integration.
- Runtime evidence is command-based; no generated assistant speech audio is retained.

## Remaining Work

No remaining implementation work for this change. The selected default remains
`es_ES/davefx/medium` because it was the fastest benchmarked Spanish voice on
this CPU-only workstation. A female Spanish alias is configured and smoke-tested
as `female` with `es_AR/daniela/high`, but it is not the default.
