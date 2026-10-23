import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import LibraryView from "@/views/LibraryView.vue";
import { useAuthStore } from "@/stores/auth";
import { useDocumentsStore } from "@/stores/documents";
import type { DocumentOut, Role } from "@/api/types";
import { calls, installFetch, jsonRes } from "./helpers/api";

const doc = (over: Partial<DocumentOut>): DocumentOut => ({
  docId: "d?", name: "x.pdf", pageCount: 10, uploadedBy: "minh@congty.vn", uploadedAt: "2026-10-19T02:12:00Z",
  sizeBytes: 1000, status: "READY", failureReason: null, usedOcr: false, canDelete: false, ...over,
});
const DOCS = [
  doc({ docId: "d1", name: "Hợp đồng ABC.pdf", pageCount: 48, uploadedAt: "2026-10-19T02:12:00Z" }),
  doc({ docId: "d2", name: "Báo giá.pdf", pageCount: null, status: "PROCESSING", uploadedAt: "2026-10-18T02:12:00Z" }),
  doc({ docId: "d3", name: "Zeta.pdf", status: "FAILED", failureReason: "FILE_CORRUPTED", uploadedAt: "2026-10-17T02:12:00Z" }),
];

function mountLibrary(role: Role = "BD_USER") {
  setActivePinia(createPinia());
  const auth = useAuthStore();
  auth.me = { email: "lan@congty.vn", role, allowed: true };
  auth.status = "allowed";
  return mount(LibraryView);
}

describe("library", () => {
  beforeEach(() => {
    process.env.TZ = "Asia/Ho_Chi_Minh";
  });
  afterEach(() => vi.unstubAllGlobals());

  it("renders_rows_with_fields", async () => {
    installFetch({ "GET /api/v1/documents": () => jsonRes(200, { items: DOCS, total: 3 }) });
    const w = mountLibrary();
    await flushPromises();
    const rows = w.findAll("[data-testid=doc-row]");
    expect(rows).toHaveLength(3);
    expect(w.get("[data-testid=doc-count]").text()).toBe("(3)");
    const first = rows[0]!;
    expect(first.get("[data-testid=doc-name]").text()).toBe("Hợp đồng ABC.pdf");
    expect(first.get("[data-testid=doc-pages]").text()).toBe("48");
    expect(first.get("[data-testid=doc-uploader]").text()).toBe("minh@congty.vn");
    expect(first.get("[data-testid=doc-time]").text()).toBe("19/10/2026 09:12");
    expect(first.get("[data-testid=status-badge]").text()).toContain("Sẵn sàng");
    expect(rows[1]!.get("[data-testid=doc-pages]").text()).toBe("—");
    expect(rows[2]!.text()).toContain("Thất bại – Tệp bị hỏng.");
    expect(w.findAll("thead th")).toHaveLength(6);
  });

  it("search_filters_by_name", async () => {
    const fetchMock = installFetch({ "GET /api/v1/documents": () => jsonRes(200, { items: DOCS, total: 3 }) });
    const w = mountLibrary();
    await flushPromises();
    await w.get("[data-testid=search]").setValue("hop dong");
    const rows = w.findAll("[data-testid=doc-row]");
    expect(rows).toHaveLength(1);
    expect(rows[0]!.text()).toContain("Hợp đồng ABC.pdf");
    expect(calls(fetchMock).filter((c) => c === "GET /api/v1/documents")).toHaveLength(1);
    await w.get("[data-testid=search]").setValue("khong co");
    expect(w.find("[data-testid=no-match]").exists()).toBe(true);
  });

  it("sort_by_name", async () => {
    installFetch({ "GET /api/v1/documents": () => jsonRes(200, { items: DOCS, total: 3 }) });
    const w = mountLibrary();
    await flushPromises();
    await w.get("[data-testid=sort-name]").trigger("click");
    const names = w.findAll("[data-testid=doc-name]").map((n) => n.text());
    expect(names).toEqual(["Báo giá.pdf", "Hợp đồng ABC.pdf", "Zeta.pdf"]);
    expect(w.findAll("th")[0]!.attributes("aria-sort")).toBe("ascending");
    await w.get("[data-testid=sort-name]").trigger("click");
    expect(w.findAll("th")[0]!.attributes("aria-sort")).toBe("descending");
    expect(w.findAll("[data-testid=doc-name]")[0]!.text()).toBe("Zeta.pdf");
  });

  it("shows_empty_and_error_states", async () => {
    let fail = false;
    const fetchMock = installFetch({
      "GET /api/v1/documents": () => (fail ? jsonRes(500, { code: "INTERNAL", retryable: false }) : jsonRes(200, { items: [], total: 0 })),
    });
    let w = mountLibrary("BD_USER");
    await flushPromises();
    expect(w.get("[data-testid=empty]").text()).toContain("Chưa có tài liệu.");
    expect(w.get("[data-testid=empty]").text()).not.toContain("Kéo thả");
    w = mountLibrary("TEAM_LEAD");
    await flushPromises();
    expect(w.get("[data-testid=empty]").text()).toContain("Chưa có tài liệu. Kéo thả PDF vào đây.");

    fail = true;
    w = mountLibrary("BD_USER");
    await flushPromises();
    expect(w.get("[data-testid=load-error]").text()).toContain("Không tải được danh sách.");
    fail = false;
    const before = calls(fetchMock).length;
    await w.get("[data-testid=retry]").trigger("click");
    await flushPromises();
    expect(calls(fetchMock).length).toBe(before + 1);
    expect(w.find("[data-testid=load-error]").exists()).toBe(false);
  });

  it("loading_shows_skeleton", async () => {
    installFetch({ "GET /api/v1/documents": () => new Promise<Response>(() => {}) });
    const w = mountLibrary();
    await flushPromises();
    expect(w.find("[data-testid=skeleton]").exists()).toBe(true);
    expect(w.findAll(".skeleton-row")).toHaveLength(5);
  });

  it("upload_not_allowed_line", async () => {
    installFetch({ "GET /api/v1/documents": () => jsonRes(200, { items: DOCS, total: 3 }) });
    for (const role of ["BD_USER", "ADMIN"] as Role[]) {
      const w = mountLibrary(role);
      await flushPromises();
      expect(w.get("[data-testid=upload-not-allowed]").text()).toBe("Chỉ Trưởng nhóm BD tải được tài liệu lên.");
      expect(w.find("[data-testid=upload-slot]").exists()).toBe(false);
    }
    const lead = mountLibrary("TEAM_LEAD");
    await flushPromises();
    expect(lead.find("[data-testid=upload-not-allowed]").exists()).toBe(false);
  });

  it("store_apply_event_and_remove", async () => {
    installFetch({ "GET /api/v1/documents": () => jsonRes(200, { items: DOCS, total: 3 }) });
    mountLibrary();
    await flushPromises();
    const store = useDocumentsStore();
    store.applyEvent({ docId: "d2", status: "READY", failureReason: null, pageCount: 12 });
    expect(store.items.find((d) => d.docId === "d2")).toMatchObject({ status: "READY", pageCount: 12 });
    expect(store.readyItems).toHaveLength(2);
    store.applyEvent({ docId: "d1", status: "DELETED", failureReason: null, pageCount: null });
    expect(store.items.map((d) => d.docId)).toEqual(["d2", "d3"]);
  });
});
