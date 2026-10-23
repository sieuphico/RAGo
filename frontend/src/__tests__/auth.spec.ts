import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory, type Router } from "vue-router";
import { routes } from "@/router";
import { installGuards } from "@/router/guards";
import { useAuthStore } from "@/stores/auth";
import { useFeaturesStore } from "@/stores/features";
import { request } from "@/api/client";
import DeniedView from "@/views/DeniedView.vue";
import LoginView from "@/views/LoginView.vue";
import * as nav from "@/utils/navigate";
import { calls, flush, installFetch, jsonRes } from "./helpers/api";

const ME = (role: string | null, allowed = true) => () => jsonRes(200, { email: "lan@congty.vn", role, allowed });
const UNAUTH = () => jsonRes(401, { code: "AUTH_EXPIRED", retryable: false });

function setup(): { router: Router } {
  setActivePinia(createPinia());
  const router = createRouter({ history: createMemoryHistory(), routes });
  installGuards(router);
  return { router };
}

describe("auth", () => {
  beforeEach(() => sessionStorage.clear());
  afterEach(() => vi.unstubAllGlobals());

  it("guard_redirects_unauthenticated", async () => {
    installFetch({ "GET /api/v1/me": UNAUTH });
    const { router } = setup();
    await router.push("/library");
    expect(router.currentRoute.value.path).toBe("/login");
    expect(useAuthStore().status).toBe("unauthenticated");
    expect(sessionStorage.getItem("cwd_return_to")).toBe("/library");
  });

  it("guard_role_denied", async () => {
    installFetch({ "GET /api/v1/me": ME("BD_USER") });
    const { router } = setup();
    await router.push("/admin/users");
    expect(router.currentRoute.value.path).toBe("/denied");
    await router.push("/library");
    expect(router.currentRoute.value.path).toBe("/library");
  });

  it("sponsor_home_is_metrics", async () => {
    installFetch({ "GET /api/v1/me": ME("SPONSOR") });
    const { router } = setup();
    await router.push("/");
    expect(router.currentRoute.value.path).toBe("/metrics");
    await router.push("/library");
    expect(router.currentRoute.value.path).toBe("/denied");
  });

  it("denied_page_shows_no_documents", async () => {
    const fetchMock = installFetch({ "GET /api/v1/me": ME(null, false) });
    const { router } = setup();
    await router.push("/library");
    expect(router.currentRoute.value.path).toBe("/denied");
    expect(useAuthStore().status).toBe("denied");
    const w = mount(DeniedView, { global: { plugins: [router] } });
    expect(w.text()).toContain("Bạn chưa được cấp quyền");
    expect(w.text()).toContain("Liên hệ quản trị viên.");
    expect(calls(fetchMock).some((c) => c.includes("/api/v1/documents"))).toBe(false);
  });

  it("revoked_message", async () => {
    installFetch({
      "GET /api/v1/me": ME("BD_USER"),
      "GET /api/v1/documents": () => jsonRes(403, { code: "AUTH_FORBIDDEN", retryable: false }),
    });
    const { router } = setup();
    await router.push("/library");
    expect(useAuthStore().status).toBe("allowed");
    await expect(request("/api/v1/documents")).rejects.toMatchObject({ code: "AUTH_FORBIDDEN" });
    await flush();
    expect(router.currentRoute.value.path).toBe("/denied");
    expect(useAuthStore().status).toBe("revoked");
    const w = mount(DeniedView, { global: { plugins: [router] } });
    expect(w.get("[data-testid=denied-title]").text()).toBe("Quyền truy cập của bạn đã bị thu hồi.");
  });

  it("draft_survives_reauth", async () => {
    installFetch({
      "GET /api/v1/me": ME("BD_USER"),
      "GET /api/v1/chat/sessions/abc": UNAUTH,
    });
    const { router } = setup();
    await router.push("/chat/abc");
    sessionStorage.setItem("cwd_draft", "câu hỏi dở");
    await expect(request("/api/v1/chat/sessions/abc")).rejects.toMatchObject({ code: "AUTH_EXPIRED" });
    await flush();
    expect(sessionStorage.getItem("cwd_return_to")).toBe("/chat/abc");
    expect(router.currentRoute.value.fullPath).toBe("/login?expired=1");
    const w = mount(LoginView, { global: { plugins: [router] } });
    expect(w.get("[data-testid=expired-banner]").text()).toBe("Phiên đã hết hạn. Đăng nhập lại để tiếp tục.");
    expect(sessionStorage.getItem("cwd_draft")).toBe("câu hỏi dở");
  });

  it("login_returns_to_previous_path", async () => {
    installFetch({ "GET /api/v1/me": UNAUTH });
    const { router } = setup();
    const redirect = vi.spyOn(nav, "redirect").mockImplementation(() => {});
    await router.push("/library");
    const w = mount(LoginView, { global: { plugins: [router] } });
    expect(w.find("[data-testid=expired-banner]").exists()).toBe(false);
    await w.get("[data-testid=login-button]").trigger("click");
    expect(redirect).toHaveBeenCalledWith("/auth/login?next=%2Flibrary");
  });

  it("logout_posts_and_goes_to_login", async () => {
    const fetchMock = installFetch({
      "GET /api/v1/me": ME("TEAM_LEAD"),
      "POST /auth/logout": () => jsonRes(204),
    });
    const { router } = setup();
    await router.push("/library");
    await useAuthStore().logout();
    expect(calls(fetchMock)).toContain("POST /auth/logout");
    expect(router.currentRoute.value.path).toBe("/login");
    expect(useAuthStore().status).toBe("unauthenticated");
  });

  it("features_load_after_allowed_and_default_off", async () => {
    installFetch({
      "GET /api/v1/me": ME("BD_USER"),
      "GET /api/v1/features": () =>
        jsonRes(200, {
          suggestions: true, summary: false, history: true, rating: false,
          copy: true, scope: false, followup: true, duplicateCheck: false,
        }),
    });
    const { router } = setup();
    expect(useFeaturesStore().flags.history).toBe(false);
    await router.push("/library");
    expect(useFeaturesStore().flags).toMatchObject({ suggestions: true, history: true, summary: false });
  });

  it("features_failure_hides_everything", async () => {
    installFetch({ "GET /api/v1/me": ME("BD_USER") }); // /features → 404
    const { router } = setup();
    await router.push("/library");
    expect(Object.values(useFeaturesStore().flags).every((v) => v === false)).toBe(true);
  });
});
