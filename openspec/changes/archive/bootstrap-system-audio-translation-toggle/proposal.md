# Proposal

## Title

Bootstrap real-time system audio translation toggle

## Why

The project already has a capability for real-time system-audio transcription, but the intended user experience is now clearer:

- press a keyboard shortcut once to open a dedicated window and start listening
- capture the audio currently going to the system speakers
- transcribe and translate it into Spanish in real time
- press the same shortcut again to stop listening and close the window
- allow pausing, resuming, and retrying from the window itself without losing visible history

This needs to be modeled explicitly because it spans shortcut behavior, streaming orchestration, system audio capture, and a dedicated live-reading window.

## Scope

- define a toggle-style shortcut flow for the capability
- define the first target behavior as translation to Spanish
- define the window lifecycle and active/inactive states
- define pause, resume, reset, and close behavior from the window
- define the Linux-first technical direction for capturing system output audio
- define how temporary backend failures are handled without losing live session context
- prepare the implementation tasks for a first iteration

## Phase 1

The first implementation phase should prioritize a working Linux MVP with the shortest path to useful live subtitles:

- Linux desktop only
- Python + Poetry, aligned with the rest of the project
- normal resizable desktop window
- system-output audio capture through the Linux monitor source
- remote streaming translation backend
- English audio translated to Spanish
- translated text as the primary live output
- speaker labels treated as best effort, not as a launch blocker

This phase should optimize for:

- low perceived latency
- reliable start/stop behavior from the same shortcut
- readable scrolling history
- explicit error and reconnect handling

It should not block on:

- polished multi-platform packaging
- exact speaker identification
- local-model parity
- overlay-style UX instead of a standard system window

## Out of Scope

- production-grade diarization
- polished subtitle UX across multiple windows
- support for every Linux audio stack
- implementation of remote multilingual expansion beyond the first target flow
