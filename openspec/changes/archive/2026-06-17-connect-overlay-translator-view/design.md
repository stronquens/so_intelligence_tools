## Desktop Window Boundary

Use Electron main-process window ownership for the launcher-to-translator action. The launcher sends an `open-translator` desktop command through the preload bridge; Electron opens or focuses a separate frameless translator `BrowserWindow` with `?view=translator`.

This keeps the launcher visible and independently draggable while still avoiding the old Linux translation UI or Python CLI path. The boundary matters because this change is only connecting the new desktop UI surface, not starting live audio capture.

## Runtime Boundary

`Traducir audio` opens the new translator UI in its own desktop window. Live audio capture, provider selection, stream orchestration, and Windows virtual audio routing remain separate capabilities.
