<script setup lang="ts">
// Thao tác dưới câu trả lời (CMP-12): Sao chép kèm nguồn, 👍/👎 kèm lý do. P1 (cờ `copy`, `rating`).
import { computed, ref, watch } from "vue";
import { ApiError, request } from "@/api/client";
import { messageFor } from "@/api/errors";
import { track } from "@/api/telemetry";
import type { UiMessage } from "@/api/types";
import { useToast } from "@/composables/useToast";
import { t } from "@/content/messages";
import { useFeaturesStore } from "@/stores/features";
import { copyText } from "@/utils/answerText";
import IconGlyph from "./IconGlyph.vue";
import RatingDialog, { type ReasonCode } from "./RatingDialog.vue";

const props = defineProps<{ message: UiMessage }>();

const features = useFeaturesStore();
const toast = useToast();
const rating = ref<"UP" | "DOWN" | null>(props.message.rating ?? null);
const dialogOpen = ref(false);
watch(
  () => props.message.rating,
  (r) => (rating.value = r ?? null),
);

const showCopy = computed(() => features.flags.copy && props.message.state === "COMPLETED");
const showRate = computed(
  () =>
    features.flags.rating &&
    !!props.message.messageId &&
    (props.message.state === "COMPLETED" || props.message.state === "NOT_FOUND"),
);

function fallbackCopy(text: string): boolean {
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  let ok = false;
  try {
    ok = document.execCommand("copy");
  } catch {
    ok = false;
  }
  area.remove();
  return ok;
}

async function copy() {
  const text = copyText(props.message);
  let ok = false;
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      ok = true;
    } catch {
      ok = fallbackCopy(text);
    }
  } else {
    ok = fallbackCopy(text);
  }
  if (ok) {
    toast.show(t("copy.done"), "success");
    if (props.message.messageId) track("answer_copied", { question_id: props.message.messageId });
  }
}

async function rate(value: "UP" | "DOWN", reasonCode: ReasonCode | null) {
  const id = props.message.messageId;
  if (!id) return;
  try {
    await request(`/api/v1/chat/messages/${id}/rating`, { method: "POST", body: { value, reasonCode } });
    rating.value = value;
  } catch (e) {
    toast.show(messageFor(e instanceof ApiError ? e.code : "INTERNAL"), "error");
  }
}

function onDown() {
  dialogOpen.value = true;
}

async function onSubmit(reason: ReasonCode | null) {
  dialogOpen.value = false;
  await rate("DOWN", reason);
}

async function onSkip() {
  dialogOpen.value = false;
  await rate("DOWN", null);
}
</script>

<template>
  <div v-if="showCopy || showRate" class="answer-actions" data-testid="answer-actions">
    <button
      v-if="showCopy"
      type="button"
      class="btn btn-sm"
      :aria-label="t('actions.copyAria')"
      data-testid="copy"
      @click="copy"
    >
      <IconGlyph name="copy" /> {{ t("actions.copyLabel") }}
    </button>
    <template v-if="showRate">
      <button
        type="button"
        class="btn btn-sm btn-icon"
        :aria-label="t('actions.upAria')"
        :aria-pressed="rating === 'UP'"
        data-testid="rate-up"
        @click="rate('UP', null)"
      >
        <IconGlyph name="thumbUp" />
      </button>
      <button
        type="button"
        class="btn btn-sm btn-icon"
        :aria-label="t('actions.downAria')"
        :aria-pressed="rating === 'DOWN'"
        data-testid="rate-down"
        @click="onDown"
      >
        <IconGlyph name="thumbDown" />
      </button>
    </template>
    <RatingDialog :open="dialogOpen" @submit="onSubmit" @skip="onSkip" />
  </div>
</template>
