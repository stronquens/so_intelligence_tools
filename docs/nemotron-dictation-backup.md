# Linux Nemotron Streaming Dictation

Status: Retired prototype / Linux realtime streaming backup.

The current recommended push-to-talk dictation path is [Linux Whisper Dictation](linux-whisper-dictation.md). This page keeps the previous Linux Nemotron ONNX CPU prototype documented so it can be inspected, restored, or reintroduced later when realtime streaming dictation is worth revisiting.

## Reference Commit

Known-good reference commit:

```text
e448d56 Improve public docs and Codex workspace guidance
```

That commit still contained:

```text
docs/push-to-talk-dictation.md
openspec/changes/add-nemotron-streaming-dictation/
openspec/specs/push-to-talk-dictation/spec.md
src/so_intelligence_tools/push_to_talk_dictation/onnx_cpu.py
```

Commit `0d7d422 Implement desktop overlay and Whisper dictation` moved the project toward faster-whisper HTTP and removed the live Nemotron runtime code/change from the current tree.

## What Nemotron Did

The prototype recorded while the shortcut was held, streamed audio into a local ONNX CPU ASR runtime, and inserted Spanish text into the focused field while the session was active.

Linux shortcut:

```text
Ctrl + Alt + Space
```

Runtime configuration used by the prototype:

```env
PUSH_TO_TALK_DICTATION_RUNTIME=onnx_cpu
PUSH_TO_TALK_DICTATION_MODEL_REPO=onnx-community/nemotron-3.5-asr-streaming-0.6b-onnx-int4
PUSH_TO_TALK_DICTATION_LANGUAGE=es-ES
PUSH_TO_TALK_DICTATION_SAMPLE_RATE_HZ=16000
PUSH_TO_TALK_DICTATION_CHUNK_MS=560
PUSH_TO_TALK_DICTATION_INSERTION_STRATEGY=final_segments
```

## When To Choose Nemotron

Choose this path only if you specifically want to continue the realtime streaming experiment:

- You want partial/final text behavior while speaking.
- You want a fully local CPU ASR prototype without the faster-whisper Docker server.
- You are comfortable working on insertion stabilization.

Do not choose it as the daily backend right now if reliability matters more than realtime behavior.

## Known Issues From Testing

The prototype was useful, but not stable enough to keep as the recommended path:

- The first words could be lost while the model/session warmed up.
- Text could appear out of order during insertion.
- Already inserted text could sometimes be replaced or partially deleted.
- The listener was oriented toward Linux/X11.
- Latency and insertion stability still needed more work.

Those limitations are why faster-whisper HTTP is currently preferred.

## Switching From Whisper Back To Nemotron

Nemotron is not selectable in the current runtime tree. To switch back, restore it in a branch and reintroduce it deliberately.

Recommended branch:

```bash
git switch -c restore-nemotron-dictation
```

Restore the old runtime files:

```bash
git restore --source e448d56 -- \
  src/so_intelligence_tools/push_to_talk_dictation/onnx_cpu.py \
  openspec/changes/add-nemotron-streaming-dictation
```

Then update the current dictation app so both runtimes can coexist:

```env
PUSH_TO_TALK_DICTATION_RUNTIME=onnx_cpu
```

Do not overwrite the current `docs/push-to-talk-dictation.md` with the old file unless the goal is to fully revert the documentation. The better long-term shape is one selector with two backend guides:

- `faster_whisper_http`: stable final-text route
- `onnx_cpu`: experimental realtime streaming route

## Inspect The Old Implementation

View the old dictation docs:

```bash
git show e448d56:docs/push-to-talk-dictation.md
```

View the old runtime implementation:

```bash
git show e448d56:src/so_intelligence_tools/push_to_talk_dictation/onnx_cpu.py
```

List the old OpenSpec change:

```bash
git ls-tree -r --name-only e448d56 openspec/changes/add-nemotron-streaming-dictation
```

Read the old validation notes:

```bash
git show e448d56:openspec/changes/add-nemotron-streaming-dictation/validation.md
```

## Restore The Old Docs Exactly

If you need the exact old dictation page for comparison:

```bash
git show e448d56:docs/push-to-talk-dictation.md
```

If you intentionally want to restore the old page into a branch:

```bash
git restore --source e448d56 -- \
  docs/push-to-talk-dictation.md
```

The current dictation app expects `faster_whisper_http`, so restoring old docs alone does not restore runtime support.

## Suggested Reintroduction Plan

If we bring Nemotron back later:

1. Add an explicit runtime selector supporting both `faster_whisper_http` and `onnx_cpu`.
2. Keep faster-whisper as the default.
3. Add tests that cover runtime selection and failure messages.
4. Fix or redesign live insertion so partial/final text cannot reorder or delete existing text.
5. Document Linux-only support and expected latency.
