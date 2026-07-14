<template>
  <div class="model-picker" :class="{ open }">
    <button
      ref="triggerRef"
      class="model-select-trigger"
      type="button"
      aria-label="Transcription model"
      aria-haspopup="listbox"
      :aria-expanded="open"
      :disabled="pending"
      @click="toggleMenu"
      @keydown.down.prevent="openMenu"
      @keydown.up.prevent="openMenu"
    >
      <Box :size="18" />
      <span>{{ selectedOption.label }}</span>
      <LoaderCircle v-if="pending" class="language-select-spinner" :size="18" />
      <ChevronDown v-else class="model-select-chevron" :size="18" />
    </button>

    <Teleport to="body">
      <div
        v-if="open"
        ref="menuRef"
        class="model-menu"
        :style="menuStyle"
        role="listbox"
        aria-label="Transcription model options"
        @keydown.esc.prevent="closeMenu(true)"
        @keydown.down.prevent="focusRelative(1)"
        @keydown.up.prevent="focusRelative(-1)"
      >
        <button
          v-for="option in options"
          :key="option.value"
          class="model-option"
          type="button"
          role="option"
          :data-model="option.value"
          :aria-selected="option.value === modelValue"
          @click="selectModel(option.value)"
        >
          <Sparkles v-if="option.value === 'translate_es_openai_realtime'" :size="19" />
          <Box v-else :size="18" />
          <span>{{ option.label }}</span>
          <Check v-if="option.value === modelValue" :size="18" />
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { Box, Check, ChevronDown, LoaderCircle, Sparkles } from "@lucide/vue";
import type { SessionMode } from "./types";

const props = defineProps<{ modelValue: SessionMode; pending?: boolean }>();
const emit = defineEmits<{ change: [value: SessionMode] }>();
const options: { value: SessionMode; label: string }[] = [
  { value: "translate_es_chunked", label: "Chunked transcription" },
  { value: "translate_es_openai_realtime", label: "OpenAI Realtime API" },
];
const selectedOption = computed(() => options.find((option) => option.value === props.modelValue) ?? options[1]);
const open = ref(false);
const triggerRef = ref<HTMLButtonElement | null>(null);
const menuRef = ref<HTMLElement | null>(null);
const menuStyle = ref<Record<string, string>>({});

function positionMenu() {
  const trigger = triggerRef.value;
  if (!trigger) return;
  const rect = trigger.getBoundingClientRect();
  const height = options.length * 46 + 12;
  const below = window.innerHeight - rect.bottom - 12;
  const opensBelow = below >= height || below >= rect.top;
  const width = Math.max(220, rect.width);
  menuStyle.value = {
    left: `${Math.min(Math.max(12, rect.left), window.innerWidth - width - 12)}px`,
    top: opensBelow ? `${rect.bottom + 6}px` : "auto",
    bottom: opensBelow ? "auto" : `${window.innerHeight - rect.top + 6}px`,
    width: `${width}px`,
  };
}

async function openMenu() {
  if (props.pending || open.value) return;
  open.value = true;
  await nextTick();
  positionMenu();
  menuRef.value?.querySelector<HTMLButtonElement>(`[data-model="${props.modelValue}"]`)?.focus();
}

function closeMenu(restoreFocus = false) {
  open.value = false;
  if (restoreFocus) nextTick(() => triggerRef.value?.focus());
}

function toggleMenu() {
  if (open.value) closeMenu();
  else void openMenu();
}

function selectModel(value: SessionMode) {
  closeMenu(true);
  if (value !== props.modelValue) emit("change", value);
}

function focusRelative(offset: number) {
  const optionElements = Array.from(menuRef.value?.querySelectorAll<HTMLButtonElement>(".model-option") ?? []);
  if (!optionElements.length) return;
  const current = optionElements.indexOf(document.activeElement as HTMLButtonElement);
  optionElements[(current + offset + optionElements.length) % optionElements.length]?.focus();
}

function handlePointerDown(event: PointerEvent) {
  const target = event.target as Node;
  if (!triggerRef.value?.contains(target) && !menuRef.value?.contains(target)) closeMenu();
}

function handleViewportChange() {
  if (open.value) positionMenu();
}

onMounted(() => {
  document.addEventListener("pointerdown", handlePointerDown);
  window.addEventListener("resize", handleViewportChange);
  window.addEventListener("scroll", handleViewportChange, true);
});

onBeforeUnmount(() => {
  document.removeEventListener("pointerdown", handlePointerDown);
  window.removeEventListener("resize", handleViewportChange);
  window.removeEventListener("scroll", handleViewportChange, true);
});
</script>
