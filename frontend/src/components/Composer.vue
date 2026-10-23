<script setup lang="ts">
// Ô nhập câu hỏi (CMP-05): Enter gửi, Shift+Enter xuống dòng, "/" focus ô nhập, bộ đếm, bản nháp, mất mạng.
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { t } from "@/content/messages";
import { useOnline } from "@/composables/useOnline";
import { useChatStore } from "@/stores/chat";
import { formatInt } from "@/utils/format";
import IconGlyph from "./IconGlyph.vue";

const emit = defineEmits<{ submit: [text: string]; stop: [] }>();

const MAX_CHARS = 2000;
const chat = useChatStore();
const { online } = useOnline();
const input = ref<HTMLTextAreaElement | null>(null);

const length = computed(() => chat.draft.length);
const trimmedLength = computed(() => chat.draft.trim().length);
const overLimit = computed(() => trimmedLength.value > MAX_CHARS);
const canSend = computed(
  () => trimmedLength.value > 0 && !overLimit.value && online.value && !chat.libraryEmpty && !chat.busy,
);

function submit() {
  if (!canSend.value) return;
  emit("submit", chat.draft.trim());
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    submit();
  }
}

function onGlobalKey(e: KeyboardEvent) {
  if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
  const el = document.activeElement;
  const typing =
    el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement || el instanceof HTMLSelectElement ||
    (el instanceof HTMLElement && el.isContentEditable);
  if (typing) return;
  e.preventDefault();
  input.value?.focus();
}

onMounted(() => document.addEventListener("keydown", onGlobalKey));
onBeforeUnmount(() => document.removeEventListener("keydown", onGlobalKey));

defineExpose({ focus: () => input.value?.focus() });
</script>

<template>
  <div class="composer">
    <div v-if="!online" class="banner" role="alert" data-testid="offline-banner">
      <span aria-hidden="true">⚠</span> {{ t("net.offline") }}
    </div>
    <div class="composer-box">
      <label for="composer-input" class="sr-only">{{ t("composer.label") }}</label>
      <textarea
        id="composer-input"
        ref="input"
        v-model="chat.draft"
        rows="2"
        :placeholder="t('composer.placeholder')"
        :disabled="chat.libraryEmpty"
        aria-describedby="composer-note composer-counter"
        data-testid="composer-input"
        @keydown="onKeydown"
      ></textarea>
      <div class="composer-bar">
        <div class="bar-start"><slot name="bar-start" /></div>
        <div class="bar-end">
          <span id="composer-counter" class="counter" :class="{ 'is-over': length > MAX_CHARS }" data-testid="counter">{{
            t("composer.counter", { n: formatInt(length) })
          }}</span>
          <button v-if="chat.busy" type="button" class="btn" data-testid="stop" @click="emit('stop')">
            <IconGlyph name="stop" /> {{ t("composer.stop") }}
          </button>
          <button v-else type="button" class="btn btn-primary" :disabled="!canSend" data-testid="send" @click="submit">
            {{ t("composer.send") }}
          </button>
        </div>
      </div>
    </div>
    <p id="composer-note" class="ai-note" data-testid="disclaimer">{{ t("composer.disclaimer") }}</p>
  </div>
</template>

<style scoped>
.bar-end {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
</style>
