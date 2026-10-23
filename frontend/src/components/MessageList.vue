<script setup lang="ts">
// Danh sách tin nhắn (CMP-04/06): người dùng căn phải, trợ lý căn trái; chỉ thông báo cho trình đọc màn hình khi câu trả lời xong.
import { nextTick, onMounted, ref, watch } from "vue";
import type { CitationOut, UiMessage, UiMessageState } from "@/api/types";
import { t } from "@/content/messages";
import AnswerBlock from "./AnswerBlock.vue";
import AnswerState from "./AnswerState.vue";

const props = defineProps<{ messages: UiMessage[] }>();
const emit = defineEmits<{ openCitation: [messageId: string, c: CitationOut]; retry: [id: string]; stop: [] }>();

const scroller = ref<HTMLElement | null>(null);
const announcement = ref("");
let stick = true; // người dùng đang ở cuối danh sách

const IN_PROGRESS: UiMessageState[] = ["SUBMITTING", "SEARCHING", "STREAMING"];
const FINISHED: UiMessageState[] = ["COMPLETED", "NOT_FOUND"];

function onScroll() {
  const el = scroller.value;
  if (el) stick = el.scrollHeight - el.scrollTop - el.clientHeight < 48;
}

function scrollToEnd() {
  const el = scroller.value;
  if (el) el.scrollTop = el.scrollHeight;
}

// Thông báo một lần khi một câu trả lời chuyển từ đang xử lý sang xong (không đọc từng chữ).
watch(
  () => props.messages.map((m) => m.state),
  async (now, before) => {
    const done = now.some((s, i) => FINISHED.includes(s) && before?.[i] !== undefined && IN_PROGRESS.includes(before[i]!));
    if (!done) return;
    announcement.value = "";
    await nextTick();
    announcement.value = t("answer.done");
  },
);

watch(
  () => [props.messages.length, props.messages[props.messages.length - 1]?.text.length ?? 0],
  async () => {
    if (!stick) return;
    await nextTick();
    scrollToEnd();
  },
);

onMounted(scrollToEnd);
</script>

<template>
  <div ref="scroller" class="chat-scroll" data-testid="message-scroll" @scroll="onScroll">
    <div class="chat-inner">
      <slot name="before" />
      <div
        class="message-log"
        role="log"
        aria-live="off"
        :aria-label="t('chat.logAria')"
        data-testid="message-log"
      >
        <template v-for="m in messages" :key="m.id">
          <div v-if="m.role === 'user'" class="msg-user" data-testid="user-message">{{ m.text }}</div>
          <AnswerBlock
            v-else
            :message="m"
            @open="emit('openCitation', m.messageId ?? m.id, $event)"
          >
            <template #state><AnswerState :message="m" @retry="emit('retry', m.id)" @stop="emit('stop')" /></template>
            <template #actions><slot name="actions" :message="m" /></template>
          </AnswerBlock>
        </template>
      </div>
    </div>
    <div class="sr-only" aria-live="polite" data-testid="announcer">{{ announcement }}</div>
  </div>
</template>

<style scoped>
.message-log {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}
.msg-user {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
</style>
