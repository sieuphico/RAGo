import { describe, it, expect } from "vitest";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import AppHeader from "@/components/AppHeader.vue";
import { routes } from "@/router";
import { navItems } from "@/router/nav";

const labels = (role: Parameters<typeof navItems>[0]) => navItems(role).map((i) => i.label);

describe("header", () => {
  it("header_shows_items_per_role", () => {
    expect(labels("BD_USER")).toEqual(["Hỏi đáp", "Kho tài liệu"]);
    expect(labels("TEAM_LEAD")).toEqual(["Hỏi đáp", "Kho tài liệu"]);
    expect(labels("ADMIN")).toEqual(["Hỏi đáp", "Kho tài liệu", "Số liệu", "Quản trị"]);
    expect(labels("SPONSOR")).toEqual(["Số liệu"]);
    expect(navItems(null)).toEqual([]);
  });

  it("router_has_all_routes", () => {
    const byPath = Object.fromEntries(routes.map((r) => [r.path, r.meta?.roles]));
    const chat = ["BD_USER", "TEAM_LEAD", "ADMIN"];
    expect(Object.keys(byPath).sort()).toEqual(
      ["/login", "/denied", "/", "/chat/:sessionId", "/library", "/admin/users", "/admin/audit", "/metrics"].sort(),
    );
    expect(byPath["/"]).toEqual(chat);
    expect(byPath["/chat/:sessionId"]).toEqual(chat);
    expect(byPath["/library"]).toEqual(chat);
    expect(byPath["/admin/users"]).toEqual(["ADMIN"]);
    expect(byPath["/admin/audit"]).toEqual(["ADMIN"]);
    expect(byPath["/metrics"]).toEqual(["ADMIN", "SPONSOR"]);
    expect(byPath["/login"]).toBeUndefined();
    expect(byPath["/denied"]).toBeUndefined();
  });

  async function mountHeader(role: "BD_USER" | "ADMIN", path = "/") {
    const router = createRouter({ history: createMemoryHistory(), routes });
    router.push(path);
    await router.isReady();
    return mount(AppHeader, { props: { role, userName: "Lan" }, global: { plugins: [router] } });
  }

  it("skip_link_first", async () => {
    const w = await mountHeader("BD_USER");
    const first = (w.element as HTMLElement).querySelector<HTMLElement>("a[href], button, [tabindex]");
    expect(first?.getAttribute("data-testid")).toBe("skip-link");
    expect(first?.textContent).toBe("Bỏ qua tới nội dung chính");
    expect(first?.getAttribute("href")).toBe("#main");
  });

  it("marks_current_item_and_renders_links", async () => {
    const w = await mountHeader("ADMIN", "/chat/abc");
    const nav = w.get("nav");
    const links = nav.findAll("a");
    expect(links.map((a) => a.text())).toEqual(["Hỏi đáp", "Kho tài liệu", "Số liệu", "Quản trị"]);
    expect(links.map((a) => a.attributes("aria-current"))).toEqual(["page", undefined, undefined, undefined]);
    expect(w.get("[data-testid=user-name]").text()).toBe("Lan");
    await w.get("[data-testid=logout]").trigger("click");
    expect(w.emitted("logout")).toHaveLength(1);
  });

  it("no_hardcoded_colors", () => {
    const dir = join(__dirname, "..", "components");
    for (const f of readdirSync(dir).filter((n) => n.endsWith(".vue"))) {
      const src = readFileSync(join(dir, f), "utf8");
      expect(src.match(/#[0-9a-fA-F]{3,6}\b/g), f).toBeNull();
    }
  });
});
