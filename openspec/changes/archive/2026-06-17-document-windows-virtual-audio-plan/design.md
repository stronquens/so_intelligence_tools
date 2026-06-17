# Design

## Current Linux Model

System audio capture uses the default PulseAudio/PipeWire sink monitor. The tool discovers the default sink with `pactl`, appends `.monitor`, and captures raw PCM with `parec`.

Translated virtual microphone output creates an internal null sink and remaps that sink monitor into a named source:

```text
module-null-sink -> so_ai_translated_mic_sink
so_ai_translated_mic_sink.monitor -> module-remap-source -> so_ai_translated_mic
```

The application writes PCM to the sink with `pacat`. Call apps select `so_ai_translated_mic` as microphone while keeping normal headphones or speakers as output.

## Windows Model

Windows has a good built-in answer for capture, but not for creating a virtual microphone in user space:

- Use WASAPI loopback to capture the render endpoint mix.
- Use Application Loopback Capture when per-process capture is needed on supported Windows builds.
- For virtual microphone output, depend initially on an installed virtual audio cable driver such as VB-CABLE.
- Defer custom driver work based on SysVAD because it requires WDK, driver signing/deployment, administrator work, and substantially higher maintenance.

## Recommended First Slice

1. Add Windows device discovery and preflight checks.
2. Capture incoming/system audio through WASAPI loopback.
3. Write translated PCM to a configured virtual cable playback endpoint, for example `CABLE Input`.
4. Instruct the user to select the paired recording endpoint, for example `CABLE Output`, as the microphone in Meet/Zoom/Slack.
5. Keep physical speakers/headphones separate to avoid feedback.

## Risks

- Device names can be localized or renamed by Windows/user settings; adapters should prefer stable endpoint IDs where possible.
- VB-CABLE requires administrator installation and reboot, though the application itself can remain user-level.
- One virtual cable can publish translated microphone output; more complex bidirectional routing may need a second cable or Voicemeeter.
