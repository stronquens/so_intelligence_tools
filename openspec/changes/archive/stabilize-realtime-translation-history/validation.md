# Validation

## Summary

The realtime history lifecycle is validated against the production failure pattern, the full Python suite, and a subsequent user-run live conversation. A complete later turn now publishes while an earlier translation-only turn remains pending, and receiver cancellation deterministically finalizes residual content before connection state is discarded. The live session persisted all 13 translated turns.

## Validation Approach

- Added deterministic async event-stream regressions around the existing controller callback contract.
- Exercised normal stream completion and task cancellation separately.
- Verified identity-based deduplication and bounded-queue observability.
- Ran the focused realtime tests and full Python suite.
- Ran scoped Ruff lint/format, strict OpenSpec validation, and patch whitespace validation.
- Preserved the anonymized production-log findings in `research/production-log-analysis.md`.
- Reviewed the latest user-run live session using aggregate metrics without
  reproducing private conversation text.

## Requirement Mapping

### Independent realtime turn publication

- **Earlier turn has no original transcript:** `test_complete_later_turn_is_not_blocked_by_translation_only_earlier_turn` keeps the receiver open and observes the later complete block before cancelling it.
- **Original and translation complete in either order:** existing tests cover transcription-first, translation-first, final-original, and partial-original sequences; all pass after the tracker change.
- **Identical translation text:** `test_distinct_turns_with_identical_translation_are_both_published` observes two distinct `Sí.` history blocks.

### Realtime residual turn finalization

- **Complete pending content:** `test_receiver_cancellation_flushes_complete_partial_turn` observes a block built from pending original and translated partial text.
- **Translation only:** `test_stream_end_publishes_translation_only_residual_and_logs_fallback` observes `original_text=None` plus a `translation_only=true` log event.
- **Original only:** `test_stream_end_logs_original_only_residual_without_publishing_block` observes an incomplete-turn log and no history block.
- **Completed-transcript compatibility:** `test_completed_transcript_mode_translates_short_residual_on_normal_stream_end` protects the pre-existing normal-end behavior.

### Realtime audio queue observability

- `test_realtime_audio_queue_logs_cumulative_overflow` verifies the configured one-chunk bound, newest-chunk retention, and cumulative drop events.

## Evidence

- [Automated test results](evidence/test-results.txt)
- [Static and OpenSpec validation](evidence/static-validation.txt)
- [Anonymized production log analysis](research/production-log-analysis.md)
- [Latest live-session readability report](research/latest-session-readability-report/report.html)

## Live Session Follow-up

The user confirmed that the history fix worked in normal use. The latest session
contained 13 `translation_final` events and 13 `block_published` events. The
follow-up also identified a separate readability concern: five published blocks
contained five translated words or fewer, with the final short turns arriving
roughly 1.4–2.1 seconds apart. That concern is attributed primarily to exposing
provider VAD turns directly in the UI and is not treated as a history-loss
regression.

## Residual Risk

- No paid live OpenAI Realtime session was started during automated validation; provider integration remains covered through recorded event shapes and deterministic fakes.
- The provider can still emit `active response in progress` under aggressive VAD turn overlap. This change prevents that reconnect from silently discarding accumulated turn content but does not retune VAD or serialize provider responses.
- Finalized callbacks that occur while Tkinter is already closing remain in its UI queue even though controller history and the session log are correct. UI shutdown draining belongs to a separate window-lifecycle change.
- The bounded queue still discards old audio under sustained backpressure; it is now observable rather than silent.
- Repository-wide Ruff currently reports unrelated pre-existing lint and formatting debt. Scoped checks for both modified Python files pass.

## Result

Validated. The change is ready for spec synchronization and archive when requested.
