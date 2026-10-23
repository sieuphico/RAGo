<script setup lang="ts">
// Trạng thái của một câu trả lời (Blueprint 3.5.2): đang tìm, chậm, không tìm thấy, đã dừng, mất kết nối, lỗi, ghi chú ngôn ngữ.
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { messageFor } from "@/api/errors";
import type { UiMessage } from "@/api/types";
import { t } from "@/content/messages";
import IconGlyph from "./IconGlyph.vue";

const SLOW_MS = 15_000; // EC-06
const TIMEOUT_MS = 65_000; // dự phòng khi máy chủ không gửi sự kiện kết thúc `[Đề xuất]`

const props = defineProps<{ message: UiMessage }>();
const emit = defineEmits<{ retry: []; stop: [] }>();

const slow = ref(false);
const timedOut = ref(false);
let slowTimer: ReturnType<typeof setTimeout> | null = null;
let timeoutTimer: ReturnType<typeof setTimeout> | null = null;

function clear() {
  if (slowTimer) clearTimeout(slowTimer);
  if (timeoutTimer) clearTimeout(timeoutTimer);
  slowTimer = timeoutTimer = null;
}

const waiting = computed(() => props.message.state === "SUBMITTING" || props.message.state === "SEARCHING");

watch(
  waiting,
  (isWaiting) => {
    clear();
    if (!isWaiting) {
      slow.value = false;
      return;
    }
    slowTimer = setTimeout(() => (slow.value = true), SLOW_MS);
    timeoutTimer = setTimeout(() => (timedOut.value = true), TIMEOUT_MS);
  },
  { immediate: true },
);
onBeforeUnmount(clear);

const showTimeout = computed(() => timedOut.value && waiting.value);
const failedCode = computed(() => (showTimeout.value ? "TIMEOUT" : (props.message.errorCode ?? "INTERNAL")));
const searchingText = computed(() =>
  props.message.docCount === undefined ? t("answer.searchingNoCount") : t("answer.searching", { N: props.message.docCount }),
);
const notFoundNoDocs = computed(() => props.message.notFoundReason === "NO_READY_DOCS");
</script>

<template>
  <div class="answer-state" data-testid="answer-state" :data-state="showTimeout ? 'FAILED' : message.state">
    <!-- Đang tìm -->
    <template v-if="waiting && !showTimeout">
      <div class="msg-searching" role="status" data-testid="searching">
        <IconGlyph name="spin" />
        <span>{{ searchingText }}</span>
        <span v-if="slow" data-testid="slow-notice">{{ t("answer.slow") }}</span>
        <button type="button" class="btn btn-sm" data-testid="state-stop" @click="emit('stop')">
          <IconGlyph name="stop" /> {{ t("composer.stop") }}
        </button>
      </div>
    </template>

    <!-- Không tìm thấy: nền trung tính, không dùng màu lỗi (DD-03) -->
    <div v-else-if="message.state === 'NOT_FOUND'" class="msg-not-found" data-testid="not-found">
      <template v-if="notFoundNoDocs">
        <strong><IconGlyph name="search" /> {{ t("answer.noReadyDocs") }}</strong>
      </template>
      <template v-else>
        <strong><IconGlyph name="search" /> {{ t("answer.notFound") }}</strong>
        <span>{{ t("answer.notFoundHint") }}</span>
      </template>
    </div>

    <!-- Đã dừng -->
    <div v-else-if="message.state === 'STOPPED'" class="msg-notice is-neutral" data-testid="stopped">
      <span>{{ t("answer.stopped") }}</span>
      <button type="button" class="btn btn-sm" data-testid="ask-again" @click="emit('retry')">{{ t("action.askAgain") }}</button>
    </div>

    <!-- Mất kết nối giữa chừng: giữ phần đã nhận -->
    <div v-else-if="message.state === 'INTERRUPTED'" class="msg-notice is-warning" role="alert" data-testid="interrupted">
      <span><IconGlyph name="warn" /> {{ t("answer.interrupted") }}</span>
      <button type="button" class="btn btn-sm" data-testid="ask-again" @click="emit('retry')">{{ t("action.askAgain") }}</button>
    </div>

    <!-- Lỗi: thông báo theo mã, không bao giờ hiện mã -->
    <div v-else-if="message.state === 'FAILED' || showTimeout" class="msg-notice is-danger" role="alert" data-testid="failed">
      <span><IconGlyph name="warn" /> {{ messageFor(failedCode) }}</span>
      <button type="button" class="btn btn-sm" data-testid="retry" @click="emit('retry')">{{ t("action.retry") }}</button>
    </div>

    <p v-if="message.notice === 'LANG_UNSUPPORTED'" class="caption muted" data-testid="lang-notice">
      {{ t("answer.langNotice") }}
    </p>
  </div>
</template>

<style scoped>
.answer-state {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.answer-state:empty {
  display: none;
}
.msg-not-found strong {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
</style>
