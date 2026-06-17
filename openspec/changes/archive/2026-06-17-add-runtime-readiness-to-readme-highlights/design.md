## Context

The README already has a Highlights table with capability, description, and status. The requested addition is a documentation-only improvement for public GitHub readers.

## Goals / Non-Goals

**Goals:**

- Add a compact column that distinguishes local/on-prem readiness from API-backed readiness.
- Preserve the existing status semantics.
- Avoid overloading the table with long explanations.

**Non-Goals:**

- Do not change implementation status.
- Do not document every backend detail inside the Highlights table.
- Do not modify application behavior.

## Decisions

- Name the new column `Runtime` to keep the table narrow.
- Use stable labels:
  - `Local/on-prem`
  - `API`
  - `Both`
  - `Planned`
- Use short clarifiers only where a capability is not fully implemented yet.

## Risks / Trade-offs

- A compact table cannot explain every backend nuance. Detailed backend setup remains in docs and configuration sections.
