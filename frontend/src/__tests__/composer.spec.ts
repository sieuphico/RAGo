import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import Composer from "@/components/Composer.vue";
import { useChatStore } from "@/stores/chat";

function mountComposer() {
  return mount(Composer, { attachTo: document.body });
}

describe("Composer", () => {
  beforeEach(() => {
    sessionStorage.clear();
    setActivePinia(createPinia());
  });
  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("enter_sends_shift_enter_newline", async () => {
    const w = mountComposer();
    const input = w.get("[data-testid=composer-input]");
    await input.setValue("abc");
    await input.trigger("keydown", { key: "Enter" });
    expect(w.emitted("submit")).toEqual([["abc"]]);
    await input.setValue("x");
    await input.trigger("keydown", { key: "Enter", shiftKey: true });
    expect(w.emitted("submit")).toHaveLength(1); // Shift+Enter không gửi (trình duyệt tự xuống dòng)
  });

  it("enter_on_empty_does_not_send", async () => {
    const w = mountComposer();
    await w.get("[data-testid=composer-input]").setValue("   ");
    await w.get("[data-testid=composer-input]").trigger("keydown", { key: "Enter" });
    expect(w.emitted("submit")).toBeUndefined();
  });

  it("blocks_empty_and_overlong", async () => {
    const w = mountComposer();
    const input = w.get("[data-testid=composer-input]");
    await input.setValue("   ");
    expect(w.get("[data-testid=send]").attributes("disabled")).toBeDefined();
    await input.setValue("a".repeat(2001));
    expect(w.get("[data-testid=send]").attributes("disabled")).toBeDefined();
    const counter = w.get("[data-testid=counter]");
    expect(counter.text()).toBe("2.001/2.000");
    expect(counter.classes()).toContain("is-over");
    await input.setValue("a".repeat(2000));
    expect(w.get("[data-testid=send]").attributes("disabled")).toBeUndefined();
    expect(w.get("[data-testid=counter]").classes()).not.toContain("is-over");
  });

  it("keeps_draft_on_offline", async () => {
    const w = mountComposer();
    await w.get("[data-testid=composer-input]").setValue("câu dở");
    window.dispatchEvent(new Event("offline"));
    await w.vm.$nextTick();
    expect(w.get("[data-testid=offline-banner]").text()).toContain("Mất kết nối. Đang thử kết nối lại…");
    expect((w.get("[data-testid=composer-input]").element as HTMLTextAreaElement).value).toBe("câu dở");
    expect(w.get("[data-testid=send]").attributes("disabled")).toBeDefined();
    window.dispatchEvent(new Event("online"));
    await w.vm.$nextTick();
    expect(w.find("[data-testid=offline-banner]").exists()).toBe(false);
    expect(w.get("[data-testid=send]").attributes("disabled")).toBeUndefined();
  });

  it("draft_restored", () => {
    sessionStorage.setItem("cwd_draft", "nháp");
    setActivePinia(createPinia());
    const w = mountComposer();
    expect((w.get("[data-testid=composer-input]").element as HTMLTextAreaElement).value).toBe("nháp");
  });

  it("draft_is_saved_on_typing", async () => {
    const w = mountComposer();
    await w.get("[data-testid=composer-input]").setValue("đang gõ");
    await w.vm.$nextTick();
    expect(sessionStorage.getItem("cwd_draft")).toBe("đang gõ");
    await w.get("[data-testid=composer-input]").setValue("");
    await w.vm.$nextTick();
    expect(sessionStorage.getItem("cwd_draft")).toBeNull();
  });

  it("slash_focuses_input", () => {
    const w = mountComposer();
    const other = document.createElement("button");
    document.body.appendChild(other);
    other.focus();
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "/", bubbles: true }));
    expect(document.activeElement).toBe(w.get("[data-testid=composer-input]").element);
  });

  it("busy_shows_stop_button", async () => {
    const chat = useChatStore();
    const w = mountComposer();
    chat.busy = true;
    await w.vm.$nextTick();
    expect(w.find("[data-testid=send]").exists()).toBe(false);
    await w.get("[data-testid=stop]").trigger("click");
    expect(w.emitted("stop")).toHaveLength(1);
  });

  it("empty_library_disables_input_and_shows_disclaimer", async () => {
    const chat = useChatStore();
    const w = mountComposer();
    expect(w.get("[data-testid=disclaimer]").text()).toBe(
      "Câu trả lời do AI tạo – hãy kiểm tra trích dẫn với thông tin quan trọng.",
    );
    chat.libraryEmpty = true;
    await w.vm.$nextTick();
    expect(w.get("[data-testid=composer-input]").attributes("disabled")).toBeDefined();
  });
});
