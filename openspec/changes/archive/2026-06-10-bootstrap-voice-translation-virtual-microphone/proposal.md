# Bootstrap Voice Translation Virtual Microphone

## Summary

Implement the first Linux version of the voice translation virtual microphone capability.
The tool will capture the user's physical microphone, send Spanish speech to a remote
realtime speech-to-speech translation model, and publish the translated audio through a
virtual microphone selectable by external apps.

## Motivation

The project already supports translating system speaker audio into Spanish text. The next
step is the complementary live communication workflow: the user speaks Spanish, and video
call apps receive translated spoken audio from a virtual microphone.

This must be implemented as an operating-system integration rather than a Zoom, Meet, Slack,
or browser-specific integration.

## Scope

- Add a Linux/PulseAudio first implementation of a virtual microphone device.
- Add a realtime voice translation controller backed by OpenAI-compatible realtime audio
  output, with `gpt-realtime-translate` as the default model.
- Add a CLI toggle command and GNOME shortcut installer.
- Add safe cleanup for loaded PulseAudio modules and spawned audio processes.
- Add logs and clear user-facing errors for missing API key, missing audio tools, and
  virtual microphone setup failures.
- Keep the current selected text correction and system audio translation features unchanged.

## Out of Scope

- No production tray icon in this first iteration.
- No Electron/Vue UI for this capability yet.
- No Windows/macOS backend yet.
- No custom voice cloning.
- No translation provider marketplace or provider auto-selection.
- No automatic integration with specific videoconference apps.

## Decisions

- V1 targets Linux with PulseAudio-compatible tooling (`pactl`, `parec`, `pacat`).
- The virtual microphone is implemented as a named null sink; apps can select its monitor
  source as the microphone.
- The physical microphone is captured directly from the default PulseAudio source unless
  overridden by configuration.
- The first translation direction defaults to Spanish input and English output.
- OpenAI Realtime Translate is the preferred remote provider because official docs describe
  `gpt-realtime-translate` as a streaming speech-to-speech translation model that returns
  translated audio while source audio is still arriving.
- Passthrough remains part of the capability contract, but the first implementation may
  expose it as an explicit fallback mode rather than silently mixing original and translated
  audio.

## Risks

- Some applications may hide PulseAudio monitor sources unless input devices are refreshed
  after the virtual microphone is created.
- Laptop CPU and network conditions can still affect conversational latency.
- OpenAI realtime output audio chunk events may differ slightly across SDK versions; the
  implementation should tolerate both GA and legacy event names where practical.
- Cost accrues while the realtime session is active and receiving audio.
