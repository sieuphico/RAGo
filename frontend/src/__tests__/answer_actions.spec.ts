import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import AnswerActions from "@/components/AnswerActions.vue";
import { copyText } from "@/utils/answerText";
import { useFeaturesStore } from "@/stores/features";
import { useToastState } from "@/composables/useToast";
import * as telemetry from "@/api/telemetry";
import type { UiMessage } from "@/api/types";
import { installFetch, jsonRes } from "./helpers/api";

const M1 = "11111111-1111-4111-8111-111111111111";

const message = (over: Partial<UiMessage> = {}): UiMessage => ({
  id: "a1", role: "assistant", messageId: M1, text: "Thời hạn 24 tháng [[1]].", state: "COMPLETED", sentAt: 0,
  citations: [{ index: 1, docId: "d1", docName: "HD_ABC_2026.pdf", page: 12, snippet: "s", deleted: false }], ...over,
});

function setup(msg: UiMessage, flags = { copy: true, rating: true }) {
  setActivePinia(createPinia());
  useFeaturesStore().flags = { ...useFeaturesStore().flags, ...flags };
  return mount(AnswerActions, { props: { message: msg }, attachTo: document.body });
}

describe("AnswerActions", () => {
  beforeEach(() => useToastState().items.splice(0));
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    document.body.innerHTML = "";
    Object.defineProperty(navigator, "clipboard", { value: undefined, configurable: true });
  });

  it("copy_includes_sources", () => {
    expect(copyText(message())).toBe("Thời hạn 24 tháng [1].\n\nNguồn:\n[1] HD_ABC_2026.pdf, tr. 12");
    expect(copyText(message({ text: "Không có nguồn", citations: [] }))).toBe("Không có nguồn");
    const two = message({
      text: "A [[2]] B [[1]]",
      citations: [
        { index: 2, docId: "d2", docName: "B.pdf", page: 3, snippet: "", deleted: false },
        { index: 1, docId: "d1", docName: "A.pdf", page: 1, snippet: "", deleted: false },
      ],
    });
    expect(copyText(two)).toBe("A [2] B [1]\n\nNguồn:\n[1] A.pdf, tr. 1\n[2] B.pdf, tr. 3");
  });

  it("copy_uses_clipboard_api_and_tracks", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    const track = vi.spyOn(telemetry, "track").mockImplementation(() => {});
    const w = setup(message());
    await w.get("[data-testid=copy]").trigger("click");
    await flushPromises();
    expect(writeText).toHaveBeenCalledWith("Thời hạn 24 tháng [1].\n\nNguồn:\n[1] HD_ABC_2026.pdf, tr. 12");
    expect(track).toHaveBeenCalledWith("answer_copied", { question_id: M1 });
    expect(useToastState().items.map((i) => i.text)).toEqual(["Đã sao chép"]);
  });

  it("clipboard_fallback", async () => {
    Object.defineProperty(navigator, "clipboard", { value: undefined, configurable: true });
    const exec = vi.fn(() => true);
    (document as unknown as { execCommand: unknown }).execCommand = exec;
    vi.spyOn(telemetry, "track").mockImplementation(() => {});
    const w = setup(message());
    await w.get("[data-testid=copy]").trigger("click");
    await flushPromises();
    expect(exec).toHaveBeenCalledWith("copy");
    expect(useToastState().items.map((i) => i.text)).toEqual(["Đã sao chép"]);
    expect(document.querySelector("textarea")).toBeNull(); // textarea tạm đã gỡ
  });

  it("rate_up", async () => {
    const fetchMock = installFetch({ [`POST /api/v1/chat/messages/${M1}/rating`]: () => jsonRes(204) });
    const w = setup(message());
    await w.get("[data-testid=rate-up]").trigger("click");
    await flushPromises();
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(JSON.parse(init.body as string)).toEqual({ value: "UP", reasonCode: null });
    expect(w.get("[data-testid=rate-up]").attributes("aria-pressed")).toBe("true");
    expect(w.get("[data-testid=rate-down]").attributes("aria-pressed")).toBe("false");
  });

  it("rating_dialog_skip_still_records", async () => {
    const fetchMock = installFetch({ [`POST /api/v1/chat/messages/${M1}/rating`]: () => jsonRes(204) });
    const w = setup(message());
    await w.get("[data-testid=rate-down]").trigger("click");
    await flushPromises();
    expect(fetchMock).not.toHaveBeenCalled(); // chưa gửi trước khi chọn
    expect(w.get("dialog h2").text()).toBe("Câu trả lời chưa tốt ở điểm nào? (tùy chọn)");
    expect(w.findAll("[data-testid=rating-reasons] input")).toHaveLength(4);
    await w.get("[data-testid=dialog-cancel]").trigger("click");
    await flushPromises();
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(JSON.parse(init.body as string)).toEqual({ value: "DOWN", reasonCode: null });
    expect(w.get("[data-testid=rate-down]").attributes("aria-pressed")).toBe("true");
  });

  it("rating_dialog_with_reason", async () => {
    const fetchMock = installFetch({ [`POST /api/v1/chat/messages/${M1}/rating`]: () => jsonRes(204) });
    const w = setup(message());
    await w.get("[data-testid=rate-down]").trigger("click");
    await flushPromises();
    await w.get("[data-testid=reason-WRONG_CITATION]").setValue(true);
    await w.get("[data-testid=dialog-confirm]").trigger("click");
    await flushPromises();
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(JSON.parse(init.body as string)).toEqual({ value: "DOWN", reasonCode: "WRONG_CITATION" });
  });

  it("rating_not_sent_by_ui_as_telemetry", async () => {
    installFetch({ [`POST /api/v1/chat/messages/${M1}/rating`]: () => jsonRes(204) });
    const track = vi.spyOn(telemetry, "track").mockImplementation(() => {});
    const w = setup(message());
    await w.get("[data-testid=rate-up]").trigger("click");
    await flushPromises();
    expect(track).not.toHaveBeenCalled();
  });

  it("rating_error_shows_toast_and_keeps_state", async () => {
    installFetch({ [`POST /api/v1/chat/messages/${M1}/rating`]: () => jsonRes(409, { code: "MESSAGE_NOT_RATEABLE", retryable: false }) });
    const w = setup(message());
    await w.get("[data-testid=rate-up]").trigger("click");
    await flushPromises();
    expect(useToastState().items[0]!.text).toBe("Chỉ đánh giá được câu trả lời đã hoàn tất.");
    expect(w.get("[data-testid=rate-up]").attributes("aria-pressed")).toBe("false");
  });

  it("hidden_while_streaming", () => {
    for (const state of ["STREAMING", "SEARCHING", "FAILED", "STOPPED", "INTERRUPTED"] as const) {
      const w = setup(message({ state }));
      expect(w.find("button").exists(), state).toBe(false);
    }
  });

  it("not_found_can_be_rated_but_not_copied", () => {
    const w = setup(message({ state: "NOT_FOUND", text: "", citations: [] }));
    expect(w.find("[data-testid=copy]").exists()).toBe(false);
    expect(w.find("[data-testid=rate-up]").exists()).toBe(true);
  });

  it("flags_off_hide_buttons", () => {
    const w = setup(message(), { copy: false, rating: false });
    expect(w.find("button").exists()).toBe(false);
    const onlyCopy = setup(message(), { copy: true, rating: false });
    expect(onlyCopy.find("[data-testid=copy]").exists()).toBe(true);
    expect(onlyCopy.find("[data-testid=rate-up]").exists()).toBe(false);
  });

  it("buttons_have_accessible_names", () => {
    const w = setup(message());
    expect(w.get("[data-testid=copy]").attributes("aria-label")).toBe("Sao chép câu trả lời");
    expect(w.get("[data-testid=rate-up]").attributes("aria-label")).toBe("Câu trả lời hữu ích");
    expect(w.get("[data-testid=rate-down]").attributes("aria-label")).toBe("Câu trả lời chưa tốt");
  });
});
