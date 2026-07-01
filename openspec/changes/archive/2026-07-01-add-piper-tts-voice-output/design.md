## Context

The project already uses a warm Docker model server for push-to-talk dictation through faster-whisper. The desired reverse path is local text-to-speech: a service that stays warm when voice output is wanted, and can be stopped when the user wants silent text-only operation.

The July 1, 2026 CPU benchmark found Piper to be the best first implementation target on this workstation: it generated Spanish audio much faster than realtime, while NeuTTS, Qwen3-TTS, and Chatterbox all completed but were multiple times slower than realtime on CPU.

The requested client surface is a Codex/VS Code workflow that reads aloud assistant progress and messages. This design treats that as a visible-event integration only: hidden reasoning, private chain-of-thought, or unavailable internal model state is out of scope and must not be requested or synthesized.

## Goals / Non-Goals

**Goals:**

- Provide a Dockerized Piper runtime that starts warm and exposes a local HTTP API.
- Use a Spanish-capable Piper voice by default, with configuration ready for a female Spanish voice if one is selected and validated.
- Add lifecycle commands for start, stop, status, and readiness, mirroring the operational style of the Whisper Docker runtime.
- Add a client-side voice-output bridge that can send visible assistant text to the local TTS API and play the resulting audio.
- Make stopped/unavailable TTS equivalent to voice-output off.
- Keep audio ephemeral by default.

**Non-Goals:**

- Do not implement hidden chain-of-thought access or speech. Only visible UI/event text can be spoken.
- Do not build a high-quality expressive TTS stack around Qwen, Chatterbox, or NeuTTS in this iteration.
- Do not require the TTS service for normal text workflows.
- Do not retain generated assistant audio by default.
- Do not make the VS Code/Codex integration depend on undocumented private APIs if a stable event source is unavailable.

## Decisions

### Use Piper as the first local TTS runtime

Piper is the first runtime because it is fast enough for CPU-only interactive use and has simple runtime requirements. The initial Docker service should package `piper-tts`, a selected Spanish voice model, and a small HTTP wrapper.

Alternatives considered:

- Kokoro ONNX: still fast enough, but slower than Piper and less direct as a first Docker baseline.
- NeuTTS Nano Spanish: stronger Spanish focus and reference voice support, but around 3x slower than realtime on this CPU.
- Qwen3-TTS and Chatterbox: richer control surfaces, but far too slow for interactive CPU-only use.

### Keep the model warm behind an HTTP API

The service should load the Piper voice at container startup and keep it ready. A `GET /health` endpoint reports readiness after the voice is loaded. A `POST /v1/audio/speech` endpoint accepts JSON text and returns WAV audio or a structured error.

The API should intentionally resemble a simple local speech endpoint rather than couple to any one UI. The expected request shape is:

```json
{
  "text": "Texto visible que se va a leer",
  "voice": "default",
  "speaker": null,
  "speed": 1.0
}
```

### Use container lifecycle as the primary off switch

If the Docker service is stopped or unhealthy, client integrations must treat voice output as disabled and continue silently. This makes Docker Desktop or CLI control enough for the user to turn speech on/off.

A later UI setting can layer on top of this, but it must not be the only way to stop speech.

### Add a small local client/playback layer

The Python side should provide a TTS client that:

- checks service readiness before speaking,
- normalizes or chunks long text,
- sends text to the local service,
- plays the returned audio through the local audio stack,
- serializes playback so messages do not overlap,
- can cancel or skip pending speech when requested.

Playback should prefer existing Linux tools from the repo bootstrap path if available. If a cross-platform Python playback dependency is introduced, it must be explicit in Poetry and documented.

### Speak visible assistant events only

The Codex/VS Code integration should subscribe only to visible text/events that the extension already displays, such as status messages, assistant response chunks, command summaries, or final answers. It must not attempt to access private chain-of-thought, hidden reasoning, prompt internals, or any unavailable internal model stream.

To avoid extremely noisy output, the first implementation should support event filtering:

- speak final assistant messages by default,
- optionally speak visible progress/status events,
- skip code blocks or truncate them unless the user explicitly enables verbose reading,
- debounce partial streaming chunks into sentence-like segments.

### Voice selection

The first implementation should keep the currently benchmarked Spanish Piper voices available. Before making a female voice the default, the implementation should identify and smoke-test an available Spanish female Piper voice, then record its latency and a short audio sample in the change evidence.

If no acceptable Spanish female voice is available in Piper voices, the default should remain the best validated Spanish voice and the limitation should be documented.

## Risks / Trade-offs

- [Risk] The Codex/VS Code extension may not expose stable event hooks for all visible messages. -> Mitigation: implement the bridge behind an adapter interface and support a file/stdin/WebSocket event source if direct extension hooks are not available.
- [Risk] Reading every status event aloud may be distracting. -> Mitigation: default to final assistant messages and provide filters for progress/status verbosity.
- [Risk] Long messages can create large audio and delayed playback. -> Mitigation: chunk text, queue playback, and allow cancellation.
- [Risk] Piper voice quality may be less natural than larger models. -> Mitigation: keep Piper as the latency baseline and preserve benchmark evidence for future GPU/higher-quality alternatives.
- [Risk] Generated audio may contain private work content. -> Mitigation: do not persist speech audio by default and document debug capture separately if ever added.
- [Risk] A stopped TTS container could look like a failure. -> Mitigation: status commands and logs should clearly distinguish "voice output disabled because service is stopped" from synthesis errors.
