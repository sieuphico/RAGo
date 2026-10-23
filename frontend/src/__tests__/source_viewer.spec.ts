import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import { routes } from "@/router";
import SourceViewer from "@/components/SourceViewer.vue";
import ChatView from "@/views/ChatView.vue";
import { useChatStore } from "@/stores/chat";
import * as telemetry from "@/api/telemetry";
import { installFetch } from "./helpers/api";

async function makeRouter(path: string) {
  const router = createRouter({ history: createMemoryHistory(), routes });
  router.push(path);
  await router.isReady();
  return router;
}

function stubFile(status: number | "network") {
  const fn = vi.fn(async () => {
    if (status === "network") throw new TypeError("net");
    return new Response(null, { status });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

const props = { docId: "d1", docName: "HD_ABC_2026.pdf", page: 12, pageCount: 48 };

describe("SourceViewer", () => {
  beforeEach(() => {
    window.innerWidth = 1440;
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    window.innerWidth = 1024;
    document.body.innerHTML = "";
  });

  it("opens_at_cited_page", async () => {
    const fetchMock = stubFile(206);
    const router = await makeRouter("/?doc=d1&page=12");
    const w = mount(SourceViewer, { props, global: { plugins: [router] } });
    await flushPromises();
    expect((w.get("[data-testid=viewer-iframe]").element as HTMLIFrameElement).getAttribute("src")).toBe(
      "/api/v1/documents/d1/file#page=12",
    );
    expect(w.get("iframe").attributes("title")).toBe("Trang nguồn: HD_ABC_2026.pdf, trang 12");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, { headers: Record<string, string> }];
    expect(url).toBe("/api/v1/documents/d1/file");
    expect(init.headers.Range).toBe("bytes=0-0");
    expect(w.get("[data-testid=viewer-page]").text()).toBe("Trang 12 / 48");
  });

  it("next_page_updates_url", async () => {
    stubFile(206);
    const router = await makeRouter("/?doc=d1&page=12");
    const w = mount(SourceViewer, { props, global: { plugins: [router] } });
    await flushPromises();
    await w.get("[data-testid=viewer-next]").trigger("click");
    await flushPromises();
    expect(w.get("iframe").attributes("src")).toBe("/api/v1/documents/d1/file#page=13");
    expect(router.currentRoute.value.query.page).toBe("13");
    expect(router.currentRoute.value.query.doc).toBe("d1");
    expect(w.emitted("page")).toEqual([[13]]);
    await w.get("[data-testid=viewer-prev]").trigger("click");
    expect(w.get("iframe").attributes("src")).toContain("#page=12");
  });

  it("page_buttons_respect_bounds", async () => {
    stubFile(206);
    const router = await makeRouter("/?doc=d1&page=1");
    const w = mount(SourceViewer, { props: { ...props, page: 1, pageCount: 1 }, global: { plugins: [router] } });
    await flushPromises();
    expect(w.get("[data-testid=viewer-prev]").attributes("disabled")).toBeDefined();
    expect(w.get("[data-testid=viewer-next]").attributes("disabled")).toBeDefined();
  });

  it("esc_closes_and_restores_focus", async () => {
    stubFile(206);
    const chip = document.createElement("button");
    document.body.appendChild(chip);
    chip.focus();
    const router = await makeRouter("/?doc=d1&page=12");
    const w = mount(SourceViewer, { props, global: { plugins: [router] }, attachTo: document.body });
    await flushPromises();
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    await flushPromises();
    expect(w.emitted("close")).toHaveLength(1);
    expect(document.activeElement).toBe(chip);
    expect(router.currentRoute.value.query.doc).toBeUndefined();
    expect(router.currentRoute.value.query.page).toBeUndefined();
  });

  it("close_button_closes", async () => {
    stubFile(206);
    const router = await makeRouter("/?doc=d1&page=12");
    const w = mount(SourceViewer, { props, global: { plugins: [router] } });
    await flushPromises();
    await w.get("[data-testid=viewer-close]").trigger("click");
    expect(w.emitted("close")).toHaveLength(1);
  });

  it("deleted_document", async () => {
    stubFile(404);
    const router = await makeRouter("/?doc=d1&page=12");
    const w = mount(SourceViewer, { props, global: { plugins: [router] } });
    await flushPromises();
    expect(w.get("[data-testid=viewer-deleted]").text()).toBe("Tài liệu đã bị xóa");
    expect(w.find("iframe").exists()).toBe(false);
  });

  it("load_error_retry", async () => {
    let calls = 0;
    vi.stubGlobal("fetch", async () => {
      calls += 1;
      if (calls === 1) throw new TypeError("net");
      return new Response(null, { status: 206 });
    });
    const router = await makeRouter("/?doc=d1&page=12");
    const w = mount(SourceViewer, { props, global: { plugins: [router] } });
    await flushPromises();
    expect(w.get("[data-testid=viewer-error]").text()).toContain("Không mở được trang.");
    expect(w.find("iframe").exists()).toBe(false);
    await w.get("[data-testid=viewer-retry]").trigger("click");
    await flushPromises();
    expect(w.find("iframe").exists()).toBe(true);
  });

  it("overlay_below_1280", async () => {
    window.innerWidth = 1100;
    stubFile(206);
    const router = await makeRouter("/?doc=d1&page=12");
    const w = mount(SourceViewer, { props, global: { plugins: [router] }, attachTo: document.body });
    await flushPromises();
    expect(w.get("[data-testid=source-viewer]").attributes("role")).toBe("dialog");
    expect(w.get("[data-testid=source-viewer]").attributes("aria-modal")).toBe("true");
    expect(document.activeElement).toBe(w.get("[data-testid=viewer-close]").element);
    // Giam focus: Tab ở phần tử cuối quay về phần tử đầu.
    const items = Array.from((w.element as HTMLElement).querySelectorAll<HTMLElement>("button:not([disabled]), iframe"));
    items[items.length - 1]!.focus();
    const ev = new KeyboardEvent("keydown", { key: "Tab", bubbles: true, cancelable: true });
    document.dispatchEvent(ev);
    expect(ev.defaultPrevented).toBe(true);
    expect(document.activeElement).toBe(items[0]);
  });

  it("not_dialog_at_1440", async () => {
    stubFile(206);
    const router = await makeRouter("/?doc=d1&page=12");
    const w = mount(SourceViewer, { props, global: { plugins: [router] } });
    await flushPromises();
    expect(w.get("[data-testid=source-viewer]").attributes("aria-modal")).toBeUndefined();
  });
});

describe("ChatView opens citations", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("tracks_citation_clicked", async () => {
    setActivePinia(createPinia());
    installFetch({});
    const track = vi.spyOn(telemetry, "track").mockImplementation(() => {});
    const router = await makeRouter("/");
    const chat = useChatStore();
    chat.messages = [
      {
        id: "a", role: "assistant", messageId: "m1", text: "Có [[1]]", state: "COMPLETED", sentAt: 0,
        citations: [{ index: 1, docId: "d1", docName: "HD_ABC_2026.pdf", page: 12, snippet: "s", deleted: false }],
      },
    ];
    const w = mount(ChatView, { global: { plugins: [router] } });
    await flushPromises();
    await w.get("[data-testid=citation]").trigger("click");
    await flushPromises();
    expect(track).toHaveBeenCalledWith("citation_clicked", { question_id: "m1", doc_id: "d1", page: 12 });
    expect(router.currentRoute.value.query).toMatchObject({ doc: "d1", page: "12" });
    expect(w.find("[data-testid=source-viewer]").exists()).toBe(true);
    expect(w.get("[data-testid=viewer-name]").text()).toBe("HD_ABC_2026.pdf");
  });
});
