// Giữ tham chiếu router đang dùng để store điều hướng mà không nhập vòng với router/guards.
import type { Router } from "vue-router";

let current: Router | null = null;

export function setRouter(r: Router): void {
  current = r;
}

export function getRouter(): Router {
  if (!current) throw new Error("Router chưa được cài đặt");
  return current;
}
