<script setup lang="ts">
withDefaults(defineProps<{ rows?: number; label?: string }>(), { rows: 5, label: undefined });
</script>

<template>
  <section aria-busy="true" :aria-label="label" data-testid="skeleton">
    <div v-for="n in rows" :key="n" class="skeleton skeleton-row"></div>
  </section>
</template>
