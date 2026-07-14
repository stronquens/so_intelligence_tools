## 1. Implementation

- [x] 1.1 Change Linux and Windows push-to-talk dictation defaults to `Ctrl + Shift + Space`.
- [x] 1.2 Add explicit Shift parsing and key normalization to the press-and-hold listener.
- [x] 1.3 Update shortcut map, desktop UI defaults, and legacy desktop settings migration.

## 2. Documentation

- [x] 2.1 Update `.env.example`, README, AGENTS, and relevant docs to show the new dictation shortcut.
- [x] 2.2 Update active OpenSpec specs and active change notes that currently describe `Ctrl + Space` as the dictation default.

## 3. Validation

- [x] 3.1 Run focused Python tests for shortcut parsing, shortcut map, dictation listener selection, and service install behavior.
- [x] 3.2 Run focused desktop tests for settings defaults and migration.
- [x] 3.3 Record validation results and residual risk in this change.
