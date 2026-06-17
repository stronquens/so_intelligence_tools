import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("translatorBridge", {
  sendCommand: (command: unknown) => ipcRenderer.invoke("ui-command", command),
});

contextBridge.exposeInMainWorld("desktopBridge", {
  sendCommand: (command: unknown) => ipcRenderer.invoke("desktop-command", command),
});
