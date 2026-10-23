import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useChatStore } from "@/stores/chat";
import { useToastState } from "@/composables/useToast";
import { ApiError } from "@/api/client";
import type { StreamHandlers } from "@/api/sse";
import * as sse from "@/api/sse";
import { calls, installFetch, jsonRes } from "./helpers/api";

type Impl = (path: string, body: unknown, h: StreamHandlers, signal: AbortSignal) => Promise<void>;

const DONE = { messageId: "m1", citationCount: 0, isNotFound: false, notFoundReason: null, notice: null, stopped: false };
const STATUS = { stage: "searching" as const, docCount: 3, messageId: "m1", scopeRemoved: [] as string[] };

function mockStream(impl: Impl) {
  return vi.spyOn(sse, "streamPost").mockImplementation(impl);
}

describe("chat store", () => {
  beforeEach(() => {
    sessionStorage.clear();
    setActivePinia(createPinia());
    useToastState().items.splice(0);
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("send_creates_session_once", async () => {
    const fetchMock = installFetch({
      "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1", title: null, createdAt: "x" }),
    });
    const stream = mockStream(async (_p, _b, h) => h.onDone(DONE));
    const chat = useChatStore();
    await chat.send("câu 1");
    await chat.send("câu 2");
    expect(calls(fetchMock).filter((c) => c === "POST /api/v1/chat/sessions")).toHaveLength(1);
    expect(stream).toHaveBeenCalledTimes(2);
    expect(stream.mock.calls[0]![0]).toBe("/api/v1/chat/sessions/s1/messages");
    expect(stream.mock.calls[1]![1]).toEqual({ text: "câu 2", scopeDocIds: [] });
    expect(chat.messages).toHaveLength(4);
  });

  it("stream_updates_message", async () => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    const seen: string[] = [];
    const chat = useChatStore();
    mockStream(async (_p, _b, h) => {
      const ai = () => chat.messages[chat.messages.length - 1]!;
      seen.push(ai().state);
      h.onStatus(STATUS);
      seen.push(ai().state);
      h.onCitation({ index: 1, docId: "d1", docName: "HD_ABC_2026.pdf", page: 12, snippet: "…" });
      h.onToken({ text: "Thời hạn " });
      seen.push(ai().state);
      h.onToken({ text: "24 tháng [[1]]" });
      h.onDone({ ...DONE, citationCount: 1 });
    });
    await chat.send("Thời hạn?");
    const ai = chat.messages[1]!;
    expect(seen).toEqual(["SUBMITTING", "SEARCHING", "STREAMING"]);
    expect(ai).toMatchObject({ state: "COMPLETED", messageId: "m1", docCount: 3, text: "Thời hạn 24 tháng [[1]]" });
    expect(ai.citations).toHaveLength(1);
    expect(ai.citations[0]).toMatchObject({ docName: "HD_ABC_2026.pdf", page: 12, deleted: false });
    expect(chat.busy).toBe(false);
    expect(chat.messages[0]).toMatchObject({ role: "user", text: "Thời hạn?" });
    expect(chat.draft).toBe("");
  });

  it.each([
    [{ isNotFound: true, notFoundReason: "NO_EVIDENCE" as const }, "NOT_FOUND"],
    [{ stopped: true }, "STOPPED"],
    [{ notice: "LANG_UNSUPPORTED" as const }, "COMPLETED"],
  ])("done_maps_state %j", async (extra, state) => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    mockStream(async (_p, _b, h) => h.onDone({ ...DONE, ...extra }));
    const chat = useChatStore();
    await chat.send("q");
    expect(chat.messages[1]!.state).toBe(state);
    expect(chat.messages[1]!.notice ?? null).toBe((extra as { notice?: string }).notice ?? null);
  });

  it("error_and_interrupt_states", async () => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    const chat = useChatStore();
    mockStream(async (_p, _b, h) => h.onError({ code: "AI_UNAVAILABLE", retryable: true }));
    await chat.send("q1");
    expect(chat.messages[1]).toMatchObject({ state: "FAILED", errorCode: "AI_UNAVAILABLE" });
    mockStream(async (_p, _b, h) => {
      h.onToken({ text: "dở" });
      h.onInterrupted();
    });
    await chat.send("q2");
    expect(chat.messages[3]).toMatchObject({ state: "INTERRUPTED", text: "dở" });
    expect(chat.busy).toBe(false);
  });

  it("stop_calls_api09", async () => {
    vi.useFakeTimers();
    const fetchMock = installFetch({
      "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }),
      "POST /api/v1/chat/messages/m1/stop": () => jsonRes(200, { messageId: "m1", status: "STOPPED" }),
    });
    let aborted = false;
    const chat = useChatStore();
    mockStream(
      (_p, _b, h, signal) =>
        new Promise<void>((resolve) => {
          h.onStatus(STATUS);
          h.onToken({ text: "a" });
          signal.addEventListener("abort", () => {
            aborted = true;
            resolve();
          });
        }),
    );
    const sending = chat.send("q");
    await vi.advanceTimersByTimeAsync(0);
    expect(chat.messages[1]!.state).toBe("STREAMING");
    await chat.stop();
    expect(calls(fetchMock)).toContain("POST /api/v1/chat/messages/m1/stop");
    expect(chat.busy).toBe(true);
    await vi.advanceTimersByTimeAsync(2000);
    expect(aborted).toBe(true);
    expect(chat.messages[1]!.state).toBe("STOPPED");
    expect(chat.busy).toBe(false);
    await sending;
  });

  it("stop_before_status_aborts_locally", async () => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    const chat = useChatStore();
    mockStream((_p, _b, _h, signal) => new Promise<void>((resolve) => signal.addEventListener("abort", () => resolve())));
    const sending = chat.send("q");
    await vi.waitFor(() => expect(chat.messages[1]!.state).toBe("SUBMITTING"));
    await chat.stop();
    await sending;
    expect(chat.messages[1]!.state).toBe("STOPPED");
    expect(chat.busy).toBe(false);
  });

  it("question_in_progress_toast", async () => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    mockStream(async () => {
      throw new ApiError("QUESTION_IN_PROGRESS", true, 409);
    });
    const chat = useChatStore();
    await chat.send("hỏi");
    expect(useToastState().items.map((i) => i.text)).toEqual([
      "Đang trả lời câu hỏi trước. Hãy chờ hoặc bấm Dừng.",
    ]);
    expect(chat.messages).toHaveLength(0);
    expect(chat.draft).toBe("hỏi");
    expect(chat.busy).toBe(false);
  });

  it("other_api_error_marks_failed", async () => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    mockStream(async () => {
      throw new ApiError("QUESTION_TOO_LONG", false, 400);
    });
    const chat = useChatStore();
    await chat.send("hỏi");
    expect(chat.messages[1]).toMatchObject({ state: "FAILED", errorCode: "QUESTION_TOO_LONG" });
  });

  it("session_creation_failure_marks_failed", async () => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(503, { code: "AI_UNAVAILABLE", retryable: true }) });
    const stream = mockStream(async () => {});
    const chat = useChatStore();
    await chat.send("hỏi");
    expect(stream).not.toHaveBeenCalled();
    expect(chat.messages[1]).toMatchObject({ state: "FAILED", errorCode: "AI_UNAVAILABLE" });
  });

  it("client_timeout_after_65s", async () => {
    vi.useFakeTimers();
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    const chat = useChatStore();
    mockStream((_p, _b, _h, signal) => new Promise<void>((resolve) => signal.addEventListener("abort", () => resolve())));
    const sending = chat.send("q");
    await vi.advanceTimersByTimeAsync(64_000);
    expect(chat.busy).toBe(true);
    await vi.advanceTimersByTimeAsync(1_500);
    expect(chat.messages[1]).toMatchObject({ state: "FAILED", errorCode: "TIMEOUT" });
    expect(chat.busy).toBe(false);
    await sending;
  });

  it("scope_removed_updates_scope_and_toasts", async () => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    mockStream(async (_p, body, h) => {
      expect((body as { scopeDocIds: string[] }).scopeDocIds).toEqual(["A", "B"]);
      h.onStatus({ ...STATUS, scopeRemoved: ["B"] });
      h.onDone(DONE);
    });
    const chat = useChatStore();
    chat.scope = ["A", "B"];
    await chat.send("q");
    expect(chat.scope).toEqual(["A"]);
    expect(useToastState().items.map((i) => i.text)).toContain(
      "Một tài liệu trong phạm vi đã bị xóa và được bỏ khỏi phạm vi.",
    );
  });

  it("ignores_send_while_busy_or_blank", async () => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    const stream = mockStream(async (_p, _b, h) => h.onDone(DONE));
    const chat = useChatStore();
    await chat.send("   ");
    expect(stream).not.toHaveBeenCalled();
    chat.busy = true;
    await chat.send("q");
    expect(stream).not.toHaveBeenCalled();
  });

  it("new_session_clears_everything", async () => {
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    mockStream(async (_p, _b, h) => h.onDone(DONE));
    const chat = useChatStore();
    await chat.send("q");
    chat.newSession();
    expect(chat.sessionId).toBeNull();
    expect(chat.messages).toEqual([]);
  });

  it("open_maps_session_detail", async () => {
    installFetch({
      "GET /api/v1/chat/sessions/s9": () =>
        jsonRes(200, {
          sessionId: "s9", title: "t", createdAt: "2026-10-19T02:12:00Z", scopeDocIds: ["d1"],
          messages: [
            { messageId: "u1", role: "user", text: "q", status: "COMPLETED", createdAt: "2026-10-19T02:12:00Z", isNotFound: false, citations: [], rating: null },
            {
              messageId: "a1", role: "assistant", text: "Có [[1]]", status: "COMPLETED", createdAt: "2026-10-19T02:12:05Z", isNotFound: false,
              citations: [{ index: 1, docId: "d1", docName: "A.pdf", page: 2, snippet: "s", deleted: true }], rating: "UP",
            },
            { messageId: "a2", role: "assistant", text: "dở", status: "STREAMING", createdAt: "2026-10-19T02:13:00Z", isNotFound: false, citations: [], rating: null },
          ],
        }),
    });
    const chat = useChatStore();
    await chat.open("s9");
    expect(chat.sessionId).toBe("s9");
    expect(chat.scope).toEqual(["d1"]);
    expect(chat.messages.map((m) => m.state)).toEqual(["COMPLETED", "COMPLETED", "INTERRUPTED"]);
    expect(chat.messages[1]!.citations[0]!.deleted).toBe(true);
    expect(chat.messages[1]!.rating).toBe("UP");
  });

  it("open_failure_toasts_and_resets", async () => {
    installFetch({ "GET /api/v1/chat/sessions/zz": () => jsonRes(404, { code: "SESSION_NOT_FOUND", retryable: false }) });
    const chat = useChatStore();
    await chat.open("zz");
    expect(chat.sessionId).toBeNull();
    expect(useToastState().items[0]!.text).toBe("Không tìm thấy phiên hội thoại.");
  });
});
