import { reactive } from "vue";

export type ToastKind = "info" | "success" | "error";
export interface ToastItem {
  id: number;
  text: string;
  kind: ToastKind;
}

export const TOAST_MS = 4000;

// Trạng thái dùng chung toàn ứng dụng; ToastHost hiển thị.
const state = reactive<{ items: ToastItem[] }>({ items: [] });
let seq = 0;

export function dismissToast(id: number): void {
  const i = state.items.findIndex((t) => t.id === id);
  if (i !== -1) state.items.splice(i, 1);
}

/** Thông báo tạm: `info`/`success` tự ẩn sau 4 giây; `error` giữ tới khi bấm đóng (Blueprint 3.8.2). */
export function useToast(): { show(text: string, kind?: ToastKind): void } {
  return {
    show(text, kind = "info") {
      const id = ++seq;
      state.items.push({ id, text, kind });
      if (kind !== "error") setTimeout(() => dismissToast(id), TOAST_MS);
    },
  };
}

export function useToastState() {
  return state;
}
