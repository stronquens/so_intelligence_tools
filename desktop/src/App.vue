<template>
  <main class="translator-shell">
    <header class="titlebar">
      <div class="window-dots" aria-hidden="true">
        <span class="dot red"></span>
        <span class="dot yellow"></span>
        <span class="dot green"></span>
      </div>
      <h1>Real-Time Translator</h1>
      <div class="header-actions">
        <span class="live-chip"><span></span>Live</span>
        <button class="icon-button" title="Settings" type="button">
          <Settings :size="22" />
        </button>
      </div>
    </header>

    <section class="workspace">
      <aside class="sidebar">
        <section class="stream-card">
          <div class="section-kicker">
            <span class="status-dot"></span>
            <strong>STREAMING</strong>
            <AudioLines :size="22" />
          </div>
          <div class="timer">{{ elapsed }}</div>
          <p>Live audio input</p>
          <div class="waveform" aria-label="Incoming audio level">
            <span v-for="(bar, index) in waveform" :key="index" :style="{ height: `${bar}px` }"></span>
          </div>
          <p>Incoming audio</p>
        </section>

        <section class="sidebar-section">
          <h2>LANGUAGES</h2>
          <button class="language-row" type="button">
            <span class="flag">🇺🇸</span>
            <span>English</span>
            <AudioLines :size="21" />
          </button>
          <button class="swap-badge" type="button" title="Swap languages">
            <ArrowUpDown :size="20" />
          </button>
          <button class="language-row" type="button">
            <span class="flag">🇪🇸</span>
            <span>Spanish</span>
          </button>
          <button class="swap-wide" type="button">
            <Repeat2 :size="18" />
            Swap Languages
          </button>
        </section>

        <section class="sidebar-section model-section">
          <h2>TRANSCRIPTION MODEL</h2>
          <button class="model-select" type="button">
            <Box :size="18" />
            <span>OpenAI Realtime API</span>
            <ChevronDown :size="18" />
          </button>
          <div class="model-menu">
            <button type="button"><Box :size="17" /> Whisper Tiny (Local)</button>
            <button class="selected" type="button"><Sparkles :size="17" /> OpenAI Realtime API <Check :size="17" /></button>
            <button type="button"><RadioTower :size="17" /> Deepgram API</button>
          </div>
        </section>

        <section class="connection-card">
          <ShieldCheck :size="28" />
          <div>
            <strong>Connection stable</strong>
            <span>Good network</span>
          </div>
          <Signal :size="24" />
        </section>
      </aside>

      <section class="main-stage">
        <section class="conversation-panel">
          <div class="panel-header">
            <div>
              <AudioLines :size="24" />
              <strong>LIVE TRANSCRIPT & TRANSLATION</strong>
            </div>
            <span>Source: English <ArrowRight :size="16" /> Target: Spanish</span>
          </div>

          <div ref="timelineRef" class="timeline" data-testid="timeline">
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
              <div class="bubble-stack">
                <div class="bubble source">
                  <span class="lang-pill">EN</span>
                  <p>{{ pair.sourceText }}</p>
                  <Ellipsis v-if="pair.status === 'streaming'" class="typing" :size="26" />
                </div>
                <div class="bubble translation">
                  <span class="lang-pill">ES</span>
                  <p>{{ pair.translatedText }}</p>
                  <CheckCircle2 v-if="pair.status === 'complete'" class="complete-icon" :size="23" />
                  <Ellipsis v-else class="typing" :size="26" />
                </div>
              </div>
            </article>
          </div>
        </section>

        <footer class="control-bar">
          <button class="control-button secondary" type="button" title="Microphone">
            <Mic :size="28" />
            <span>Microphone</span>
          </button>
          <button class="control-button secondary" type="button" title="Speaker">
            <Volume2 :size="28" />
            <span>Speaker</span>
          </button>
          <button class="control-button primary" type="button" title="Pause or resume" @click="togglePause">
            <Pause v-if="!paused" :size="34" />
            <Play v-else :size="34" />
            <span>{{ paused ? "Resume" : "Pause" }}</span>
          </button>
          <button class="control-button secondary" type="button" title="Swap">
            <Repeat2 :size="28" />
            <span>Swap</span>
          </button>
          <button class="control-button danger" type="button" title="Stop" @click="sendCommand({ type: 'stop' })">
            <Square :size="28" />
            <span>Stop</span>
          </button>
        </footer>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";
import {
  ArrowRight,
  ArrowUpDown,
  AudioLines,
  Box,
  Check,
  CheckCircle2,
  ChevronDown,
  Ellipsis,
  Mic,
  Pause,
  Play,
  RadioTower,
  Repeat2,
  Settings,
  ShieldCheck,
  Signal,
  Sparkles,
  Square,
  Volume2,
} from "@lucide/vue";
import type { TranscriptPair, UiCommand } from "./types";

const paused = ref(false);
const timelineRef = ref<HTMLElement | null>(null);
const seconds = ref(154);
const waveform = [42, 42, 38, 27, 34, 28, 43, 31, 30, 38, 28, 27, 30, 31, 38, 44, 25, 30, 46, 58, 42, 32, 52, 26, 20, 16];

const transcriptPairs = ref<TranscriptPair[]>([
  {
    id: "1",
    timestamp: "10:15:23",
    sourceText: "Good morning everyone, thanks for joining the meeting today.",
    translatedText: "Buenos dias a todos, gracias por uniros a la reunion de hoy.",
    status: "complete",
  },
  {
    id: "2",
    timestamp: "10:15:29",
    sourceText: "We are reviewing the product timeline and the next release milestones.",
    translatedText: "Estamos revisando el calendario del producto y los proximos hitos de la version.",
    status: "complete",
  },
  {
    id: "3",
    timestamp: "10:15:36",
    sourceText: "If everything goes well, we can start testing next week.",
    translatedText: "Si todo va bien, podemos empezar las pruebas la semana que viene.",
    status: "complete",
  },
  {
    id: "live",
    timestamp: "10:15:42",
    sourceText: "Please let me know if you have any questions before we move forward...",
    translatedText: "Por favor, decidme si teneis alguna pregunta antes de continuar...",
    status: "streaming",
  },
]);

const elapsed = computed(() => {
  const minutes = Math.floor(seconds.value / 60).toString().padStart(2, "0");
  const secs = (seconds.value % 60).toString().padStart(2, "0");
  return `00:${minutes}:${secs}`;
});

async function sendCommand(command: UiCommand) {
  if (window.translatorBridge) {
    await window.translatorBridge.sendCommand(command);
  }
}

async function togglePause() {
  paused.value = !paused.value;
  await sendCommand({ type: paused.value ? "pause" : "resume" });
}

function scrollTimeline() {
  nextTick(() => {
    if (timelineRef.value) {
      timelineRef.value.scrollTop = timelineRef.value.scrollHeight;
    }
  });
}

onMounted(() => {
  scrollTimeline();
  window.setInterval(() => {
    if (!paused.value) {
      seconds.value += 1;
    }
  }, 1000);
});
</script>
