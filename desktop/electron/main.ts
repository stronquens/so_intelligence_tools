import { app, BrowserWindow, ipcMain, screen } from "electron";
import { spawn } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, "..", "..");
const appIconPath = path.join(
  projectRoot,
  "assets",
  "branding",
  process.platform === "win32" ? "app-icon.ico" : "app-icon.png",
);
const hasSingleInstanceLock = app.requestSingleInstanceLock();

app.setAppUserModelId("so_intelligence_tools");

let mainWindow: BrowserWindow | null = null;
let settingsWindow: BrowserWindow | null = null;
let translatorWindow: BrowserWindow | null = null;

const launcherWindowSize = {
  width: 680,
  height: 472,
};

const settingsWindowSize = {
  width: 373,
  height: 620,
};

const settingsWindowGap = 28;

const translatorWindowSize = {
  width: 1440,
  height: 820,
};

type OverlayToolId =
  | "selected-text-correction"
  | "screenshot-ocr"
  | "system-audio-translation"
  | "voice-translation-microphone"
  | "push-to-talk-dictation"
  | "assistant"
  | "summary"
  | "intelligent-capture";

type ShortcutActionId = OverlayToolId | "open-overlay";

interface ShortcutSetting {
  id: ShortcutActionId;
  label: string;
  value: string;
}

interface DesktopSettings {
  shortcuts: ShortcutSetting[];
  startAtLogin: boolean;
  overlayAlwaysVisible: boolean;
}

type DesktopCommand =
  | { type: "run-tool"; toolId: OverlayToolId }
  | { type: "open-translator" }
  | { type: "hide-overlay" }
  | { type: "toggle-settings" }
  | { type: "close-settings" }
  | { type: "get-settings" }
  | { type: "save-settings"; settings: DesktopSettings };

interface DesktopCommandResult {
  status: "success" | "failed" | "pending";
  message: string;
  toolId?: OverlayToolId;
  details?: string;
  settings?: DesktopSettings;
}

const defaultDesktopSettings: DesktopSettings = {
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

function centerWindowOnActiveDisplay(window: BrowserWindow) {
  const cursorPoint = screen.getCursorScreenPoint();
  const display = screen.getDisplayNearestPoint(cursorPoint);
  const { x, y, width, height } = display.workArea;
  const [windowWidth, windowHeight] = window.getSize();

  window.setPosition(
    Math.round(x + (width - windowWidth) / 2),
    Math.round(y + (height - windowHeight) / 2),
  );
}

function createWindow() {
  const window = new BrowserWindow({
    width: launcherWindowSize.width,
    height: launcherWindowSize.height,
    minWidth: launcherWindowSize.width,
    minHeight: launcherWindowSize.height,
    backgroundColor: "#00000000",
    frame: false,
    show: false,
    transparent: true,
    alwaysOnTop: true,
    title: "so_intelligence_tools",
    icon: appIconPath,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  loadAppView(window, "overlay");

  window.setAlwaysOnTop(true, "screen-saver");
  window.once("ready-to-show", () => {
    centerWindowOnActiveDisplay(window);
    window.show();
    window.focus();
  });

  window.on("closed", () => {
    if (mainWindow === window) {
      mainWindow = null;
    }
  });

  mainWindow = window;
  return window;
}

function createSettingsWindow() {
  if (settingsWindow && !settingsWindow.isDestroyed()) {
    settingsWindow.show();
    settingsWindow.focus();
    return settingsWindow;
  }

  const window = new BrowserWindow({
    width: settingsWindowSize.width,
    height: settingsWindowSize.height,
    minWidth: settingsWindowSize.width,
    minHeight: settingsWindowSize.height,
    backgroundColor: "#00000000",
    frame: false,
    show: false,
    transparent: true,
    alwaysOnTop: true,
    title: "so_intelligence_tools Ajustes",
    icon: appIconPath,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  loadAppView(window, "settings");
  window.setAlwaysOnTop(true, "screen-saver");
  window.once("ready-to-show", () => {
    positionSettingsWindow(window);
    window.show();
    window.focus();
  });

  window.on("closed", () => {
    if (settingsWindow === window) {
      settingsWindow = null;
    }
  });

  settingsWindow = window;
  return window;
}

function createTranslatorWindow() {
  if (translatorWindow && !translatorWindow.isDestroyed()) {
    translatorWindow.show();
    translatorWindow.focus();
    return translatorWindow;
  }

  const window = new BrowserWindow({
    width: translatorWindowSize.width,
    height: translatorWindowSize.height,
    minWidth: 1080,
    minHeight: 680,
    backgroundColor: "#f8fafc",
    frame: false,
    show: false,
    title: "so_intelligence_tools Traductor",
    icon: appIconPath,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  loadAppView(window, "translator");
  window.once("ready-to-show", () => {
    centerWindowOnActiveDisplay(window);
    window.show();
    window.focus();
  });

  window.on("closed", () => {
    if (translatorWindow === window) {
      translatorWindow = null;
    }
  });

  translatorWindow = window;
  return window;
}

function loadAppView(window: BrowserWindow, view: "overlay" | "settings" | "translator") {
  const devServerUrl = process.env.SO_AI_DESKTOP_DEV_SERVER_URL;
  if (devServerUrl) {
    const url = new URL(devServerUrl);
    if (view !== "overlay") {
      url.searchParams.set("view", view);
    }

    window.loadURL(url.toString());
    return;
  }

  if (view === "overlay") {
    window.loadFile(path.join(__dirname, "../dist/index.html"));
    return;
  }

  window.loadFile(path.join(__dirname, "../dist/index.html"), {
    query: { view },
  });
}

function positionSettingsWindow(window: BrowserWindow) {
  if (!mainWindow || mainWindow.isDestroyed()) {
    centerWindowOnActiveDisplay(window);
    return;
  }

  const mainBounds = mainWindow.getBounds();
  const display = screen.getDisplayMatching(mainBounds);
  const { x, y, width, height } = display.workArea;
  const [settingsWidth, settingsHeight] = window.getSize();
  const targetX = mainBounds.x + mainBounds.width + settingsWindowGap;
  const targetY = Math.round(mainBounds.y + (mainBounds.height - settingsHeight) / 2);

  window.setPosition(
    Math.min(Math.max(targetX, x), x + width - settingsWidth),
    Math.min(Math.max(targetY, y), y + height - settingsHeight),
  );
}

if (!hasSingleInstanceLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    toggleMainWindow();
  });

  app.whenReady().then(() => {
    createWindow();

    app.on("activate", () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
        return;
      }

      showMainWindow();
    });
  });
}

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

function toggleMainWindow() {
  if (!mainWindow || mainWindow.isDestroyed()) {
    createWindow();
    return;
  }

  if (mainWindow.isVisible() && !mainWindow.isMinimized()) {
    closeSettingsWindow();
    mainWindow.minimize();
    return;
  }

  showMainWindow();
}

function showMainWindow() {
  if (!mainWindow || mainWindow.isDestroyed()) {
    createWindow();
    return;
  }

  if (mainWindow.isMinimized()) {
    mainWindow.restore();
  }

  centerWindowOnActiveDisplay(mainWindow);
  mainWindow.show();
  mainWindow.focus();
}

function toggleSettingsWindow() {
  if (settingsWindow && !settingsWindow.isDestroyed() && settingsWindow.isVisible()) {
    closeSettingsWindow();
    return;
  }

  ensureMainWindowVisible();
  createSettingsWindow();
}

function ensureMainWindowVisible() {
  if (!mainWindow || mainWindow.isDestroyed()) {
    createWindow();
    return;
  }

  if (mainWindow.isMinimized()) {
    mainWindow.restore();
  }

  if (!mainWindow.isVisible()) {
    mainWindow.show();
  }
}

function closeSettingsWindow() {
  if (!settingsWindow || settingsWindow.isDestroyed()) {
    settingsWindow = null;
    return;
  }

  settingsWindow.close();
  settingsWindow = null;
}

ipcMain.handle("ui-command", (_event, command) => {
  return {
    accepted: true,
    command,
    handledBy: "electron-mock-bridge",
  };
});

ipcMain.handle("desktop-command", async (event, command: unknown): Promise<DesktopCommandResult> => {
  const parsedCommand = parseDesktopCommand(command);
  const window = BrowserWindow.fromWebContents(event.sender);

  if (!parsedCommand) {
    return {
      status: "failed",
      message: "Comando de escritorio no valido.",
    };
  }

  if (parsedCommand.type === "hide-overlay") {
    closeSettingsWindow();
    window?.hide();
    return {
      status: "success",
      message: "Overlay oculto.",
    };
  }

  if (parsedCommand.type === "toggle-settings") {
    toggleSettingsWindow();
    return {
      status: "success",
      message: "Ajustes alternados.",
    };
  }

  if (parsedCommand.type === "open-translator") {
    createTranslatorWindow();
    return {
      status: "success",
      message: "Traductor abierto.",
      toolId: "system-audio-translation",
    };
  }

  if (parsedCommand.type === "close-settings") {
    closeSettingsWindow();
    return {
      status: "success",
      message: "Ajustes cerrados.",
    };
  }

  if (parsedCommand.type === "get-settings") {
    const settings = await loadDesktopSettings();
    return {
      status: "success",
      message: "Ajustes cargados.",
      settings,
    };
  }

  if (parsedCommand.type === "save-settings") {
    try {
      const settings = sanitizeDesktopSettings(parsedCommand.settings);
      await saveDesktopSettings(settings);
      app.setLoginItemSettings({ openAtLogin: settings.startAtLogin });
      return {
        status: "success",
        message: "Ajustes guardados.",
        settings,
      };
    } catch (error) {
      return {
        status: "failed",
        message: error instanceof Error ? error.message : "No se pudieron guardar los ajustes.",
      };
    }
  }

  if (parsedCommand.toolId !== "selected-text-correction") {
    return {
      status: "pending",
      toolId: parsedCommand.toolId,
      message: "Esta herramienta todavia no esta conectada.",
    };
  }

  return runSelectedTextCorrection(window);
});

function parseDesktopCommand(command: unknown): DesktopCommand | null {
  if (!command || typeof command !== "object") {
    return null;
  }

  const candidate = command as Partial<DesktopCommand>;

  if (candidate.type === "hide-overlay") {
    return { type: "hide-overlay" };
  }

  if (candidate.type === "toggle-settings") {
    return { type: "toggle-settings" };
  }

  if (candidate.type === "open-translator") {
    return { type: "open-translator" };
  }

  if (candidate.type === "close-settings") {
    return { type: "close-settings" };
  }

  if (candidate.type === "get-settings") {
    return { type: "get-settings" };
  }

  if (candidate.type === "save-settings") {
    const settings = (command as { settings?: unknown }).settings;
    if (isDesktopSettingsCandidate(settings)) {
      return {
        type: "save-settings",
        settings,
      };
    }
  }

  if (candidate.type === "run-tool" && isOverlayToolId(candidate.toolId)) {
    return {
      type: "run-tool",
      toolId: candidate.toolId,
    };
  }

  return null;
}

function isOverlayToolId(toolId: unknown): toolId is OverlayToolId {
  return (
    toolId === "selected-text-correction" ||
    toolId === "screenshot-ocr" ||
    toolId === "system-audio-translation" ||
    toolId === "voice-translation-microphone" ||
    toolId === "push-to-talk-dictation" ||
    toolId === "assistant" ||
    toolId === "summary" ||
    toolId === "intelligent-capture"
  );
}

function isShortcutActionId(value: unknown): value is ShortcutActionId {
  return value === "open-overlay" || isOverlayToolId(value);
}

function isDesktopSettingsCandidate(value: unknown): value is DesktopSettings {
  if (!value || typeof value !== "object") {
    return false;
  }

  const candidate = value as Partial<DesktopSettings>;
  return (
    Array.isArray(candidate.shortcuts) &&
    typeof candidate.startAtLogin === "boolean" &&
    typeof candidate.overlayAlwaysVisible === "boolean"
  );
}

async function loadDesktopSettings(): Promise<DesktopSettings> {
  try {
    const raw = await readFile(settingsFilePath(), "utf8");
    return sanitizeDesktopSettings(JSON.parse(raw));
  } catch {
    return cloneDefaultDesktopSettings();
  }
}

async function saveDesktopSettings(settings: DesktopSettings): Promise<void> {
  const targetPath = settingsFilePath();
  await mkdir(path.dirname(targetPath), { recursive: true });
  await writeFile(targetPath, `${JSON.stringify(settings, null, 2)}\n`, "utf8");
}

function settingsFilePath() {
  return path.join(app.getPath("userData"), "desktop-settings.json");
}

function sanitizeDesktopSettings(candidate: DesktopSettings): DesktopSettings {
  const incomingShortcuts = new Map(
    candidate.shortcuts
      .filter((shortcut) => isShortcutActionId(shortcut.id))
      .map((shortcut) => [shortcut.id, shortcut]),
  );
  migrateLegacyShortcutDefaults(incomingShortcuts);

  const shortcuts = defaultDesktopSettings.shortcuts.map((defaultShortcut) => {
    const incoming = incomingShortcuts.get(defaultShortcut.id);
    const value = normalizeShortcutValue(incoming?.value ?? defaultShortcut.value);
    if (!value) {
      throw new Error(`El atajo de ${defaultShortcut.label} no puede estar vacio.`);
    }

    return {
      ...defaultShortcut,
      value,
    };
  });

  return {
    shortcuts,
    startAtLogin: candidate.startAtLogin,
    overlayAlwaysVisible: candidate.overlayAlwaysVisible,
  };
}

function migrateLegacyShortcutDefaults(incomingShortcuts: Map<ShortcutActionId, ShortcutSetting>) {
  const openOverlay = incomingShortcuts.get("open-overlay");
  const assistant = incomingShortcuts.get("assistant");
  const dictation = incomingShortcuts.get("push-to-talk-dictation");

  if (
    normalizeShortcutValue(openOverlay?.value) === "Ctrl + Space" &&
    normalizeShortcutValue(assistant?.value) === "Ctrl + Alt + A"
  ) {
    incomingShortcuts.set("open-overlay", {
      id: "open-overlay",
      label: openOverlay?.label ?? "Abrir overlay",
      value: "Ctrl + Alt + A",
    });
    incomingShortcuts.set("assistant", {
      id: "assistant",
      label: assistant?.label ?? "Asistente",
      value: "Sin asignar",
    });
  }

  if (
    normalizeShortcutValue(dictation?.value) === "Ctrl + Space" ||
    normalizeShortcutValue(dictation?.value) === "Ctrl + Shift + D" ||
    normalizeShortcutValue(dictation?.value) === "Ctrl + Alt + Space"
  ) {
    incomingShortcuts.set("push-to-talk-dictation", {
      id: "push-to-talk-dictation",
      label: dictation?.label ?? "Dictado",
      value: "Ctrl + Shift + Space",
    });
  }
}

function normalizeShortcutValue(value: unknown) {
  if (typeof value !== "string") {
    return "";
  }

  return value
    .split("+")
    .map((part) => normalizeShortcutPart(part.trim()))
    .filter(Boolean)
    .join(" + ");
}

function normalizeShortcutPart(value: string) {
  const normalized = value.toLowerCase();

  if (normalized === "control" || normalized === "ctrl") {
    return "Ctrl";
  }

  if (normalized === "alt" || normalized === "option") {
    return "Alt";
  }

  if (normalized === "shift") {
    return "Shift";
  }

  if (normalized === "meta" || normalized === "cmd" || normalized === "win" || normalized === "windows") {
    return "Meta";
  }

  if (normalized === " " || normalized === "space" || normalized === "spacebar") {
    return "Space";
  }

  if (value.length === 1) {
    return value.toUpperCase();
  }

  return value;
}

function cloneDefaultDesktopSettings(): DesktopSettings {
  return {
    shortcuts: defaultDesktopSettings.shortcuts.map((shortcut) => ({ ...shortcut })),
    startAtLogin: defaultDesktopSettings.startAtLogin,
    overlayAlwaysVisible: defaultDesktopSettings.overlayAlwaysVisible,
  };
}

async function runSelectedTextCorrection(window: BrowserWindow | null): Promise<DesktopCommandResult> {
  window?.hide();
  await delay(180);

  const result = await runProjectCli(["run-selected-text-correction", "--debug"]);

  if (window && !window.isDestroyed()) {
    centerWindowOnActiveDisplay(window);
    window.show();
    window.focus();
  }

  if (result.exitCode === 0) {
    return {
      status: "success",
      toolId: "selected-text-correction",
      message: "Texto corregido.",
      details: result.stdout,
    };
  }

  return {
    status: "failed",
    toolId: "selected-text-correction",
    message: result.stderr || result.stdout || "No se pudo corregir el texto seleccionado.",
    details: result.stdout || result.stderr,
  };
}

function runProjectCli(args: string[]): Promise<{ exitCode: number | null; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const child = spawn(commandForPlatform("poetry"), ["run", "so-intelligence-tools", ...args], {
      cwd: projectRoot,
      shell: false,
      windowsHide: true,
    });

    let stdout = "";
    let stderr = "";

    child.stdout?.on("data", (chunk: Buffer) => {
      stdout += chunk.toString("utf8");
    });

    child.stderr?.on("data", (chunk: Buffer) => {
      stderr += chunk.toString("utf8");
    });

    child.on("error", (error) => {
      resolve({
        exitCode: 1,
        stdout,
        stderr: error.message,
      });
    });

    child.on("close", (exitCode) => {
      resolve({
        exitCode,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
      });
    });
  });
}

function commandForPlatform(command: string) {
  return process.platform === "win32" ? `${command}.cmd` : command;
}

function delay(milliseconds: number) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}
