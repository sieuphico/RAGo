<script setup lang="ts">
// Hộp thoại lý do cho 👎 (Blueprint 4.5): chọn một trong 4 lý do có sẵn (không có ô nhập tự do: telemetry cấm văn bản tự do).
import { ref, watch } from "vue";
import { M, t } from "@/content/messages";
import ConfirmDialog from "./ConfirmDialog.vue";

export type ReasonCode = "WRONG_INFO" | "WRONG_CITATION" | "MISSING_INFO" | "OTHER";
const REASONS: ReasonCode[] = ["WRONG_INFO", "WRONG_CITATION", "MISSING_INFO", "OTHER"];

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{ submit: [reason: ReasonCode | null]; skip: [] }>();

const reason = ref<ReasonCode | null>(null);
watch(
  () => props.open,
  (o) => {
    if (o) reason.value = null;
  },
);
</script>

<template>
  <ConfirmDialog
    :open="open"
    :title="t('rating.title')"
    :confirm-label="t('rating.send')"
    :cancel-label="t('rating.skip')"
    @confirm="emit('submit', reason)"
    @cancel="emit('skip')"
  >
    <fieldset class="radio-row" data-testid="rating-reasons">
      <label v-for="r in REASONS" :key="r">
        <input v-model="reason" type="radio" name="rating-reason" :value="r" :data-testid="`reason-${r}`" />
        {{ M[`rating.${r}`] }}
      </label>
    </fieldset>
  </ConfirmDialog>
</template>

<style scoped>
fieldset {
  border: 0;
  padding: 0;
  margin: 0;
}
</style>
