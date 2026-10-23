import { describe, it, expect } from "vitest";
import { createApp } from "vue";
import { createPinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import App from "@/App.vue";

describe("app", () => {
  it("app mounts", async () => {
    const host = document.createElement("div");
    host.id = "app";
    document.body.appendChild(host);
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: "/", component: { template: "<p>trang thử</p>" } }],
    });
    router.push("/");
    await router.isReady();
    const app = createApp(App).use(createPinia()).use(router);
    expect(() => app.mount(host)).not.toThrow();
    expect(document.querySelector("#app")?.children.length).toBeGreaterThan(0);
    app.unmount();
    host.remove();
  });
});
