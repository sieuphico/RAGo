import { describe, it, expect, vi, afterEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import { routes } from "@/router";
import ChatView from "@/views/ChatView.vue";
import { useChatStore } from "@/stores/chat";
import { useDocumentsStore } from "@/stores/documents";
import type { DocumentOut } from "@/api/types";
import { installFetch } from "./helpers/api";

const doc = (i: number): DocumentOut => ({
  docId: `d${i}`, name: `f${i}.pdf`, pageCount: 1, uploadedBy: "a@b.vn", uploadedAt: "2026-10-19T02:12:00Z",
  sizeBytes: 1, status: "READY", failureReason: null, usedOcr: false, canDelete: false,
});

async function mountChat(width: number, path = "/") {
  window.innerWidth = width;
  setActivePinia(createPinia());
  installFetch({});
  const router = createRouter({ history: createMemoryHistory(), routes });
  router.push(path);
  await router.isReady();
  const w = mount(ChatView, { global: { plugins: [router] } });
  await flushPromises();
  return { w, router };
}

describe("chat layout", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    window.innerWidth = 1024;
  });

  it("three_columns_at_1280", async () => {
    const { w } = await mountChat(1280, "/?doc=d1");
    expect(w.find("[data-testid=sidebar]").exists()).toBe(true);
    expect(w.find("[data-testid=conversation]").exists()).toBe(true);
    expect(w.find("[data-testid=viewer-slot]").exists()).toBe(true);
    expect(w.get("[data-testid=chat-shell]").classes()).toContain("layout-wide");
    expect(w.get("[data-testid=sidebar]").classes()).not.toContain("collapsed");
  });

  it("no_viewer_without_doc_param", async () => {
    const { w } = await mountChat(1440);
    expect(w.find("[data-testid=viewer-slot]").exists()).toBe(false);
  });

  it("collapsed_sidebar_1100", async () => {
    const { w } = await mountChat(1100, "/?doc=d1");
    expect(w.get("[data-testid=sidebar]").classes()).toContain("collapsed");
    expect(w.get("[data-testid=viewer-slot]").classes()).toContain("overlay");
  });

  it("single_column_below_1024_with_menu", async () => {
    const { w } = await mountChat(900);
    expect(w.get("[data-testid=chat-shell]").classes()).toContain("layout-narrow");
    expect(w.get("[data-testid=sidebar]").attributes("style") ?? "").toContain("display: none");
    await w.get("[data-testid=menu-button]").trigger("click");
    expect(w.get("[data-testid=sidebar]").attributes("style") ?? "").not.toContain("display: none");
  });

  it("new_session_resets", async () => {
    const { w, router } = await mountChat(1280, "/chat/abc");
    const chat = useChatStore();
    expect(chat.sessionId).toBe("abc");
    const spy = vi.spyOn(chat, "newSession");
    await w.get("[data-testid=new-session]").trigger("click");
    await flushPromises();
    expect(spy).toHaveBeenCalledTimes(1);
    expect(router.currentRoute.value.path).toBe("/");
    expect(chat.sessionId).toBeNull();
  });

  it("sidebar_doc_count", async () => {
    setActivePinia(createPinia());
    const docs = useDocumentsStore();
    docs.items = Array.from({ length: 125 }, (_, i) => doc(i));
    window.innerWidth = 1280;
    installFetch({});
    const router = createRouter({ history: createMemoryHistory(), routes });
    router.push("/");
    await router.isReady();
    const w = mount(ChatView, { global: { plugins: [router] } });
    await flushPromises();
    expect(w.get("[data-testid=sidebar-doc-count]").text()).toBe("125 tài liệu");
  });
});
