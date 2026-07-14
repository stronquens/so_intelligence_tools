<template>
  <div class="language-select-wrap" :class="{ open, pending }">
    <button
      ref="triggerRef"
      class="language-select language-select-trigger"
      type="button"
      :aria-label="label"
      aria-haspopup="listbox"
      :aria-expanded="open"
      :disabled="disabled || pending"
      @click="toggleMenu"
      @keydown.down.prevent="openMenu"
      @keydown.up.prevent="openMenu"
    >
      <Globe2 v-if="modelValue === 'auto'" class="auto-language-icon" :size="23" />
      <img v-else class="language-flag" :src="flagUrl(modelValue)" alt="" />
      <span class="language-select-label">{{ selectedLabel }}</span>
      <LoaderCircle v-if="pending" class="language-select-spinner" :size="18" aria-hidden="true" />
      <ChevronDown v-else class="language-select-chevron" :size="18" aria-hidden="true" />
    </button>

    <Teleport to="body">
      <div
        v-if="open"
        ref="menuRef"
        class="language-menu"
        :style="menuStyle"
        role="listbox"
        :aria-label="`${label} options`"
        @keydown.esc.prevent="closeMenu(true)"
        @keydown.down.prevent="focusRelative(1)"
        @keydown.up.prevent="focusRelative(-1)"
      >
        <button
          v-if="allowAuto"
          class="language-option"
          type="button"
          role="option"
          data-language-code="auto"
          :aria-selected="modelValue === 'auto'"
          @click="selectLanguage('auto')"
        >
          <Globe2 class="auto-language-icon" :size="23" />
          <span>Auto detect</span>
          <Check v-if="modelValue === 'auto'" :size="18" />
        </button>
        <button
          v-for="language in options"
          :key="language.code"
          class="language-option"
          type="button"
          role="option"
          :data-language-code="language.code"
          :aria-selected="modelValue === language.code"
          @click="selectLanguage(language.code)"
        >
          <img class="language-flag" :src="flagUrl(language.code)" alt="" />
          <span>{{ language.label }}</span>
          <Check v-if="modelValue === language.code" :size="18" />
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { Check, ChevronDown, Globe2, LoaderCircle } from "@lucide/vue";
import { flagUrl } from "./languageFlags";
import type { LanguageOption } from "./types";

const props = withDefaults(defineProps<{
  label: string;
  modelValue: string;
  options: LanguageOption[];
  allowAuto?: boolean;
  disabled?: boolean;
  pending?: boolean;
}>(), {
  allowAuto: false,
  disabled: false,
  pending: false,
});

const emit = defineEmits<{ change: [value: string] }>();
const open = ref(false);
const triggerRef = ref<HTMLButtonElement | null>(null);
const menuRef = ref<HTMLElement | null>(null);
const menuStyle = ref<Record<string, string>>({});
const selectedLabel = computed(() => props.modelValue === "auto"
  ? "Auto detect"
  : props.options.find((language) => language.code === props.modelValue)?.label ?? props.modelValue.toUpperCase());

function positionMenu() {
  const trigger = triggerRef.value;
  if (!trigger) return;
  const rect = trigger.getBoundingClientRect();
  const desiredHeight = Math.min(360, (props.options.length + (props.allowAuto ? 1 : 0)) * 50 + 12);
  const below = window.innerHeight - rect.bottom - 12;
  const above = rect.top - 12;
  const opensBelow = below >= Math.min(desiredHeight, 220) || below >= above;
  const availableHeight = Math.max(120, opensBelow ? below : above);
  const width = Math.max(220, rect.width);
  const left = Math.min(Math.max(12, rect.left), window.innerWidth - width - 12);
  menuStyle.value = {
    left: `${left}px`,
    top: opensBelow ? `${rect.bottom + 6}px` : "auto",
    bottom: opensBelow ? "auto" : `${window.innerHeight - rect.top + 6}px`,
    width: `${width}px`,
    maxHeight: `${Math.min(desiredHeight, availableHeight)}px`,
  };
}

async function openMenu() {
  if (props.disabled || props.pending || open.value) return;
  open.value = true;
  await nextTick();
  positionMenu();
  menuRef.value?.querySelector<HTMLButtonElement>(`[data-language-code="${props.modelValue}"]`)?.focus();
}

function closeMenu(restoreFocus = false) {
  open.value = false;
  if (restoreFocus) nextTick(() => triggerRef.value?.focus());
}

function toggleMenu() {
  if (open.value) closeMenu();
  else void openMenu();
}

function selectLanguage(code: string) {
  closeMenu(true);
  if (code !== props.modelValue) emit("change", code);
}

function focusRelative(offset: number) {
  const options = Array.from(menuRef.value?.querySelectorAll<HTMLButtonElement>(".language-option") ?? []);
  if (!options.length) return;
  const current = options.indexOf(document.activeElement as HTMLButtonElement);
  options[(current + offset + options.length) % options.length]?.focus();
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
