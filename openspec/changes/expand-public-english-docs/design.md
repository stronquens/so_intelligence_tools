## Context

The project has several implemented and in-progress capabilities but only two Spanish docs in `docs/`. The README already presents the project internationally, so the documentation should be English-first and structured for GitHub readers.

## Goals / Non-Goals

**Goals:**

- Make `docs/` navigable from a single index.
- Keep each guide focused and practical.
- Clearly mark experimental and planned features.
- Document the known push-to-talk dictation limitations instead of overstating stability.
- Document security expectations for `.env` and API keys.

**Non-Goals:**

- Do not write exhaustive API reference beyond the currently exposed endpoints.
- Do not promise macOS or Windows support before adapters exist.
- Do not change product behavior or service defaults.

## Decisions

- Use English for all public docs.
- Prefer one guide per major capability so users can jump directly to their workflow.
- Keep old Spanish filenames as English compatibility pointers to avoid breaking existing links.
- Link the README to `docs/README.md` and the most important setup/troubleshooting docs.

## Risks / Trade-offs

- Some docs describe experimental behavior that may change. Mitigation: label experimental items explicitly.
- The docs may need follow-up updates when dictation and the desktop UI stabilize.
