# Validation

Validated on Windows from `C:\Dev\Active\so_intelligence_tools` on 2026-06-17.

## Commands

- `rg -n "selected text correction with|focused on selected text|mock commands|local ONNX CPU ASR runtime|proper tools overlay|configurable shortcut management|Windows support is starting" README.md AGENTS.md docs -S`: passed; no stale high-level phrasing remained.
- `rg -n "Ctrl \+ Alt \+ A|Ctrl \+ Alt \+ D|faster-whisper HTTP|show-shortcuts|main overlay|overlay launcher" README.md AGENTS.md docs -S`: passed; updated references are present.
- `poetry run so-intelligence-tools show-shortcuts --platform windows`: passed; output lists `Open overlay` as `Ctrl + Alt + A`, selected text correction and push-to-talk dictation.
- `openspec validate sync-session-documentation --strict`: passed.
- `openspec validate --all --strict`: passed, 28 items.

## Result

README, AGENTS and relevant `docs/` pages now describe the current Windows state: `Ctrl + Alt + A` opens/toggles the overlay, `Ctrl + Alt + C` corrects selected text, `Ctrl + Alt + D` runs push-to-talk dictation, and faster-whisper HTTP in Docker is the validated preferred Windows ASR backend.
