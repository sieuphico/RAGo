import { describe, it, expect, vi, afterEach } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import AnswerState from "@/components/AnswerState.vue";
import { useChatStore } from "@/stores/chat";
import type { UiMessage } from "@/api/types";
import { installFetch, jsonRes } from "./helpers/api";

const msg = (over: Partial<UiMessage>): UiMessage => ({
  id: "a1", role: "assistant", text: "", state: "SEARCHING", citations: [], sentAt: 0, ...over,
});
const view = (m: UiMessage) => mount(AnswerState, { props: { message: m } });

describe("AnswerState", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("searching_with_count", async () => {
    const w = view(msg({ docCount: 125 }));
    expect(w.text()).toContain("Đang tìm trong 125 tài liệu…");
    await w.get("[data-testid=state-stop]").trigger("click");
    expect(w.emitted("stop")).toHaveLength(1);
    expect(view(msg({ state: "SUBMITTING" })).text()).toContain("Đang tìm trong tài liệu…");
  });

  it("slow_notice_after_15s", async () => {
    vi.useFakeTimers();
    const w = view(msg({ docCount: 3 }));
    expect(w.find("[data-testid=slow-notice]").exists()).toBe(false);
    await vi.advanceTimersByTimeAsync(14_900);
    expect(w.find("[data-testid=slow-notice]").exists()).toBe(false);
    await vi.advanceTimersByTimeAsync(200);
    expect(w.get("[data-testid=slow-notice]").text()).toBe("Câu hỏi đang mất nhiều thời gian hơn bình thường…");
  });

  it("client_timeout_fallback", async () => {
    vi.useFakeTimers();
    const w = view(msg({}));
    await vi.advanceTimersByTimeAsync(65_000);
    expect(w.get("[data-testid=failed]").text()).toContain("Không thể trả lời lúc này.");
    await w.get("[data-testid=retry]").trigger("click");
    expect(w.emitted("retry")).toHaveLength(1);
  });

  it("timers_are_cleared_when_answer_arrives", async () => {
    vi.useFakeTimers();
    const w = view(msg({}));
    await w.setProps({ message: msg({ state: "STREAMING" }) });
    await vi.advanceTimersByTimeAsync(70_000);
    expect(w.find("[data-testid=failed]").exists()).toBe(false);
    w.unmount();
    expect(vi.getTimerCount()).toBe(0);
  });

  it("not_found_is_neutral", () => {
    const w = view(msg({ state: "NOT_FOUND", notFoundReason: "NO_EVIDENCE" }));
    const box = w.get("[data-testid=not-found]");
    expect(box.text()).toContain("Không tìm thấy thông tin này trong các tài liệu hiện có.");
    expect(box.text()).toContain("Thử diễn đạt khác, hoặc kiểm tra tài liệu đã được tải lên chưa.");
    expect(box.classes().join(" ")).not.toMatch(/danger/);
    expect(box.attributes("style") ?? "").not.toContain("--color-danger");
    // Kiểu nền của khối không dùng token lỗi.
    const css = readFileSync(join(__dirname, "..", "styles", "base.css"), "utf8");
    const rule = /\.msg-not-found \{[^}]*\}/.exec(css)?.[0] ?? "";
    expect(rule).toContain("--color-not-found-bg");
    expect(rule).not.toMatch(/danger/);
  });

  it("no_ready_docs_text", () => {
    const w = view(msg({ state: "NOT_FOUND", notFoundReason: "NO_READY_DOCS" }));
    expect(w.get("[data-testid=not-found]").text()).toContain("Kho chưa có tài liệu sẵn sàng. Hãy tải PDF lên để bắt đầu.");
    expect(w.text()).not.toContain("Không tìm thấy thông tin này");
  });

  it("interrupted_keeps_partial", async () => {
    // Văn bản một phần nằm ở AnswerBlock; AnswerState chỉ thêm thông báo và nút.
    const w = view(msg({ state: "INTERRUPTED", text: "Hợp đồng có thời hạn 24" }));
    expect(w.get("[data-testid=interrupted]").text()).toContain("Mất kết nối – câu trả lời chưa đầy đủ.");
    await w.get("[data-testid=ask-again]").trigger("click");
    expect(w.emitted("retry")).toHaveLength(1);
    expect(w.get("[data-testid=ask-again]").text()).toBe("Hỏi lại");
  });

  it("stopped_label", () => {
    const w = view(msg({ state: "STOPPED" }));
    expect(w.get("[data-testid=stopped]").text()).toContain("Đã dừng");
    expect(w.get("[data-testid=ask-again]").text()).toBe("Hỏi lại");
  });

  it("failed_uses_error_table", async () => {
    const w = view(msg({ state: "FAILED", errorCode: "AI_UNAVAILABLE" }));
    expect(w.text()).toContain("Dịch vụ hỏi đáp tạm thời gián đoạn. Vui lòng thử lại sau ít phút.");
    expect(w.text()).not.toContain("AI_UNAVAILABLE");
    expect(w.get("[data-testid=retry]").text()).toBe("Thử lại");
    expect(view(msg({ state: "FAILED", errorCode: "WHATEVER" })).text()).toContain("Đã có lỗi xảy ra.");
  });

  it("lang_notice", () => {
    const w = view(msg({ state: "COMPLETED", notice: "LANG_UNSUPPORTED" }));
    expect(w.get("[data-testid=lang-notice]").text()).toBe("Hiện chỉ hỗ trợ tốt tiếng Việt và tiếng Anh.");
    expect(view(msg({ state: "COMPLETED" })).find("[data-testid=lang-notice]").exists()).toBe(false);
  });

  it("completed_and_streaming_show_nothing_extra", () => {
    expect(view(msg({ state: "COMPLETED" })).text()).toBe("");
    expect(view(msg({ state: "STREAMING", text: "a" })).text()).toBe("");
  });
});

describe("chat.retry", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("resends_the_same_question_once", async () => {
    setActivePinia(createPinia());
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    const sse = await import("@/api/sse");
    const spy = vi.spyOn(sse, "streamPost").mockImplementation(async (_p, _b, h) =>
      h.onDone({ messageId: "m", citationCount: 0, isNotFound: false, notFoundReason: null, notice: null, stopped: false }),
    );
    const chat = useChatStore();
    chat.messages = [
      { id: "u", role: "user", text: "câu hỏi gốc", state: "COMPLETED", citations: [], sentAt: 0 },
      { id: "a", role: "assistant", text: "", state: "FAILED", citations: [], sentAt: 0, errorCode: "TIMEOUT" },
    ];
    await chat.retry("a");
    expect(spy).toHaveBeenCalledTimes(1);
    expect((spy.mock.calls[0]![1] as { text: string }).text).toBe("câu hỏi gốc");
    expect(chat.messages.map((m) => m.role)).toEqual(["user", "assistant"]);
    expect(chat.messages[1]!.state).toBe("COMPLETED");
  });
});
