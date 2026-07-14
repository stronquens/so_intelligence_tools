# Production Log Analysis

The investigation used existing local session logs under `~/.cache/so_intelligence_tools/system_audio_logs/`. Transcript contents are intentionally not copied into this change.

## Observed Counts

| Session | Translation finals | Published blocks | Reconnects |
| --- | ---: | ---: | ---: |
| 2026-06-10 17:03 | 132 | 75 | 7 |
| 2026-06-18 16:55 | 88 | 5 | 1 |
| 2026-07-09 11:32 | 201 | 39 | 3 |

In the July session, a short turn received a translation final but no original transcription. The old ordered publication loop then stopped at that turn for every later event. Later turns continued receiving both final transcripts and final translations but were not published. Publication resumed only after a provider error forced a reconnect and discarded the connection-local turn state.

The two largest observed publication gaps in that session were 609 seconds and 630 seconds. This matches the head-of-line regression now encoded in `test_complete_later_turn_is_not_blocked_by_translation_only_earlier_turn`.

## Reproduction Before The Fix

A controlled live iterator emitted:

1. a translation-only first turn;
2. a fully transcribed and translated second turn;
3. no stream termination.

Before the fix, both `blocks_while_stream_is_live` and `blocks_after_cancellation` were empty. The new regression keeps the stream open and verifies that the second turn is published immediately, then verifies that cancellation finalizes the first turn as translation-only.
