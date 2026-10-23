import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { mount, flushPromises } from "@vue/test-utils";
import { nextTick, reactive } from "vue";
import MessageList from "@/components/MessageList.vue";
import CitationChip from "@/components/CitationChip.vue";
import { splitAnswer } from "@/utils/answerText";
import type { CitationOut, UiMessage } from "@/api/types";

const cite = (over: Partial<CitationOut> = {}): CitationOut => ({
  index: 1, docId: "d1", docName: "HD_ABC_2026.pdf", page: 12, snippet: "…thời hạn 24 tháng kể từ…", deleted: false, ...over,
});

const ai = (over: Partial<UiMessage> = {}): UiMessage => ({
  id: "a1", role: "assistant", text: "", state: "SEARCHING", citations: [], sentAt: 0, ...over,
});

describe("answer rendering", () => {
  it("split_answer", () => {
    expect(splitAnswer("A [[1]] B [[2]].")).toEqual([
      { kind: "text", value: "A " },
      { kind: "cite", index: 1 },
      { kind: "text", value: " B " },
      { kind: "cite", index: 2 },
      { kind: "text", value: "." },
    ]);
    expect(splitAnswer("")).toEqual([]);
    expect(splitAnswer("[[3]]")).toEqual([{ kind: "cite", index: 3 }]);
    expect(splitAnswer("không có dấu")).toEqual([{ kind: "text", value: "không có dấu" }]);
  });

  it("streams_text_and_citations", async () => {
    const messages = reactive<UiMessage[]>([ai({ state: "SEARCHING" })]);
    const w = mount(MessageList, { props: { messages } });
    messages[0]!.citations.push(cite());
    messages[0]!.text += "Thời hạn ";
    messages[0]!.state = "STREAMING";
    await nextTick();
    messages[0]!.text += "24 tháng [[1]]";
    await nextTick();
    expect(w.get("[data-testid=answer-text]").text()).toContain("Thời hạn 24 tháng");
    const chips = w.findAll("[data-testid=citation]");
    expect(chips).toHaveLength(1);
    expect(chips[0]!.get("[data-testid=citation-label]").text()).toBe("[HD_ABC_2026.pdf – tr. 12]");
    expect(chips[0]!.attributes("aria-label")).toBe("Trích dẫn: HD_ABC_2026.pdf, trang 12, mở trang nguồn");
  });

  it("unknown_citation_index_renders_nothing", () => {
    const w = mount(MessageList, { props: { messages: [ai({ state: "COMPLETED", text: "Có [[2]] ở đây" })] } });
    expect(w.findAll("[data-testid=citation]")).toHaveLength(0);
    expect(w.get("[data-testid=answer-text]").text()).not.toContain("[[");
  });

  it("no_html_injection", () => {
    const evil = "<img src=x onerror=alert(1)>";
    const w = mount(MessageList, {
      props: { messages: [ai({ state: "COMPLETED", text: evil }), { ...ai({ id: "u" }), role: "user", text: evil, state: "COMPLETED" }] },
    });
    expect(w.find("img").exists()).toBe(false);
    expect(w.get("[data-testid=answer-text]").text()).toBe(evil);
    expect(w.get("[data-testid=user-message]").text()).toBe(evil);
  });

  it("no_v_html_in_components", () => {
    for (const f of ["MessageList", "AnswerBlock", "CitationChip"]) {
      expect(readFileSync(join(__dirname, "..", "components", `${f}.vue`), "utf8")).not.toContain("v-html");
    }
  });

  it("announces_only_on_completion", async () => {
    const messages = reactive<UiMessage[]>([ai({ state: "SEARCHING" })]);
    const w = mount(MessageList, { props: { messages } });
    const live = () => w.get("[data-testid=announcer]");
    expect(live().attributes("aria-live")).toBe("polite");
    messages[0]!.state = "STREAMING";
    for (let i = 0; i < 5; i++) {
      messages[0]!.text += "chữ ";
      await nextTick();
    }
    expect(live().text()).toBe("");
    expect(w.get("[data-testid=message-log]").attributes("aria-live")).toBe("off");
    messages[0]!.state = "COMPLETED";
    await flushPromises();
    expect(live().text()).toBe("Câu trả lời đã xong");
  });

  it("does_not_announce_when_loading_history", async () => {
    const messages = reactive<UiMessage[]>([]);
    const w = mount(MessageList, { props: { messages } });
    messages.push(ai({ state: "COMPLETED", text: "đã lưu" }));
    await nextTick();
    await nextTick();
    expect(w.get("[data-testid=announcer]").text()).toBe("");
  });

  it("chip_keyboard_open", async () => {
    const c = cite();
    const w = mount(CitationChip, { props: { citation: c }, attachTo: document.body });
    const btn = w.get("button");
    expect(btn.element.tagName).toBe("BUTTON"); // Tab tới được; Enter/Space kích hoạt click
    (btn.element as HTMLButtonElement).focus();
    expect(document.activeElement).toBe(btn.element);
    await btn.trigger("click");
    expect(w.emitted("open")).toEqual([[c]]);
    w.unmount();
  });

  it("list_emits_open_citation_with_message_id", async () => {
    const c = cite();
    const w = mount(MessageList, {
      props: { messages: [ai({ state: "COMPLETED", messageId: "m9", text: "x [[1]]", citations: [c] })] },
    });
    await w.get("[data-testid=citation]").trigger("click");
    expect(w.emitted("openCitation")).toEqual([["m9", c]]);
  });

  it("deleted_chip_disabled", async () => {
    const w = mount(CitationChip, { props: { citation: cite({ deleted: true }) } });
    expect(w.get("button").attributes("disabled")).toBeDefined();
    expect(w.text()).toBe("Tài liệu đã bị xóa");
    await w.get("button").trigger("click");
    expect(w.emitted("open")).toBeUndefined();
  });

  it("long_doc_name_is_truncated_in_the_middle", () => {
    const name = "Hop_dong_cung_cap_dich_vu_rat_dai_2026_ban_cuoi.pdf";
    const w = mount(CitationChip, { props: { citation: cite({ docName: name }) } });
    const label = w.get("[data-testid=citation-label]").text();
    expect(label).toContain("…");
    expect(label.endsWith(" – tr. 12]")).toBe(true);
    expect(w.get("button").attributes("title")).toBe(name);
  });
});
