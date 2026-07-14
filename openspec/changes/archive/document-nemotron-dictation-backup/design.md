## Context

Commit `e448d56` documented the Nemotron ONNX CPU dictation prototype as the current Linux runtime. Commit `0d7d422` migrated documentation and code toward faster-whisper HTTP, deleted `src/so_intelligence_tools/push_to_talk_dictation/onnx_cpu.py`, and removed the active `openspec/changes/add-nemotron-streaming-dictation/` change from the live tree.

## Goals / Non-Goals

**Goals:**

- Preserve the old Nemotron runtime details in a stable English doc.
- Record the exact commit and paths needed for inspection or rollback.
- Keep the current Whisper docs clearly marked as the supported path.

**Non-Goals:**

- Do not restore Nemotron code now.
- Do not make Nemotron selectable again in runtime configuration.
- Do not change current Windows or Linux dictation behavior.

## Decisions

- Add a dedicated `docs/nemotron-dictation-backup.md` guide instead of mixing legacy rollback steps into the main dictation guide.
- Link the guide from `docs/push-to-talk-dictation.md` and `docs/README.md`.
- Treat `e448d56` as the known-good documentation/code reference for the old prototype.

## Risks / Trade-offs

- The backup guide references Git history. If history is rewritten, those commands would need updating.
- The old prototype had known insertion and latency issues; the guide must state those limitations clearly so readers do not mistake it for the recommended path.
