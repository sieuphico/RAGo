// Client API duy nhất của giao diện (CONTRACTS mục 10.6). Gọi API chỉ qua `request` (và `streamPost` ở sse.ts).
import type { ErrorBody } from "./types";

export class ApiError extends Error {
  code: string;
  retryable: boolean;
  status?: number;
  constructor(code: string, retryable: boolean, status?: number) {
    super(code);
    this.name = "ApiError";
    this.code = code;
    this.retryable = retryable;
    this.status = status;
  }
}

let authExpiredHandler: (() => void) | null = null;
let forbiddenHandler: (() => void) | null = null;

/** T-505 đăng ký: `request` gọi khi nhận `AUTH_EXPIRED` (tránh nhập vòng). */
export function setAuthExpiredHandler(fn: () => void): void {
  authExpiredHandler = fn;
}

/** T-505 đăng ký: `request` gọi khi nhận `AUTH_FORBIDDEN` (quyền bị thu hồi khi đang dùng). */
export function setForbiddenHandler(fn: () => void): void {
  forbiddenHandler = fn;
}

export const CSRF_HEADER = "X-Requested-With";
export const CSRF_VALUE = "cwd";

/** Đọc thân lỗi `{code, retryable}` thành `ApiError`; thân không đúng dạng → `INTERNAL`. */
export async function toApiError(res: Response): Promise<ApiError> {
  let body: Partial<ErrorBody> | null = null;
  try {
    body = (await res.json()) as Partial<ErrorBody>;
  } catch {
    body = null;
  }
  const code = typeof body?.code === "string" ? body.code : "INTERNAL";
  const retryable = typeof body?.retryable === "boolean" ? body.retryable : false;
  return new ApiError(code, retryable, res.status);
}

function notifyHandlers(err: ApiError): void {
  if (err.code === "AUTH_EXPIRED") authExpiredHandler?.();
  else if (err.code === "AUTH_FORBIDDEN") forbiddenHandler?.();
}

export async function request<T>(
  path: string,
  opts: { method?: string; body?: unknown; signal?: AbortSignal } = {},
): Promise<T> {
  const method = (opts.method ?? "GET").toUpperCase();
  const headers: Record<string, string> = { Accept: "application/json" };
  if (method !== "GET") headers[CSRF_HEADER] = CSRF_VALUE;
  let body: string | undefined;
  if (opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.body);
  }

  let res: Response;
  try {
    res = await fetch(path, {
      method,
      credentials: "same-origin",
      headers,
      body,
      signal: opts.signal,
    });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") throw e;
    throw new ApiError("NETWORK", true);
  }

  if (!res.ok) {
    const err = await toApiError(res);
    notifyHandlers(err);
    throw err;
  }
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}
