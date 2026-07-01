## ADDED Requirements

### Requirement: Warm Piper TTS Runtime
The system SHALL provide a local Dockerized Piper TTS runtime that loads the configured voice at startup and remains warm while the container is running.

#### Scenario: Service starts and becomes ready
- **WHEN** the user starts the Piper TTS Docker service
- **THEN** the service SHALL load the configured Piper voice before reporting ready
- **AND** the service SHALL expose a health endpoint that reports readiness.

#### Scenario: Service is stopped
- **WHEN** the Piper TTS Docker service is stopped
- **THEN** voice output SHALL be considered disabled
- **AND** normal text-only assistant workflows SHALL continue without blocking.

### Requirement: Local Speech API
The system SHALL expose a local HTTP API for converting visible text to speech audio.

#### Scenario: Text is synthesized
- **WHEN** a client sends valid text to the local speech endpoint
- **THEN** the service SHALL synthesize the text with Piper
- **AND** the service SHALL return playable audio with a content type and status code that clients can handle deterministically.

#### Scenario: Voice is selected per request
- **WHEN** the Piper service is configured with multiple voice aliases
- **THEN** clients SHALL be able to select a voice by passing a `voice` parameter to the local speech endpoint
- **AND** the service SHALL use the requested voice without requiring a separate container per voice.

#### Scenario: Invalid or empty text is submitted
- **WHEN** a client sends empty or invalid text to the local speech endpoint
- **THEN** the service SHALL reject the request with a structured error
- **AND** the service SHALL NOT crash or restart the loaded model.

### Requirement: Voice Output Toggle Semantics
The system SHALL treat TTS service availability as the primary voice-output toggle.

#### Scenario: TTS service is unavailable
- **WHEN** a client attempts to speak text and the local TTS service is stopped, unreachable, or unhealthy
- **THEN** the client SHALL skip speech silently or report a non-blocking disabled status
- **AND** the client SHALL NOT retry aggressively or delay the visible text workflow.

#### Scenario: TTS service is available
- **WHEN** a client attempts to speak text and the local TTS service is ready
- **THEN** the client SHALL submit the text for synthesis
- **AND** the resulting audio SHALL be played through the local audio output.

#### Scenario: One Codex window is muted
- **WHEN** multiple Codex voice bridge sessions are active and the user disables one session
- **THEN** new speech events from that session SHALL be skipped
- **AND** other active sessions SHALL continue speaking if they remain enabled
- **AND** the local TTS service SHALL remain running.

#### Scenario: One Codex window uses a different voice or detail mode
- **WHEN** multiple Codex voice bridge sessions are active and the user changes the voice or speech detail for one session
- **THEN** new speech events from that session SHALL use the updated voice or detail mode
- **AND** other active sessions SHALL keep their own settings.

### Requirement: Visible Assistant Event Speech
The system SHALL only speak assistant or Codex events that are visible to the user in the client experience.

#### Scenario: Visible assistant message is emitted
- **WHEN** a supported client emits a visible assistant message or final answer
- **THEN** the voice-output bridge SHALL be allowed to send that visible text to the TTS service according to the user's speech filters.

#### Scenario: Visible lifecycle activity is emitted
- **WHEN** a supported client emits visible lifecycle events such as assistant text deltas, tool start/completion, command start/completion, plan updates, web-search status, or file-change status
- **THEN** the default voice-output bridge SHALL be allowed to read safe visible summaries of that activity aloud
- **AND** the bridge SHALL provide a reduced mode for reading final visible assistant messages only.

#### Scenario: Hidden reasoning is not exposed
- **WHEN** hidden model reasoning, private chain-of-thought, prompts, tool internals, or unavailable internal streams exist
- **THEN** the voice-output bridge SHALL NOT request, expose, log, synthesize, or read that hidden content aloud.

### Requirement: Speech Filtering And Queueing
The system SHALL provide client-side filtering and queueing so voice output remains understandable during assistant activity.

#### Scenario: Speech detail mode is configured
- **WHEN** the user configures a Codex voice detail mode
- **THEN** the listener SHALL support modes for task-boundary-only speech, action/tool lifecycle speech, standard visible message speech, no-code visible message speech, and exhaustive visible message speech.

#### Scenario: Streaming text arrives in chunks
- **WHEN** a visible assistant response arrives as multiple partial chunks
- **THEN** the client SHALL debounce or chunk the text into readable segments before synthesis
- **AND** the client SHALL avoid overlapping playback.

#### Scenario: Turn completion arrives while prior speech is queued
- **WHEN** a turn completion event arrives while older visible message segments are still queued for playback
- **THEN** the client SHALL clear pending queued speech
- **AND** it SHALL speak the configured turn-completion phrase next
- **AND** it MAY allow the currently playing audio segment to finish.

#### Scenario: Verbose content is encountered
- **WHEN** visible content includes code blocks, long logs, or long command output
- **THEN** the default voice-output behavior SHALL skip, summarize, or truncate that content rather than reading it in full.

#### Scenario: Markdown code blocks are encountered
- **WHEN** visible content includes fenced code blocks such as `bash`, `python`, or `json`
- **THEN** the default voice-output behavior SHALL announce that a code block exists and include the language when available
- **AND** it SHALL NOT read the block contents aloud by default
- **AND** it SHALL avoid silently dropping the entire block.

#### Scenario: URLs are encountered
- **WHEN** visible content includes raw URLs or Markdown links
- **THEN** the default voice-output behavior SHALL avoid reading the full URL aloud
- **AND** it SHALL summarize the URL using only a short final path segment or fallback host label.

#### Scenario: Newline-delimited progress is streamed
- **WHEN** visible content arrives as headings, list items, or status lines separated by newlines without sentence-ending punctuation
- **THEN** the client SHALL treat completed lines as readable boundaries
- **AND** it SHALL NOT wait until turn completion to speak them.

### Requirement: Ephemeral Generated Audio
Generated speech audio SHALL be ephemeral by default.

#### Scenario: Message is spoken
- **WHEN** the system synthesizes speech for a visible assistant message
- **THEN** the generated audio SHALL NOT be retained as a durable file by default
- **AND** any temporary playback files SHALL be removed after playback or process exit.

### Requirement: Linux Operational Documentation
The system SHALL document how Linux users install, start, stop, verify, and troubleshoot the Piper TTS runtime and voice-output bridge.

#### Scenario: User wants speech disabled
- **WHEN** the user wants to stop assistant speech
- **THEN** the documentation SHALL explain that stopping the Piper TTS container disables voice output while leaving text workflows unchanged.

#### Scenario: User wants a different voice
- **WHEN** the user wants to change the Piper voice
- **THEN** the documentation SHALL explain where the voice is configured and how to verify the selected voice with a smoke-test phrase.
