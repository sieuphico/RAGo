import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import LibraryView from "@/views/LibraryView.vue";
import { useAuthStore } from "@/stores/auth";
import type { DocumentOut } from "@/api/types";
import { calls, installFetch, jsonRes } from "./helpers/api";

class FakeES {
  static all: FakeES[] = [];
  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;
  closed = false;
  listeners: Record<string, ((e: MessageEvent) => void)[]> = {};
  constructor(public url: string) {
    FakeES.all.push(this);
  }
  addEventListener(name: string, fn: (e: MessageEvent) => void) {
    (this.listeners[name] ??= []).push(fn);
  }
  close() {
    this.closed = true;
  }
  emit(name: string, data: unknown) {
    for (const fn of this.listeners[name] ?? []) fn({ data: JSON.stringify(data) } as MessageEvent);
  }
}

const doc = (over: Partial<DocumentOut>): DocumentOut => ({
  docId: "d1", name: "HD_ABC.pdf", pageCount: null, uploadedBy: "minh@congty.vn", uploadedAt: "2026-10-19T02:12:00Z",
  sizeBytes: 1, status: "PROCESSING", failureReason: null, usedOcr: false, canDelete: false, ...over,
});

async function mountLibrary(items: DocumentOut[]) {
  setActivePinia(createPinia());
  const auth = useAuthStore();
  auth.me = { email: "minh@congty.vn", role: "TEAM_LEAD", allowed: true };
  auth.status = "allowed";
  const fetchMock = installFetch({ "GET /api/v1/documents": () => jsonRes(200, { items, total: items.length }) });
  const w = mount(LibraryView);
  await flushPromises();
  return { w, fetchMock };
}

describe("document events", () => {
  beforeEach(() => {
    FakeES.all = [];
    vi.stubGlobal("EventSource", FakeES);
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("updates_badge_on_event", async () => {
    const { w } = await mountLibrary([doc({})]);
    expect(FakeES.all[0]!.url).toBe("/api/v1/documents/events");
    FakeES.all[0]!.emit("status", { docId: "d1", status: "READY", failureReason: null, pageCount: 12 });
    await flushPromises();
    const row = w.get("[data-testid=doc-row]");
    expect(row.text()).toContain("Sẵn sàng");
    expect(row.get("[data-testid=doc-pages]").text()).toBe("12");
    expect(w.get("[data-testid=sr-live]").text()).toBe("HD_ABC.pdf: Sẵn sàng");
  });

  it("announces_failure_with_reason", async () => {
    const { w } = await mountLibrary([doc({})]);
    FakeES.all[0]!.emit("status", { docId: "d1", status: "FAILED", failureReason: "OCR_UNREADABLE", pageCount: null });
    await flushPromises();
    expect(w.get("[data-testid=sr-live]").text()).toBe("HD_ABC.pdf: Thất bại – Không đọc được nội dung.");
  });

  it("deleted_event_removes_row", async () => {
    const { w } = await mountLibrary([doc({}), doc({ docId: "d2", name: "B.pdf" })]);
    FakeES.all[0]!.emit("status", { docId: "d1", status: "DELETED", failureReason: null, pageCount: null });
    await flushPromises();
    expect(w.findAll("[data-testid=doc-row]")).toHaveLength(1);
  });

  it("falls_back_to_polling", async () => {
    vi.useFakeTimers();
    const { fetchMock } = await mountLibrary([doc({})]);
    const base = calls(fetchMock).filter((c) => c === "GET /api/v1/documents").length;
    FakeES.all[0]!.onerror?.();
    expect(FakeES.all[0]!.closed).toBe(false); // mới lỗi 1 lần
    FakeES.all[0]!.onerror?.();
    expect(FakeES.all[0]!.closed).toBe(true);
    await vi.advanceTimersByTimeAsync(9000);
    expect(calls(fetchMock).filter((c) => c === "GET /api/v1/documents").length - base).toBe(3);
  });

  it("reopens_sse_after_60s", async () => {
    vi.useFakeTimers();
    await mountLibrary([doc({})]);
    FakeES.all[0]!.onerror?.();
    FakeES.all[0]!.onerror?.();
    await vi.advanceTimersByTimeAsync(60_000);
    expect(FakeES.all).toHaveLength(2);
    expect(FakeES.all[1]!.closed).toBe(false);
  });

  it("successful_open_resets_error_count", async () => {
    vi.useFakeTimers();
    await mountLibrary([doc({})]);
    FakeES.all[0]!.onerror?.();
    FakeES.all[0]!.onopen?.();
    FakeES.all[0]!.onerror?.();
    expect(FakeES.all[0]!.closed).toBe(false);
  });

  it("slow_ocr_flag", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-19T02:28:00Z")); // 16 phút sau khi tải
    const { w } = await mountLibrary([doc({ status: "OCR_PROCESSING", usedOcr: true })]);
    await vi.advanceTimersByTimeAsync(60_000);
    expect(w.get("[data-testid=status-badge]").text()).toContain("Xử lý lâu bất thường");
  });

  it("not_slow_when_recent", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-19T02:20:00Z")); // 8 phút
    const { w } = await mountLibrary([doc({ status: "OCR_PROCESSING" })]);
    await vi.advanceTimersByTimeAsync(60_000);
    expect(w.get("[data-testid=status-badge]").text()).not.toContain("lâu bất thường");
  });

  it("closes_on_unmount", async () => {
    vi.useFakeTimers();
    const { w, fetchMock } = await mountLibrary([doc({})]);
    FakeES.all[0]!.onerror?.();
    FakeES.all[0]!.onerror?.();
    w.unmount();
    expect(FakeES.all[0]!.closed).toBe(true);
    const before = calls(fetchMock).length;
    await vi.advanceTimersByTimeAsync(120_000);
    expect(calls(fetchMock).length).toBe(before);
    expect(FakeES.all).toHaveLength(1);
    expect(vi.getTimerCount()).toBe(0);
  });
});
