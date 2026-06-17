# Validation

## Commands

```powershell
cd C:\Dev\Active\so_intelligence_tools\desktop
npm run build
npm run test

cd C:\Dev\Active\so_intelligence_tools
openspec validate make-overlay-hotkey-toggle-single-instance --strict
openspec validate --all --strict
git diff --check
```

## Results

- `npm run build`: passed, Vite build and Electron TypeScript build completed.
- `npm run test`: passed, 1 test file, 10 tests.
- `openspec validate make-overlay-hotkey-toggle-single-instance --strict`: passed.
- `openspec validate --all --strict`: passed.
- `git diff --check`: passed; only Windows CRLF conversion warnings were reported.

## Behavior Covered

- Electron now uses `app.requestSingleInstanceLock()`.
- A second launch exits immediately and sends `second-instance` to the running process.
- If the overlay is visible, second launch minimizes it to the Windows taskbar.
- If the overlay is minimized/hidden, second launch restores, centers, shows and focuses it.
