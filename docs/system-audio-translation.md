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

## Limitations

- Realtime translation can require a paid provider API key.
- Speaker separation is not currently a polished feature.
- Audio routing depends on the local Linux audio stack.

