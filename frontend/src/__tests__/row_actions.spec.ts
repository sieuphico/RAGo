import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount, flushPromises, type VueWrapper } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import LibraryView from "@/views/LibraryView.vue";
import { useAuthStore } from "@/stores/auth";
import { useFeaturesStore } from "@/stores/features";
import { useToastState } from "@/composables/useToast";
import { resetUploadsForTest, useUpload } from "@/composables/useUpload";
import type { DocumentOut } from "@/api/types";
import { calls, installFetch, jsonRes } from "./helpers/api";

const doc = (over: Partial<DocumentOut>): DocumentOut => ({
  docId: "d1", name: "HD.pdf", pageCount: 3, uploadedBy: "minh@congty.vn", uploadedAt: "2026-10-19T02:12:00Z",
  sizeBytes: 4_404_019, status: "READY", failureReason: null, usedOcr: false, canDelete: true, ...over,
});

class QuietXHR {
  static sent = 0;
  upload = { onprogress: null };
  onload = null;
  onerror = null;
  onabort = null;
  ontimeout = null;
  withCredentials = false;
  open() {}
  setRequestHeader() {}
  send() {
    QuietXHR.sent += 1;
  }
}

async function mountLibrary(items: DocumentOut[], opts: { role?: "TEAM_LEAD" | "ADMIN"; dup?: boolean; routes?: Parameters<typeof installFetch>[0] } = {}) {
  setActivePinia(createPinia());
  useFeaturesStore().flags = { ...useFeaturesStore().flags, duplicateCheck: opts.dup ?? true };
  const auth = useAuthStore();
  auth.me = { email: "minh@congty.vn", role: opts.role ?? "TEAM_LEAD", allowed: true };
  auth.status = "allowed";
  const fetchMock = installFetch({
    "GET /api/v1/documents": () => jsonRes(200, { items, total: items.length }),
    ...opts.routes,
  });
  const w = mount(LibraryView, { attachTo: document.body });
  await flushPromises();
  return { w, fetchMock };
}

const rowFor = (w: VueWrapper, name: string) => w.findAll("[data-testid=doc-row]").find((r) => r.text().includes(name))!;

describe("row actions", () => {
  beforeEach(() => {
    QuietXHR.sent = 0;
    vi.stubGlobal("XMLHttpRequest", QuietXHR);
    resetUploadsForTest();
    useToastState().items.splice(0);
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    document.body.innerHTML = "";
  });

  it("delete_button_visibility", async () => {
    const { w } = await mountLibrary([doc({ docId: "d1", name: "Khong.pdf", canDelete: false }), doc({ docId: "d2", name: "Co.pdf", canDelete: true })]);
    const first = rowFor(w, "Khong.pdf");
    expect(first.find("[data-testid=menu-trigger]").exists()).toBe(false);
    expect(first.find("[data-testid=menu-delete]").exists()).toBe(false);
    const second = rowFor(w, "Co.pdf");
    await second.get("[data-testid=menu-trigger]").trigger("click");
    expect(second.find("[role=menu]").exists()).toBe(true);
    expect(second.get("[data-testid=menu-delete]").text()).toBe("Xóa");
    expect(second.get("[data-testid=menu-trigger]").attributes("aria-label")).toBe("Thao tác với Co.pdf");
  });

  it("failed_row_has_direct_delete_button", async () => {
    const { w } = await mountLibrary([doc({ status: "FAILED", failureReason: "FILE_CORRUPTED", name: "Hong.pdf" })]);
    const btn = w.get("[data-testid=delete-direct]");
    expect(btn.text()).toContain("Xóa");
    expect(btn.attributes("aria-label")).toBe("Xóa Hong.pdf");
  });

  it("cancel_keeps_document", async () => {
    const { w, fetchMock } = await mountLibrary([doc({})]);
    await w.get("[data-testid=menu-trigger]").trigger("click");
    await w.get("[data-testid=menu-delete]").trigger("click");
    await flushPromises();
    expect(w.get("dialog h2").text()).toBe("Xóa tài liệu?");
    expect(w.get("dialog .dlg-body").text()).toBe(
      "Bạn sắp xóa \"HD.pdf\". Cả đội sẽ không thể hỏi về tài liệu này nữa. Dữ liệu được xóa trong 24 giờ.",
    );
    expect(document.activeElement).toBe(w.get("[data-testid=dialog-cancel]").element);
    await w.get("[data-testid=dialog-cancel]").trigger("click");
    await flushPromises();
    expect(calls(fetchMock).some((c) => c.startsWith("DELETE"))).toBe(false);
    expect(w.findAll("[data-testid=doc-row]")).toHaveLength(1);
  });

  it("confirm_deletes", async () => {
    const { w, fetchMock } = await mountLibrary([doc({}), doc({ docId: "d2", name: "Khac.pdf" })], {
      routes: { "DELETE /api/v1/documents/d1": () => jsonRes(200, { docId: "d1", alreadyDeleted: false }) },
    });
    await rowFor(w, "HD.pdf").get("[data-testid=menu-trigger]").trigger("click");
    await rowFor(w, "HD.pdf").get("[data-testid=menu-delete]").trigger("click");
    await flushPromises();
    expect(w.get("[data-testid=dialog-confirm]").text()).toBe("Xóa tài liệu");
    await w.get("[data-testid=dialog-confirm]").trigger("click");
    await flushPromises();
    expect(calls(fetchMock)).toContain("DELETE /api/v1/documents/d1");
    expect(w.findAll("[data-testid=doc-row]")).toHaveLength(1);
    expect(w.text()).not.toContain("HD.pdf");
    expect(useToastState().items).toHaveLength(0);
  });

  it("already_deleted_toast", async () => {
    const { w } = await mountLibrary([doc({})], {
      routes: { "DELETE /api/v1/documents/d1": () => jsonRes(200, { docId: "d1", alreadyDeleted: true }) },
    });
    await w.get("[data-testid=menu-trigger]").trigger("click");
    await w.get("[data-testid=menu-delete]").trigger("click");
    await flushPromises();
    await w.get("[data-testid=dialog-confirm]").trigger("click");
    await flushPromises();
    expect(useToastState().items.map((i) => i.text)).toEqual(["Tài liệu đã được xóa trước đó."]);
    expect(w.findAll("[data-testid=doc-row]")).toHaveLength(0);
  });

  it("delete_error_shows_toast_and_keeps_row", async () => {
    const { w } = await mountLibrary([doc({})], {
      routes: { "DELETE /api/v1/documents/d1": () => jsonRes(403, { code: "NOT_FOUND", retryable: false }) },
    });
    await w.get("[data-testid=menu-trigger]").trigger("click");
    await w.get("[data-testid=menu-delete]").trigger("click");
    await flushPromises();
    await w.get("[data-testid=dialog-confirm]").trigger("click");
    await flushPromises();
    expect(useToastState().items[0]!.text).toBe("Không tìm thấy nội dung yêu cầu.");
    expect(w.findAll("[data-testid=doc-row]")).toHaveLength(1);
  });

  it("menu_closes_with_escape_and_restores_focus", async () => {
    const { w } = await mountLibrary([doc({})]);
    const trigger = w.get("[data-testid=menu-trigger]");
    await trigger.trigger("click");
    await flushPromises();
    expect(document.activeElement).toBe(w.get("[data-testid=menu-delete]").element);
    await w.get("[data-testid=menu-delete]").trigger("keydown", { key: "Escape" });
    await flushPromises();
    expect(w.find("[role=menu]").exists()).toBe(false);
    expect(document.activeElement).toBe(trigger.element);
  });

  function dropFile(w: VueWrapper, f: File) {
    return w.get("[data-testid=dropzone]").trigger("drop", { dataTransfer: { files: [f] } });
  }
  const dupDialog = (w: VueWrapper) => w.findAll("dialog").find((d) => d.find("[data-testid=duplicate-body]").exists())!;
  const sameFile = () => {
    const f = new File(["x"], "HD.pdf", { type: "application/pdf" });
    Object.defineProperty(f, "size", { value: 4_404_019 });
    return f;
  };

  it("duplicate_dialog_choices", async () => {
    const { w } = await mountLibrary([doc({})]);
    await dropFile(w, sameFile());
    await flushPromises();
    expect(dupDialog(w).get("h2").text()).toBe("Tài liệu này có thể đã có trong kho");
    expect(w.get("[data-testid=duplicate-body]").text()).toBe(
      "\"HD.pdf\" (4,2 MB) trùng tên và kích thước với tài liệu đã tải 19/10/2026.",
    );
    expect(useUpload().items.value).toHaveLength(0); // chưa tải trước khi chọn
    await dupDialog(w).get("[data-testid=dialog-cancel]").trigger("click");
    await flushPromises();
    expect(useUpload().items.value).toHaveLength(0);
    expect(w.find("[data-testid=duplicate-body]").exists()).toBe(false);

    await dropFile(w, sameFile());
    await flushPromises();
    expect(dupDialog(w).get("[data-testid=dialog-confirm]").text()).toBe("Vẫn tải lên");
    await dupDialog(w).get("[data-testid=dialog-confirm]").trigger("click");
    await flushPromises();
    expect(useUpload().items.value).toHaveLength(1);
    expect(QuietXHR.sent).toBe(1);
  });

  it("different_file_uploads_without_dialog", async () => {
    const { w } = await mountLibrary([doc({})]);
    const other = new File(["x"], "Moi.pdf", { type: "application/pdf" });
    await dropFile(w, other);
    await flushPromises();
    expect(w.find("[data-testid=duplicate-body]").exists()).toBe(false);
    expect(useUpload().items.value).toHaveLength(1);
  });

  it("duplicate_flag_off", async () => {
    const { w } = await mountLibrary([doc({})], { dup: false });
    await dropFile(w, sameFile());
    await flushPromises();
    expect(w.find("[data-testid=duplicate-body]").exists()).toBe(false);
    expect(useUpload().items.value).toHaveLength(1);
  });
});
