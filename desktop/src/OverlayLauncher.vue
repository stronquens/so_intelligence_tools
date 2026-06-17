<template>
  <main class="overlay-desktop" data-testid="overlay-launcher">
    <section class="launcher-panel glass-panel" aria-label="so_intelligence_tools">
      <header class="launcher-header">
        <div class="launcher-drag-handle">
          <div class="brand-mark" aria-hidden="true">
            <Sparkles :size="31" />
          </div>
          <div>
            <h1>so_intelligence_tools</h1>
            <p>Herramientas de IA para el sistema</p>
          </div>
        </div>
        <button class="panel-icon-button" type="button" title="Ajustes" @click="toggleSettings">
          <Settings :size="22" />
        </button>
        <button class="panel-close-button" type="button" title="Cerrar" @click="hideOverlay">
          <X :size="22" />
        </button>
      </header>

      <div class="tool-grid">
        <button
          v-for="tool in tools"
          :key="tool.title"
          class="tool-card"
          :class="tool.tone"
          :disabled="runningToolId === tool.id"
          type="button"
          @click="runTool(tool.id)"
        >
          <span class="tool-icon-wrap">
            <component :is="tool.icon" :size="43" stroke-width="2.1" />
            <component
              :is="tool.badgeIcon"
              v-if="tool.badgeIcon"
              class="tool-badge-icon"
              :size="20"
              stroke-width="2.2"
            />
          </span>
          <strong>{{ tool.title }}</strong>
          <span class="tool-description">{{ tool.description }}</span>
        </button>
      </div>

      <p class="command-status" :class="statusClass" role="status">{{ commandStatus }}</p>

      <footer class="launcher-shortcut">
        <template v-for="(part, index) in openOverlayShortcutParts" :key="`${part}-${index}`">
          <span v-if="index > 0">+</span>
          <kbd :class="{ 'shortcut-key-wide': part.toLowerCase() === 'space' }">{{ part }}</kbd>
        </template>
        <p>para abrir el overlay</p>
      </footer>
    </section>

  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, type Component } from "vue";
import {
  AudioLines,
  Bot,
  ClipboardPen,
  FileText,
  Languages,
  Mic,
  ScanText,
  ScanSearch,
  Settings,
  Sparkles,
  X,
} from "@lucide/vue";
import type { DesktopCommandResult, DesktopSettings, OverlayToolId } from "./types";

const runningToolId = ref<OverlayToolId | null>(null);
const lastResult = ref<DesktopCommandResult | null>(null);
const settings = ref<DesktopSettings>(createDefaultSettings());

const commandStatus = computed(() => {
  if (runningToolId.value) {
    return "Ejecutando herramienta...";
  }

  return lastResult.value?.message ?? "Selecciona una herramienta para ejecutarla.";
});

const statusClass = computed(() => {
  if (runningToolId.value) {
    return "running";
  }

  return lastResult.value?.status ?? "idle";
});

const openOverlayShortcutParts = computed(() => {
  const shortcut = settings.value.shortcuts.find((item) => item.id === "open-overlay");
  return splitShortcutParts(shortcut?.value ?? "Ctrl + Alt + A");
});

const tools = [
  {
    id: "selected-text-correction",
    title: "Corregir texto",
    description: "Mejora gramatica y estilo al instante",
    icon: ClipboardPen,
    tone: "pink",
  },
  {
    id: "screenshot-ocr",
    title: "OCR pantalla",
    description: "Extrae texto de cualquier parte de la pantalla",
    icon: ScanSearch,
    tone: "blue",
  },
  {
    id: "system-audio-translation",
    title: "Traducir audio",
    description: "Traduce audio en tiempo real",
    icon: AudioLines,
    tone: "green",
  },
  {
    id: "voice-translation-microphone",
    title: "Microfono traducido",
    description: "Traduce tu voz a otro idioma",
    icon: Mic,
    badgeIcon: Languages,
    tone: "gold",
  },
  {
    id: "push-to-talk-dictation",
    title: "Dictado",
    description: "Convierte tu voz en texto",
    icon: Mic,
    tone: "cyan",
  },
  {
    id: "assistant",
    title: "Asistente",
    description: "Asistencia inteligente para cualquier tarea",
    icon: Bot,
    tone: "violet",
  },
  {
    id: "summary",
    title: "Resumen",
    description: "Resume textos largos al instante",
    icon: FileText,
    tone: "teal",
  },
  {
    id: "intelligent-capture",
    title: "Captura inteligente",
    description: "Captura y entiende cualquier contenido",
    icon: ScanText,
    tone: "rose",
  },
] satisfies Array<{
  id: OverlayToolId;
  title: string;
  description: string;
  icon: Component;
  badgeIcon?: Component;
  tone: string;
}>;

async function runTool(toolId: OverlayToolId) {
  if (toolId === "system-audio-translation") {
    await openTranslatorWindow();
    return;
  }

  if (toolId !== "selected-text-correction") {
    lastResult.value = {
      status: "pending",
      toolId,
      message: "Esta herramienta todavia no esta conectada.",
    };
    return;
  }

  if (runningToolId.value) {
    return;
  }

  runningToolId.value = toolId;
  lastResult.value = null;

  if (!window.desktopBridge) {
    lastResult.value = {
      status: "failed",
      toolId,
      message: "El bridge de escritorio no esta disponible.",
    };
    runningToolId.value = null;
    return;
  }

  try {
    lastResult.value = await window.desktopBridge.sendCommand({
      type: "run-tool",
      toolId,
    });
  } catch (error) {
    lastResult.value = {
      status: "failed",
      toolId,
      message: error instanceof Error ? error.message : "No se pudo ejecutar la herramienta.",
    };
  } finally {
    runningToolId.value = null;
  }
}

async function openTranslatorWindow() {
  if (!window.desktopBridge) {
    lastResult.value = {
      status: "failed",
      toolId: "system-audio-translation",
      message: "El bridge de escritorio no esta disponible.",
    };
    return;
  }

  lastResult.value = await window.desktopBridge.sendCommand({ type: "open-translator" });
}

async function openSettings() {
  if (!window.desktopBridge) {
    lastResult.value = {
      status: "failed",
      message: "El bridge de escritorio no esta disponible.",
    };
    return;
  }

  await window.desktopBridge.sendCommand({ type: "toggle-settings" });
}

function toggleSettings() {
  void openSettings();
}

async function hideOverlay() {
  if (!window.desktopBridge) {
    window.close();
    return;
  }

  await window.desktopBridge.sendCommand({ type: "hide-overlay" });
}

async function loadShortcutSettings() {
  if (!window.desktopBridge) {
    return;
  }
  try {
    const result = await window.desktopBridge.sendCommand({ type: "get-settings" });
    if (result.status === "success" && result.settings) {
      settings.value = cloneSettings(result.settings);
    }
  } catch {
    settings.value = createDefaultSettings();
  }
}

function createDefaultSettings(): DesktopSettings {
  return {
    shortcuts: [
      { id: "open-overlay", label: "Abrir overlay", value: "Ctrl + Alt + A" },
      { id: "selected-text-correction", label: "Corregir texto", value: "Ctrl + Alt + C" },
      { id: "screenshot-ocr", label: "OCR pantalla", value: "Ctrl + Alt + O" },
      { id: "system-audio-translation", label: "Traducir audio", value: "Ctrl + Alt + T" },
      { id: "voice-translation-microphone", label: "Microfono traducido", value: "Ctrl + Alt + M" },
      { id: "push-to-talk-dictation", label: "Dictado", value: "Ctrl + Space" },
      { id: "assistant", label: "Asistente", value: "Sin asignar" },
      { id: "summary", label: "Resumen", value: "Ctrl + Alt + R" },
      { id: "intelligent-capture", label: "Captura inteligente", value: "Ctrl + Alt + I" },
    ],
    startAtLogin: true,
    overlayAlwaysVisible: false,
  };
}

function cloneSettings(value: DesktopSettings): DesktopSettings {
  return {
    shortcuts: value.shortcuts.map((shortcut) => ({ ...shortcut })),
    startAtLogin: value.startAtLogin,
    overlayAlwaysVisible: value.overlayAlwaysVisible,
  };
}

function splitShortcutParts(value: string) {
  return value
    .split("+")
    .map((part) => part.trim())
    .filter(Boolean);
}

onMounted(() => {
  void loadShortcutSettings();
});
</script>
