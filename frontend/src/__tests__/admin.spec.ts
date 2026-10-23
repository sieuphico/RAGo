import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import { routes } from "@/router";
import { installGuards } from "@/router/guards";
import AdminUsersView from "@/views/AdminUsersView.vue";
import AdminAuditView from "@/views/AdminAuditView.vue";
import { useToastState } from "@/composables/useToast";
import { calls, installFetch, jsonRes } from "./helpers/api";

const USERS = [
  { email: "quantri@congty.vn", role: "ADMIN", addedBy: "system", addedAt: "2026-10-19T02:12:00Z" },
  { email: "minh@congty.vn", role: "TEAM_LEAD", addedBy: "quantri@congty.vn", addedAt: "2026-10-19T02:12:00Z" },
];

async function mountUsers(routes_: Record<string, () => Response | Promise<Response>> = {}) {
  setActivePinia(createPinia());
  const fetchMock = installFetch({
    "GET /api/v1/admin/users": () => jsonRes(200, { items: USERS, count: 2, limit: 20 }),
    ...routes_,
  });
  const router = createRouter({ history: createMemoryHistory(), routes });
  router.push("/admin/users");
  await router.isReady();
  const w = mount(AdminUsersView, { global: { plugins: [router] }, attachTo: document.body });
  await flushPromises();
  return { w, fetchMock };
}

describe("admin users (S-07)", () => {
  beforeEach(() => {
    process.env.TZ = "Asia/Ho_Chi_Minh";
    useToastState().items.splice(0);
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    document.body.innerHTML = "";
  });

  it("renders_users_with_role_names_and_count", async () => {
    const { w } = await mountUsers();
    expect(w.get("[data-testid=user-count]").text()).toBe("(2/20)");
    const rows = w.findAll("[data-testid=user-row]");
    expect(rows).toHaveLength(2);
    expect(rows[0]!.text()).toContain("Quản trị viên");
    expect(rows[1]!.text()).toContain("Trưởng nhóm BD");
    expect(rows[1]!.text()).toContain("19/10/2026 09:12");
    expect(w.findAll("thead th")).toHaveLength(4);
  });

  it("add_user_validation", async () => {
    const { w, fetchMock } = await mountUsers();
    await w.get("[data-testid=open-add]").trigger("click");
    await w.get("[data-testid=email-input]").setValue("lan@");
    await w.get("[data-testid=add-form]").trigger("submit");
    expect(w.get("[data-testid=email-error]").text()).toBe("Email không hợp lệ.");
    expect(w.get("[data-testid=email-input]").attributes("aria-describedby")).toBe("new-user-email-error");
    expect(calls(fetchMock).some((c) => c.startsWith("POST"))).toBe(false);
  });

  it("add_user_success", async () => {
    const { w, fetchMock } = await mountUsers({
      "POST /api/v1/admin/users": () =>
        jsonRes(201, { email: "lan@congty.vn", role: "BD_USER", addedBy: "quantri@congty.vn", addedAt: "2026-10-20T02:12:00Z" }),
    });
    await w.get("[data-testid=open-add]").trigger("click");
    await w.get("[data-testid=email-input]").setValue("lan@congty.vn");
    await w.get("[data-testid=role-select]").setValue("BD_USER");
    await w.get("[data-testid=add-form]").trigger("submit");
    await flushPromises();
    expect(w.findAll("[data-testid=user-row]")).toHaveLength(3);
    expect(w.get("[data-testid=user-count]").text()).toBe("(3/20)");
    const post = fetchMock.mock.calls.find((c) => (c[1] as RequestInit).method === "POST")!;
    expect(JSON.parse((post[1] as RequestInit).body as string)).toEqual({ email: "lan@congty.vn", role: "BD_USER" });
    expect(w.find("[data-testid=add-form]").exists()).toBe(false);
  });

  it("duplicate_user_error", async () => {
    const { w } = await mountUsers({
      "POST /api/v1/admin/users": () => jsonRes(409, { code: "USER_EXISTS", retryable: false }),
    });
    await w.get("[data-testid=open-add]").trigger("click");
    await w.get("[data-testid=email-input]").setValue("minh@congty.vn");
    await w.get("[data-testid=add-form]").trigger("submit");
    await flushPromises();
    expect(w.get("[data-testid=email-error]").text()).toBe("Người dùng này đã có trong danh sách.");
    expect(w.findAll("[data-testid=user-row]")).toHaveLength(2);
  });

  it("limit_reached_error_on_top_of_form", async () => {
    const { w } = await mountUsers({
      "POST /api/v1/admin/users": () => jsonRes(409, { code: "USER_LIMIT_REACHED", retryable: false }),
    });
    await w.get("[data-testid=open-add]").trigger("click");
    await w.get("[data-testid=email-input]").setValue("x@congty.vn");
    await w.get("[data-testid=add-form]").trigger("submit");
    await flushPromises();
    expect(w.get("[data-testid=form-error]").text()).toBe("Đã đạt giới hạn 20 người dùng.");
  });

  it("remove_user_with_confirmation", async () => {
    const { w, fetchMock } = await mountUsers({ "DELETE /api/v1/admin/users/minh%40congty.vn": () => jsonRes(204) });
    await w.findAll("[data-testid=remove]")[1]!.trigger("click");
    await flushPromises();
    expect(w.get("dialog h2").text()).toBe("Gỡ quyền của minh@congty.vn?");
    expect(document.activeElement).toBe(w.get("[data-testid=dialog-cancel]").element);
    await w.get("[data-testid=dialog-confirm]").trigger("click");
    await flushPromises();
    expect(calls(fetchMock)).toContain("DELETE /api/v1/admin/users/minh%40congty.vn");
    expect(w.findAll("[data-testid=user-row]")).toHaveLength(1);
    expect(useToastState().items.map((i) => i.text)).toContain("Đã gỡ quyền của minh@congty.vn");
  });

  it("remove_cancel_does_nothing", async () => {
    const { w, fetchMock } = await mountUsers();
    await w.findAll("[data-testid=remove]")[0]!.trigger("click");
    await flushPromises();
    await w.get("[data-testid=dialog-cancel]").trigger("click");
    expect(calls(fetchMock).some((c) => c.startsWith("DELETE"))).toBe(false);
    expect(w.findAll("[data-testid=user-row]")).toHaveLength(2);
  });

  it("last_admin_toast", async () => {
    const { w } = await mountUsers({
      "DELETE /api/v1/admin/users/quantri%40congty.vn": () => jsonRes(409, { code: "LAST_ADMIN", retryable: false }),
    });
    await w.findAll("[data-testid=remove]")[0]!.trigger("click");
    await flushPromises();
    await w.get("[data-testid=dialog-confirm]").trigger("click");
    await flushPromises();
    expect(useToastState().items.map((i) => i.text)).toContain("Không thể gỡ quản trị viên cuối cùng.");
    expect(w.findAll("[data-testid=user-row]")).toHaveLength(2);
  });

  it("empty_states", async () => {
    const { w } = await mountUsers({ "GET /api/v1/admin/users": () => jsonRes(200, { items: [], count: 0, limit: 20 }) });
    expect(w.get("[data-testid=empty]").text()).toContain("Chưa có người dùng nào được cấp quyền");
  });

  it("error_state_with_retry", async () => {
    let fail = true;
    const { w } = await mountUsers({
      "GET /api/v1/admin/users": () => (fail ? jsonRes(500, { code: "INTERNAL", retryable: false }) : jsonRes(200, { items: USERS, count: 2, limit: 20 })),
    });
    expect(w.get("[data-testid=load-error]").text()).toContain("Không tải được danh sách người dùng.");
    fail = false;
    await w.get("[data-testid=retry]").trigger("click");
    await flushPromises();
    expect(w.findAll("[data-testid=user-row]")).toHaveLength(2);
  });
});

describe("admin audit (S-08)", () => {
  beforeEach(() => {
    process.env.TZ = "Asia/Ho_Chi_Minh";
  });
  afterEach(() => vi.unstubAllGlobals());

  async function mountAudit(handler: () => Response) {
    setActivePinia(createPinia());
    const fetchMock = installFetch({ "GET /api/v1/admin/audit-log": handler });
    const router = createRouter({ history: createMemoryHistory(), routes });
    router.push("/admin/audit");
    await router.isReady();
    const w = mount(AdminAuditView, { global: { plugins: [router] } });
    await flushPromises();
    return { w, fetchMock };
  }

  it("audit_table_columns", async () => {
    const { w, fetchMock } = await mountAudit(() =>
      jsonRes(200, {
        items: [
          { actor: "minh@congty.vn", action: "UPLOAD", docId: "d1", docName: "HD_XYZ.pdf", at: "2026-10-19T02:12:00Z" },
          { actor: "system", action: "PURGE", docId: "d2", docName: "Cu.pdf", at: "2026-10-18T02:12:00Z" },
        ],
      }),
    );
    expect(w.findAll("thead th").map((h) => h.text())).toEqual(["Người thực hiện", "Thao tác", "Tài liệu", "Thời điểm"]);
    const rows = w.findAll("[data-testid=audit-row]");
    expect(rows[0]!.findAll("td").map((c) => c.text())).toEqual(["minh@congty.vn", "Tải lên", "HD_XYZ.pdf", "19/10/2026 09:12"]);
    expect(rows[1]!.findAll("td")[1]!.text()).toBe("Xóa dữ liệu (hệ thống)");
    expect(calls(fetchMock)).toContain("GET /api/v1/admin/audit-log");
    expect(String(fetchMock.mock.calls[0]![0])).toBe("/api/v1/admin/audit-log?limit=100");
  });

  it("empty_and_error", async () => {
    const empty = await mountAudit(() => jsonRes(200, { items: [] }));
    expect(empty.w.get("[data-testid=empty]").text()).toBe("Chưa có hoạt động nào");
    const err = await mountAudit(() => jsonRes(500, { code: "INTERNAL", retryable: false }));
    expect(err.w.get("[data-testid=load-error]").text()).toContain("Không tải được nhật ký.");
  });
});

describe("admin route guard", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("admin_only_route", async () => {
    setActivePinia(createPinia());
    installFetch({ "GET /api/v1/me": () => jsonRes(200, { email: "minh@congty.vn", role: "TEAM_LEAD", allowed: true }) });
    const router = createRouter({ history: createMemoryHistory(), routes });
    installGuards(router);
    await router.push("/admin/users");
    expect(router.currentRoute.value.path).toBe("/denied");
    await router.push("/admin/audit");
    expect(router.currentRoute.value.path).toBe("/denied");
  });

  it("admin_can_enter", async () => {
    setActivePinia(createPinia());
    installFetch({ "GET /api/v1/me": () => jsonRes(200, { email: "quantri@congty.vn", role: "ADMIN", allowed: true }) });
    const router = createRouter({ history: createMemoryHistory(), routes });
    installGuards(router);
    await router.push("/admin/users");
    expect(router.currentRoute.value.path).toBe("/admin/users");
  });
});
