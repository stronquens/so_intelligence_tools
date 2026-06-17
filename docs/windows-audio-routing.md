# Windows Audio Routing Research

Status: researched, not implemented.

This page compares the existing Linux audio model with a practical Windows plan for:

- capturing system audio for live transcription or translation
- publishing translated speech as a virtual microphone for call apps

## Current Linux Implementation

Linux currently relies on PulseAudio/PipeWire-compatible tools:

| Need | Linux mechanism | Code path |
| --- | --- | --- |
| Capture audio playing on the system | Detect default sink with `pactl`, capture its `.monitor` source with `parec` | `system_audio_translation/audio_capture.py` |
| Capture the physical microphone | Detect default source with `pactl`, reject `.monitor` and project virtual sources, capture with `parec` | `voice_translation_virtual_microphone/audio.py` |
| Create translated virtual microphone | Load `module-null-sink`, then expose its monitor as a microphone with `module-remap-source` | `voice_translation_virtual_microphone/audio.py` |
| Write final PCM audio | Stream PCM into the internal sink with `pacat` | `voice_translation_virtual_microphone/audio.py` |
| Optional debug recording | Record the virtual sink monitor with `parecord` | `voice_translation_virtual_microphone/audio.py` |

The virtual microphone flow is:

```text
physical microphone -> app capture -> realtime provider
provider translated PCM -> pacat -> so_ai_translated_mic_sink
so_ai_translated_mic_sink.monitor -> so_ai_translated_mic
call app microphone -> so_ai_translated_mic
call app speaker -> normal headphones or speakers
```

The internal sink behaves like a virtual speaker, but users should not select it as the call speaker. The call app should select the remapped source `so_ai_translated_mic` as its microphone and keep normal headphones or speakers for output.

## Windows Equivalents

Windows does not provide the same user-space `pactl load-module` model. The two halves need different strategies.

### System Audio Capture

Use WASAPI loopback capture for the first Windows implementation.

Microsoft documents that WASAPI loopback captures audio being played by a render endpoint. The capture stream is opened on a rendering endpoint with `AUDCLNT_STREAMFLAGS_LOOPBACK`, and the stream must run in shared mode.

For future per-app routing, Microsoft also provides an Application Loopback Capture sample using `ActivateAudioInterfaceAsync`. That path can include or exclude a specific process tree on Windows 10 build 20348 or later.

Recommended first adapter:

```text
WindowsWasapiLoopbackCapture
  input: default render endpoint or configured endpoint id
  output: PCM s16le chunks matching the existing capture port
```

### Translated Virtual Microphone Output

Windows needs an actual audio endpoint that external apps can enumerate as a recording device. For the first version, use an installed virtual audio cable driver instead of building a custom driver.

Recommended first dependency:

```text
VB-CABLE
playback endpoint: CABLE Input
recording endpoint: CABLE Output
```

VB-Audio describes VB-CABLE as a virtual audio driver where audio sent to the playback/input side is forwarded to the recording/output side. That maps well to the Linux `pacat -> sink -> remap-source` design:

```text
provider translated PCM -> Windows audio render/write -> CABLE Input
CABLE Output -> selected microphone in Meet/Zoom/Slack
call app speaker -> normal headphones or speakers
```

Recommended first adapter:

```text
WindowsVirtualCableMicrophoneOutput
  config: virtual cable playback endpoint id/name
  writes: translated PCM to the cable playback endpoint
  setup check: paired recording endpoint exists and is user-selectable
```

## Recommended Windows Setup

For the first Windows virtual microphone slice:

1. Install VB-CABLE or another explicit virtual audio cable driver.
2. Configure the app to write translated audio to the cable playback endpoint.
3. In Meet, Zoom, Slack, or similar apps, select the paired cable recording endpoint as microphone.
4. Keep the app speaker set to normal headphones or speakers.
5. Use headphones for serious tests to avoid the physical microphone capturing remote audio.

One cable is enough for translated microphone output. A second cable or a mixer such as Voicemeeter may be useful later if we need isolated bidirectional routing, but it should not be required for the first implementation.

## Why Not Build A Driver First

Microsoft's SysVAD sample is the right reference if the project eventually needs a first-party virtual audio driver. It is intentionally a driver-development path: WDK, Visual Studio, driver deployment, administrator actions, signing/test-signing, reboot and installer planning.

That is too heavy for the next product slice. The better path is:

```text
first: WASAPI capture + third-party virtual cable
later: optional first-party driver if distribution requires it
```

## Sources

- Microsoft WASAPI loopback recording: https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording
- Microsoft Application Loopback Capture sample: https://learn.microsoft.com/en-us/samples/microsoft/windows-classic-samples/applicationloopbackaudio-sample/
- Microsoft SysVAD virtual audio driver sample: https://learn.microsoft.com/en-us/samples/microsoft/windows-driver-samples/sysvad-virtual-audio-device-driver-sample/
- Microsoft sample audio drivers: https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/sample-audio-drivers
- VB-Audio Virtual Cable: https://vb-audio.com/Cable/
