<script setup lang="ts">
import { useBannerState } from "@/composables/useBanner";

const state = useBannerState();
</script>

<template>
  <div v-if="state.text" class="banner" role="alert" data-testid="banner">
    <span aria-hidden="true">⚠</span> {{ state.text }}
  </div>
</template>
