---
name: openspec-validate-change
description: Validate a completed or nearly completed OpenSpec change. Use when implementation is ready for verification, when visual/manual evidence should be captured, or before archiving a change so validation.md, evidence, and research are preserved inside the change.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: codex
  version: "1.0"
---

Validate an OpenSpec change and preserve evidence inside the change folder.

**Input**: Optionally specify a change name. If omitted, infer from context or use the only active change.

## Workflow

1. **Select the change**

   Use the change from context when clear. Otherwise inspect `openspec status --json` or `openspec list --json`.

2. **Read the change context**

   Read:
   - `proposal.md`
   - all delta `spec.md` files
   - `design.md`
   - `tasks.md`

   If `validation.md` already exists, read it too and update it rather than replacing it.

3. **Determine validation scope**

   Build a short checklist directly from the spec:
   - key scenarios to verify
   - required user-visible states
   - any known technical fallback already accepted in design

4. **Run validation**

   Use the most appropriate method for the change:
   - automated tests if they exist
   - manual/browser validation for visual features
   - logs or CLI checks for technical workflows

   For frontend work, prefer browser validation with screenshots and concrete state checks over vague visual claims.

5. **Preserve evidence inside the change**

   Store durable artifacts inside the change directory:
   - final screenshots in `evidence/`
   - useful technical spikes or prototypes in `research/`

   Do not leave validation artifacts scattered in the project root if they are meant to justify the archived change.

6. **Write or update `validation.md`**

   Create `validation.md` in the change root if missing.

   Include:
   - summary of what was validated
   - validation approach
   - mapping from spec requirements/scenarios to observed validation
   - evidence links to files inside `evidence/` or `research/`
   - residual risk or gaps

   Keep `spec.md` as the contract. Do not turn the spec into an evidence dump.

7. **Align `tasks.md` with reality**

   If validation is complete and the remaining task is validation/polish, mark it complete.
   If validation uncovered issues, leave tasks open or add follow-up tasks instead of pretending the change is done.

8. **Prepare for archive**

   Before suggesting archive, confirm:
   - implementation is validated
   - `validation.md` exists
   - evidence needed to understand the final state lives inside the change
   - disposable scratch artifacts are either removed or intentionally ignored

## Guardrails

- Validation claims must be backed by something observable: test output, screenshot, dimensions, logs, or explicit manual checks.
- Prefer stable files inside the change over temporary files in the repo root.
- If the change is not actually validated yet, do not mark tasks done just to unblock archive.
- If the user says the feature is visually correct after review, record that human acceptance in `validation.md`.
