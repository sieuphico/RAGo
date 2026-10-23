// sessionStorage/localStorage luôn bọc try/catch: trang phải chạy đúng khi bộ nhớ trình duyệt không dùng được (CONTRACTS 10.6).

type Kind = "session" | "local";

function area(kind: Kind): Storage | null {
  try {
    return kind === "session" ? window.sessionStorage : window.localStorage;
  } catch {
    return null;
  }
}

export function storageGet(key: string, kind: Kind = "session"): string | null {
  try {
    return area(kind)?.getItem(key) ?? null;
  } catch {
    return null;
  }
}

export function storageSet(key: string, value: string, kind: Kind = "session"): void {
  try {
    area(kind)?.setItem(key, value);
  } catch {
    /* bộ nhớ bị chặn hoặc đầy: bỏ qua */
  }
}

export function storageRemove(key: string, kind: Kind = "session"): void {
  try {
    area(kind)?.removeItem(key);
  } catch {
    /* bỏ qua */
  }
}

export const KEY_RETURN_TO = "cwd_return_to";
export const KEY_DRAFT = "cwd_draft";
export const KEY_ONBOARDED = "cwd_onboarded";
