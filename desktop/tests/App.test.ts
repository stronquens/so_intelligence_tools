import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../src/App.vue";
import type { DesktopSettings } from "../src/types";

function createSettings(): DesktopSettings {
  return {
    shortcuts: [
      { id: "open-overlay", label: "Abrir overlay", value: "Ctrl + Alt + A" },
      { id: "selected-text-correction", label: "Corregir texto", value: "Ctrl + Alt + C" },
      { id: "screenshot-ocr", label: "OCR pantalla", value: "Ctrl + Alt + O" },
      { id: "system-audio-translation", label: "Traducir audio", value: "Ctrl + Alt + T" },
      { id: "voice-translation-microphone", label: "Microfono traducido", value: "Ctrl + Alt + M" },
      { id: "push-to-talk-dictation", label: "Dictado", value: "Ctrl + Shift + Space" },
      { id: "assistant", label: "Asistente", value: "Sin asignar" },
      { id: "summary", label: "Resumen", value: "Ctrl + Alt + R" },
      { id: "intelligent-capture", label: "Captura inteligente", value: "Ctrl + Alt + I" },
    ],
    startAtLogin: true,
    overlayAlwaysVisible: false,
  };
}

afterEach(() => {
  window.history.pushState({}, "", "/");
  delete window.desktopBridge;
  delete window.translatorBridge;
});

describe("Overlay launcher UI", () => {
  it("renders only the overlay launcher by default", () => {
    const wrapper = mount(App);

    expect(wrapper.find('[data-testid="overlay-launcher"]').exists()).toBe(true);
    expect(wrapper.text()).toContain("so_intelligence_tools");
    expect(wrapper.text()).toContain("Corregir texto");
    expect(wrapper.text()).toContain("OCR pantalla");
    expect(wrapper.text()).toContain("Microfono traducido");
    expect(wrapper.findAll(".tool-card")).toHaveLength(8);
    expect(wrapper.find(".settings-panel").exists()).toBe(false);
    expect(wrapper.find(".overlay-topbar").exists()).toBe(false);
    expect(wrapper.find(".document-window").exists()).toBe(false);
    expect(wrapper.find(".desktop-dock").exists()).toBe(false);
  });

  it("opens the independent settings window from the launcher settings button", async () => {
    const sendCommand = vi.fn().mockResolvedValue({
      status: "success",
      message: "Ajustes alternados.",
    });
    window.desktopBridge = { sendCommand };
    const wrapper = mount(App);

    await wrapper.find(".panel-icon-button").trigger("click");
    await flushPromises();

    expect(wrapper.find(".settings-panel").exists()).toBe(false);
    expect(sendCommand).toHaveBeenCalledWith({ type: "toggle-settings" });
  });

  it("dispatches settings toggle each time the launcher settings button is clicked", async () => {
    const sendCommand = vi.fn().mockResolvedValue({
      status: "success",
      message: "Ajustes alternados.",
    });
    window.desktopBridge = { sendCommand };
    const wrapper = mount(App);

    await wrapper.find(".panel-icon-button").trigger("click");
    await wrapper.find(".panel-icon-button").trigger("click");

    expect(sendCommand.mock.calls.filter(([command]) => command.type === "toggle-settings")).toHaveLength(2);
  });

  it("keeps the launcher visible instead of replacing it with settings when the desktop bridge is missing", async () => {
    const wrapper = mount(App);

    await wrapper.find(".panel-icon-button").trigger("click");
    await flushPromises();

    expect(window.location.search).toBe("");
    expect(wrapper.find('[data-testid="overlay-launcher"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="settings-window"]').exists()).toBe(false);
    expect(wrapper.text()).toContain("El bridge de escritorio no esta disponible.");
  });

  it("hides the overlay from the launcher close button", async () => {
    const sendCommand = vi.fn().mockResolvedValue({
      status: "success",
      message: "Overlay oculto.",
    });
    window.desktopBridge = { sendCommand };
    const wrapper = mount(App);

    await wrapper.find(".panel-close-button").trigger("click");

    expect(sendCommand).toHaveBeenCalledWith({ type: "hide-overlay" });
  });

  it("renders the independent settings window when requested", async () => {
    window.history.pushState({}, "", "/?view=settings");
    const settings = createSettings();
    const sendCommand = vi.fn().mockResolvedValue({
      status: "success",
      message: "Ajustes cargados.",
      settings,
    });
    window.desktopBridge = { sendCommand };
    const wrapper = mount(App);

    await flushPromises();

    expect(wrapper.find('[data-testid="settings-window"]').exists()).toBe(true);
    expect(wrapper.text()).toContain("Atajos de teclado");
    expect(wrapper.findAll(".shortcut-row")).toHaveLength(9);
    expect(sendCommand).toHaveBeenCalledWith({ type: "get-settings" });
  });

  it("closes the independent settings window from the close control", async () => {
    window.history.pushState({}, "", "/?view=settings");
    const sendCommand = vi.fn().mockResolvedValue({
      status: "success",
      message: "Ajustes cargados.",
      settings: createSettings(),
    });
    window.desktopBridge = { sendCommand };
    const wrapper = mount(App);

    await flushPromises();
    await wrapper.find(".settings-close").trigger("click");

    expect(sendCommand).toHaveBeenLastCalledWith({ type: "close-settings" });
  });

  it("edits and saves shortcut settings through the desktop bridge", async () => {
    window.history.pushState({}, "", "/?view=settings");
    const settings = createSettings();
    const sendCommand = vi.fn((command) => {
      if (command.type === "get-settings") {
        return Promise.resolve({
          status: "success",
          message: "Ajustes cargados.",
          settings,
        });
      }

      return Promise.resolve({
        status: "success",
        message: "Ajustes guardados.",
        settings: command.settings,
      });
    });
    window.desktopBridge = { sendCommand };
    const wrapper = mount(App);

    await flushPromises();
    await wrapper.findAll(".shortcut-row button")[1].trigger("click");
    await wrapper.find(".shortcut-input").trigger("keydown", {
      key: "K",
      ctrlKey: true,
      altKey: true,
    });
    await wrapper.find(".save-settings").trigger("click");
    await flushPromises();

    expect(sendCommand).toHaveBeenLastCalledWith(
      expect.objectContaining({
        type: "save-settings",
        settings: expect.objectContaining({
          shortcuts: expect.arrayContaining([
            expect.objectContaining({
              id: "selected-text-correction",
              value: "Ctrl + Alt + K",
            }),
          ]),
        }),
      }),
    );
    expect(wrapper.text()).toContain("Ajustes guardados.");
  });

  it("blocks duplicate shortcut assignments before saving", async () => {
    window.history.pushState({}, "", "/?view=settings");
    const sendCommand = vi.fn().mockResolvedValue({
      status: "success",
      message: "Ajustes cargados.",
      settings: createSettings(),
    });
    window.desktopBridge = { sendCommand };
    const wrapper = mount(App);

    await flushPromises();
    await wrapper.findAll(".shortcut-row button")[1].trigger("click");
    await wrapper.find(".shortcut-input").setValue("Ctrl + Alt + A");
    await wrapper.find(".save-settings").trigger("click");

    expect(sendCommand).toHaveBeenCalledTimes(1);
    expect(wrapper.text()).toContain("Conflicto:");
  });

  it("dispatches selected text correction from the first tool card", async () => {
    const sendCommand = vi.fn().mockResolvedValue({
      status: "success",
      toolId: "selected-text-correction",
      message: "Texto corregido.",
    });
    window.desktopBridge = { sendCommand };
    const wrapper = mount(App);

    await wrapper.findAll(".tool-card")[0].trigger("click");
    await flushPromises();

    expect(sendCommand).toHaveBeenCalledWith({
      type: "run-tool",
      toolId: "selected-text-correction",
    });
    expect(wrapper.text()).toContain("Texto corregido.");
  });

  it("opens the translator as an independent desktop window from the audio translation card", async () => {
    const sendCommand = vi.fn().mockResolvedValue({
      status: "success",
      toolId: "system-audio-translation",
      message: "Traductor abierto.",
    });
    window.desktopBridge = { sendCommand };
    const wrapper = mount(App);

    await wrapper.findAll(".tool-card")[2].trigger("click");
    await flushPromises();

    expect(window.location.search).toBe("");
    expect(wrapper.find('[data-testid="overlay-launcher"]').exists()).toBe(true);
    expect(wrapper.text()).not.toContain("Real-Time Translator");
    expect(sendCommand).toHaveBeenCalledWith({ type: "open-translator" });
    expect(wrapper.text()).toContain("Traductor abierto.");
  });

  it("shows pending feedback for tools that are not wired yet", async () => {
    window.desktopBridge = {
      sendCommand: vi.fn().mockResolvedValue({
        status: "pending",
        toolId: "screenshot-ocr",
        message: "Esta herramienta todavia no esta conectada.",
      }),
    };
    const wrapper = mount(App);

    await wrapper.findAll(".tool-card")[1].trigger("click");
    await flushPromises();

    expect(wrapper.text()).toContain("Esta herramienta todavia no esta conectada.");
  });

  it("shows pending feedback for unwired tools without requiring the desktop bridge", async () => {
    const wrapper = mount(App);

    await wrapper.findAll(".tool-card")[1].trigger("click");
    await flushPromises();

    expect(wrapper.text()).toContain("Esta herramienta todavia no esta conectada.");
    expect(wrapper.text()).not.toContain("bridge de escritorio");
  });
});

describe("Real-Time Translator UI", () => {
  it("renders grouped English and Spanish transcript pairs when requested", () => {
    window.history.pushState({}, "", "/?view=translator");
    const wrapper = mount(App);

    expect(wrapper.text()).toContain("Real-Time Translator");
    expect(wrapper.text()).toContain("Good morning everyone");
    expect(wrapper.text()).toContain("Buenos dias a todos");
    expect(wrapper.findAll(".timeline-pair").length).toBeGreaterThanOrEqual(4);
  });

  it("sends pause commands through the desktop bridge", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const sendCommand = vi.fn().mockResolvedValue({ accepted: true });
    window.translatorBridge = { sendCommand };
    const wrapper = mount(App);

    await wrapper.find(".control-button.primary").trigger("click");

    expect(sendCommand).toHaveBeenCalledWith({ type: "pause" });
  });
});
