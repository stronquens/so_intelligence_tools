## Context

The OpenAI Realtime controller correlates input transcription events and translated response events in an ordered dictionary. Publication currently stops at the oldest incomplete entry. Real sessions contain short provider turns that produce translated output without an original transcription, so a single such entry can block every later turn until the connection is replaced. Connection teardown cancels the receiver task and its local turn store before residual turns can be finalized.

The controller must continue accepting event orders in which original and translated content complete independently. The existing Tkinter callback contract and `TranscriptBlock` model should remain stable so this backend fix does not depend on the pending Electron integration.

## Goals / Non-Goals

**Goals:**

- Publish every independently complete realtime turn exactly once.
- Prevent missing original text in one turn from blocking later turns.
- Preserve the best available content when a stream is stopped, cancelled, or reconnected.
- Deduplicate by provider identity and record incomplete finalization and queue overflow.
- Keep callbacks, history entries, and session logs consistent.

**Non-Goals:**

- Connect the Electron translator to Python.
- Redesign the Tkinter translation window.
- Change audio routing or the virtual microphone pipeline.
- Replace OpenAI Realtime or tune translation quality and VAD defaults beyond lifecycle correctness.

## Decisions

### Store connection turn state in a dedicated tracker

Introduce a connection-scoped turn tracker that owns turns, response associations, and published identities. Event parsing continues to update turns by `input_item_id`, but publication scans all unpublished turns rather than returning at the first incomplete entry.

This keeps provider correlation localized while removing head-of-line blocking. Moving the state onto an object also allows deterministic finalization from `finally` when the receiver is cancelled.

Alternative considered: remove an incomplete oldest turn immediately. Rejected because its original transcript may arrive after the translation and should still be paired when possible.

### Publish ready turns independently and finalize residual content with fallback

A normally ready turn requires a translation final and the best original text. Ready turns are published as soon as both exist, regardless of earlier turns.

On receiver exit, cancellation, reconnect, or stop, residual turns with both original and translated content use their best final/partial text. Translation-only turns are published with `original_text=None` rather than discarded. Original-only turns are logged as incomplete but are not presented as translated history.

Alternative considered: add a wall-clock timeout per incomplete turn. Deferred because it would introduce timers and UI update semantics that are not required to stop the confirmed data loss. Terminal connection lifecycle provides a deterministic first boundary.

### Deduplicate by input item identity

`published_input_items` remains the authoritative deduplication key. The global translated-text comparison is removed because identical phrases can be separate valid turns.

### Guarantee finalization with `try/finally`

The receiver loop finalizes its tracker in a `finally` block so task cancellation cannot bypass residual processing. Callback and history publication are synchronous, so finalization completes before cancellation propagates.

Controlled stop still cancels network tasks, but no longer discards the receiver's accumulated text. A future provider-specific buffer commit/drain can be added separately if final server events must be awaited.

### Make audio overflow observable

Before appending to a full bounded audio deque, record an `audio_chunk_dropped` event with a cumulative count. Retaining a bounded queue protects memory; observability makes the loss diagnosable without changing the current backpressure model.

## Risks / Trade-offs

- **Translation-only history blocks can have no original text** → Renderers already support `original_text=None`; log an explicit residual source so the fallback is visible in evidence.
- **Scanning all turns is linear** → Realtime turn counts are small between publications, and published entries are removed; the simplicity is preferable to another scheduling structure.
- **A cancelled connection may publish partial translation text** → This preserves visible user content instead of silently losing it and is limited to terminal connection boundaries.
- **Callbacks during window shutdown may be queued after Tkinter begins closing** → Controller history and session logs remain correct; UI-queue draining is left for a later visual lifecycle change.
- **Bounded audio still drops data under sustained backpressure** → Keep the existing memory bound and add explicit metrics; a backpressure redesign is out of scope.
