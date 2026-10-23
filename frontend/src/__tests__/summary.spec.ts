import { describe, it, expect, vi, afterEach } from "vitest";
import { mount, flushPromises, type VueWrapper } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import { routes } from "@/router";
import LibraryView from "@/views/LibraryView.vue";
import { useAuthStore } from "@/stores/auth";
import { useFeaturesStore } from "@/stores/features";
import type { DocumentOut } from "@/api/types";
import { calls, installFetch, jsonRes } from "./helpers/api";

const doc = (over: Partial<DocumentOut>): DocumentOut => ({
  docId: "d1", name: "HD_ABC.pdf", pageCount: 10, uploadedBy: "minh@congty.vn", uploadedAt: "2026-10-19T02:12:00Z",
  sizeBytes: 1, status: "READY", failureReason: null, usedOcr: false, canDelete: false, ...over,
});

const SUMMARY = {
  docId: "d1", docName: "HD_ABC.pdf", text: "Ý 1 [[1]].",
  citations: [{ index: 1, docId: "d1", docName: "HD_ABC.pdf", page: 3, snippet: "s", deleted: false }],
};

async function mountLibrary(items: DocumentOut[], opts: { summary?: boolean; routes?: Parameters<typeof installFetch>[0] } = {}) {
  setActivePinia(createPinia());
  useFeaturesStore().flags = { ...useFeaturesStore().flags, summary: opts.summary ?? true };
  const auth = useAuthStore();
  auth.me = { email: "lan@congty.vn", role: "BD_USER", allowed: true };
  auth.status = "allowed";
  const fetchMock = installFetch({ "GET /api/v1/documents": () => jsonRes(200, { items, total: items.length }), ...opts.routes });
  const router = createRouter({ history: createMemoryHistory(), routes });
  router.push("/library");
  await router.isReady();
  const w = mount(LibraryView, { global: { plugins: [router] }, attachTo: document.body });
  await flushPromises();
  return { w, router, fetchMock };
}

const row = (w: VueWrapper, name: string) => w.findAll("[data-testid=doc-row]").find((r) => r.text().includes(name))!;
async function openSummary(w: VueWrapper, name = "HD_ABC.pdf") {
  await row(w, name).get("[data-testid=menu-trigger]").trigger("click");
  await row(w, name).get("[data-testid=menu-summary]").trigger("click");
  await flushPromises();
}

describe("summary", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    document.body.innerHTML = "";
  });

  it("summary_only_for_ready", async () => {
    const { w } = await mountLibrary([doc({}), doc({ docId: "d2", name: "Dang.pdf", status: "PROCESSING" })]);
    expect(row(w, "HD_ABC.pdf").find("[data-testid=menu-trigger]").exists()).toBe(true);
    await row(w, "HD_ABC.pdf").get("[data-testid=menu-trigger]").trigger("click");
    expect(row(w, "HD_ABC.pdf").get("[data-testid=menu-summary]").text()).toBe("Tóm tắt");
    // Dòng đang xử lý, không có thao tác nào: không có menu
    expect(row(w, "Dang.pdf").find("[data-testid=menu-trigger]").exists()).toBe(false);
    expect(row(w, "Dang.pdf").find("[data-testid=menu-summary]").exists()).toBe(false);
  });

  it("renders_summary_with_citations", async () => {
    const { w, fetchMock } = await mountLibrary([doc({})], {
      routes: { "POST /api/v1/documents/d1/summary": () => jsonRes(200, SUMMARY) },
    });
    await openSummary(w);
    expect(calls(fetchMock)).toContain("POST /api/v1/documents/d1/summary");
    const dialog = w.findAll("dialog").find((d) => d.find("[data-testid=summary-body]").exists())!;
    expect(dialog.get("h2").text()).toBe("Tóm tắt do AI tạo cho HD_ABC.pdf");
    expect(dialog.get("[data-testid=answer-text]").text()).toContain("Ý 1");
    const chip = dialog.get("[data-testid=citation-label]");
    expect(chip.text()).toBe("[HD_ABC.pdf – tr. 3]");
  });

  it("shows_loading_while_waiting", async () => {
    const { w } = await mountLibrary([doc({})], { routes: { "POST /api/v1/documents/d1/summary": () => new Promise<Response>(() => {}) } });
    await openSummary(w);
    expect(w.get("[data-testid=summary-loading]").text()).toContain("Đang tạo tóm tắt…");
  });

  it("citation_navigates", async () => {
    const { w, router } = await mountLibrary([doc({})], { routes: { "POST /api/v1/documents/d1/summary": () => jsonRes(200, SUMMARY) } });
    await openSummary(w);
    await w.get("[data-testid=citation]").trigger("click");
    await flushPromises();
    expect(router.currentRoute.value.path).toBe("/");
    expect(router.currentRoute.value.query).toMatchObject({ doc: "d1", page: "3" });
    expect(w.findAll("dialog").every((d) => d.attributes("open") === undefined)).toBe(true);
  });

  it("hidden_when_flag_off", async () => {
    const { w } = await mountLibrary([doc({})], { summary: false });
    expect(w.find("[data-testid=menu-trigger]").exists()).toBe(false);
    expect(w.find("[data-testid=menu-summary]").exists()).toBe(false);
  });

  it("error_retry", async () => {
    let fail = true;
    const { w } = await mountLibrary([doc({})], {
      routes: {
        "POST /api/v1/documents/d1/summary": () => (fail ? jsonRes(503, { code: "AI_UNAVAILABLE", retryable: true }) : jsonRes(200, SUMMARY)),
      },
    });
    await openSummary(w);
    expect(w.get("[data-testid=summary-error]").text()).toContain("Dịch vụ hỏi đáp tạm thời gián đoạn.");
    fail = false;
    await w.get("[data-testid=summary-retry]").trigger("click");
    await flushPromises();
    expect(w.find("[data-testid=summary-error]").exists()).toBe(false);
    expect(w.find("[data-testid=answer-text]").exists()).toBe(true);
  });

  it("close_button_closes_dialog", async () => {
    const { w } = await mountLibrary([doc({})], { routes: { "POST /api/v1/documents/d1/summary": () => jsonRes(200, SUMMARY) } });
    await openSummary(w);
    const dialog = w.findAll("dialog").find((d) => d.find("[data-testid=summary-body]").exists())!;
    expect(dialog.attributes("open")).toBeDefined();
    expect(dialog.find("[data-testid=dialog-confirm]").exists()).toBe(false); // chỉ có nút Đóng
    await dialog.get("[data-testid=dialog-cancel]").trigger("click");
    await flushPromises();
    expect(dialog.attributes("open")).toBeUndefined();
  });
});
