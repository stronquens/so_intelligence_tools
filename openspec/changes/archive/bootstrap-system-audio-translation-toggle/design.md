# Design

## Summary

This capability should be built as a toggle workflow owned by one long-lived controller:

- `shortcut pressed` while inactive:
  - open window
  - begin system-audio capture
  - start streaming transcription/translation

- `shortcut pressed` while active:
  - stop capture
  - stop streaming
  - close window

This differs from push-to-talk dictation because it is stateful and windowed rather than hold-to-record.

Inside the active window, the user should also be able to:

- pause capture and remote consumption
- resume the same session
- retry after an error without losing visible history
- close the window to end the session entirely

## Phase 1 Technical Direction

For this repository, the most coherent first implementation is:

- Python application code inside the existing Poetry project
- Linux-first desktop integration
- dedicated desktop window built with a native Python UI toolkit
- system-output capture through the Linux monitor source
- remote streaming translation provider

Electron is not the preferred first path here because the repository, tooling, and current desktop integrations are already Python-centric. The UI is not the latency bottleneck; audio capture, chunking, transport, and streaming inference are.

## Product Behavior

First iteration target:

- input source: system output audio
- expected source language: English-first
- output language: Spanish
- fixed initial session mode: `translate_es`
- presentation: translated live text in a dedicated window
- history: scrolling accumulated transcript blocks with timestamps
- speaker labels: best effort only
- validated provider path: remote first

The user should not need to choose the source application. The feature should follow whatever is sounding through the speakers at that moment.

## Phase 1 UI Choice

Prefer a Python-native desktop window rather than a web shell.

Recommended order:

- `PySide6` if we optimize for implementation speed and cross-platform windowing ergonomics
- `GTK/PyGObject` if we optimize for GNOME-native behavior

For a first spike, `PySide6` is the most practical default unless Linux integration testing reveals a strong GTK-specific advantage.

## Main Components

### Shortcut toggle action

Use the keyboard-shortcuts capability to register a dedicated shortcut that toggles the feature on and off.

The action must be idempotent:

- if already running, it stops
- if stopped, it starts

The exact default shortcut should be chosen to minimize conflicts with common Linux and application shortcuts, while remaining configurable later.

### Session controller

Introduce an application-level controller for the capability, responsible for:

- current active/inactive state
- paused state
- reconnecting/error state
- current session mode
- window lifecycle
- capture lifecycle
- stream lifecycle
- controlled shutdown on second toggle or error
- deferred session-log persistence on end

Recommended controller states:

- `inactive`
- `starting`
- `active`
- `paused`
- `reconnecting`
- `error`
- `stopping`

### Audio capture

Linux-first implementation should target system output capture through the active desktop audio stack rather than per-app integration.

The most likely first path is PipeWire or PulseAudio monitor sources, abstracted behind an adapter so the rest of the flow stays portable.

For Phase 1, the simplest realistic capture path is:

- use the system monitor source exposed through PipeWire/PulseAudio compatibility
- start capture through a subprocess adapter, likely `parec`
- read PCM16 mono chunks from stdout
- stream those chunks through the translation client

Initial practical defaults to validate:

- mono audio
- `24000 Hz`
- chunk windows around `40-80 ms`

This path is intentionally Linux-specific for the first implementation, but should sit behind an adapter boundary such as `SystemAudioCapturePort`.

If the backend connection drops temporarily, capture should keep enough recent context in a bounded in-memory buffer to allow a best-effort catch-up once the stream reconnects.

### Translation backend

The first validated iteration should assume a remote-capable streaming backend because this capability is highly sensitive to both latency and quality.

Local inference remains architecturally open, but should be treated as an experimental later path until a spike validates it for this use case.

At the orchestration level, the capability should consume a stream-friendly inference interface that can later resolve to:

- local backend
- remote backend

The provider choice should also remain open to:

- LiteLLM Proxy
- OpenAI realtime or audio-capable APIs
- other OpenAI-compatible or provider-specific streaming backends if they materially improve quality

For Phase 1, the implementation should explicitly test two families of backend:

- direct realtime translation API
- streaming ASR plus separate translation pipeline

The current hypothesis is:

- direct realtime translation is likely the shortest path to usable subtitles
- diarization-friendly ASR plus separate translation may become necessary if speaker separation becomes a stronger requirement

This change should therefore leave model and provider benchmarking as an explicit spike rather than freezing the decision too early.

## Window

The window should be a normal resizable system window:

- clear active indicator
- obvious stopped/idle/paused/error state
- continuously updating translated text
- scrollable accumulated history
- controls for pause, resume, reset, and close

The first iteration does not need a visible mode selector, but the window model should leave room for a future dropdown or equivalent selector without reworking the core session flow.

For the first iteration, show the translated text as the primary content. The original text can be added later if it does not hurt latency or clarity.

The first UI does not need to be visually elaborate. It should optimize for:

- fast startup
- large readable text
- clear session status
- stable scrolling history
- explicit pause/resume/reset controls
- a visible mode dropdown that can switch between the low-latency OpenAI realtime path and the chunked fallback path

## Error Handling

Important failure modes:

- no valid monitor source for system audio
- backend stream failure
- window creation failure
- duplicate concurrent start requests
- partial reconnect with missed audio
- speaker separation unavailable

On failure:

- keep the visible history if possible
- notify the user clearly
- allow explicit retry from the window
- keep capture and bounded buffering active during brief reconnect attempts when feasible

## Open Spikes

The first implementation should explicitly investigate:

- which provider/model gives the best latency-quality balance for English-to-Spanish live translation
- whether OpenAI realtime or other specialized audio APIs outperform generic multimodal LLM routes
- what buffering window is realistic for reconnect-and-catch-up behavior
- whether speaker diarization is feasible as best effort without harming latency too much
- whether `PySide6` or `GTK/PyGObject` produces the least friction for this repository on Linux
- whether `parec` over PipeWire/PulseAudio compatibility is sufficient for Zoom/Meet/Slack audio on the target machine

## Why This Split

This design keeps the feature aligned with the rest of the project:

- business flow in Python runners
- shortcut-specific behavior in keyboard integration
- backend provider hidden behind the inference API boundary
- Linux-specific capture isolated in adapters
