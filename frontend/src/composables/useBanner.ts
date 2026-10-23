import { reactive } from "vue";

const state = reactive<{ text: string | null }>({ text: null });

/** Một dải thông báo đầu trang (ví dụ mất kết nối). */
export function useBanner(): { show(text: string): void; hide(): void } {
  return {
    show(text) {
      state.text = text;
    },
    hide() {
      state.text = null;
    },
  };
}

export function useBannerState() {
  return state;
}
