<script setup lang="ts">
import { dismissToast, useToastState } from "@/composables/useToast";
import { t } from "@/content/messages";
import IconGlyph from "./IconGlyph.vue";

const state = useToastState();
</script>

<template>
  <div class="toast-host" role="status" data-testid="toast-host">
    <div
      v-for="item in state.items"
      :key="item.id"
      class="toast"
      :class="{ 'is-error': item.kind === 'error' }"
      :role="item.kind === 'error' ? 'alert' : undefined"
      data-testid="toast"
    >
      <span>{{ item.text }}</span>
      <button
        v-if="item.kind === 'error'"
        type="button"
        class="btn btn-ghost btn-sm toast-close"
        :aria-label="t('toast.close')"
        @click="dismissToast(item.id)"
      >
        <IconGlyph name="x" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.toast-close {
  color: var(--color-on-primary);
}
</style>
