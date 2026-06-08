# Validation

## Automated

- `poetry run pytest -q` -> `60 passed`
- `python3 -m compileall src tests` -> correcto
- `poetry run pytest tests/test_system_audio_translation_*.py -q` -> `24 passed`

## Manual / Spike Evidence

- Linux monitor source detectable on the target machine:
  - `pactl list short sources`
  - default monitor source present: `alsa_output.pci-0000_00_1f.3.analog-stereo.monitor`
- Required local binaries available:
  - `parec`
  - `pactl`
  - `tkinter`
- Remote OpenAI-compatible audio transcription path validated against the company LiteLLM Proxy:
  - `POST /v1/audio/transcriptions`
  - confirmed working models included `whisper-1`
- Initial implementation path chosen:
  - capture system audio with `parec`
  - selectable mode from a visible dropdown in the window
  - `translate_es_chunked` fallback:
    - chunk PCM audio
    - transcribe remotely
    - translate text through the existing text inference backend
  - `translate_es_openai_realtime` path:
    - stream PCM audio directly into the OpenAI Realtime SDK
    - receive progressive text deltas in the UI
    - show input transcription deltas as live activity while translated output is being generated
    - render original transcription and Spanish translation in a live split view with a grouped shared history
    - default to the pure Realtime API path, with `server_vad`, no automatic response interruption, and VAD sensitivity exposed through `.env`
    - keep a separate optional completed-transcript translation mode available for comparison, but not as the default path
- Realtime alignment spike against `/home/sciling/Descargas/fishing.mp3`:
  - converted MP3 to 24 kHz PCM with GStreamer for testing
  - compared `server_vad` and `semantic_vad`
  - selected `server_vad` as the default because it produced better aligned original/translation pairs in the current use case
- Session logs now include diagnostic events:
  - state changes
  - speech start/stop
  - committed input items
  - partial updates
  - final transcriptions
  - final translations
  - published blocks and residual best-effort blocks
- Manual toggle smoke test executed:
  - first invocation of `poetry run so-intelligence-tools run-system-audio-translation-toggle` opened the session
  - second invocation sent the toggle signal and closed it cleanly
- OpenAI realtime connectivity was probed against the configured key:
  - websocket connection opened
  - first server event: `session.created`
  - after `session.update`, server replied with `session.updated`
  - conclusion: the direct OpenAI realtime path is valid with the configured `OPENAI_API_KEY`

## Remaining Manual Validation

- Broader validation against Zoom, Meet, Slack, or equivalent real calls
- Longer latency and cost tuning with conversational audio from multiple speakers
