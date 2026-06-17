## Single Instance

Use Electron `app.requestSingleInstanceLock()`. If a new process starts while one instance already owns the lock, the new process exits and the existing process receives `second-instance`.

## Toggle Behavior

The existing process handles `second-instance` as the user pressing the Windows shortcut again:

- visible and not minimized -> `minimize()`
- minimized -> `restore()`, center, show, focus
- hidden -> center, show, focus

This matches the current Windows shortcut approach based on a `.lnk` hotkey while preventing runaway Electron instances.

## Boundary

This is not the final internal hotkey system. A future change can register configurable shortcuts directly with Electron `globalShortcut`, but this change fixes the immediate Windows `.lnk` behavior.
