<template>
  <OverlayLauncher v-if="activeView === 'overlay'" />
  <TranslatorView v-else-if="activeView === 'translator'" />
  <SettingsView v-else />
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import OverlayLauncher from "./OverlayLauncher.vue";
import SettingsView from "./SettingsView.vue";
import TranslatorView from "./TranslatorView.vue";

const currentSearch = ref(window.location.search);

const activeView = computed(() => {
  const params = new URLSearchParams(currentSearch.value);
  const view = params.get("view");
  if (view === "translator" || view === "settings") {
    return view;
  }

  return "overlay";
});

function syncCurrentSearch() {
  currentSearch.value = window.location.search;
}

onMounted(() => {
  window.addEventListener("popstate", syncCurrentSearch);
});

onUnmounted(() => {
  window.removeEventListener("popstate", syncCurrentSearch);
});
</script>
