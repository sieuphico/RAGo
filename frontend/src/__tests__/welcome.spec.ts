import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import { routes } from "@/router";
import WelcomePanel from "@/components/WelcomePanel.vue";
import { useAuthStore } from "@/stores/auth";
import { useChatStore } from "@/stores/chat";
import { useDocumentsStore } from "@/stores/documents";
import { useFeaturesStore } from "@/stores/features";
import * as telemetry from "@/api/telemetry";
import type { DocumentOut } from "@/api/types";
import { calls, installFetch, jsonRes } from "./helpers/api";

const doc = (i: number, status: DocumentOut["status"] = "READY"): DocumentOut => ({
  docId: `d${i}`, name: `f${i}.pdf`, pageCount: 1, uploadedBy: "a@b.vn", uploadedAt: "2026-10-19T02:12:00Z", sizeBytes: 1,
  status, failureReason: null, usedOcr: false, canDelete: false,
});

const SUGGESTIONS = [
  { docId: "d1", text: "Điều khoản thanh toán trong hợp đồng X là gì?" },
  { docId: "d2", text: "Thời hạn hợp đồng ABC?" },
  { docId: "d3", text: "Giá dịch vụ năm 2026?" },
];

async function setup(opts: { docs: DocumentOut[]; role?: "BD_USER" | "TEAM_LEAD"; flag?: boolean; loaded?: boolean }) {
  setActivePinia(createPinia());
  const docs = useDocumentsStore();
  docs.items = opts.docs;
  docs.loaded = opts.loaded ?? true;
  useFeaturesStore().flags = { ...useFeaturesStore().flags, suggestions: opts.flag ?? true };
  const auth = useAuthStore();
  auth.me = { email: "lan@congty.vn", role: opts.role ?? "BD_USER", allowed: true };
  const fetchMock = installFetch({ "GET /api/v1/suggestions": () => jsonRes(200, { items: SUGGESTIONS }) });
  const router = createRouter({ history: createMemoryHistory(), routes });
  router.push("/");
  await router.isReady();
  const track = vi.spyOn(telemetry, "track").mockImplementation(() => {});
  const w = mount(WelcomePanel, { props: { userName: "Lan" }, global: { plugins: [router] } });
  await flushPromises();
  return { w, fetchMock, track };
}

describe("WelcomePanel", () => {
  beforeEach(() => localStorage.clear());
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  const many = Array.from({ length: 125 }, (_, i) => doc(i));

  it("shows_three_suggestions", async () => {
    const { w } = await setup({ docs: many });
    expect(w.get("[data-testid=welcome-title]").text()).toBe("Xin chào Lan! Kho đang có 125 tài liệu.");
    expect(w.findAll("[data-testid=suggestion]")).toHaveLength(3);
    expect(w.text()).toContain("Gợi ý câu hỏi");
  });

  it("click_suggestion_sends", async () => {
    const { w, track } = await setup({ docs: many });
    const chat = useChatStore();
    const send = vi.spyOn(chat, "send").mockResolvedValue();
    await w.findAll("[data-testid=suggestion]")[1]!.trigger("click");
    expect(send).toHaveBeenCalledWith("Thời hạn hợp đồng ABC?");
    expect(track).toHaveBeenCalledWith("suggestion_clicked", { suggestion_index: 1 });
  });

  it("empty_library_disables_input", async () => {
    const { w, fetchMock } = await setup({ docs: [], role: "TEAM_LEAD" });
    const chat = useChatStore();
    expect(w.get("[data-testid=welcome-empty]").text()).toContain("Kho chưa có tài liệu.");
    expect(w.get("[data-testid=upload-cta]").text()).toBe("Tải PDF lên");
    expect(w.get("[data-testid=upload-cta]").attributes("href")).toBe("/library");
    expect(chat.libraryEmpty).toBe(true);
    expect(calls(fetchMock)).not.toContain("GET /api/v1/suggestions");
    w.unmount();
    expect(chat.libraryEmpty).toBe(false);
  });

  it("empty_library_for_non_lead_has_no_upload_link", async () => {
    const { w } = await setup({ docs: [], role: "BD_USER" });
    expect(w.find("[data-testid=upload-cta]").exists()).toBe(false);
    expect(w.text()).toContain("Kho chưa có tài liệu.");
  });

  it("processing_count", async () => {
    const { w } = await setup({ docs: [doc(1), doc(2), doc(3, "PROCESSING"), doc(4, "PROCESSING"), doc(5, "OCR_PROCESSING")] });
    expect(w.get("[data-testid=processing-note]").text()).toBe("3 tài liệu đang được xử lý, chưa dùng để trả lời.");
    expect(useChatStore().libraryEmpty).toBe(false);
  });

  it("only_processing_docs_is_not_an_empty_library", async () => {
    const { w, fetchMock } = await setup({ docs: [doc(1, "PROCESSING")] });
    expect(w.find("[data-testid=welcome-empty]").exists()).toBe(false);
    expect(w.get("[data-testid=welcome-title]").text()).toContain("Kho đang có 0 tài liệu.");
    expect(calls(fetchMock)).not.toContain("GET /api/v1/suggestions");
  });

  it("onboarding_once", async () => {
    const first = await setup({ docs: many });
    expect(first.track).toHaveBeenCalledWith("onboarding_viewed", { doc_count: 125 });
    const second = await setup({ docs: many });
    expect(second.track.mock.calls.filter((c) => c[0] === "onboarding_viewed")).toHaveLength(0);
    expect(localStorage.getItem("cwd_onboarded")).toBe("1");
  });

  it("onboarding_waits_until_documents_are_loaded", async () => {
    const { w, track } = await setup({ docs: [], loaded: false });
    expect(track).not.toHaveBeenCalled();
    expect(w.find("[data-testid=welcome-empty]").exists()).toBe(false);
    const docs = useDocumentsStore();
    docs.items = [doc(1), doc(2)];
    docs.loaded = true;
    await flushPromises();
    expect(track).toHaveBeenCalledWith("onboarding_viewed", { doc_count: 2 });
  });

  it("flag_off_no_suggestions", async () => {
    const { w, fetchMock } = await setup({ docs: many, flag: false });
    expect(calls(fetchMock)).not.toContain("GET /api/v1/suggestions");
    expect(w.find("[data-testid=suggestion]").exists()).toBe(false);
    expect(w.text()).not.toContain("Gợi ý câu hỏi");
  });
});
