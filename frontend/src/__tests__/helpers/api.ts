// Trợ giúp test: thay `fetch` toàn cục bằng bảng route giả theo CONTRACTS mục 4 (ADR 0101).
import { vi, type Mock } from "vitest";

export function jsonRes(status: number, body?: unknown): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export interface FakeReq {
  url: string;
  path: string;
  method: string;
  body: unknown;
  headers: Record<string, string>;
}

export type FakeHandler = (req: FakeReq) => Response | Promise<Response>;

/** Khóa dạng `"GET /api/v1/me"` (không kèm chuỗi truy vấn). Route không khai báo trả 404 `NOT_FOUND`. */
export function installFetch(routes: Record<string, FakeHandler>): Mock {
  const fn = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const path = url.split("?")[0]!;
    const method = (init?.method ?? "GET").toUpperCase();
    const headers = (init?.headers ?? {}) as Record<string, string>;
    let body: unknown = init?.body;
    if (typeof body === "string") {
      try {
        body = JSON.parse(body);
      } catch {
        /* giữ nguyên chuỗi */
      }
    }
    const handler = routes[`${method} ${path}`];
    if (!handler) return jsonRes(404, { code: "NOT_FOUND", retryable: false });
    return handler({ url, path, method, body, headers });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

export function calls(fn: Mock): string[] {
  return fn.mock.calls.map((c) => `${((c[1] as RequestInit | undefined)?.method ?? "GET").toUpperCase()} ${String(c[0]).split("?")[0]}`);
}

export const flush = async (): Promise<void> => {
  for (let i = 0; i < 5; i++) await Promise.resolve();
  await new Promise((r) => setTimeout(r, 0));
};
