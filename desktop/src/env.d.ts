/// <reference types="vite/client" />

export {};

declare global {
  interface Window {
    translatorBridge?: {
      sendCommand: (command: unknown) => Promise<unknown>;
    };
  }
}
