import { describe, it, expect, vi, afterEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import { routes } from "@/router";
import ChatView from "@/views/ChatView.vue";
import HistoryList from "@/components/HistoryList.vue";
import { groupSessions } from "@/utils/history";
import { useFeaturesStore } from "@/stores/features";
import { useChatStore } from "@/stores/chat";
import type { SessionSummaryOut } from "@/api/types";
import { calls, installFetch, jsonRes } from "./helpers/api";

const at = (iso: string): SessionSummaryOut => ({
  sessionId: `s-${iso}`, title: `Phiên ${iso}`, createdAt: iso, lastMessageAt: iso,
});

describe("history", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("groups_by_time", () => {
    const now = new Date(2026, 11, 21, 10, 0); // 21/12/2026 10:00 giờ máy
    const today = at(new Date(2026, 11, 21, 8, 0).toISOString());
    const three = at(new Date(2026, 11, 18, 9, 0).toISOString());
    const thirty = at(new Date(2026, 10, 21, 9, 0).toISOString());
    const g = groupSessions([today, three, thirty], now);
    expect(g.today).toEqual([today]);
    expect(g.last7).toEqual([three]);
    expect(g.older).toEqual([thirty]);
    const edge = at(new Date(2026, 11, 14, 23, 0).toISOString()); // đúng 7 ngày trước (theo ngày lịch)
    expect(groupSessions([edge], now).last7).toEqual([edge]);
    const eight = at(new Date(2026, 11, 13, 23, 0).toISOString());
    expect(groupSessions([eight], now).older).toEqual([eight]);
  });

  async function mountChat(routesMap: Parameters<typeof installFetch>[0], flags = { history: true }) {
    setActivePinia(createPinia());
    useFeaturesStore().flags = { ...useFeaturesStore().flags, ...flags };
    const fetchMock = installFetch(routesMap);
    const router = createRouter({ history: createMemoryHistory(), routes });
    router.push("/");
    await router.isReady();
    window.innerWidth = 1440;
    const w = mount(ChatView, { global: { plugins: [router] }, attachTo: document.body });
    await flushPromises();
    return { w, router, fetchMock };
  }

  it("reopens_session_with_citations", async () => {
    const now = new Date().toISOString();
    const { w, router } = await mountChat({
      "GET /api/v1/chat/sessions": () => jsonRes(200, { items: [{ sessionId: "s1", title: "Thời hạn hợp đồng?", createdAt: now, lastMessageAt: now }] }),
      "GET /api/v1/chat/sessions/s1": () =>
        jsonRes(200, {
          sessionId: "s1", title: "Thời hạn hợp đồng?", createdAt: now, scopeDocIds: [],
          messages: [
            { messageId: "u1", role: "user", text: "Thời hạn hợp đồng?", status: "COMPLETED", createdAt: now, isNotFound: false, citations: [], rating: null },
            {
              messageId: "a1", role: "assistant", text: "24 tháng [[1]].", status: "COMPLETED", createdAt: now, isNotFound: false, rating: null,
              citations: [{ index: 1, docId: "d1", docName: "HD_ABC.pdf", page: 12, snippet: "s", deleted: true }],
            },
          ],
        }),
    });
    const link = w.get("[data-testid=history-item]");
    expect(link.text()).toBe("Thời hạn hợp đồng?");
    expect(w.find("[data-testid=group-today]").exists()).toBe(true);
    await link.trigger("click");
    await flushPromises();
    expect(router.currentRoute.value.path).toBe("/chat/s1");
    const chat = useChatStore();
    expect(chat.messages).toHaveLength(2);
    const chip = w.get("[data-testid=citation]");
    expect(chip.attributes("disabled")).toBeDefined();
    expect(w.get("[data-testid=history-item]").attributes("aria-current")).toBe("page");
  });

  it("empty_and_error_states", async () => {
    let fail = false;
    const { w } = await mountChat({
      "GET /api/v1/chat/sessions": () => (fail ? jsonRes(500, { code: "INTERNAL", retryable: false }) : jsonRes(200, { items: [] })),
    });
    expect(w.get("[data-testid=history-empty]").text()).toBe("Chưa có phiên nào");
    fail = true;
    const h = mount(HistoryList, { global: { plugins: [createRouter({ history: createMemoryHistory(), routes })] } });
    await flushPromises();
    expect(h.get("[data-testid=history-error]").text()).toContain("Không tải được lịch sử.");
    fail = false;
    await h.get("[data-testid=history-retry]").trigger("click");
    await flushPromises();
    expect(h.find("[data-testid=history-error]").exists()).toBe(false);
  });

  it("loading_state", async () => {
    setActivePinia(createPinia());
    useFeaturesStore().flags = { ...useFeaturesStore().flags, history: true };
    installFetch({ "GET /api/v1/chat/sessions": () => new Promise<Response>(() => {}) });
    const h = mount(HistoryList, { global: { plugins: [createRouter({ history: createMemoryHistory(), routes })] } });
    await flushPromises();
    expect(h.findAll(".skeleton-row")).toHaveLength(3);
  });

  it("flag_off_hidden", async () => {
    const { w, fetchMock } = await mountChat({ "GET /api/v1/chat/sessions": () => jsonRes(200, { items: [] }) }, { history: false });
    expect(calls(fetchMock)).not.toContain("GET /api/v1/chat/sessions");
    expect(w.find("[data-testid=history]").exists()).toBe(false);
  });

  it("refreshes_after_a_question_completes", async () => {
    const { fetchMock } = await mountChat({ "GET /api/v1/chat/sessions": () => jsonRes(200, { items: [] }) });
    const before = calls(fetchMock).filter((c) => c === "GET /api/v1/chat/sessions").length;
    const chat = useChatStore();
    chat.busy = true;
    await flushPromises();
    chat.busy = false;
    await flushPromises();
    expect(calls(fetchMock).filter((c) => c === "GET /api/v1/chat/sessions").length).toBe(before + 1);
  });
});
