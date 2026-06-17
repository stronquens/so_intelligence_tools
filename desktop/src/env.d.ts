/// <reference types="vite/client" />

export {};

declare global {
  interface Window {
    translatorBridge?: {
      sendCommand: (command: unknown) => Promise<unknown>;
    };
    desktopBridge?: {
      sendCommand: (command: import("./types").DesktopCommand) => Promise<import("./types").DesktopCommandResult>;
    };
  }
}
