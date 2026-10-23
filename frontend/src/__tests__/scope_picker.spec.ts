import { describe, it, expect, vi, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { createPinia, setActivePinia } from "pinia";
import ScopePicker from "@/components/ScopePicker.vue";
import { useChatStore } from "@/stores/chat";
import { useDocumentsStore } from "@/stores/documents";
import { useToastState } from "@/composables/useToast";
import * as sse from "@/api/sse";
import type { DocumentOut } from "@/api/types";
import { installFetch, jsonRes } from "./helpers/api";

const doc = (id: string, name: string, status: DocumentOut["status"] = "READY"): DocumentOut => ({
  docId: id, name, pageCount: 1, uploadedBy: "a@b.vn", uploadedAt: "2026-10-19T02:12:00Z", sizeBytes: 1,
  status, failureReason: null, usedOcr: false, canDelete: false,
});

function setup() {
  setActivePinia(createPinia());
  const docs = useDocumentsStore();
  docs.items = [doc("A", "Hợp đồng A.pdf"), doc("B", "Báo giá B.pdf"), doc("C", "Đang xử lý.pdf", "PROCESSING")];
  const chat = useChatStore();
  const w = mount(ScopePicker, {
    props: { modelValue: chat.scope, "onUpdate:modelValue": (v: string[]) => { chat.scope = v; void w.setProps({ modelValue: v }); } },
    attachTo: document.body,
  });
  return { w, chat };
}

describe("ScopePicker", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    document.body.innerHTML = "";
    useToastState().items.splice(0);
  });

  it("sends_selected_scope", async () => {
    const { w, chat } = setup();
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    const stream = vi.spyOn(sse, "streamPost").mockImplementation(async (_p, _b, h) =>
      h.onDone({ messageId: "m", citationCount: 0, isNotFound: false, notFoundReason: null, notice: null, stopped: false }),
    );
    expect(w.get("[data-testid=scope-button]").text()).toContain("Phạm vi: Tất cả tài liệu");
    await w.get("[data-testid=scope-button]").trigger("click");
    await w.findAll("[data-testid=scope-option]")[0]!.trigger("click");
    await nextTick();
    expect(chat.scope).toEqual(["A"]);
    expect(w.get("[data-testid=scope-button]").text()).toContain("Đang hỏi trong 1 tài liệu");
    await chat.send("hỏi");
    expect((stream.mock.calls[0]![1] as { scopeDocIds: string[] }).scopeDocIds).toEqual(["A"]);
  });

  it("select_all_resets", async () => {
    const { w, chat } = setup();
    chat.scope = ["A", "B"];
    await w.setProps({ modelValue: ["A", "B"] });
    expect(w.get("[data-testid=scope-button]").text()).toContain("Đang hỏi trong 2 tài liệu");
    await w.get("[data-testid=scope-button]").trigger("click");
    await w.get("[data-testid=scope-option-all]").trigger("click");
    await nextTick();
    expect(chat.scope).toEqual([]);
    expect(w.get("[data-testid=scope-button]").text()).toContain("Phạm vi: Tất cả tài liệu");
  });

  it("toggle_off_selected_doc", async () => {
    const { w, chat } = setup();
    chat.scope = ["A"];
    await w.setProps({ modelValue: ["A"] });
    await w.get("[data-testid=scope-button]").trigger("click");
    const opt = w.findAll("[data-testid=scope-option]")[0]!;
    expect(opt.attributes("aria-selected")).toBe("true");
    await opt.trigger("click");
    expect(chat.scope).toEqual([]);
  });

  it("removed_doc_notice", async () => {
    const { chat } = setup();
    installFetch({ "POST /api/v1/chat/sessions": () => jsonRes(201, { sessionId: "s1" }) });
    vi.spyOn(sse, "streamPost").mockImplementation(async (_p, _b, h) => {
      h.onStatus({ stage: "searching", docCount: 1, messageId: "m", scopeRemoved: ["B"] });
      h.onDone({ messageId: "m", citationCount: 0, isNotFound: false, notFoundReason: null, notice: null, stopped: false });
    });
    chat.scope = ["A", "B"];
    await chat.send("q");
    expect(useToastState().items.map((i) => i.text)).toContain("Một tài liệu trong phạm vi đã bị xóa và được bỏ khỏi phạm vi.");
    expect(chat.scope).toEqual(["A"]);
  });

  it("keyboard_navigation", async () => {
    const { w, chat } = setup();
    const button = w.get("[data-testid=scope-button]");
    (button.element as HTMLButtonElement).focus();
    await button.trigger("keydown", { key: "Enter" });
    await nextTick();
    expect(w.find("[data-testid=scope-popup]").exists()).toBe(true);
    const box = w.get("[data-testid=scope-listbox]");
    expect(document.activeElement).toBe(box.element);
    await box.trigger("keydown", { key: "ArrowDown" });
    await box.trigger("keydown", { key: " " });
    await nextTick();
    expect(chat.scope).toEqual(["A"]); // mục thứ nhất được chọn
    expect(box.attributes("aria-activedescendant")).toBe(w.findAll("[data-testid=scope-option]")[0]!.attributes("id"));
    await box.trigger("keydown", { key: "Escape" });
    await nextTick();
    expect(w.find("[data-testid=scope-popup]").exists()).toBe(false);
    expect(document.activeElement).toBe(button.element);
  });

  it("only_ready_listed", async () => {
    const { w } = setup();
    await w.get("[data-testid=scope-button]").trigger("click");
    const names = w.findAll("[data-testid=scope-option]").map((o) => o.text());
    expect(names).toHaveLength(2);
    expect(names.join(" ")).not.toContain("Đang xử lý");
    expect(w.get("[data-testid=scope-listbox]").attributes("aria-multiselectable")).toBe("true");
  });

  it("filter_by_name_ignores_diacritics", async () => {
    const { w } = setup();
    await w.get("[data-testid=scope-button]").trigger("click");
    await w.get("[data-testid=scope-filter]").setValue("bao gia");
    const opts = w.findAll("[data-testid=scope-option]");
    expect(opts).toHaveLength(1);
    expect(opts[0]!.text()).toContain("Báo giá B.pdf");
  });
});
