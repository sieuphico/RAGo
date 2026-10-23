<script setup lang="ts">
// Khung xem nguồn (S-05, CMP-09): trình xem PDF của trình duyệt qua <iframe> (AD-07). Dưới 1280 px là lớp phủ hộp thoại.
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useViewport } from "@/composables/useViewport";
import { t } from "@/content/messages";
import { truncateMiddle } from "@/utils/format";
import IconGlyph from "./IconGlyph.vue";

const props = defineProps<{ docId: string; docName: string; page: number; pageCount?: number | null }>();
const emit = defineEmits<{ close: []; page: [n: number] }>();

const route = useRoute();
const router = useRouter();
const { width } = useViewport();

type Phase = "loading" | "ready" | "deleted" | "error";
const phase = ref<Phase>("loading");
const current = ref(props.page);
const root = ref<HTMLElement | null>(null);
const closeBtn = ref<HTMLButtonElement | null>(null);
const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null; // thẻ trích dẫn đã mở khung

const overlay = computed(() => width.value < 1280);
const fileUrl = computed(() => `/api/v1/documents/${encodeURIComponent(props.docId)}/file`);
const src = computed(() => `${fileUrl.value}#page=${current.value}`);
const iframeTitle = computed(() => t("viewer.iframeTitle", { "tên tài liệu": props.docName, N: current.value }));
const pageLabel = computed(() =>
  props.pageCount ? t("viewer.pageOf", { page: current.value, pageCount: props.pageCount }) : t("viewer.pageOnly", { page: current.value }),
);
const canPrev = computed(() => current.value > 1);
const canNext = computed(() => !props.pageCount || current.value < props.pageCount);

// Kiểm tra tệp còn tồn tại trước khi gắn iframe: yêu cầu 1 byte đầu (API-06).
let checkSeq = 0;
async function check() {
  const seq = ++checkSeq;
  phase.value = "loading";
  try {
    const res = await fetch(fileUrl.value, { headers: { Range: "bytes=0-0" }, credentials: "same-origin" });
    if (seq !== checkSeq) return;
    if (res.status === 404) phase.value = "deleted";
    else phase.value = res.ok ? "ready" : "error";
  } catch {
    if (seq === checkSeq) phase.value = "error";
  }
}

watch(() => props.docId, check);
watch(
  () => props.page,
  (p) => (current.value = p),
);

function goto(n: number) {
  if (n < 1 || (props.pageCount && n > props.pageCount)) return;
  current.value = n;
  emit("page", n);
  void router.replace({ query: { ...route.query, page: String(n) } });
}

function close() {
  const query = { ...route.query };
  delete query.doc;
  delete query.page;
  void router.replace({ query });
  emit("close");
  void nextTick(() => {
    if (opener && opener.isConnected) opener.focus();
  });
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") {
    e.preventDefault();
    close();
    return;
  }
  // Giam focus trong lớp phủ (EC-19).
  if (e.key === "Tab" && overlay.value && root.value) {
    const items = Array.from(
      root.value.querySelectorAll<HTMLElement>("button:not([disabled]), iframe, [href], [tabindex]:not([tabindex='-1'])"),
    );
    if (items.length === 0) return;
    const first = items[0]!;
    const last = items[items.length - 1]!;
    const active = document.activeElement;
    if (e.shiftKey && (active === first || !root.value.contains(active))) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && (active === last || !root.value.contains(active))) {
      e.preventDefault();
      first.focus();
    }
  }
}

onMounted(() => {
  document.addEventListener("keydown", onKeydown);
  void check();
  if (overlay.value) void nextTick(() => closeBtn.value?.focus());
});
onBeforeUnmount(() => document.removeEventListener("keydown", onKeydown));
</script>

<template>
  <section
    ref="root"
    class="viewer"
    :role="overlay ? 'dialog' : 'region'"
    :aria-modal="overlay ? 'true' : undefined"
    :aria-label="t('viewer.title')"
    data-testid="source-viewer"
  >
    <div class="viewer-head">
      <span class="doc-title" :title="docName" data-testid="viewer-name">{{ truncateMiddle(docName, 40) }}</span>
      <button
        ref="closeBtn"
        type="button"
        class="btn btn-ghost btn-icon"
        :aria-label="t('viewer.close')"
        data-testid="viewer-close"
        @click="close"
      >
        <IconGlyph name="x" />
      </button>
    </div>
    <div class="viewer-nav">
      <button
        type="button"
        class="btn btn-sm btn-icon"
        :aria-label="t('viewer.prev')"
        :disabled="!canPrev"
        data-testid="viewer-prev"
        @click="goto(current - 1)"
      >
        ◀
      </button>
      <span aria-live="polite" data-testid="viewer-page">{{ pageLabel }}</span>
      <button
        type="button"
        class="btn btn-sm btn-icon"
        :aria-label="t('viewer.next')"
        :disabled="!canNext"
        data-testid="viewer-next"
        @click="goto(current + 1)"
      >
        ▶
      </button>
    </div>
    <div class="viewer-body">
      <p v-if="phase === 'loading'" class="muted" role="status" data-testid="viewer-loading">
        <IconGlyph name="spin" /> {{ t("viewer.loading") }}
      </p>
      <p v-else-if="phase === 'deleted'" class="muted" data-testid="viewer-deleted">{{ t("citation.deleted") }}</p>
      <div v-else-if="phase === 'error'" class="state-box is-error" role="alert" data-testid="viewer-error">
        <strong>{{ t("viewer.error") }}</strong>
        <button type="button" class="btn" data-testid="viewer-retry" @click="check">{{ t("action.retry") }}</button>
      </div>
      <iframe v-else class="pdf-frame" :src="src" :title="iframeTitle" data-testid="viewer-iframe"></iframe>
    </div>
  </section>
</template>

<style scoped>
.viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
  overflow: hidden;
  background: var(--color-surface);
}
.viewer-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-divider);
  background: var(--color-white);
}
.doc-title {
  flex: 1;
  min-width: 0;
  font-weight: 600;
  font-size: var(--font-caption);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.viewer-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-2);
  font-size: var(--font-caption);
}
.viewer-body {
  flex: 1;
  min-height: 0;
  display: flex;
  justify-content: center;
  align-items: stretch;
  padding: var(--space-2);
}
.viewer-body > p,
.viewer-body > .state-box {
  align-self: flex-start;
}
.pdf-frame {
  width: 100%;
  height: 100%;
  border: 0;
  background: var(--color-white);
}
</style>
