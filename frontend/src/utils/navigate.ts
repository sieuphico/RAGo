/** Chuyển cả trình duyệt tới URL ngoài ứng dụng (ví dụ `/auth/login`). Tách riêng để test thay thế được. */
export function redirect(url: string): void {
  window.location.assign(url);
}
