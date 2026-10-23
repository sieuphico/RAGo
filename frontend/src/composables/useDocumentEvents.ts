// Cập nhật trạng thái tài liệu theo thời gian thực qua EventSource (API-04, T-509), có phương án dự phòng hỏi lại API-03.
import { onBeforeUnmount, onMounted, ref, type Ref } from "vue";
import { messageFor } from "@/api/errors";
import type { DocumentStatusData } from "@/api/types";
import { t } from "@/content/messages";
import { useDocumentsStore } from "@/stores/documents";

export const EVENTS_URL = "/api/v1/documents/events";
export const POLL_MS = 3000;
export const SSE_RETRY_MS = 60_000;
export const SLOW_CHECK_MS = 60_000;
export const SLOW_OCR_MS = 15 * 60_000;

export function useDocumentEvents(): { mode: Ref<"sse" | "polling">; announcement: Ref<string> } {
  const docs = useDocumentsStore();
  const mode = ref<"sse" | "polling">("sse");
  const announcement = ref("");

  let es: EventSource | null = null;
  let errors = 0;
  let pollTimer: ReturnType<typeof setInterval> | null = null;
  let retryTimer: ReturnType<typeof setTimeout> | null = null;
  let slowTimer: ReturnType<typeof setInterval> | null = null;
  let disposed = false;

  function announce(text: string) {
    announcement.value = text;
  }

  function onStatus(e: MessageEvent) {
    let data: DocumentStatusData;
    try {
      data = JSON.parse(e.data as string) as DocumentStatusData;
    } catch {
      return;
    }
    const found = docs.items.find((d) => d.docId === data.docId);
    const before = found ? { name: found.name, status: found.status } : null; // trước khi áp dụng sự kiện
    docs.applyEvent(data);
    if (before && before.status !== data.status) {
      if (data.status === "READY") announce(t("docs.announceReady", { tên: before.name }));
      else if (data.status === "FAILED") {
        announce(t("docs.announceFailed", { tên: before.name, "lý do": messageFor(data.failureReason ?? "PROCESSING_ERROR") }));
      }
    }
  }

  function stopPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = null;
  }

  function openSse() {
    if (disposed) return;
    stopPolling();
    es = new EventSource(EVENTS_URL);
    es.onopen = () => {
      errors = 0;
      mode.value = "sse";
    };
    es.addEventListener("status", onStatus as EventListener);
    es.onerror = () => {
      errors += 1;
      if (errors >= 2) fallBack();
    };
  }

  function closeSse() {
    es?.close();
    es = null;
  }

  // SSE hỏng 2 lần liên tiếp: đóng, hỏi lại API-03 mỗi 3 giây, thử mở lại SSE sau 60 giây.
  function fallBack() {
    closeSse();
    mode.value = "polling";
    stopPolling();
    pollTimer = setInterval(() => void docs.fetch({ silent: true }), POLL_MS);
    if (retryTimer) clearTimeout(retryTimer);
    retryTimer = setTimeout(() => {
      errors = 0;
      openSse();
    }, SSE_RETRY_MS);
  }

  // OCR quá 15 phút: đánh dấu "Xử lý lâu bất thường" (EC-20).
  function checkSlow() {
    const now = Date.now();
    const slow = new Set<string>();
    for (const d of docs.items) {
      if (d.status === "OCR_PROCESSING" && now - Date.parse(d.uploadedAt) > SLOW_OCR_MS) slow.add(d.docId);
    }
    docs.slowIds = slow;
  }

  onMounted(() => {
    openSse();
    checkSlow();
    slowTimer = setInterval(checkSlow, SLOW_CHECK_MS);
  });

  onBeforeUnmount(() => {
    disposed = true;
    closeSse();
    stopPolling();
    if (retryTimer) clearTimeout(retryTimer);
    if (slowTimer) clearInterval(slowTimer);
    retryTimer = slowTimer = null;
  });

  return { mode, announcement };
}
