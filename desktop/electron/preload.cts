import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("translatorBridge", {
  sendCommand: (command: unknown) => ipcRenderer.invoke("ui-command", command),
  ready: () => ipcRenderer.invoke("translator-ready"),
  onEvent: (listener: (event: unknown) => void) => {
    const handler = (_event: Electron.IpcRendererEvent, payload: unknown) => listener(payload);
    ipcRenderer.on("ui-event", handler);
    return () => ipcRenderer.removeListener("ui-event", handler);
  },
  windowAction: (action: unknown) => ipcRenderer.invoke("translator-window-action", action),
});

contextBridge.exposeInMainWorld("desktopBridge", {
  sendCommand: (command: unknown) => ipcRenderer.invoke("desktop-command", command),
});
