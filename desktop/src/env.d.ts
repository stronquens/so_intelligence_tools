/// <reference types="vite/client" />

export {};

declare global {
  interface Window {
    translatorBridge?: {
      sendCommand: (command: import("./types").UiCommand) => Promise<import("./types").UiCommandResult>;
      ready: () => Promise<import("./types").TranslatorReadyResult>;
      onEvent: (listener: (event: import("./types").UiEvent) => void) => () => void;
      windowAction: (action: import("./types").TranslatorWindowAction) => Promise<{ accepted: boolean }>;
    };
    desktopBridge?: {
      sendCommand: (command: import("./types").DesktopCommand) => Promise<import("./types").DesktopCommandResult>;
    };
  }
}
