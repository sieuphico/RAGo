<script setup lang="ts">
// Biểu tượng SVG nội tuyến, chép từ prototype (assets/app.js). Luôn aria-hidden: nhãn chữ đi kèm ở nơi dùng.
import type { IconName } from "./icons";
defineProps<{ name: IconName }>();
</script>

<template>
  <svg
    v-if="name === 'stop'" class="icon" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true" width="14" height="14"
    data-icon="stop"
  ><rect x="3" y="3" width="10" height="10" rx="1.5" /></svg>
  <svg
    v-else class="icon" :class="{ spin: name === 'spin' || name === 'ocr' }" viewBox="0 0 16 16" fill="none" stroke="currentColor"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" :data-icon="name"
  >
    <path v-if="name === 'check'" d="M3 8.5l3.2 3L13 4.5" />
    <path v-else-if="name === 'x'" d="M4 4l8 8M12 4l-8 8" />
    <path v-else-if="name === 'up'" d="M8 13V3M4 7l4-4 4 4" />
    <path v-else-if="name === 'warn'" d="M8 2l6.5 11.5h-13zM8 6.5v3.2M8 11.6v.1" />
    <path v-else-if="name === 'spin'" d="M8 2a6 6 0 1 0 6 6" />
    <template v-else-if="name === 'ocr'"><path d="M8 2a6 6 0 1 0 6 6" /><path d="M5.5 8h5M8 5.5v5" stroke-width="1.4" /></template>
    <template v-else-if="name === 'search'"><circle cx="7" cy="7" r="4.5" /><path d="M10.5 10.5L14 14" /></template>
    <template v-else-if="name === 'copy'"><rect x="5.5" y="5.5" width="8" height="8" rx="1.5" /><path d="M10.5 3.5v-.5a1 1 0 0 0-1-1h-6a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h.5" /></template>
    <path v-else-if="name === 'thumbUp'" d="M5 7.5V14H3V7.5zM5 7.5l3-5.5c1.2 0 1.8 1 1.5 2l-.5 2.5h3.2a1.3 1.3 0 0 1 1.3 1.6l-.9 4A1.5 1.5 0 0 1 11.1 14H5" stroke-width="1.6" />
    <path v-else-if="name === 'thumbDown'" d="M5 8.5V2H3v6.5zM5 8.5l3 5.5c1.2 0 1.8-1 1.5-2l-.5-2.5h3.2a1.3 1.3 0 0 0 1.3-1.6l-.9-4A1.5 1.5 0 0 0 11.1 2H5" stroke-width="1.6" />
    <path v-else-if="name === 'trash'" d="M3 4.5h10M6.5 4.5V3h3v1.5M4.5 4.5l.6 8.5h5.8l.6-8.5" stroke-width="1.5" />
  </svg>
</template>

<style scoped>
.icon {
  width: 14px;
  height: 14px;
  flex: none;
}
</style>
