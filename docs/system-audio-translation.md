# System Audio Translation

Status: Working, API-backed for the realtime mode.

System audio translation listens to audio playing on the computer and displays live Spanish translation in its own window.

## Shortcut

Default:

```text
Ctrl + Alt + Y
```

Manual command:

```bash
poetry run so-intelligence-tools run-system-audio-translation-toggle
```

## Modes

Common mode:

```env
SYSTEM_AUDIO_TRANSLATION_MODE=translate_es_openai_realtime
```

The code also keeps chunked translation paths for fallback and development. Realtime mode currently depends on an external provider API.

## Configuration

```env
OPENAI_API_KEY=
SYSTEM_AUDIO_TRANSLATION_SOURCE_LANGUAGE=auto
SYSTEM_AUDIO_TRANSLATION_TARGET_LANGUAGE=es
SYSTEM_AUDIO_TRANSLATION_OPENAI_REALTIME_MODEL=gpt-realtime
SYSTEM_AUDIO_TRANSLATION_OPENAI_REALTIME_CHUNK_MS=80
SYSTEM_AUDIO_TRANSLATION_OPENAI_REALTIME_SILENCE_DURATION_MS=280
```

`SYSTEM_AUDIO_TRANSLATION_OPENAI_REALTIME_SILENCE_DURATION_MS` controls how
quickly the provider closes a spoken turn after silence. Lower values reduce
latency but can produce shorter history blocks. Tune it conservatively because
larger values delay every completed translation.

## Realtime History Behavior

Realtime history is tracked by provider turn identity rather than translated
text. This means:

- a complete later turn is published even if an earlier turn is still missing
  its original transcript;
- two distinct turns with identical translated text are both preserved;
- original and translated finals may arrive in either order and still produce
  one history block;
- pending original-and-translation content is finalized when the receiver
  stops, reconnects or is cancelled;
- a translation-only residual is preserved as a fallback history block, while
  an original-only residual is logged but is not presented as a completed
  translation.

## Linux Audio

The tool uses PulseAudio/PipeWire-compatible capture tooling. Make sure `pulseaudio-utils` is installed and that `pactl` and `parec` are available.

Implementation details:

- The Linux adapter detects the default output sink with `pactl`.
- It captures the sink monitor source, for example `<default-sink>.monitor`.
- It reads mono `s16le` PCM chunks with `parec` and forwards those chunks to the translation pipeline.

## Windows Audio Plan

Windows system audio capture is not implemented yet. The planned approach is WASAPI loopback capture. See [Windows Audio Routing Research](windows-audio-routing.md).

## Logs And Control Socket

```bash
tail -n 120 ~/.cache/so_intelligence_tools/system_audio_shortcut.log
ls ~/.cache/so_intelligence_tools/system_audio_logs
```

Default socket:

```text
~/.cache/so_intelligence_tools/system_audio_translation.sock
```

Realtime session logs include structured lifecycle events such as
`block_published`, `residual_block_published`,
`residual_original_without_translation` and `audio_chunk_dropped`. The last
event reports a cumulative drop count and the pending-queue limit, making audio
loss under backpressure visible instead of silent.

At startup, a small number of dropped chunks can indicate that capture began
before the realtime connection finished warming up. Repeated drops later in a
session indicate sustained backpressure and should be investigated separately
from history rendering.

## Limitations

- Realtime translation can require a paid provider API key.
- Speaker separation is not currently a polished feature.
- Audio routing depends on the local Linux audio stack.
