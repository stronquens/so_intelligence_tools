# Design

## Architecture

```text
Physical microphone
  -> local passthrough capture/playback into PulseAudio null sink
  -> null sink monitor source selected as microphone in Zoom/Meet/Slack

When translation is active:
Physical microphone
  -> local passthrough capture/playback, ducked volume
  -> OpenAI realtime speech-to-speech translation
  -> translated PCM audio chunks, boosted volume
  -> same PulseAudio null sink
  -> same null sink monitor source selected as microphone in Zoom/Meet/Slack
```

The backend stays in Python and uses the same operating-system integration style as the
existing tools. The app-level pipeline separates virtual microphone lifecycle, local
passthrough, remote translation session, status logging, and cleanup. This keeps the virtual
microphone usable as a normal Logitech passthrough device when no remote API session is
active.

## Virtual Audio Device

V1 uses PulseAudio-compatible commands:

- `pactl load-module module-null-sink sink_name=so_ai_translated_mic ...`
- `pacat --device=so_ai_translated_mic --format=s16le --rate=24000 --channels=1`
- the selectable microphone is expected to appear as `so_ai_translated_mic.monitor`

The implementation records module IDs returned by `pactl` and unloads them during shutdown.
If cleanup fails, logs should include the module IDs and device names so the user can remove
them manually.

## Realtime Provider

The provider opens a realtime session with:

- model: `gpt-realtime-translate` by default
- input audio: PCM 24 kHz mono
- output audio: PCM 24 kHz mono
- source language: Spanish by default
- target language: English by default

The controller connects to the dedicated translation WebSocket endpoint:

- `wss://api.openai.com/v1/realtime/translations?model=gpt-realtime-translate`

It sends microphone chunks using `session.input_audio_buffer.append` and consumes audio
delta events such as `session.output_audio.delta`. The session update is intentionally
minimal and configures only the output language:

```json
{
  "type": "session.update",
  "session": {
    "audio": {
      "output": {
        "language": "en"
      }
    }
  }
}
```

Text transcript deltas may be logged for debugging, but the virtual microphone output is
driven by audio deltas, not by an intermediate text translation + TTS pipeline.

When stopping a translation session, the controller sends `session.close` and keeps reading
until `session.closed` or a short timeout. This prevents dropping translated audio that is
still draining from the session.

## Toggle Behavior

The CLI follows the existing app pattern:

- If no session is running, start the virtual mic, open the realtime provider, and keep the
  process alive.
- If a session is running, send a stop command through a local Unix socket.
- On stop, close OpenAI, stop capture, stop playback, unload PulseAudio modules, and write
  a session log.

## Configuration

New settings should be environment-driven:

- `VOICE_TRANSLATION_OPENAI_API_KEY` with fallback to `OPENAI_API_KEY`
- `VOICE_TRANSLATION_OPENAI_BASE_URL` with fallback to `OPENAI_BASE_URL`
- `VOICE_TRANSLATION_OPENAI_MODEL`, default `gpt-realtime-translate`
- `VOICE_TRANSLATION_SOURCE_LANGUAGE`, default `es`
- `VOICE_TRANSLATION_TARGET_LANGUAGE`, default `en`
- `VOICE_TRANSLATION_VOICE`, default provider-recommended voice when applicable
- `VOICE_TRANSLATION_SAMPLE_RATE_HZ`, default `24000`
- `VOICE_TRANSLATION_CHUNK_MS`, default `80`
- `VOICE_TRANSLATION_PHYSICAL_SOURCE`, optional PulseAudio source override
- `VOICE_TRANSLATION_PASSTHROUGH_VOLUME`, default `1.0`
- `VOICE_TRANSLATION_DUCKED_PASSTHROUGH_VOLUME`, default `0.18`
- `VOICE_TRANSLATION_OUTPUT_VOLUME`, default `1.25`
- `VOICE_TRANSLATION_VIRTUAL_SINK_NAME`, default `so_ai_translated_mic`
- `VOICE_TRANSLATION_CONTROL_SOCKET_PATH`
- `VOICE_TRANSLATION_LOGS_DIR`
- `VOICE_TRANSLATION_DEBUG_RECORDING_ENABLED`, default `false`
- `VOICE_TRANSLATION_DEBUG_RECORDINGS_DIR`, default
  `~/.cache/so_intelligence_tools/voice_translation_debug_audio`
- `GNOME_VOICE_TRANSLATION_BINDING`

When debug recording is enabled, the implementation records the final virtual microphone
monitor source with `parecord` instead of duplicating internal chunks. This captures the
same mixed signal external apps receive, including local passthrough, ducking and translated
audio overlay.

## User Feedback

V1 can use terminal output, notifications, and logs. A later UI/tray capability may provide
better controls and a persistent toolbar indicator.

## Validation Strategy

- Unit tests for PulseAudio command construction and cleanup.
- Unit tests for realtime event parsing and output audio routing.
- CLI smoke checks that can run without calling OpenAI by mocking provider/audio layers.
- Manual smoke test:
  1. Start the tool.
  2. Confirm `so_ai_translated_mic.monitor` appears in available input sources.
  3. Select it in a recording app.
  4. Speak Spanish.
  5. Confirm translated English audio reaches the selected app.
