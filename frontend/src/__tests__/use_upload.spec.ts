import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { createPinia, setActivePinia } from "pinia";
import { useUpload, resetUploadsForTest } from "@/composables/useUpload";
import { useDocumentsStore } from "@/stores/documents";
import { useAuthStore } from "@/stores/auth";
import UploadQueue from "@/components/UploadQueue.vue";
import { setAuthExpiredHandler } from "@/api/client";
import * as telemetry from "@/api/telemetry";

class FakeXHR {
  static all: FakeXHR[] = [];
  upload: { onprogress: ((e: ProgressEvent) => void) | null } = { onprogress: null };
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onabort: (() => void) | null = null;
  ontimeout: (() => void) | null = null;
  withCredentials = false;
  status = 0;
  responseText = "";
  method = "";
  url = "";
  headers: Record<string, string> = {};
  body: FormData | null = null;
  sent = false;
  constructor() {
    FakeXHR.all.push(this);
  }
  open(m: string, u: string) {
    this.method = m;
    this.url = u;
  }
  setRequestHeader(k: string, v: string) {
    this.headers[k] = v;
  }
  send(b: FormData) {
    this.body = b;
    this.sent = true;
  }
  progress(loaded: number, total: number) {
    this.upload.onprogress?.({ lengthComputable: true, loaded, total } as ProgressEvent);
  }
  respond(status: number, body: unknown) {
    this.status = status;
    this.responseText = JSON.stringify(body);
    this.onload?.();
  }
}

const pdf = (name: string, bytes = 1024) => {
  const f = new File(["x"], name, { type: "application/pdf" });
  Object.defineProperty(f, "size", { value: bytes });
  return f;
};
const accepted = (name: string) => ({ results: [{ name, docId: `id-${name}`, status: "PROCESSING", error: null }] });
const sent = () => FakeXHR.all.filter((x) => x.sent);

describe("useUpload", () => {
  beforeEach(() => {
    FakeXHR.all = [];
    vi.stubGlobal("XMLHttpRequest", FakeXHR);
    setActivePinia(createPinia());
    useAuthStore().me = { email: "minh@congty.vn", role: "TEAM_LEAD", allowed: true };
    resetUploadsForTest();
    vi.spyOn(telemetry, "track").mockImplementation(() => {});
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("uploads_each_file", () => {
    const up = useUpload();
    const docs = useDocumentsStore();
    up.enqueue([pdf("a.pdf"), pdf("b.pdf"), pdf("c.pdf")]);
    expect(sent()).toHaveLength(2); // tối đa 2 cùng lúc
    expect(sent()[0]!.method).toBe("POST");
    expect(sent()[0]!.url).toBe("/api/v1/documents");
    expect(sent()[0]!.headers["X-Requested-With"]).toBe("cwd");
    expect(sent()[0]!.withCredentials).toBe(true);
    expect((sent()[0]!.body as FormData).getAll("files")).toHaveLength(1);
    sent()[0]!.respond(202, accepted("a.pdf"));
    expect(sent()).toHaveLength(3); // tệp thứ 3 được gửi khi có chỗ
    sent()[1]!.respond(202, accepted("b.pdf"));
    sent()[2]!.respond(202, accepted("c.pdf"));
    expect(up.items.value.map((i) => i.state)).toEqual(["DONE", "DONE", "DONE"]);
    expect(docs.items).toHaveLength(3);
    expect(docs.items.every((d) => d.status === "PROCESSING" && d.uploadedBy === "minh@congty.vn")).toBe(true);
    expect(docs.items.map((d) => d.name).sort()).toEqual(["a.pdf", "b.pdf", "c.pdf"]);
  });

  it("ten_valid_files_all_done", () => {
    const up = useUpload();
    up.enqueue(Array.from({ length: 10 }, (_, i) => pdf(`f${i}.pdf`)));
    for (let i = 0; i < 10; i++) {
      const x = sent()[i]!;
      x.respond(202, accepted(`f${i}.pdf`));
    }
    expect(up.items.value.filter((i) => i.state === "DONE")).toHaveLength(10);
  });

  it("progress_updates", async () => {
    const up = useUpload();
    up.enqueue([pdf("a.pdf", 1000)]);
    sent()[0]!.progress(500, 1000);
    expect(up.items.value[0]!.progress).toBe(50);
    const w = mount(UploadQueue, { global: { plugins: [] } });
    await nextTick();
    expect(w.get("[data-testid=upload-row]").text()).toContain("Đang tải lên (50%)");
  });

  it("network_error_interrupted", () => {
    const up = useUpload();
    up.enqueue([pdf("1.pdf"), pdf("2.pdf"), pdf("3.pdf")]);
    sent()[0]!.respond(202, accepted("1.pdf"));
    sent()[1]!.onerror?.();
    sent()[2]!.respond(202, accepted("3.pdf"));
    expect(up.items.value.map((i) => i.state)).toEqual(["DONE", "INTERRUPTED", "DONE"]);
  });

  it("retry_single_failed_file", async () => {
    const up = useUpload();
    up.enqueue([pdf("1.pdf"), pdf("2.pdf"), pdf("3.pdf")]);
    sent()[0]!.respond(202, accepted("1.pdf"));
    sent()[1]!.onerror?.();
    sent()[2]!.respond(202, accepted("3.pdf"));
    const before = FakeXHR.all.length;
    const w = mount(UploadQueue);
    expect(w.get("[data-testid=upload-row]").text()).toContain("Tải lên bị gián đoạn");
    await w.get("[data-testid=upload-retry]").trigger("click");
    expect(FakeXHR.all.length).toBe(before + 1);
    const again = FakeXHR.all[before]!;
    expect((again.body as FormData).get("files")).toBeInstanceOf(File);
    expect(((again.body as FormData).get("files") as File).name).toBe("2.pdf");
    again.respond(202, accepted("2.pdf"));
    expect(up.items.value[1]!.state).toBe("DONE");
  });

  it("server_rejection_shown", async () => {
    const up = useUpload();
    up.enqueue([pdf("x.pdf")]);
    sent()[0]!.respond(202, { results: [{ name: "x.pdf", docId: null, status: null, error: "FILE_NOT_PDF" }] });
    expect(up.items.value[0]).toMatchObject({ state: "REJECTED", errorCode: "FILE_NOT_PDF" });
    const w = mount(UploadQueue);
    expect(w.get("[data-testid=upload-rejected]").text()).toBe("Chỉ hỗ trợ tệp PDF.");
    expect(useDocumentsStore().items).toHaveLength(0);
  });

  it("upload_started_tracked", () => {
    const track = vi.spyOn(telemetry, "track");
    useUpload().enqueue([pdf("a.pdf", 1.5 * 1024 * 1024), pdf("b.pdf", 2.5 * 1024 * 1024)]);
    expect(track).toHaveBeenCalledTimes(1);
    expect(track).toHaveBeenCalledWith("document_upload_started", { file_count: 2, total_size_mb: 4 });
  });

  it("auth_expired_triggers_reauth_flow_and_keeps_file", () => {
    const handler = vi.fn();
    setAuthExpiredHandler(handler);
    const up = useUpload();
    up.enqueue([pdf("a.pdf")]);
    sent()[0]!.respond(401, { code: "AUTH_EXPIRED", retryable: false });
    expect(handler).toHaveBeenCalledTimes(1);
    expect(up.items.value[0]!.state).toBe("INTERRUPTED");
  });

  it("server_error_is_retryable_and_validation_is_rejected", () => {
    const up = useUpload();
    up.enqueue([pdf("a.pdf"), pdf("b.pdf")]);
    sent()[0]!.respond(500, { code: "INTERNAL", retryable: false });
    sent()[1]!.respond(400, { code: "FILE_TOO_MANY", retryable: false });
    expect(up.items.value.map((i) => i.state)).toEqual(["INTERRUPTED", "REJECTED"]);
  });
});
