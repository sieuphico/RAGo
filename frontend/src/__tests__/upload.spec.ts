import { describe, it, expect, vi, afterEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import DropZone from "@/components/DropZone.vue";
import LibraryView from "@/views/LibraryView.vue";
import { useAuthStore } from "@/stores/auth";
import * as telemetry from "@/api/telemetry";
import { validateFiles } from "@/utils/validateFiles";
import type { Role } from "@/api/types";
import { installFetch, jsonRes } from "./helpers/api";

const MB = 1024 * 1024;
function file(name: string, size: number): File {
  const f = new File(["x"], name, { type: "application/pdf" });
  Object.defineProperty(f, "size", { value: size });
  return f;
}

describe("validateFiles", () => {
  it("rejects_non_pdf_and_oversize", () => {
    const a = file("a.docx", MB), b = file("b.pdf", 51 * MB), c = file("c.pdf", MB);
    const r = validateFiles([a, b, c], { maxFiles: 10, maxBytes: 50 * MB });
    expect(r.accepted).toEqual([c]);
    expect(r.rejected).toEqual([
      { file: a, code: "FILE_NOT_PDF" },
      { file: b, code: "FILE_TOO_LARGE" },
    ]);
  });

  it("extension_is_case_insensitive_and_limit_is_inclusive", () => {
    const ok = file("BAO CAO.PDF", 50 * MB);
    expect(validateFiles([ok]).accepted).toEqual([ok]);
  });

  it("too_many_files", () => {
    const files = Array.from({ length: 12 }, (_, i) => file(`f${i}.pdf`, MB));
    const r = validateFiles(files, { maxFiles: 10, maxBytes: 50 * MB });
    expect(r.accepted).toEqual(files.slice(0, 10));
    expect(r.rejected.map((x) => x.code)).toEqual(["FILE_TOO_MANY", "FILE_TOO_MANY"]);
    expect(r.rejected.map((x) => x.file)).toEqual(files.slice(10));
  });
});

describe("DropZone", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("keeps_valid_files_in_batch", async () => {
    const track = vi.spyOn(telemetry, "track").mockImplementation(() => {});
    const w = mount(DropZone);
    const png = file("x.png", MB), pdf = file("y.pdf", MB);
    await w.get("[data-testid=dropzone]").trigger("drop", { dataTransfer: { files: [png, pdf] } });
    expect(w.emitted("accepted")).toEqual([[[pdf]]]);
    expect(w.get("[data-testid=rejections]").text()).toBe("x.png – Chỉ hỗ trợ tệp PDF.");
    expect(track).toHaveBeenCalledWith("document_upload_rejected", { reason: "not_pdf" });
  });

  it("reports_each_rejection_reason", async () => {
    const track = vi.spyOn(telemetry, "track").mockImplementation(() => {});
    const w = mount(DropZone);
    const files = [file("a.txt", 1), file("big.pdf", 60 * MB), ...Array.from({ length: 11 }, (_, i) => file(`f${i}.pdf`, MB))];
    await w.get("[data-testid=dropzone]").trigger("drop", { dataTransfer: { files } });
    expect(track.mock.calls.map((c) => (c[1] as { reason: string }).reason)).toEqual(["not_pdf", "too_large", "too_many"]);
    const lines = w.findAll("[data-testid=rejections] li").map((l) => l.text());
    expect(lines).toContain("big.pdf – Tệp vượt quá 50 MB.");
    expect(lines).toContain("f10.pdf – Chỉ tải tối đa 10 tệp mỗi lần.");
    expect((w.emitted("accepted")![0]![0] as File[]).length).toBe(10);
  });

  it("nothing_accepted_emits_nothing", async () => {
    vi.spyOn(telemetry, "track").mockImplementation(() => {});
    const w = mount(DropZone);
    await w.get("[data-testid=dropzone]").trigger("drop", { dataTransfer: { files: [file("a.txt", 1)] } });
    expect(w.emitted("accepted")).toBeUndefined();
  });

  it("keyboard_choose_file", async () => {
    const w = mount(DropZone, { attachTo: document.body });
    const input = w.get("[data-testid=file-input]").element as HTMLInputElement;
    const click = vi.spyOn(input, "click");
    const btn = w.get("[data-testid=pick]");
    expect(btn.element.tagName).toBe("BUTTON"); // phần tử focus được; Enter/Space kích hoạt click
    (btn.element as HTMLButtonElement).focus();
    expect(document.activeElement).toBe(btn.element);
    await btn.trigger("click");
    expect(click).toHaveBeenCalledTimes(1);
    expect(input.getAttribute("accept")).toBe("application/pdf,.pdf");
    expect(input.multiple).toBe(true);
    w.unmount();
  });

  it("drag_over_highlights", async () => {
    const w = mount(DropZone);
    await w.get("[data-testid=dropzone]").trigger("dragover");
    expect(w.get("[data-testid=dropzone]").classes()).toContain("is-over");
    await w.get("[data-testid=dropzone]").trigger("dragleave");
    expect(w.get("[data-testid=dropzone]").classes()).not.toContain("is-over");
  });
});

describe("LibraryView dropzone visibility", () => {
  afterEach(() => vi.unstubAllGlobals());

  async function mountFor(role: Role) {
    setActivePinia(createPinia());
    installFetch({ "GET /api/v1/documents": () => jsonRes(200, { items: [], total: 0 }) });
    const auth = useAuthStore();
    auth.me = { email: "a@b.vn", role, allowed: true };
    auth.status = "allowed";
    const w = mount(LibraryView);
    await flushPromises();
    return w;
  }

  it("hidden_for_non_team_lead", async () => {
    for (const role of ["BD_USER", "ADMIN", "SPONSOR"] as Role[]) {
      expect((await mountFor(role)).find("[data-testid=dropzone]").exists(), role).toBe(false);
    }
    expect((await mountFor("TEAM_LEAD")).find("[data-testid=dropzone]").exists()).toBe(true);
  });
});
