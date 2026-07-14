# Selector, meter and virtual microphone audit — 2026-07-14

## Findings and corrections

1. The language control was bound to the last backend value and did not update
   Vue state before sending the command. The browser therefore displayed the
   choice briefly and immediately rendered the old value again. Selection is
   now optimistic, ignores stale configuration events while pending and rolls
   back only when the command fails.
2. Native option elements could not render the approved flag treatment. The
   new teleported listbox shows a real flag for every one of the 18 backend
   languages, supports keyboard focus and remains outside sidebar clipping.
3. The native model select did not match the mock. Its replacement restores the
   icon/check popover treatment while listing only `OpenAI Realtime API` and
   `Chunked transcription`, the modes Python actually supports.
4. The waveform used fixed heights and a periodic CSS pulse. Production now
   receives throttled normalized PCM RMS events, selects system or physical-mic
   input according to the active feature and decays to silence. Only labelled
   mock mode generates synthetic levels for visual QA.
5. The window buttons no longer paint the enlarged hit target on hover. Their
   17 px mark receives a tight shadow while the surrounding target stays clear.
6. Two stale PulseAudio module pairs had published a suffixed `.2` endpoint.
   With no active audio process, only that duplicate pair was unloaded. The
   adapter now reused the exact existing `so_ai_translated_mic_sink` and
   `so_ai_translated_mic` pair without loading or unloading it.

## Provider-safe functional evidence

- A local passthrough smoke captured 11 physical-microphone level events while
  the pipeline was running and confirmed that translation remained inactive.
- A second local smoke read 4,800 PCM bytes from `so_ai_translated_mic` through
  the route `physical microphone → internal sink → virtual microphone`.
- Neither smoke constructed a realtime translation controller or started the
  paid provider API.
- Existing real logs from 2026-06-12 contain `realtime_connected` followed by
  repeated `output_audio_written` events for `so_ai_translated_mic`, including
  sessions with at least 2,880,000 translated PCM bytes. No new paid session was
  needed for this visual/route correction.

## Visual evidence

- [Final model popover and mock-only moving meter](08-final-model-and-meter-1680x946.png)
- [Window-control hover without hit-area fill](09-final-window-hover.png)
- [Full flag menu positioned above its control at 900 × 600](10-final-language-menu-900x600.png)

All screenshots were captured through `npm run translator:mock`. Process checks
confirmed that `run-system-audio-translation-desktop-bridge` was absent.
