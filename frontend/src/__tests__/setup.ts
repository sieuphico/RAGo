// Thiết lập chung cho Vitest (jsdom).
// jsdom chưa cài đặt <dialog>.showModal()/close(); bổ sung bản tối thiểu để test hộp thoại.
if (typeof HTMLDialogElement !== "undefined") {
  const proto = HTMLDialogElement.prototype as unknown as Record<string, unknown>;
  proto.showModal = function (this: HTMLDialogElement) {
    this.setAttribute("open", "");
  };
  proto.close = function (this: HTMLDialogElement) {
    if (!this.hasAttribute("open")) return;
    this.removeAttribute("open");
    this.dispatchEvent(new Event("close"));
  };
}

// jsdom không có EventSource: bản giả không làm gì; test cần hành vi riêng dùng vi.stubGlobal (ADR 0101).
if (typeof globalThis.EventSource === "undefined") {
  class NoopEventSource {
    onopen: (() => void) | null = null;
    onerror: (() => void) | null = null;
    addEventListener(): void {}
    close(): void {}
  }
  (globalThis as unknown as { EventSource: unknown }).EventSource = NoopEventSource;
}

export {};
