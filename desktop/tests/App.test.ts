import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../src/App.vue";
import type { DesktopSettings, UiEvent } from "../src/types";

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

function createTranslatorBridge(initialEvents: UiEvent[] = []) {
  let listener: ((event: UiEvent) => void) | undefined;
  return {
    sendCommand: vi.fn().mockResolvedValue({ accepted: true }),
    windowAction: vi.fn().mockResolvedValue({ accepted: true }),
    ready: vi.fn().mockResolvedValue({ accepted: true, events: initialEvents }),
    onEvent: vi.fn((nextListener: (event: UiEvent) => void) => {
      listener = nextListener;
      return () => {
        listener = undefined;
      };
    }),
    emit(event: UiEvent) {
      listener?.(event);
    },
  };
}

afterEach(() => {
  document.querySelectorAll(".language-menu").forEach((menu) => menu.remove());
  document.querySelectorAll(".model-menu").forEach((menu) => menu.remove());
  window.history.pushState({}, "", "/");
  window.localStorage.removeItem("translator-density");
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
    expect(wrapper.text()).toContain("Buenos días a todos");
    expect(wrapper.findAll(".timeline-pair")).toHaveLength(4);
    expect(wrapper.text()).toContain("Preview");
    expect(wrapper.findAll(".language-flag")).toHaveLength(2);
  });

  it("keeps the Electron visual mock disconnected from the paid bridge", async () => {
    window.history.pushState({}, "", "/?view=translator&mock=1");
    const bridge = createTranslatorBridge([
      { type: "session_state", state: "active", message: "Paid session" },
    ]);
    window.translatorBridge = bridge;

    const wrapper = mount(App);
    await flushPromises();

    expect(wrapper.text()).toContain("Preview");
    expect(wrapper.text()).toContain("Good morning everyone");
    expect(wrapper.text()).not.toContain("Paid session");
    expect(bridge.ready).not.toHaveBeenCalled();
  });

  it("sends pause commands through the desktop bridge", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const bridge = createTranslatorBridge([
      { type: "session_state", state: "active", message: "Escuchando" },
    ]);
    window.translatorBridge = bridge;
    const wrapper = mount(App);

    await flushPromises();
    await wrapper.find(".control-button.primary").trigger("click");

    expect(bridge.sendCommand).toHaveBeenCalledWith({ type: "pause" });
  });

  it("renders buffered blocks and live partial updates from Python", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const bridge = createTranslatorBridge([
      { type: "session_state", state: "active", message: "Escuchando y traduciendo" },
      {
        type: "block",
        id: "block-1",
        sourceText: "Can everyone see my screen?",
        translatedText: "¿Podéis ver todos mi pantalla?",
        timestamp: "12:04:08",
      },
    ]);
    window.translatorBridge = bridge;
    const wrapper = mount(App);
    await flushPromises();

    expect(wrapper.text()).toContain("Can everyone see my screen?");
    expect(wrapper.text()).toContain("¿Podéis ver todos mi pantalla?");
    expect(wrapper.text()).not.toContain("Preview");

    bridge.emit({ type: "partial", kind: "original", text: "The next point" });
    bridge.emit({ type: "partial", kind: "translation", text: "El siguiente punto" });
    await flushPromises();

    expect(wrapper.text()).toContain("The next point");
    expect(wrapper.text()).toContain("El siguiente punto");
    expect(wrapper.find(".timeline-pair.streaming").exists()).toBe(true);
  });

  it("keeps completed history visible when the backend reconnects", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const bridge = createTranslatorBridge([
      {
        type: "block",
        id: "block-1",
        sourceText: "Completed original",
        translatedText: "Traducción completada",
        timestamp: "12:05:00",
      },
    ]);
    window.translatorBridge = bridge;
    const wrapper = mount(App);
    await flushPromises();

    bridge.emit({ type: "session_state", state: "reconnecting", message: "Reconectando" });
    await flushPromises();

    expect(wrapper.text()).toContain("Traducción completada");
    expect(wrapper.text()).toContain("Reconnecting");
  });

  it("changes the real backend mode from the model menu", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const bridge = createTranslatorBridge([
      { type: "mode", mode: "translate_es_openai_realtime" },
    ]);
    window.translatorBridge = bridge;
    const wrapper = mount(App);
    await flushPromises();

    const selector = wrapper.find<HTMLButtonElement>('.model-select-trigger[aria-label="Transcription model"]');
    await selector.trigger("click");
    expect(document.querySelectorAll(".model-menu .model-option")).toHaveLength(2);
    document.querySelector<HTMLButtonElement>('.model-menu [data-model="translate_es_chunked"]')?.click();
    await flushPromises();

    expect(bridge.sendCommand).toHaveBeenCalledWith({
      type: "change_mode",
      mode: "translate_es_chunked",
    });
    expect(selector.text()).toContain("Chunked transcription");

    bridge.emit({ type: "mode", mode: "translate_es_openai_realtime" });
    await flushPromises();
    expect(selector.text()).toContain("Chunked transcription");

    bridge.emit({ type: "mode", mode: "translate_es_chunked" });
    await flushPromises();
    expect(selector.attributes("disabled")).toBeUndefined();
  });

  it("renders aligned transcript columns and persists compact density", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const wrapper = mount(App);

    expect(wrapper.findAll(".bubble-grid")).toHaveLength(4);
    expect(wrapper.find(".translator-shell").classes()).toContain("density-compact");

    await wrapper.findAll(".density-control button")[1].trigger("click");

    expect(wrapper.find(".translator-shell").classes()).toContain("density-comfortable");
    expect(window.localStorage.getItem("translator-density")).toBe("comfortable");
  });

  it("builds language selectors from backend configuration and applies a change", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const bridge = createTranslatorBridge([
      {
        type: "session_config",
        sourceLanguage: "auto",
        targetLanguage: "es",
        languages: [
          { code: "en", label: "English" },
          { code: "es", label: "Spanish" },
          { code: "fr", label: "French" },
        ],
      },
    ]);
    window.translatorBridge = bridge;
    const wrapper = mount(App);
    await flushPromises();

    const targetSelector = wrapper.find<HTMLButtonElement>('.language-select[aria-label="Target language"]');
    await targetSelector.trigger("click");
    expect(document.querySelectorAll('.language-menu [role="option"]')).toHaveLength(3);
    expect(document.querySelectorAll(".language-menu .language-flag")).toHaveLength(3);
    document.querySelector<HTMLButtonElement>('.language-menu [data-language-code="fr"]')?.click();
    await flushPromises();

    expect(bridge.sendCommand).toHaveBeenCalledWith({
      type: "change_languages",
      sourceLanguage: "auto",
      targetLanguage: "fr",
    });
    expect(targetSelector.text()).toContain("French");

    bridge.emit({
      type: "session_config",
      sourceLanguage: "auto",
      targetLanguage: "es",
      languages: [
        { code: "en", label: "English" },
        { code: "es", label: "Spanish" },
        { code: "fr", label: "French" },
      ],
    });
    await flushPromises();
    expect(targetSelector.text()).toContain("French");

    bridge.emit({
      type: "session_config",
      sourceLanguage: "auto",
      targetLanguage: "fr",
      languages: [
        { code: "en", label: "English" },
        { code: "es", label: "Spanish" },
        { code: "fr", label: "French" },
      ],
    });
    await flushPromises();
    expect(targetSelector.attributes("disabled")).toBeUndefined();
  });

  it("shows a flag for every language in the backend catalog", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const codes = ["en", "es", "fr", "de", "it", "pt", "ca", "gl", "eu", "nl", "pl", "ru", "uk", "ar", "hi", "ja", "ko", "zh"];
    const bridge = createTranslatorBridge([{
      type: "session_config",
      sourceLanguage: "en",
      targetLanguage: "es",
      languages: codes.map((code) => ({ code, label: code.toUpperCase() })),
    }]);
    window.translatorBridge = bridge;
    const wrapper = mount(App);
    await flushPromises();

    await wrapper.find('.language-select[aria-label="Target language"]').trigger("click");

    expect(document.querySelectorAll(".language-menu .language-option")).toHaveLength(codes.length);
    expect(document.querySelectorAll(".language-menu .language-flag")).toHaveLength(codes.length);
  });

  it("shows a single pending pause state until Python confirms it", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const bridge = createTranslatorBridge([
      { type: "session_state", state: "active", message: "Escuchando" },
    ]);
    window.translatorBridge = bridge;
    const wrapper = mount(App);
    await flushPromises();

    await wrapper.find(".control-button.primary").trigger("click");
    expect(wrapper.text()).toContain("Pausing…");
    expect(wrapper.find(".control-button.primary").attributes("disabled")).toBeDefined();
    expect(wrapper.find(".control-button.primary .control-icon-surface").exists()).toBe(true);
    expect(wrapper.find(".control-button.primary .pending-control-icon").exists()).toBe(true);

    bridge.emit({ type: "session_state", state: "paused", message: "Pausado" });
    await flushPromises();

    expect(wrapper.text()).toContain("Resume");
    expect(wrapper.text()).not.toContain("Pausing…");
  });

  it("drives the waveform from the selected real audio source", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const bridge = createTranslatorBridge([
      { type: "session_state", state: "active", message: "Escuchando" },
    ]);
    window.translatorBridge = bridge;
    const wrapper = mount(App);
    await flushPromises();

    bridge.emit({ type: "audio_level", source: "system", level: 0.2 });
    await flushPromises();
    expect(wrapper.text()).toContain("Incoming system audio");
    expect(wrapper.findAll(".waveform span").at(-1)?.attributes("style")).toContain("58px");

    bridge.emit({ type: "voice_translation_state", active: true, message: "Selecciona so_ai_translated_mic" });
    bridge.emit({ type: "voice_translation_output", chunks: 25, bytes: 96000 });
    bridge.emit({ type: "audio_level", source: "microphone", level: 0.3 });
    await flushPromises();
    expect(wrapper.text()).toContain("Physical microphone level");
    expect(wrapper.find(".voice-output-strip").text()).toContain("Selecciona so_ai_translated_mic");
    expect(wrapper.find(".voice-output-strip").text()).toContain("Audio confirmed · 93.8 KB · 25 chunks");
    expect(wrapper.find(".voice-output-strip").classes()).toContain("voice-active");
  });

  it("blocks duplicate translated-microphone commands until Python confirms", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const bridge = createTranslatorBridge();
    window.translatorBridge = bridge;
    const wrapper = mount(App);
    await flushPromises();

    const microphoneButton = wrapper.findAll(".control-button")[0];
    await microphoneButton.trigger("click");
    await microphoneButton.trigger("click");
    expect(wrapper.text()).toContain("Connecting…");
    expect(wrapper.find(".voice-output-strip").text()).toContain("Conectando la salida de voz traducida");
    expect(bridge.sendCommand).toHaveBeenCalledTimes(1);
    expect(microphoneButton.find(".control-icon-surface").exists()).toBe(true);
    expect(microphoneButton.find(".pending-control-icon").exists()).toBe(true);

    bridge.emit({ type: "voice_translation_state", active: true, message: "Selecciona so_ai_translated_mic" });
    await flushPromises();
    expect(wrapper.text()).toContain("Translated mic");
    expect(microphoneButton.attributes("disabled")).toBeUndefined();
  });

  it("dispatches native window controls from the titlebar", async () => {
    window.history.pushState({}, "", "/?view=translator");
    const bridge = createTranslatorBridge();
    window.translatorBridge = bridge;
    const wrapper = mount(App);
    await flushPromises();

    await wrapper.find(".dot.yellow").trigger("click");
    await wrapper.find(".dot.green").trigger("click");
    await wrapper.find(".dot.red").trigger("click");

    expect(bridge.windowAction.mock.calls).toEqual([
      ["minimize"],
      ["toggle-maximize"],
      ["close"],
    ]);
    expect(wrapper.findAll(".dot-mark")).toHaveLength(3);
  });
});
