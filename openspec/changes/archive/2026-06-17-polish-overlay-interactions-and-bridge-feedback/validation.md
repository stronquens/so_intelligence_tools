# Validation

## Commands

```powershell
cd C:\Dev\Active\so_intelligence_tools\desktop
npm run test
npm run build

cd C:\Dev\Active\so_intelligence_tools
openspec validate polish-overlay-interactions-and-bridge-feedback --strict
openspec validate --all --strict
git diff --check
```

## Results

- `npm run test`: passed, 1 test file, 15 tests.
- `npm run build`: passed, Vite build and Electron TypeScript build completed.
- `openspec validate polish-overlay-interactions-and-bridge-feedback --strict`: passed.
- `openspec validate --all --strict`: passed, 27 items.
- `git diff --check`: passed; only Windows CRLF conversion warnings were reported.
- Manual Windows desktop validation: passed. The user confirmed the launcher and settings are now two independently draggable windows.
- Manual Windows desktop validation: passed. The user confirmed the compact launcher/settings window behavior and accepted the translator opening as a separate window. Translator visual polish remains future work.
- Windows shortcut update: `D:\Users\Armando\Desktop\so_intelligence_tools Overlay.lnk` now points `IconLocation` to `C:\Dev\Active\so_intelligence_tools\assets\branding\app-icon.ico,0`.

## Behavior Covered

- Tool cards now have hover lift, glow and active press feedback.
- Icon buttons, shortcut rows, toggles and save button now have visible interaction states.
- Launcher and settings panel have entrance animations.
- Launcher shortcut footer now uses stable alignment and explicit `kbd` padding so `Ctrl + Space` stays centered and readable.
- Launcher shortcut footer now gives the `+`, `Ctrl`, `Space`, and helper text the same vertical box so the widened launcher does not make the bottom text look offset.
- Launcher panel is wider and anchored in a stable left-side position, with wider tool cards and balanced text wrapping so button labels/descriptions stay centered inside each card.
- Tool cards now keep title and subtitle closer together with a compact internal grid, while preserving centered wrapping for two-line labels.
- Glass panels now use a less transparent background so text stays readable over real desktop windows while keeping the translucent glass look.
- Opening settings no longer moves the launcher panel; screenshot/box validation showed the launcher stayed at `x=72, y=144` before and after opening settings, with a positive gap between launcher and settings.
- Removed the full-window translucent `.overlay-desktop` background/backdrop layer so only the visual app panels are painted over the desktop.
- Settings panel now uses a vertical grid and slightly taller frame so `Guardar cambios` remains inside the glass panel even when status text is visible.
- Clicking the launcher settings button while settings is already open now closes the settings panel.
- The launcher close button now dispatches `hide-overlay` through the desktop bridge so the main window can be hidden from the UI.
- Unwired placeholder tools show pending feedback without requiring `desktopBridge`.
- `selected-text-correction` still requires the desktop bridge because it dispatches real OS automation.
- Settings now opens in a separate frameless Electron `BrowserWindow` to the right of the launcher, instead of replacing the launcher route inside the same window.
- The main launcher remains open when settings opens, and each window has its own drag region so moving one does not move the other.
- Launcher and settings native window bounds now match their visible panels, avoiding invisible transparent margins that intercept clicks on neighboring windows.
- Settings now opens with a larger right gap and vertical centering relative to the launcher.
- The `Traducir audio` card now opens or focuses the translator in a separate Electron window instead of replacing the launcher view.
- The launcher shortcut footer now gives the wide key treatment only to `Space`, so `Ctrl + Alt + A` keeps compact keycaps.
- The settings drag region now covers the settings header and the `Atajos de teclado` heading area, while the close/back buttons, shortcut controls, toggles and the save button remain explicit non-draggable controls.
- The settings window now has an extra invisible top drag zone between the close/back controls, giving more room to move the window without stealing clicks from those controls.
- The Electron preload now compiles to CommonJS (`preload.cjs`) so `desktopBridge` is exposed reliably in the desktop app.
- If `desktopBridge` is missing, the launcher keeps the main overlay visible and reports the bridge issue instead of navigating to the settings view.
- App branding now includes generated `app-icon` PNG/ICO assets based on the overlay sparkle mark.
- Electron windows now set `icon` to the generated app icon, and the Vite HTML entry uses the same icon as favicon.
- Public docs and live specs were updated for the independent settings/translator window behavior and current Windows desktop icon/shortcut state.
