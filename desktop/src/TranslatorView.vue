<template>
  <main class="translator-shell" :class="[`session-${sessionState}`, `density-${density}`]">
    <header class="titlebar">
      <div class="window-dots">
        <button class="dot red" type="button" title="Close" aria-label="Close translator" @click="windowAction('close')"><span class="dot-mark"></span></button>
        <button class="dot yellow" type="button" title="Minimize" aria-label="Minimize translator" @click="windowAction('minimize')"><span class="dot-mark"></span></button>
        <button class="dot green" type="button" title="Maximize" aria-label="Maximize or restore translator" @click="windowAction('toggle-maximize')"><span class="dot-mark"></span></button>
      </div>
      <div class="title-lockup">
        <h1>Real-Time Translator</h1>
        <span v-if="previewMode" class="preview-label">Preview</span>
      </div>
      <div class="header-actions">
        <span class="live-chip" :class="stateTone"><span></span>{{ stateLabel }}</span>
        <button class="icon-button" title="Settings coming soon" type="button" disabled>
          <Settings :size="22" />
        </button>
      </div>
    </header>

    <section class="workspace">
      <aside class="sidebar">
        <section class="stream-card">
          <div class="section-kicker" :class="stateTone">
            <span class="status-dot"></span>
            <strong>{{ streamLabel }}</strong>
            <AudioLines :size="22" />
          </div>
          <div class="timer">{{ elapsed }}</div>
          <p>{{ sessionMessage }}</p>
          <div
            class="waveform"
            :class="{ quiet: waveformQuiet }"
            :aria-label="waveformQuiet ? 'Audio input paused' : waveformLabel"
          >
            <span
              v-for="(bar, index) in waveform"
              :key="index"
              :style="{ height: `${bar}px` }"
            ></span>
          </div>
          <p>{{ waveformQuiet ? "Waiting for audio" : waveformLabel }}</p>
        </section>

        <section class="sidebar-section">
          <h2>LANGUAGES</h2>
          <LanguageSelect
            label="Source language"
            :model-value="sourceLanguage"
            :options="languages"
            :pending="Boolean(pendingLanguageChange)"
            allow-auto
            @change="handleSourceLanguageChange"
          />
          <button class="swap-badge" type="button" title="Swap source and target" :disabled="sourceLanguage === 'auto'" @click="swapLanguages">
            <ArrowUpDown :size="20" />
          </button>
          <LanguageSelect
            label="Target language"
            :model-value="targetLanguage"
            :options="languages"
            :pending="Boolean(pendingLanguageChange)"
            @change="handleTargetLanguageChange"
          />
          <button class="swap-wide" type="button" :disabled="sourceLanguage === 'auto'" @click="swapLanguages">
            <Repeat2 :size="18" />
            Swap languages
          </button>
        </section>

        <section class="sidebar-section model-section">
          <h2>TRANSCRIPTION MODEL</h2>
          <ModelSelect :model-value="activeMode" :pending="Boolean(pendingModeChange)" @change="changeMode" />
        </section>

        <section class="connection-card" :class="stateTone">
          <ShieldCheck v-if="sessionState === 'active'" :size="28" />
          <LoaderCircle v-else-if="sessionState === 'starting' || sessionState === 'reconnecting'" :size="28" />
          <CircleAlert v-else-if="sessionState === 'error'" :size="28" />
          <PauseCircle v-else :size="28" />
          <div>
            <strong>{{ connectionTitle }}</strong>
            <span>{{ connectionDetail }}</span>
          </div>
          <Signal :size="24" />
        </section>
      </aside>

      <section class="main-stage">
        <section class="conversation-panel">
          <div class="panel-header">
            <div class="panel-title">
              <AudioLines :size="24" />
              <strong><span class="full-title">LIVE TRANSCRIPT & TRANSLATION</span><span class="short-title">LIVE TRANSLATION</span></strong>
            </div>
            <div class="language-route" aria-hidden="true">
              <span>Source: <b>{{ sourceLanguageLabel }}</b></span>
              <ArrowRight :size="16" />
              <span>Target: <b>{{ targetLanguageLabel }}</b></span>
            </div>
            <div class="density-control" role="group" aria-label="Message density">
              <button type="button" :class="{ active: density === 'compact' }" @click="setDensity('compact')">Compact</button>
              <button type="button" :class="{ active: density === 'comfortable' }" @click="setDensity('comfortable')">Comfort</button>
            </div>
          </div>

          <div ref="timelineRef" class="timeline" data-testid="timeline" aria-live="polite">
            <div v-if="transcriptPairs.length === 0" class="timeline-empty">
              <div class="empty-icon"><AudioLines :size="30" /></div>
              <strong>{{ emptyTitle }}</strong>
              <p>{{ emptyDetail }}</p>
            </div>
            <TransitionGroup v-else name="transcript" tag="div">
              <article
                v-for="pair in transcriptPairs"
                :key="pair.id"
                class="timeline-pair"
                :class="{ streaming: pair.status === 'streaming' }"
              >
                <div class="time-column">
                  <span>{{ pair.timestamp }}</span>
                  <i></i>
                </div>
                <div class="bubble-grid">
                  <div class="bubble source">
                    <span class="lang-pill">{{ sourceLanguage === 'auto' ? 'AUTO' : sourceLanguage.toUpperCase() }}</span>
                    <p>{{ pair.sourceText || "Listening for the original…" }}</p>
                    <Ellipsis v-if="pair.status === 'streaming'" class="typing" :size="26" />
                  </div>
                  <div class="bubble translation">
                    <span class="lang-pill">{{ targetLanguage.toUpperCase() }}</span>
                    <p>{{ pair.translatedText || "Esperando traducción…" }}</p>
                    <CheckCircle2 v-if="pair.status === 'complete'" class="complete-icon" :size="23" />
                    <Ellipsis v-else class="typing" :size="26" />
                  </div>
                </div>
              </article>
            </TransitionGroup>
          </div>
        </section>

        <div class="voice-output-strip" :class="`voice-${voiceTranslationState}`" role="status" aria-live="polite">
          <Mic :size="18" aria-hidden="true" />
          <strong>Translated voice output</strong>
          <span>{{ voiceTranslationMessage }}</span>
          <em v-if="voiceOutputBytes > 0">Audio confirmed · {{ formatByteCount(voiceOutputBytes) }} · {{ voiceOutputChunks }} chunks</em>
        </div>

        <footer class="control-bar">
          <button
            class="control-button secondary"
            :class="{ active: voiceTranslationActive }"
            type="button"
            :title="voiceTranslationMessage"
            :disabled="pendingVoiceTranslation"
            @click="toggleVoiceTranslation"
          >
            <span v-if="pendingVoiceTranslation" class="control-icon-surface">
              <LoaderCircle class="pending-control-icon" :size="28" />
            </span>
            <Mic v-else :size="28" />
            <span>{{ voiceControlLabel }}</span>
          </button>
          <button class="control-button secondary" type="button" title="Speaker control coming soon" disabled>
            <Volume2 :size="28" />
            <span>Speaker</span>
          </button>
          <button
            class="control-button primary"
            type="button"
            title="Pause or resume"
            :disabled="!canPauseOrResume"
            @click="togglePause"
          >
            <span v-if="pendingSessionAction" class="control-icon-surface primary-surface">
              <LoaderCircle class="pending-control-icon" :size="34" />
            </span>
            <Play v-else-if="sessionState === 'paused' || sessionState === 'inactive' || sessionState === 'error'" :size="34" />
            <Pause v-else :size="34" />
            <span>{{ primaryControlLabel }}</span>
          </button>
          <button class="control-button secondary" type="button" title="Swap source and target" :disabled="sourceLanguage === 'auto'" @click="swapLanguages">
            <Repeat2 :size="28" />
            <span>Swap</span>
          </button>
          <button
            class="control-button danger"
            type="button"
            title="Stop session"
            :disabled="sessionState === 'inactive' || sessionState === 'stopping'"
            @click="sendCommand({ type: 'stop' })"
          >
            <Square :size="28" />
            <span>Stop</span>
          </button>
        </footer>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import {
  ArrowRight,
  ArrowUpDown,
  AudioLines,
  CheckCircle2,
  CircleAlert,
  Ellipsis,
  LoaderCircle,
  Mic,
  Pause,
  PauseCircle,
  Play,
  Repeat2,
  Settings,
  ShieldCheck,
  Signal,
  Square,
  Volume2,
} from "@lucide/vue";
import LanguageSelect from "./LanguageSelect.vue";
import ModelSelect from "./ModelSelect.vue";
import type { LanguageOption, SessionMode, TranscriptPair, UiCommand, UiEvent } from "./types";

const previewMode = !window.translatorBridge || new URLSearchParams(window.location.search).get("mock") === "1";
const timelineRef = ref<HTMLElement | null>(null);
const sessionState = ref(previewMode ? "active" : "starting");
const sessionMessage = ref(previewMode ? "Live audio input" : "Connecting to the audio session…");
const seconds = ref(previewMode ? 154 : 0);
const activeMode = ref<SessionMode>("translate_es_openai_realtime");
const confirmedMode = ref<SessionMode>(activeMode.value);
const pendingModeChange = ref<SessionMode | null>(null);
const languages = ref<LanguageOption[]>(previewLanguages());
const sourceLanguage = ref(previewMode ? "en" : "auto");
const targetLanguage = ref("es");
const confirmedLanguages = ref({ source: sourceLanguage.value, target: targetLanguage.value });
const pendingLanguageChange = ref<{ source: string; target: string } | null>(null);
const density = ref<"compact" | "comfortable">(loadDensity());
const pendingSessionAction = ref<"pause" | "resume" | "reset" | null>(null);
const completedPairs = ref<TranscriptPair[]>(previewMode ? createPreviewPairs() : []);
const partialOriginal = ref(previewMode ? "Please let me know if you have any questions before we move forward…" : "");
const partialTranslation = ref(previewMode ? "Por favor, decidme si tenéis alguna pregunta antes de continuar…" : "");
const partialTimestamp = ref(previewMode ? "10:15:42" : "");
const voiceTranslationActive = ref(false);
const pendingVoiceTranslation = ref(false);
const voiceTranslationState = ref("off");
const voiceTranslationMessage = ref("Microphone translation is off");
const voiceOutputChunks = ref(0);
const voiceOutputBytes = ref(0);
const waveform = ref<number[]>(Array.from({ length: 26 }, () => 8));
let removeEventListener: (() => void) | undefined;
let timerId: number | undefined;
let waveformTimerId: number | undefined;
let lastAudioLevelAt = 0;
let previewWaveTick = 0;

const transcriptPairs = computed(() => {
  if (!partialOriginal.value && !partialTranslation.value) {
    return completedPairs.value;
  }
  return [
    ...completedPairs.value,
    {
      id: "live-partial",
      timestamp: partialTimestamp.value || currentTimestamp(),
      sourceText: partialOriginal.value,
      translatedText: partialTranslation.value,
      status: "streaming" as const,
    },
  ];
});

const elapsed = computed(() => {
  const hours = Math.floor(seconds.value / 3600).toString().padStart(2, "0");
  const minutes = Math.floor((seconds.value % 3600) / 60).toString().padStart(2, "0");
  const secs = (seconds.value % 60).toString().padStart(2, "0");
  return `${hours}:${minutes}:${secs}`;
});

const stateLabel = computed(() => pendingSessionAction.value ? ({
  pause: "Pausing…",
  resume: "Resuming…",
  reset: "Restarting…",
}[pendingSessionAction.value]) : ({
  active: "Live",
  paused: "Paused",
  reconnecting: "Reconnecting",
  starting: "Starting",
  stopping: "Stopping",
  error: "Error",
  inactive: "Stopped",
}[sessionState.value] ?? "Offline"));

const streamLabel = computed(() => sessionState.value === "active" && !pendingSessionAction.value ? "STREAMING" : stateLabel.value.toUpperCase());
const stateTone = computed(() => {
  if (pendingSessionAction.value) return "pending";
  if (sessionState.value === "active") return "healthy";
  if (sessionState.value === "starting" || sessionState.value === "reconnecting") return "pending";
  if (sessionState.value === "error") return "failed";
  return "muted";
});
const canPauseOrResume = computed(() => !pendingSessionAction.value && !["starting", "stopping"].includes(sessionState.value));
const primaryControlLabel = computed(() => {
  if (pendingSessionAction.value) return stateLabel.value;
  if (sessionState.value === "paused") return "Resume";
  if (sessionState.value === "inactive" || sessionState.value === "error") return "Restart";
  return "Pause";
});
const sourceLanguageLabel = computed(() => sourceLanguage.value === "auto" ? "Auto detect" : languageLabel(sourceLanguage.value));
const targetLanguageLabel = computed(() => languageLabel(targetLanguage.value));
const connectionTitle = computed(() => stateTone.value === "healthy" ? "Connection stable" : stateLabel.value);
const connectionDetail = computed(() => sessionState.value === "active" ? (previewMode ? "Good network" : "Audio stream connected") : sessionMessage.value);
const emptyTitle = computed(() => sessionState.value === "error" ? "The session needs attention" : "Listening for the first phrase");
const emptyDetail = computed(() => sessionState.value === "error" ? sessionMessage.value : "Original and translation will appear together here.");
const waveformQuiet = computed(() => sessionState.value !== "active" && !voiceTranslationActive.value);
const waveformLabel = computed(() => voiceTranslationActive.value ? "Physical microphone level" : "Incoming system audio");
const voiceControlLabel = computed(() => {
  if (voiceTranslationState.value === "starting") return "Connecting…";
  if (voiceTranslationState.value === "stopping") return "Stopping…";
  if (voiceTranslationState.value === "reconnecting") return "Cancel retry";
  return voiceTranslationActive.value ? "Translated mic" : "Microphone";
});

async function sendCommand(command: UiCommand): Promise<boolean> {
  if (!window.translatorBridge) return false;
  const result = await window.translatorBridge.sendCommand(command);
  if (!result.accepted && result.message) {
    applyEvent({ type: "error", message: result.message });
    return false;
  }
  return result.accepted;
}

async function windowAction(action: "close" | "minimize" | "toggle-maximize") {
  await window.translatorBridge?.windowAction(action);
}

async function togglePause() {
  if (sessionState.value === "inactive" || sessionState.value === "error") {
    pendingSessionAction.value = "reset";
    if (!await sendCommand({ type: "reset" })) pendingSessionAction.value = null;
    return;
  }
  const action = sessionState.value === "paused" ? "resume" : "pause";
  pendingSessionAction.value = action;
  if (!await sendCommand({ type: action })) pendingSessionAction.value = null;
}

async function toggleVoiceTranslation() {
  if (pendingVoiceTranslation.value) return;
  if (previewMode) {
    voiceTranslationActive.value = !voiceTranslationActive.value;
    voiceTranslationState.value = voiceTranslationActive.value ? "active" : "off";
    voiceTranslationMessage.value = voiceTranslationActive.value
      ? "Preview: translated microphone active"
      : "Preview: microphone translation is off";
    return;
  }
  const previousState = voiceTranslationState.value;
  const previousMessage = voiceTranslationMessage.value;
  pendingVoiceTranslation.value = true;
  voiceTranslationState.value = voiceTranslationActive.value ? "stopping" : "starting";
  voiceTranslationMessage.value = voiceTranslationActive.value
    ? "Deteniendo la salida de voz traducida…"
    : "Conectando la salida de voz traducida…";
  if (!await sendCommand({ type: "toggle_voice_translation" })) {
    pendingVoiceTranslation.value = false;
    voiceTranslationState.value = previousState;
    voiceTranslationMessage.value = previousMessage;
  }
}

async function changeMode(mode: SessionMode) {
  if (mode === activeMode.value) return;
  activeMode.value = mode;
  if (previewMode) {
    confirmedMode.value = mode;
    return;
  }
  pendingModeChange.value = mode;
  const accepted = await sendCommand({ type: "change_mode", mode });
  if (!accepted && pendingModeChange.value === mode) restoreConfirmedMode();
}

function handleSourceLanguageChange(value: string) {
  void changeLanguages(value, targetLanguage.value);
}

function handleTargetLanguageChange(value: string) {
  void changeLanguages(sourceLanguage.value, value);
}

async function changeLanguages(source: string, target: string) {
  if (source === sourceLanguage.value && target === targetLanguage.value) return;
  sourceLanguage.value = source;
  targetLanguage.value = target;
  if (previewMode) {
    confirmedLanguages.value = { source, target };
    return;
  }
  pendingLanguageChange.value = { source, target };
  const accepted = await sendCommand({ type: "change_languages", sourceLanguage: source, targetLanguage: target });
  if (!accepted && languagePairMatches(pendingLanguageChange.value, source, target)) {
    restoreConfirmedLanguages();
  }
}

function swapLanguages() {
  if (sourceLanguage.value === "auto") return;
  void changeLanguages(targetLanguage.value, sourceLanguage.value);
}

function setDensity(value: "compact" | "comfortable") {
  density.value = value;
  window.localStorage.setItem("translator-density", value);
}

function applyEvent(event: UiEvent) {
  if (event.type === "session_state") {
    sessionState.value = event.state;
    sessionMessage.value = event.message;
    pendingSessionAction.value = null;
  } else if (event.type === "partial") {
    if (!partialOriginal.value && !partialTranslation.value && event.text) {
      partialTimestamp.value = currentTimestamp();
    }
    if (event.kind === "original") partialOriginal.value = event.text;
    else partialTranslation.value = event.text;
  } else if (event.type === "block") {
    const pair: TranscriptPair = {
      id: event.id,
      timestamp: event.timestamp,
      sourceText: event.sourceText ?? "",
      translatedText: event.translatedText,
      speakerLabel: event.speakerLabel,
      status: "complete",
    };
    const existingIndex = completedPairs.value.findIndex((candidate) => candidate.id === pair.id);
    if (existingIndex >= 0) completedPairs.value.splice(existingIndex, 1, pair);
    else completedPairs.value.push(pair);
    partialOriginal.value = "";
    partialTranslation.value = "";
    scrollTimeline();
  } else if (event.type === "mode") {
    if (!pendingModeChange.value || pendingModeChange.value === event.mode) {
      activeMode.value = event.mode;
      confirmedMode.value = event.mode;
      pendingModeChange.value = null;
    }
  } else if (event.type === "voice_translation_state") {
    voiceTranslationActive.value = event.active;
    voiceTranslationMessage.value = event.message;
    voiceTranslationState.value = event.state ?? (event.active ? "active" : "off");
    pendingVoiceTranslation.value = ["starting", "stopping"].includes(voiceTranslationState.value);
    if (!event.active) {
      voiceOutputChunks.value = 0;
      voiceOutputBytes.value = 0;
    }
  } else if (event.type === "voice_translation_output") {
    voiceOutputChunks.value = event.chunks;
    voiceOutputBytes.value = event.bytes;
  } else if (event.type === "audio_level") {
    const expectedSource = voiceTranslationActive.value ? "microphone" : "system";
    if (event.source === expectedSource) pushAudioLevel(event.level);
  } else if (event.type === "session_config") {
    languages.value = event.languages;
    const pending = pendingLanguageChange.value;
    if (!pending || languagePairMatches(pending, event.sourceLanguage, event.targetLanguage)) {
      sourceLanguage.value = event.sourceLanguage;
      targetLanguage.value = event.targetLanguage;
      confirmedLanguages.value = { source: event.sourceLanguage, target: event.targetLanguage };
      pendingLanguageChange.value = null;
    }
  } else if (event.type === "error") {
    if (pendingModeChange.value) restoreConfirmedMode();
    if (pendingLanguageChange.value) restoreConfirmedLanguages();
    pendingSessionAction.value = null;
    pendingVoiceTranslation.value = false;
    sessionState.value = "error";
    sessionMessage.value = event.message;
  }
}

function languageLabel(code: string) {
  return languages.value.find((language) => language.code === code)?.label ?? code.toUpperCase();
}

function languagePairMatches(pair: { source: string; target: string } | null, source: string, target: string) {
  return pair?.source === source && pair.target === target;
}

function restoreConfirmedLanguages() {
  sourceLanguage.value = confirmedLanguages.value.source;
  targetLanguage.value = confirmedLanguages.value.target;
  pendingLanguageChange.value = null;
}

function restoreConfirmedMode() {
  activeMode.value = confirmedMode.value;
  pendingModeChange.value = null;
}

function loadDensity(): "compact" | "comfortable" {
  return window.localStorage.getItem("translator-density") === "comfortable" ? "comfortable" : "compact";
}

function previewLanguages(): LanguageOption[] {
  return [
    { code: "en", label: "English" },
    { code: "es", label: "Spanish" },
    { code: "fr", label: "French" },
    { code: "de", label: "German" },
    { code: "it", label: "Italian" },
    { code: "pt", label: "Portuguese" },
    { code: "ca", label: "Catalan" },
    { code: "gl", label: "Galician" },
    { code: "eu", label: "Basque" },
    { code: "nl", label: "Dutch" },
    { code: "pl", label: "Polish" },
    { code: "ru", label: "Russian" },
    { code: "uk", label: "Ukrainian" },
    { code: "ar", label: "Arabic" },
    { code: "hi", label: "Hindi" },
    { code: "ja", label: "Japanese" },
    { code: "ko", label: "Korean" },
    { code: "zh", label: "Chinese" },
  ];
}

function scrollTimeline() {
  nextTick(() => {
    if (timelineRef.value) timelineRef.value.scrollTop = timelineRef.value.scrollHeight;
  });
}

function currentTimestamp() {
  return new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(new Date());
}

function formatByteCount(byteCount: number): string {
  if (byteCount < 1024) return `${byteCount} B`;
  if (byteCount < 1024 * 1024) return `${(byteCount / 1024).toFixed(1)} KB`;
  return `${(byteCount / (1024 * 1024)).toFixed(1)} MB`;
}

function pushAudioLevel(level: number) {
  const normalized = Math.min(Math.max(level, 0), 1);
  const visibleLevel = Math.min(1, normalized * 5);
  const height = Math.round(8 + Math.pow(visibleLevel, 0.55) * 50);
  waveform.value = [...waveform.value.slice(1), height];
  lastAudioLevelAt = Date.now();
}

function createPreviewPairs(): TranscriptPair[] {
  return [
    {
      id: "preview-1",
      timestamp: "10:15:23",
      sourceText: "Good morning everyone, thanks for joining the meeting today.",
      translatedText: "Buenos días a todos, gracias por uniros a la reunión de hoy.",
      status: "complete",
    },
    {
      id: "preview-2",
      timestamp: "10:15:29",
      sourceText: "We are reviewing the product timeline and the next release milestones.",
      translatedText: "Estamos revisando el calendario del producto y los próximos hitos de la versión.",
      status: "complete",
    },
    {
      id: "preview-3",
      timestamp: "10:15:36",
      sourceText: "If everything goes well, we can start testing next week.",
      translatedText: "Si todo va bien, podemos empezar las pruebas la semana que viene.",
      status: "complete",
    },
  ];
}

onMounted(async () => {
  if (window.translatorBridge && !previewMode) {
    removeEventListener = window.translatorBridge.onEvent(applyEvent);
    const readyResult = await window.translatorBridge.ready();
    readyResult.events.forEach(applyEvent);
  }
  scrollTimeline();
  timerId = window.setInterval(() => {
    if (sessionState.value === "active") seconds.value += 1;
  }, 1000);
  waveformTimerId = window.setInterval(() => {
    if (previewMode) {
      previewWaveTick += 1;
      const level = 0.035 + Math.abs(Math.sin(previewWaveTick * 0.43)) * 0.12;
      pushAudioLevel(level);
    } else if (Date.now() - lastAudioLevelAt > 180) {
      pushAudioLevel(0);
    }
  }, 100);
});

onBeforeUnmount(() => {
  removeEventListener?.();
  if (timerId !== undefined) window.clearInterval(timerId);
  if (waveformTimerId !== undefined) window.clearInterval(waveformTimerId);
});
</script>
