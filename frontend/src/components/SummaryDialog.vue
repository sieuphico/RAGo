<script setup lang="ts">
// Hộp thoại tóm tắt tài liệu (CMP, US-040). P1 (cờ `summary`). Bản tóm tắt có thẻ trích dẫn bấm được.
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ApiError, request } from "@/api/client";
import { messageFor } from "@/api/errors";
import type { CitationOut, DocumentOut, SummaryOut, UiMessage } from "@/api/types";
import { t } from "@/content/messages";
import AnswerBlock from "./AnswerBlock.vue";
import ConfirmDialog from "./ConfirmDialog.vue";
import IconGlyph from "./IconGlyph.vue";

const props = defineProps<{ doc: DocumentOut; open: boolean }>();
const emit = defineEmits<{ close: [] }>();

const router = useRouter();
const loading = ref(false);
const errorCode = ref<string | null>(null);
const result = ref<SummaryOut | null>(null);
let seq = 0;

const asMessage = computed<UiMessage | null>(() =>
  result.value
    ? { id: "summary", role: "assistant", text: result.value.text, state: "COMPLETED", citations: result.value.citations, sentAt: 0 }
    : null,
);

async function load() {
  const mine = ++seq;
  loading.value = true;
  errorCode.value = null;
  result.value = null;
  try {
    const data = await request<SummaryOut>(`/api/v1/documents/${encodeURIComponent(props.doc.docId)}/summary`, {
      method: "POST",
      body: {},
    });
    if (mine === seq) result.value = data;
  } catch (e) {
    if (mine === seq) errorCode.value = e instanceof ApiError ? e.code : "INTERNAL";
  } finally {
    if (mine === seq) loading.value = false;
  }
}

watch(
  () => props.open,
  (o) => {
    if (o) void load();
    else seq++; // bỏ kết quả đang về
  },
  { immediate: true },
);

function openCitation(c: CitationOut) {
  emit("close");
  void router.push({ path: "/", query: { doc: c.docId, page: String(c.page) } });
}
</script>

<template>
  <ConfirmDialog
    :open="open"
    :title="t('summary.title', { 'tên tài liệu': doc.name })"
    :confirm-label="t('summary.close')"
    :cancel-label="t('summary.close')"
    hide-confirm
    @cancel="emit('close')"
  >
    <div data-testid="summary-body" :aria-busy="loading">
      <p v-if="loading" class="muted" role="status" data-testid="summary-loading">
        <IconGlyph name="spin" /> {{ t("summary.loading") }}
      </p>
      <div v-else-if="errorCode" role="alert" class="summary-error" data-testid="summary-error">
        <p>{{ messageFor(errorCode) }}</p>
        <button type="button" class="btn btn-sm" data-testid="summary-retry" @click="load">{{ t("action.retry") }}</button>
      </div>
      <AnswerBlock v-else-if="asMessage" :message="asMessage" @open="openCitation" />
    </div>
  </ConfirmDialog>
</template>

<style scoped>
.summary-error {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  align-items: flex-start;
  color: var(--color-danger-text);
}
</style>
