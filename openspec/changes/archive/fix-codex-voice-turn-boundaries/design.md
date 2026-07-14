## Context

The VS Code Codex voice bridge receives app-server JSONL events and converts only visible lifecycle summaries and assistant text into Piper speech. The current implementation treats `turn/completed` as the definitive end-of-task cue, but the extension can emit different completion-like item events while a turn is still active. The bridge also has no state guard around equivalent start events, so repeated turn-start notifications can be spoken back-to-back.

## Goals / Non-Goals

**Goals:**

- Speak "Empiezo a trabajar" once per active turn.
- Speak "Fin de tarea" only for true terminal turn events.
- Continue announcing tool/function/command lifecycle in `actions` mode without ending the task.
- Cover the VS Code app-server event shape with regression tests.

**Non-Goals:**

- Do not change Piper model selection, voices, Docker startup, or playback.
- Do not introduce new extension hooks or VS Code settings.
- Do not read tool payloads, arguments, command output, or hidden model internals.

## Decisions

- Add turn state to `CodexVisibleEventExtractor`. This keeps lifecycle interpretation inside the existing event parser rather than spreading deduplication into the playback queue.
- Treat only `turn/completed` and `turn/failed` methods, or their dotted JSONL equivalents, as terminal task boundaries. Intermediate `item/completed` events remain item lifecycle events.
- Suppress repeated start cues while a turn is already active. If no explicit start event was observed, a terminal turn event may still speak the end cue so CLI streams that omit start continue to work.
- Keep queued-speech clearing on true turn completion only. This preserves the earlier fix that makes "Fin de tarea" timely without discarding speech during tool calls.

## Risks / Trade-offs

- Some Codex streams may omit `turn/started`. The extractor must still announce completion when a real terminal event arrives.
- If the extension emits nested or aliased terminal events in a new shape, the bridge may need another parser update. Regression tests should use explicit samples whenever we capture new event shapes.
