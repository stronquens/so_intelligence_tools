## Context

The repository now has validated Windows dictation and an actively configured Linux CPU path that starts the same faster-whisper HTTP Docker backend. Linux and Windows share the default dictation shortcut, but they differ in service installation, startup integration, Docker profile expectations, validation evidence, and known desktop conflicts.

## Goals / Non-Goals

**Goals:**

- Make Linux docs reflect the current session's changes and evidence.
- Keep Linux and Windows instructions visually and semantically separate.
- Preserve historical benchmark and backup links for future decisions.

**Non-Goals:**

- Change product behavior, service units, Docker compose files, or shortcuts.
- Archive this documentation change in the same step.
- Re-run the Whisper model benchmark.

## Decisions

- Treat `docs/getting-started-linux.md`, `docs/linux-whisper-dictation.md`, `docs/push-to-talk-dictation.md`, `docs/keyboard-shortcuts.md`, `docs/configuration.md`, `docs/whisper-docker.md`, and README as the primary reader path.
- Use concise status tables and platform-specific subsections rather than mixing Linux and Windows caveats in the same paragraph.
- Preserve Windows as "validated" where existing docs say it is validated, and describe Linux as "configured/bootstrapped with local evidence" rather than implying identical Windows validation.

## Risks / Trade-offs

- Documentation can drift from code again if shortcut defaults change later. Mitigation: keep shortcut map CLI references in the docs and validate relative links.
- Some Linux end-to-end UX remains user-tested rather than covered by a full automated desktop smoke test. Mitigation: state validation scope precisely.
