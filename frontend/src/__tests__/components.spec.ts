import { describe, it, expect, vi, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import ToastHost from "@/components/ToastHost.vue";
import BannerHost from "@/components/BannerHost.vue";
import SkeletonRows from "@/components/SkeletonRows.vue";
import { useToast, useToastState } from "@/composables/useToast";
import { useBanner } from "@/composables/useBanner";

afterEach(() => {
  vi.useRealTimers();
  useToastState().items.splice(0);
  useBanner().hide();
  document.body.innerHTML = "";
});

describe("ConfirmDialog", () => {
  function setup(destructive: boolean) {
    const opener = document.createElement("button");
    document.body.appendChild(opener);
    opener.focus();
    const w = mount(ConfirmDialog, {
      props: { open: false, title: "Xóa tài liệu?", confirmLabel: "Xóa tài liệu", destructive },
      slots: { default: "Nội dung" },
      attachTo: document.body,
    });
    return { w, opener };
  }

  it("dialog_focus_default_cancel", async () => {
    const { w, opener } = setup(true);
    await w.setProps({ open: true });
    await nextTick();
    expect(document.activeElement).toBe(w.get("[data-testid=dialog-cancel]").element);
    expect(w.get("dialog").attributes("aria-modal")).toBe("true");
    const labelledBy = w.get("dialog").attributes("aria-labelledby")!;
    expect(w.get(`[id="${labelledBy}"]`).text()).toBe("Xóa tài liệu?");
    await w.setProps({ open: false });
    expect(document.activeElement).toBe(opener);
  });

  it("non_destructive_focuses_confirm", async () => {
    const { w } = setup(false);
    await w.setProps({ open: true });
    await nextTick();
    expect(document.activeElement).toBe(w.get("[data-testid=dialog-confirm]").element);
  });

  it("dialog_esc_closes", async () => {
    const { w } = setup(true);
    await w.setProps({ open: true });
    await w.get("dialog").trigger("keydown", { key: "Escape" });
    expect(w.emitted("cancel")).toHaveLength(1);
    await w.setProps({ open: false });
    expect(w.get("dialog").attributes("open")).toBeUndefined();
  });

  it("buttons_emit", async () => {
    const { w } = setup(true);
    await w.get("[data-testid=dialog-confirm]").trigger("click");
    await w.get("[data-testid=dialog-cancel]").trigger("click");
    expect(w.emitted("confirm")).toHaveLength(1);
    expect(w.emitted("cancel")).toHaveLength(1);
  });
});

describe("StatusBadge", () => {
  const cases: [Parameters<typeof mountBadge>[0], string][] = [
    [{ status: "UPLOADING", progress: 64 }, "Đang tải lên (64%)"],
    [{ status: "INTERRUPTED" }, "Tải lên bị gián đoạn"],
    [{ status: "PROCESSING" }, "Đang xử lý"],
    [{ status: "OCR_PROCESSING" }, "Đang nhận dạng ký tự"],
    [{ status: "OCR_PROCESSING", slow: true }, "Xử lý lâu bất thường"],
    [{ status: "READY" }, "Sẵn sàng"],
    [{ status: "FAILED", failureReason: "FILE_ENCRYPTED" }, "Thất bại – Tệp có mật khẩu."],
    [{ status: "DELETED" }, "Đã xóa"],
  ];
  function mountBadge(props: Record<string, unknown>) {
    return mount(StatusBadge, { props: props as never });
  }

  it("badge_has_text_and_icon", () => {
    for (const [props, text] of cases) {
      const w = mountBadge(props);
      expect(w.get("[data-testid=status-badge]").text(), JSON.stringify(props)).toContain(text);
      expect(w.get("svg").attributes("aria-hidden")).toBe("true");
    }
  });

  it("badge_failed_reason", () => {
    const w = mountBadge({ status: "FAILED", failureReason: "OCR_UNREADABLE" });
    expect(w.get("[data-testid=status-badge]").text()).toBe("Thất bại – Không đọc được nội dung.");
    expect(w.text()).toContain("Thử tải bản quét rõ nét hơn.");
  });

  it("ocr_shows_note", () => {
    expect(mountBadge({ status: "OCR_PROCESSING" }).text()).toContain("Tài liệu dạng ảnh quét cần thêm thời gian xử lý.");
  });

  it("tone_classes", () => {
    expect(mountBadge({ status: "READY" }).get(".badge").classes()).toContain("badge-success");
    expect(mountBadge({ status: "FAILED" }).get(".badge").classes()).toContain("badge-danger");
    expect(mountBadge({ status: "INTERRUPTED" }).get(".badge").classes()).toContain("badge-warning");
  });
});

describe("toast and banner", () => {
  it("toast_error_persists", async () => {
    vi.useFakeTimers();
    const w = mount(ToastHost);
    const toast = useToast();
    toast.show("lỗi", "error");
    toast.show("thường", "info");
    await nextTick();
    expect(w.findAll("[data-testid=toast]")).toHaveLength(2);
    vi.advanceTimersByTime(10_000);
    await nextTick();
    const left = w.findAll("[data-testid=toast]");
    expect(left).toHaveLength(1);
    expect(left[0]!.text()).toContain("lỗi");
    await left[0]!.get("button").trigger("click");
    expect(w.findAll("[data-testid=toast]")).toHaveLength(0);
  });

  it("toast_info_hides_after_4s", async () => {
    vi.useFakeTimers();
    const w = mount(ToastHost);
    useToast().show("x", "success");
    await nextTick();
    vi.advanceTimersByTime(3900);
    await nextTick();
    expect(w.findAll("[data-testid=toast]")).toHaveLength(1);
    vi.advanceTimersByTime(200);
    await nextTick();
    expect(w.findAll("[data-testid=toast]")).toHaveLength(0);
    expect(w.get("[data-testid=toast-host]").attributes("role")).toBe("status");
  });

  it("banner_show_hide", async () => {
    const w = mount(BannerHost);
    expect(w.find("[data-testid=banner]").exists()).toBe(false);
    useBanner().show("Mất kết nối");
    await nextTick();
    expect(w.get("[data-testid=banner]").attributes("role")).toBe("alert");
    useBanner().hide();
    await nextTick();
    expect(w.find("[data-testid=banner]").exists()).toBe(false);
  });

  it("skeleton_rows", () => {
    const w = mount(SkeletonRows, { props: { rows: 3 } });
    expect(w.findAll(".skeleton-row")).toHaveLength(3);
    expect(w.get("section").attributes("aria-busy")).toBe("true");
  });
});
