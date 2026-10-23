import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { ApiError, request, setAuthExpiredHandler, setForbiddenHandler } from "@/api/client";

function jsonResponse(status: number, body: unknown): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function headersOf(call: unknown[]): Record<string, string> {
  return (call[1] as { headers: Record<string, string> }).headers;
}

describe("request", () => {
  const fetchMock = vi.fn();
  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
    setAuthExpiredHandler(() => {});
    setForbiddenHandler(() => {});
  });
  afterEach(() => vi.unstubAllGlobals());

  it("post_has_csrf_header", async () => {
    fetchMock.mockImplementation(() => Promise.resolve(jsonResponse(200, { ok: true })));
    await request("/x", { method: "POST", body: {} });
    await request("/x");
    expect(headersOf(fetchMock.mock.calls[0]!)["X-Requested-With"]).toBe("cwd");
    expect(headersOf(fetchMock.mock.calls[1]!)["X-Requested-With"]).toBeUndefined();
    expect((fetchMock.mock.calls[0]![1] as RequestInit).credentials).toBe("same-origin");
  });

  it("error_body_to_api_error", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(409, { code: "QUESTION_IN_PROGRESS", retryable: true }),
    );
    const err = await request("/x", { method: "POST", body: {} }).catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err).toMatchObject({ code: "QUESTION_IN_PROGRESS", retryable: true, status: 409 });
  });

  it("auth_expired_calls_handler", async () => {
    const handler = vi.fn();
    setAuthExpiredHandler(handler);
    fetchMock.mockResolvedValue(jsonResponse(401, { code: "AUTH_EXPIRED", retryable: false }));
    await expect(request("/x")).rejects.toMatchObject({ code: "AUTH_EXPIRED" });
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it("forbidden_calls_handler", async () => {
    const handler = vi.fn();
    setForbiddenHandler(handler);
    fetchMock.mockResolvedValue(jsonResponse(403, { code: "AUTH_FORBIDDEN", retryable: false }));
    await expect(request("/x")).rejects.toMatchObject({ code: "AUTH_FORBIDDEN" });
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it("network_error", async () => {
    fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(request("/x")).rejects.toMatchObject({ code: "NETWORK", retryable: true });
  });

  it("returns_undefined_on_204_and_parses_json", async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));
    expect(await request("/x", { method: "DELETE" })).toBeUndefined();
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { a: 1 }));
    expect(await request("/x")).toEqual({ a: 1 });
  });

  it("malformed_error_body_is_internal", async () => {
    fetchMock.mockResolvedValue(new Response("<html>boom</html>", { status: 502 }));
    await expect(request("/x")).rejects.toMatchObject({ code: "INTERNAL", retryable: false, status: 502 });
  });

  it("sends_json_body", async () => {
    fetchMock.mockResolvedValue(jsonResponse(200, {}));
    await request("/x", { method: "POST", body: { a: 1 } });
    const init = fetchMock.mock.calls[0]![1] as RequestInit;
    expect(init.body).toBe('{"a":1}');
    expect(headersOf(fetchMock.mock.calls[0]!)["Content-Type"]).toBe("application/json");
  });
});
