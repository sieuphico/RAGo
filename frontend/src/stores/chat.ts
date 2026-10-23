import { ref, watch } from "vue";
import { defineStore } from "pinia";
import { ApiError, request } from "@/api/client";
import { messageFor } from "@/api/errors";
import { streamPost, type StreamHandlers } from "@/api/sse";
import type { SessionDetailOut, UiMessage, UiMessageState } from "@/api/types";
import { useToast } from "@/composables/useToast";
import { t } from "@/content/messages";
import { KEY_DRAFT, storageGet, storageRemove, storageSet } from "@/utils/storage";

/** Sau ngần này mili giây không có sự kiện kết thúc, giao diện tự đặt FAILED/TIMEOUT (T-525, dự phòng). */
export const CLIENT_TIMEOUT_MS = 65_000;
/** Sau khi gọi API-09 mà luồng chưa kết thúc: hủy luồng và đặt STOPPED (T-524). */
export const STOP_GRACE_MS = 2_000;

let localSeq = 0;
const localId = (): string => `local-${++localSeq}`;

function isUiState(s: string): s is UiMessageState {
  return ["SEARCHING", "STREAMING", "COMPLETED", "NOT_FOUND", "STOPPED", "INTERRUPTED", "FAILED"].includes(s);
}

export const useChatStore = defineStore("chat", () => {
  const sessionId = ref<string | null>(null);
  const messages = ref<UiMessage[]>([]);
  const draft = ref(storageGet(KEY_DRAFT) ?? "");
  const busy = ref(false);
  const scope = ref<string[]>([]);
  /** Đặt bởi màn hình chào (T-515) khi kho trống: vô hiệu ô nhập. */
  const libraryEmpty = ref(false);

  let controller: AbortController | null = null;
  let timeoutTimer: ReturnType<typeof setTimeout> | null = null;
  let stopTimer: ReturnType<typeof setTimeout> | null = null;

  watch(draft, (v) => {
    if (v) storageSet(KEY_DRAFT, v);
    else storageRemove(KEY_DRAFT);
  });

  function clearTimers(): void {
    if (timeoutTimer) clearTimeout(timeoutTimer);
    if (stopTimer) clearTimeout(stopTimer);
    timeoutTimer = stopTimer = null;
  }

  function lastAssistant(): UiMessage | undefined {
    for (let i = messages.value.length - 1; i >= 0; i--) {
      if (messages.value[i]!.role === "assistant") return messages.value[i];
    }
    return undefined;
  }

  function finish(m: UiMessage, state: UiMessageState, errorCode?: string): void {
    m.state = state;
    if (errorCode) m.errorCode = errorCode;
    busy.value = false;
    clearTimers();
  }

  async function ensureSession(): Promise<string> {
    if (sessionId.value) return sessionId.value;
    const created = await request<{ sessionId: string }>("/api/v1/chat/sessions", { method: "POST", body: {} });
    sessionId.value = created.sessionId;
    return created.sessionId;
  }

  async function send(raw: string): Promise<void> {
    const text = raw.trim();
    if (!text || busy.value) return;
    const now = Date.now();
    const user: UiMessage = { id: localId(), role: "user", text, state: "COMPLETED", citations: [], sentAt: now };
    const ai: UiMessage = { id: localId(), role: "assistant", text: "", state: "SUBMITTING", citations: [], sentAt: now };
    messages.value.push(user, ai);
    const target = messages.value[messages.value.length - 1]!; // bản phản ứng của `ai`
    busy.value = true;
    draft.value = "";
    controller = new AbortController();
    const myController = controller;

    timeoutTimer = setTimeout(() => {
      if (target.state === "SUBMITTING" || target.state === "SEARCHING") {
        myController.abort();
        finish(target, "FAILED", "TIMEOUT");
      }
    }, CLIENT_TIMEOUT_MS);

    const handlers: StreamHandlers = {
      onStatus(d) {
        target.state = "SEARCHING";
        target.messageId = d.messageId;
        target.docCount = d.docCount;
        if (d.scopeRemoved?.length) {
          scope.value = scope.value.filter((id) => !d.scopeRemoved.includes(id));
          useToast().show(t("scope.removed"));
        }
      },
      onCitation(d) {
        if (!target.citations.some((c) => c.index === d.index)) target.citations.push({ ...d, deleted: false });
      },
      onToken(d) {
        target.state = "STREAMING";
        target.text += d.text;
        if (timeoutTimer) {
          clearTimeout(timeoutTimer);
          timeoutTimer = null;
        }
      },
      onDone(d) {
        target.messageId = d.messageId;
        target.notFoundReason = d.notFoundReason;
        target.notice = d.notice;
        finish(target, d.stopped ? "STOPPED" : d.isNotFound ? "NOT_FOUND" : "COMPLETED");
      },
      onError(d) {
        finish(target, "FAILED", d.code);
      },
      onInterrupted() {
        finish(target, "INTERRUPTED");
      },
    };

    try {
      const sid = await ensureSession();
      if (myController.signal.aborted) return; // đã dừng/hết giờ trước khi mở luồng
      await streamPost(`/api/v1/chat/sessions/${sid}/messages`, { text, scopeDocIds: scope.value }, handlers, myController.signal);
    } catch (e) {
      const code = e instanceof ApiError ? e.code : "INTERNAL";
      if (code === "QUESTION_IN_PROGRESS") {
        useToast().show(messageFor(code), "error");
        messages.value = messages.value.filter((m) => m.id !== user.id && m.id !== ai.id);
        draft.value = text;
        busy.value = false;
        clearTimers();
      } else {
        finish(target, "FAILED", code);
      }
      return;
    }
    // Luồng kết thúc mà chưa có trạng thái cuối (ví dụ đã hủy): bảo đảm không kẹt `busy`.
    if (busy.value && controller === myController && myController.signal.aborted) busy.value = false;
  }

  async function stop(): Promise<void> {
    const m = lastAssistant();
    if (!m || !busy.value) return;
    const myController = controller;
    if (!m.messageId) {
      myController?.abort();
      finish(m, "STOPPED");
      return;
    }
    try {
      await request(`/api/v1/chat/messages/${m.messageId}/stop`, { method: "POST", body: {} });
    } catch {
      /* vẫn dừng ở phía giao diện sau thời gian chờ */
    }
    if (!busy.value) return;
    stopTimer = setTimeout(() => {
      if (busy.value && m.state !== "COMPLETED") {
        myController?.abort();
        finish(m, "STOPPED");
      }
    }, STOP_GRACE_MS);
  }

  /** Hỏi lại / Thử lại: bỏ cặp câu hỏi và câu trả lời lỗi rồi gửi lại cùng câu hỏi. */
  async function retry(assistantId: string): Promise<void> {
    if (busy.value) return;
    const i = messages.value.findIndex((m) => m.id === assistantId);
    const q = i > 0 ? messages.value[i - 1] : undefined;
    if (!q || q.role !== "user") return;
    messages.value.splice(i - 1, 2);
    await send(q.text);
  }

  function newSession(): void {
    controller?.abort();
    clearTimers();
    sessionId.value = null;
    messages.value = [];
    busy.value = false;
    scope.value = [];
  }

  /** Mở lại một phiên (API-10b) và chuyển tin nhắn sang `UiMessage`. */
  async function open(id: string): Promise<void> {
    controller?.abort();
    clearTimers();
    busy.value = false;
    try {
      const d = await request<SessionDetailOut>(`/api/v1/chat/sessions/${id}`);
      sessionId.value = d.sessionId;
      scope.value = d.scopeDocIds;
      messages.value = d.messages.map((m) => ({
        id: m.messageId,
        messageId: m.messageId,
        role: m.role,
        text: m.text,
        // Tin nhắn đang dở khi đã lưu coi như bị gián đoạn.
        state: m.role === "user" ? "COMPLETED" : isUiState(m.status) && m.status !== "SEARCHING" && m.status !== "STREAMING" ? m.status : "INTERRUPTED",
        citations: m.citations,
        sentAt: Date.parse(m.createdAt),
        rating: m.rating,
        notFoundReason: m.isNotFound ? "NO_EVIDENCE" : null,
      }));
    } catch (e) {
      const code = e instanceof ApiError ? e.code : "INTERNAL";
      useToast().show(messageFor(code), "error");
      newSession();
    }
  }

  return { sessionId, messages, draft, busy, scope, libraryEmpty, send, stop, retry, newSession, open };
});
