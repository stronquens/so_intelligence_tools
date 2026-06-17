<template>
  <main class="settings-desktop" data-testid="settings-window">
    <section class="settings-panel glass-panel" aria-label="Ajustes">
      <div class="settings-drag-zone" aria-hidden="true"></div>
      <header class="settings-header">
        <button class="settings-back" type="button" title="Volver" @click="closeSettingsWindow">
          <ChevronLeft :size="22" />
        </button>
        <h2>Ajustes</h2>
        <button class="settings-close" type="button" title="Cerrar ajustes" @click="closeSettingsWindow">
          <X :size="20" />
        </button>
      </header>

      <section class="settings-section">
        <h3>
          <Keyboard :size="19" />
          Atajos de teclado
        </h3>

        <div class="shortcut-list">
          <div v-for="shortcut in settings.shortcuts" :key="shortcut.id" class="shortcut-row">
            <span>{{ shortcut.label }}</span>
            <input
              v-if="editingShortcutId === shortcut.id"
              class="shortcut-input"
              :value="shortcut.value"
              aria-label="Nueva combinacion"
              @blur="editingShortcutId = null"
              @keydown="captureShortcut($event, shortcut.id)"
              @input="setShortcutValue(shortcut.id, ($event.target as HTMLInputElement).value)"
            />
            <kbd v-else>{{ shortcut.value }}</kbd>
            <button type="button" title="Editar atajo" @click="startShortcutEdit(shortcut.id)">
              <SquarePen :size="16" />
            </button>
          </div>
        </div>

        <p class="settings-status" :class="settingsStatusClass" role="status">{{ settingsStatus }}</p>
      </section>

      <section class="settings-options">
        <label class="toggle-row">
          <span>
            <strong>Iniciar al arrancar</strong>
            <small>Inicia so_intelligence_tools al encender el sistema</small>
          </span>
          <input v-model="settings.startAtLogin" type="checkbox" />
          <i aria-hidden="true"></i>
        </label>

        <label class="toggle-row">
          <span>
            <strong>Overlay siempre visible</strong>
            <small>Mantener el overlay visible en pantalla</small>
          </span>
          <input v-model="settings.overlayAlwaysVisible" type="checkbox" />
          <i aria-hidden="true"></i>
        </label>
      </section>

      <button class="save-settings" type="button" :disabled="savingSettings" @click="saveSettings">
        <Check :size="19" />
        {{ savingSettings ? "Guardando..." : "Guardar cambios" }}
      </button>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { Check, ChevronLeft, Keyboard, SquarePen, X } from "@lucide/vue";
import type { DesktopCommandResult, DesktopSettings, ShortcutActionId } from "./types";

const settings = ref<DesktopSettings>(createDefaultSettings());
const editingShortcutId = ref<ShortcutActionId | null>(null);
const savingSettings = ref(false);
const settingsStatus = ref("Ajustes listos.");
const settingsStatusClass = ref<DesktopCommandResult["status"] | "idle">("idle");

async function loadSettings() {
  editingShortcutId.value = null;
  settingsStatus.value = "Cargando ajustes...";
  settingsStatusClass.value = "running";

  if (!window.desktopBridge) {
    settings.value = createDefaultSettings();
    settingsStatus.value = "Bridge de escritorio no disponible. Usando defaults.";
    settingsStatusClass.value = "pending";
    return;
  }

  try {
    const result = await window.desktopBridge.sendCommand({ type: "get-settings" });
    if (result.status === "success" && result.settings) {
      settings.value = cloneSettings(result.settings);
      settingsStatus.value = "Ajustes cargados.";
      settingsStatusClass.value = "success";
      return;
    }

    settingsStatus.value = result.message;
    settingsStatusClass.value = result.status;
  } catch (error) {
    settingsStatus.value = error instanceof Error ? error.message : "No se pudieron cargar los ajustes.";
    settingsStatusClass.value = "failed";
  }
}

async function closeSettingsWindow() {
  if (!window.desktopBridge) {
    window.close();
    return;
  }

  await window.desktopBridge.sendCommand({ type: "close-settings" });
}

function startShortcutEdit(shortcutId: ShortcutActionId) {
  editingShortcutId.value = shortcutId;
  settingsStatus.value = "Pulsa una nueva combinacion.";
  settingsStatusClass.value = "idle";
}

function captureShortcut(event: KeyboardEvent, shortcutId: ShortcutActionId) {
  if (event.key === "Escape" || event.key === "Enter") {
    editingShortcutId.value = null;
    return;
  }

  const key = normalizeEventKey(event.key);
  if (!key) {
    return;
  }

  event.preventDefault();
  setShortcutValue(shortcutId, buildShortcutValue(event, key));
  editingShortcutId.value = null;
}

function setShortcutValue(shortcutId: ShortcutActionId, value: string) {
  settings.value.shortcuts = settings.value.shortcuts.map((shortcut) =>
    shortcut.id === shortcutId ? { ...shortcut, value } : shortcut,
  );
}

async function saveSettings() {
  const duplicate = findDuplicateShortcut(settings.value);
  if (duplicate) {
    settingsStatus.value = `Conflicto: ${duplicate.firstLabel} y ${duplicate.secondLabel} usan ${duplicate.value}.`;
    settingsStatusClass.value = "failed";
    return;
  }

  if (!window.desktopBridge) {
    settingsStatus.value = "El bridge de escritorio no esta disponible.";
    settingsStatusClass.value = "failed";
    return;
  }

  savingSettings.value = true;
  settingsStatus.value = "Guardando ajustes...";
  settingsStatusClass.value = "running";

  try {
    const result = await window.desktopBridge.sendCommand({
      type: "save-settings",
      settings: cloneSettings(settings.value),
    });

    if (result.settings) {
      settings.value = cloneSettings(result.settings);
    }

    settingsStatus.value = result.message;
    settingsStatusClass.value = result.status;
  } catch (error) {
    settingsStatus.value = error instanceof Error ? error.message : "No se pudieron guardar los ajustes.";
    settingsStatusClass.value = "failed";
  } finally {
    savingSettings.value = false;
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

function normalizeEventKey(key: string) {
  if (key === "Control" || key === "Alt" || key === "Shift" || key === "Meta") {
    return "";
  }

  if (key === " ") {
    return "Space";
  }

  if (key.length === 1) {
    return key.toUpperCase();
  }

  return key;
}

function buildShortcutValue(event: KeyboardEvent, key: string) {
  const parts: string[] = [];

  if (event.ctrlKey) {
    parts.push("Ctrl");
  }

  if (event.altKey) {
    parts.push("Alt");
  }

  if (event.shiftKey) {
    parts.push("Shift");
  }

  if (event.metaKey) {
    parts.push("Meta");
  }

  if (!parts.includes(key)) {
    parts.push(key);
  }

  return parts.join(" + ");
}

function splitShortcutParts(value: string) {
  return value
    .split("+")
    .map((part) => part.trim())
    .filter(Boolean);
}

function findDuplicateShortcut(value: DesktopSettings) {
  const seen = new Map<string, string>();

  for (const shortcut of value.shortcuts) {
    const normalized = splitShortcutParts(shortcut.value).join("+").toLowerCase();
    if (!normalized) {
      continue;
    }

    const previousLabel = seen.get(normalized);
    if (previousLabel) {
      return {
        firstLabel: previousLabel,
        secondLabel: shortcut.label,
        value: shortcut.value,
      };
    }

    seen.set(normalized, shortcut.label);
  }

  return null;
}

onMounted(() => {
  void loadSettings();
});
</script>
