## Summary

Codex task-boundary speech now correlates modern app-server lifecycle events by `threadId` and `turnId`. The reported interleaving sequence no longer ends the active spoken task when another thread or turn completes, and repeated terminal notifications are deduplicated.

## Validation approach

- Reproduced the original failure with two interleaved protocol-valid turns.
- Added regression tests for mismatched completion, duplicate completion with and without an observed start, background progress, active text buffering, playback queue preservation, terminal status, snake_case aliases, and identifier-less fallback.
- Ran focused Codex voice tests and the full repository suite.
- Ran Ruff checks and formatting, Python compilation, and strict OpenSpec validation.
- Restarted only the two active TTS listener children and confirmed both wrappers spawned replacement listeners while retaining their active Codex sessions.

## Requirement mapping

- **Duplicate turn start events:** existing and focused tests confirm one start cue per active turn.
- **Tool call inside active turn:** matching action events remain spoken; identified background actions are ignored.
- **Real turn completion:** a matching terminal key flushes and emits one completion cue.
- **Completion belongs to another turn:** a mismatched terminal key returns no speech and leaves active buffered text intact.
- **Duplicate correlated completion:** repeated terminal keys emit no second cue, including completion-without-start streams.
- **Turn completion without explicit start:** the first identified terminal event remains audible and is then cached for deduplication.
- **Identified background progress:** mismatched item lifecycle events are not spoken or applied to active state.
- **Legacy events lack identifiers:** the prior order-based behavior remains covered by an explicit regression.

## Evidence

- [Validation results](evidence/validation-results.txt)

## Residual risk

Identifier-less legacy streams remain inherently ambiguous and therefore retain the conservative historical heuristic. Correlation state is intentionally process-local and resets when the wrapper listener restarts.
