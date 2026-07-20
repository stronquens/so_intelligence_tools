## Context

The app-server wrapper forwards every stdout JSONL notification to one `CodexVisibleEventExtractor`. The extractor currently stores only global booleans (`_turn_active`, `_turn_start_spoken`, and `_saw_agent_message_in_turn`). Modern app-server notifications provide `params.threadId` plus either `params.turn.id` for turn boundaries or `params.turnId` for item and message events. Ignoring these identifiers allows a completion from a stale or background turn to terminate the currently spoken turn.

## Goals / Non-Goals

**Goals:**

- Correlate lifecycle speech to the same app-server thread and turn.
- Ignore unrelated terminal notifications before flushing text or clearing playback.
- Speak each correlated terminal boundary at most once.
- Preserve useful behavior for old identifier-less fixtures and legacy Codex event aliases.

**Non-Goals:**

- Select which VS Code thread is visually foregrounded through extension-private state.
- Change speech detail modes, voice selection, or TTS backends.
- Persist turn correlation across wrapper process restarts.

## Decisions

- Represent the active lifecycle with a small immutable `(thread_id, turn_id)` key extracted from protocol fields. A correlated completion is accepted only when its key matches the active key.
- Check correlation before flushing buffered text. A completion for another turn must have no effect on the active turn or its queue.
- Track a bounded recent set of terminal keys so repeated completion notifications do not speak twice. A small bounded collection avoids unbounded memory growth in long-lived extension processes.
- Filter identified message and item lifecycle events when they do not match the active correlated turn. This prevents background activity from satisfying completion heuristics or being spoken as current progress.
- Use the `params.turn.status` value to distinguish completed from failed/interrupted terminal results when available.
- Keep the existing order-based heuristic only when an event lacks a usable key. This is required for legacy aliases and tests, but modern identified events no longer depend on `_saw_agent_message_in_turn` to prove completion.

## Risks / Trade-offs

- [A stream starts mid-turn without a `turn/started` notification] → Accept the first identified terminal event once when no active correlated turn exists, preserving the documented completion-without-start behavior.
- [Two real turns run concurrently through one wrapper] → Continue speaking the first active correlated turn and ignore unrelated lifecycle events until it terminates; this is less confusing than interleaving two audio conversations.
- [Legacy identifier-less events remain ambiguous] → Retain conservative existing behavior and isolate it behind the legacy fallback.
- [Protocol field shapes evolve] → Centralize identifier extraction and cover both modern camelCase fields and legacy snake_case aliases.
