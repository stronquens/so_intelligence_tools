# Voice Translation Virtual Microphone

Status: Working, API-backed.

The voice translation virtual microphone captures your physical microphone, sends your speech to a realtime translation backend, and exposes a virtual microphone named `so_ai_translated_mic` for call apps.

## Correct Call Setup

In Slack, Meet, Zoom, or similar apps:

| Setting | Select |
| --- | --- |
| Microphone | `so_ai_translated_mic` |
| Speaker | Your normal headphones or speakers |

Do not select `so_ai_translated_mic` as the speaker output.

For serious tests, use headphones. If speakers are active, your physical microphone can capture the remote participants and send delayed audio back into the call.

## Shortcut

Default:

```text
Ctrl + Alt + U
```

Manual command:

```bash
poetry run so-intelligence-tools run-voice-translation-virtual-mic-toggle
```

## Configuration

```env
OPENAI_API_KEY=
VOICE_TRANSLATION_SOURCE_LANGUAGE=Spanish
VOICE_TRANSLATION_TARGET_LANGUAGE=English
VOICE_TRANSLATION_OPENAI_MODEL=gpt-realtime-translate
VOICE_TRANSLATION_VOICE=marin
VOICE_TRANSLATION_PHYSICAL_SOURCE=
VOICE_TRANSLATION_VIRTUAL_SINK_NAME=so_ai_translated_mic
```

Volume defaults:

```env
VOICE_TRANSLATION_PASSTHROUGH_VOLUME=1.0
VOICE_TRANSLATION_DUCKED_PASSTHROUGH_VOLUME=0.03
VOICE_TRANSLATION_MAX_DUCKED_PASSTHROUGH_VOLUME=0.12
VOICE_TRANSLATION_OUTPUT_VOLUME=0.75
```

`DUCKED_PASSTHROUGH_VOLUME` is intentionally low so your original Spanish voice does not dominate the translated English voice.

## Physical Source Safety

`VOICE_TRANSLATION_PHYSICAL_SOURCE` should point to a real microphone source, for example a USB microphone or webcam microphone.

Do not point it to:

- a `.monitor` source
- `so_ai_translated_mic`
- the internal virtual sink/source created by this tool

## Linux Virtual Audio

The Linux implementation creates the virtual microphone dynamically with PulseAudio/PipeWire-compatible modules:

- `module-null-sink` creates the internal playback sink, normally `so_ai_translated_mic_sink`.
- `module-remap-source` exposes that sink monitor as the selectable microphone `so_ai_translated_mic`.
- `pacat` writes passthrough and translated PCM into the internal sink.
- Call apps should select `so_ai_translated_mic` as microphone and keep normal headphones or speakers as output.

## Windows Audio Plan

Windows virtual microphone output is not implemented yet. The planned first approach is to write translated PCM to an installed virtual audio cable playback endpoint, for example VB-CABLE `CABLE Input`, while the call app selects the paired recording endpoint, for example `CABLE Output`, as microphone.

See [Windows Audio Routing Research](windows-audio-routing.md).

## Debug Recordings

```env
VOICE_TRANSLATION_DEBUG_RECORDING_ENABLED=true
VOICE_TRANSLATION_DEBUG_RECORDINGS_DIR=~/.cache/so_intelligence_tools/voice_translation_debug_audio
```

Use this only for local troubleshooting. Debug recordings can contain private speech.

## Troubleshooting Echo

Echo or delayed self-audio usually means one of these is happening:

- The call app speaker is set to the virtual microphone.
- Your physical microphone is capturing the call audio from speakers.
- The original passthrough volume is too high.

Recommended test setup:

```text
Microphone: so_ai_translated_mic
Speaker: headphones / normal output
VOICE_TRANSLATION_DUCKED_PASSTHROUGH_VOLUME=0.03
VOICE_TRANSLATION_OUTPUT_VOLUME=0.75
```

