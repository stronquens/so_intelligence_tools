# Validation

## Automated

```bash
poetry run pytest tests/test_voice_translation_virtual_microphone_audio.py tests/test_voice_translation_realtime.py tests/test_gnome_shortcuts.py -q
```

Result:

```text
21 passed
```

```bash
poetry run pytest -q
```

Result:

```text
88 passed, 1 warning in 3.19s
```

The warning is the pre-existing Starlette/httpx deprecation warning from FastAPI TestClient.

```bash
poetry run ruff check src tests
```

Result:

```text
All checks passed!
```

```bash
openspec validate bootstrap-voice-translation-virtual-microphone --strict
```

Result:

```text
Change 'bootstrap-voice-translation-virtual-microphone' is valid
```

## Local Audio Smoke

The PulseAudio virtual microphone backend was smoke-tested without opening an OpenAI session:

```bash
poetry run python - <<'PY'
from so_intelligence_tools.voice_translation_virtual_microphone.audio import PulseAudioVirtualMicrophone
mic = PulseAudioVirtualMicrophone(sink_name='so_ai_smoke_mic', sample_rate_hz=24000)
try:
    mic.start()
    print('monitor', mic.monitor_source_name, 'running', mic.running)
    mic.write(b'\x00\x00' * 240)
finally:
    mic.stop()
    print('stopped')
PY
pactl list short sources | rg 'so_ai_smoke_mic|so_ai_translated_mic' || true
```

Result:

```text
monitor so_ai_smoke_mic.monitor running True
stopped
```

No residual `so_ai_smoke_mic` or `so_ai_translated_mic` source remained after cleanup.

## CLI Smoke

```bash
poetry run so-intelligence-tools --help
```

Confirmed new commands:

- `run-voice-translation-virtual-mic-toggle`
- `install-gnome-voice-translation-shortcut`

## App Integration

The current system-audio translation window now includes a button to start/stop the voice
translation virtual microphone without closing the speaker-audio translation session.

Covered by:

```bash
poetry run pytest tests/test_system_audio_translation_app.py tests/test_voice_translation_realtime.py tests/test_voice_translation_virtual_microphone_audio.py -q
```

Result:

```text
7 passed in 0.33s
```

## Notes

- A paid/live OpenAI audio session was not executed in automated validation.
- The implementation is ready for a manual paid smoke test with `OPENAI_API_KEY` configured.
- The virtual source name to select in external apps is `so_ai_translated_mic.monitor`.
- Manual testing on 2026-06-10 showed `gpt-realtime-translate` rejects
  `output_modalities=["audio", "text"]` with `Invalid modalities`. The voice translation
  controller now requests `output_modalities=["audio"]` only.
- Manual testing on 2026-06-10 also showed `gpt-realtime-translate` fails on the standard
  `/v1/realtime` voice-agent endpoint with `Invalid URL (POST /v1/engines/gpt-realtime-translate/inference_stream)`.
  The controller now uses the dedicated translation WebSocket endpoint
  `/v1/realtime/translations` and translation session events.
- Manual testing on 2026-06-10 showed translation sessions reject
  `session.audio.output.voice` as an unknown parameter. The controller now configures only
  the output language for translation sessions.
- The WebSocket controller is now covered by unit tests for:
  - dedicated translation endpoint URL
  - `session.input_audio_buffer.append` input chunks
  - `session.output_audio.delta` PCM writes
  - `session.close` with receiver drain until close
- The passthrough/mixing pipeline is covered by unit tests for:
  - PCM s16le volume scaling with clipping
  - local microphone passthrough volume scaling
  - passthrough volume ducking while translation is active
  - restoring passthrough volume when translation stops
  - detailed pipeline session logs for passthrough, ducking and stop events
  - optional debug WAV recording of the final virtual microphone monitor output

## Paid Manual Smoke: 2026-06-10

A short live test was run against OpenAI with the Logitech C922 microphone fixed through
`VOICE_TRANSLATION_PHYSICAL_SOURCE`.

Observed:

- physical source: `alsa_input.usb-046d_C922_Pro_Stream_Webcam_719B22BF-02.analog-stereo`
- output virtual microphone: `so_ai_translated_mic.monitor`
- recorded file: `/tmp/translated_voice_live_test.wav`
- duration: `31.34s`
- RMS: `663`
- max peak-to-peak: `26376`
- realtime events included `session.output_audio.delta`
- `output_audio_written` reached `100` chunks and `1,920,000` bytes
- transcript deltas were produced in English, confirming Spanish-to-English translation

Conclusion: the dedicated Realtime Translation WebSocket path produced translated audio and
wrote it to the virtual microphone.
