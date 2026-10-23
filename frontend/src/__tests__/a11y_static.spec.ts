// Kiểm tra khả năng tiếp cận tĩnh trong jsdom (T-522). Quét axe trên trình duyệt thật nằm ở e2e/a11y.spec.ts (chưa chạy được: FQ-07).
import { describe, it, expect, vi, afterEach } from "vitest";
import { mount, flushPromises, type VueWrapper } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { routes } from "@/router";
import { useAuthStore } from "@/stores/auth";
import { useChatStore } from "@/stores/chat";
import LoginView from "@/views/LoginView.vue";
import DeniedView from "@/views/DeniedView.vue";
import LibraryView from "@/views/LibraryView.vue";
import ChatView from "@/views/ChatView.vue";
import AdminUsersView from "@/views/AdminUsersView.vue";
import AdminAuditView from "@/views/AdminAuditView.vue";
import MetricsView from "@/views/MetricsView.vue";
import type { Component } from "vue";
import { installFetch, jsonRes } from "./helpers/api";

const DOC = {
  docId: "d1", name: "HD_ABC.pdf", pageCount: 5, uploadedBy: "minh@congty.vn", uploadedAt: "2026-10-19T02:12:00Z",
  sizeBytes: 100, status: "READY", failureReason: null, usedOcr: false, canDelete: true,
};

function accessibleName(el: Element, root: ParentNode): string {
  const aria = el.getAttribute("aria-label");
  if (aria?.trim()) return aria.trim();
  const by = el.getAttribute("aria-labelledby");
  if (by) return by.split(/\s+/).map((id) => root.querySelector(`[id="${id}"]`)?.textContent ?? "").join(" ").trim();
  const id = el.getAttribute("id");
  if (id) {
    const label = root.querySelector(`label[for="${id}"]`);
    if (label?.textContent?.trim()) return label.textContent.trim();
  }
  if (el.tagName === "IFRAME" || el.tagName === "svg") return (el.getAttribute("title") ?? "").trim();
  return (el.textContent ?? "").trim() || (el.getAttribute("title") ?? "").trim() || (el.getAttribute("placeholder") ?? "").trim();
}

function audit(w: VueWrapper, name: string) {
  const root = w.element as HTMLElement;
  const doc = root.ownerDocument;
  const scope: ParentNode = doc;
  const problems: string[] = [];
  for (const el of Array.from(root.querySelectorAll("button, input:not([type=hidden]), select, textarea, iframe, a[href]"))) {
    if (el.getAttribute("aria-hidden") === "true") continue;
    if (!accessibleName(el, scope)) problems.push(`${name}: ${el.tagName.toLowerCase()} không có tên truy cập được`);
  }
  for (const img of Array.from(root.querySelectorAll("svg"))) {
    if (img.getAttribute("role") === "img" && !img.getAttribute("aria-label")) problems.push(`${name}: svg role=img thiếu aria-label`);
    if (img.getAttribute("role") !== "img" && img.getAttribute("aria-hidden") !== "true") problems.push(`${name}: svg trang trí phải aria-hidden`);
  }
  for (const table of Array.from(root.querySelectorAll("table"))) {
    if (!table.querySelector("caption")) problems.push(`${name}: bảng thiếu caption`);
    if (!table.querySelector("th[scope]")) problems.push(`${name}: bảng thiếu th[scope]`);
  }
  expect(root.querySelectorAll("h1").length, `${name}: đúng 1 h1`).toBe(1);
  expect((root.matches("main#main") ? 1 : 0) + root.querySelectorAll("main#main").length, `${name}: đúng 1 main#main`).toBe(1);
  expect(problems).toEqual([]);
}

async function mountView(component: Component, path: string, role: string, routesMap: Parameters<typeof installFetch>[0]) {
  setActivePinia(createPinia());
  installFetch(routesMap);
  const auth = useAuthStore();
  auth.me = { email: "quantri@congty.vn", role: role as never, allowed: true };
  auth.status = "allowed";
  const router = createRouter({ history: createMemoryHistory(), routes });
  router.push(path);
  await router.isReady();
  const w = mount(component, { global: { plugins: [router] }, attachTo: document.body });
  await flushPromises();
  return w;
}

describe("a11y (static)", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    document.body.innerHTML = "";
  });

  it("login_and_denied", async () => {
    setActivePinia(createPinia());
    const router = createRouter({ history: createMemoryHistory(), routes });
    router.push("/login?expired=1");
    await router.isReady();
    audit(mount(LoginView, { global: { plugins: [router] } }), "login");
    audit(mount(DeniedView, { global: { plugins: [router] } }), "denied");
  });

  it("library_with_rows_and_dropzone", async () => {
    const w = await mountView(LibraryView, "/library", "TEAM_LEAD", {
      "GET /api/v1/documents": () => jsonRes(200, { items: [DOC, { ...DOC, docId: "d2", status: "FAILED", failureReason: "FILE_CORRUPTED" }], total: 2 }),
    });
    audit(w, "library");
  });

  it("chat_with_answer_and_viewer", async () => {
    setActivePinia(createPinia());
    const chat = useChatStore();
    chat.messages = [
      { id: "u", role: "user", text: "q", state: "COMPLETED", citations: [], sentAt: 0 },
      {
        id: "a", role: "assistant", messageId: "m1", text: "Có [[1]]", state: "COMPLETED", sentAt: 0,
        citations: [{ index: 1, docId: "d1", docName: "HD_ABC.pdf", page: 2, snippet: "s", deleted: false }],
      },
    ];
    const w = await mountView(ChatView, "/?doc=d1&page=2", "BD_USER", {
      "GET /api/v1/documents": () => jsonRes(200, { items: [DOC], total: 1 }),
      "GET /api/v1/documents/d1/file": () => new Response(null, { status: 206 }),
    });
    audit(w, "chat");
  });

  it("admin_and_metrics", async () => {
    audit(
      await mountView(AdminUsersView, "/admin/users", "ADMIN", {
        "GET /api/v1/admin/users": () => jsonRes(200, { items: [{ email: "a@b.vn", role: "ADMIN", addedBy: "s", addedAt: "2026-10-19T02:12:00Z" }], count: 1, limit: 20 }),
      }),
      "admin-users",
    );
    audit(
      await mountView(AdminAuditView, "/admin/audit", "ADMIN", {
        "GET /api/v1/admin/audit-log": () => jsonRes(200, { items: [{ actor: "a", action: "UPLOAD", docId: "d", docName: "x.pdf", at: "2026-10-19T02:12:00Z" }] }),
      }),
      "admin-audit",
    );
    audit(
      await mountView(MetricsView, "/metrics", "ADMIN", {
        "GET /api/v1/metrics/weekly": () =>
          jsonRes(200, {
            week: "2026-12-21", weeks: ["2026-12-21"], updatedAt: "2026-12-28T06:00:00Z",
            metrics: { wauPercent: 70, wauCount: 7, allowedCount: 10, questions: 5, latencyP50Ms: 1000, latencyP90Ms: 2000, thumbsUpPercent: 80, notFoundPercent: 10 },
            series: [{ week: "2026-12-21", questions: 5, wauPercent: 70 }],
          }),
      }),
      "metrics",
    );
  });

  it("focus_ring_and_reduced_motion_are_defined", () => {
    const base = readFileSync(join(__dirname, "..", "styles", "base.css"), "utf8");
    const tokens = readFileSync(join(__dirname, "..", "styles", "tokens.css"), "utf8");
    expect(base).toMatch(/:focus-visible\s*\{[^}]*var\(--focus-ring\)/);
    expect(tokens).toContain("--focus-ring: 0 0 0 2px var(--color-white), 0 0 0 4px var(--color-primary)");
    expect(tokens).toMatch(/prefers-reduced-motion:\s*reduce/);
    expect(base).toContain(".table-wrap { overflow-x: auto; }");
  });

  it("no_external_urls_or_v_html_in_source", () => {
    const walk = (d: string): string[] =>
      readdirSync(d).flatMap((n) => (statSync(join(d, n)).isDirectory() ? (n === "__tests__" ? [] : walk(join(d, n))) : [join(d, n)]));
    for (const f of walk(join(__dirname, ".."))) {
      if (!/\.(vue|ts|css)$/.test(f)) continue;
      const src = readFileSync(f, "utf8");
      expect(src, f).not.toContain("v-html");
      expect(src.match(/https?:\/\//g), f).toBeNull();
    }
  });
});
