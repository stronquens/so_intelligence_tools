## Context

The Electron/Vue overlay is now the main desktop surface, but its buttons are not connected to the application runtime. The repository already has a Python selected-text correction runner and an Electron preload bridge used by the translator mock, so the first functional step should reuse those patterns instead of creating a new service layer.

## Goals / Non-Goals

**Goals:**

- Add a typed IPC command path from the overlay renderer to Electron main.
- Make tool cards dispatch commands and show status feedback.
- Wire `Corregir texto` to the existing Poetry CLI selected-text correction runner.
- Hide the overlay before running selected-text correction so copy/paste automation targets the previously focused app.
- Keep not-yet-implemented tools explicit with pending feedback.

**Non-Goals:**

- Implement OCR, dictation, realtime audio translation, assistant, summary, or capture flows.
- Replace the existing Windows shortcut listener.
- Build persistent settings storage or editable shortcuts.
- Introduce a backend service specifically for Electron commands.

## Decisions

- Reuse Electron IPC through the preload bridge.
  - Rationale: the translator view already uses `ipcRenderer.invoke("ui-command", ...)`, and keeping one bridge reduces surface area.
  - Alternative considered: direct renderer calls to local APIs. Rejected because context isolation is enabled and the repo already has a safer preload pattern.

- Execute selected-text correction by spawning `poetry run so-intelligence-tools run-selected-text-correction --debug` from Electron main.
  - Rationale: the existing Python CLI owns platform adapters, logging, runtime setup, and error handling.
  - Alternative considered: reimplement selected text capture in TypeScript. Rejected because it would duplicate existing Windows/Linux adapter logic.

- Hide the overlay before dispatching OS automation.
  - Rationale: selected-text correction must operate on the user application, not on the overlay window.
  - Alternative considered: keep overlay visible while running. Rejected because clipboard and keyboard automation would target the overlay.

- Return structured command results to the renderer.
  - Rationale: the UI needs to show running/success/failure/pending states without scraping logs.
  - Alternative considered: fire-and-forget commands. Rejected because it leaves users without feedback.

## Risks / Trade-offs

- Focus restoration may vary by Windows application -> hide the overlay first and use a small delay before spawning the runner.
- Long-running correction can make the UI feel idle -> show a running status while the command is in progress.
- Electron cannot guarantee every OS tool is available -> return explicit pending/failed states.
- Spawning Poetry depends on the repo-local `.venv` and PATH -> run from the repository root and use the existing Poetry workflow.
