# Validation

## Commands

```powershell
cd C:\Dev\Active\so_intelligence_tools\desktop
npm run test
npm run build

cd C:\Dev\Active\so_intelligence_tools
openspec validate connect-overlay-translator-view --strict
openspec validate --all --strict
git diff --check
```

## Results

- `npm run test`: passed, 1 test file, 10 tests.
- `npm run build`: passed, Vite build and Electron TypeScript build completed.
- `openspec validate connect-overlay-translator-view --strict`: passed.
- `openspec validate --all --strict`: passed.
- `git diff --check`: passed; only Windows CRLF conversion warnings were reported.

## Behavior Covered

- Clicking the overlay `Traducir audio` card sends `open-translator` through the desktop bridge.
- Electron opens or focuses `TranslatorView` in a separate `BrowserWindow` with `?view=translator`.
- The launcher stays visible instead of being replaced by the translator view.

## Known Boundary

This change connects the new desktop translator UI. It does not yet start live Windows audio capture or the translation runtime.
