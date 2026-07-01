## 1. Piper Runtime

- [x] 1.1 Create `docker/piper-tts/` with Dockerfile, compose file, `.env.example`, and startup script.
- [x] 1.2 Implement a small HTTP wrapper that loads Piper once at startup and exposes `GET /health`.
- [x] 1.3 Implement `POST /v1/audio/speech` for text-to-WAV synthesis with structured errors.
- [x] 1.4 Package the benchmarked Spanish Piper voices and document/configure the default voice.
- [x] 1.5 Search for available Spanish female Piper voices, smoke-test candidates, and record one sample/latency note or document why no candidate was selected.

## 2. CLI And Lifecycle

- [x] 2.1 Add CLI commands to start, stop, and show status for the Piper TTS Docker service.
- [x] 2.2 Add an install/setup command that prepares the Piper TTS `.env` without overwriting user configuration.
- [x] 2.3 Ensure stopped/unhealthy service state is reported as voice output disabled, not as a blocking application error.

## 3. Local Speech Client

- [x] 3.1 Add a Python TTS client for readiness checks and speech requests.
- [x] 3.2 Add local audio playback for returned WAV data using project-approved Linux dependencies or explicit Poetry dependencies.
- [x] 3.3 Add text normalization/chunking and serialized playback so long messages do not overlap.
- [x] 3.4 Add cancellation or queue clearing for pending speech.

## 4. Visible Event Integration

- [x] 4.1 Define a client adapter interface for visible assistant events.
- [x] 4.2 Add a first Codex/VS Code integration path if visible message hooks are available, or a documented local event-source fallback if direct hooks are not stable.
- [x] 4.3 Read the full visible Codex cycle by default, with a `--final-only` mode for reduced speech.
- [x] 4.4 Skip or truncate code blocks, long logs, and command output by default.
- [x] 4.5 Ensure hidden reasoning, private chain-of-thought, prompts, and tool internals are never requested, logged, synthesized, or spoken.
- [x] 4.6 Add per-window Codex voice session controls so one VS Code window can be muted without stopping Piper globally.
- [x] 4.7 Normalize Markdown speech so code fences are announced without reading their contents, URLs are shortened, and newline-delimited progress is spoken without long waits.
- [x] 4.8 Announce turn completion in full-cycle voice mode.
- [x] 4.9 Add configurable Codex speech detail modes and prioritize turn-completion speech over queued message segments.
- [x] 4.10 Add per-window voice/detail controls and same-container Piper voice selection by request parameter.

## 5. Documentation

- [x] 5.1 Document Linux install/start/stop/status workflow for Piper TTS.
- [x] 5.2 Document voice selection, including the female-voice validation outcome.
- [x] 5.3 Document privacy boundaries, ephemeral audio behavior, and the stopped-container off switch.
- [x] 5.4 Add troubleshooting for Docker readiness, missing audio playback tools, and unavailable VS Code/Codex hooks.

## 6. Validation

- [x] 6.1 Validate OpenSpec with `poetry run openspec validate add-piper-tts-voice-output --strict`.
- [x] 6.2 Start the Piper TTS container, verify `/health`, synthesize a Spanish smoke-test phrase, and save evidence inside the change.
- [x] 6.3 Verify stopping the container disables speech without blocking a client request.
- [x] 6.4 Verify no generated per-message audio remains outside expected temporary paths.
- [x] 6.5 Record validation commands, results, and retained evidence in `validation.md`.
