import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { streamPost, type StreamHandlers } from "@/api/sse";
import { ApiError } from "@/api/client";

const enc = new TextEncoder();

function handlers(): StreamHandlers & Record<keyof StreamHandlers, ReturnType<typeof vi.fn>> {
  return {
    onStatus: vi.fn(),
    onToken: vi.fn(),
    onCitation: vi.fn(),
    onDone: vi.fn(),
    onError: vi.fn(),
    onInterrupted: vi.fn(),
  };
}

/** Luồng giả: mỗi phần tử là một khối byte; `hold` giữ luồng mở sau khối cuối để thử hủy. */
function sseResponse(chunks: Uint8Array[], opts: { hold?: boolean } = {}): Response {
  let i = 0;
  const stream = new ReadableStream<Uint8Array>({
    pull(controller) {
      if (i < chunks.length) {
        controller.enqueue(chunks[i++]);
      } else if (!opts.hold) {
        controller.close();
      } else {
        return new Promise<void>(() => {}); // không bao giờ kết thúc; chờ cancel
      }
    },
  });
  return new Response(stream, { status: 200, headers: { "Content-Type": "text/event-stream" } });
}

const frame = (event: string, data: unknown) => enc.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);

describe("streamPost", () => {
  const fetchMock = vi.fn();
  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("parses_split_frames", async () => {
    const bytes = enc.encode('event: token\ndata: {"text":"Hợp đồng"}\n\n');
    // cắt giữa ký tự nhiều byte "ợ" (3 byte)
    const cut = bytes.indexOf(0xe1) + 1;
    fetchMock.mockResolvedValue(sseResponse([bytes.slice(0, cut), bytes.slice(cut)]));
    const h = handlers();
    await streamPost("/api/v1/chat/sessions/s/messages", { text: "q" }, h, new AbortController().signal);
    expect(h.onToken).toHaveBeenCalledTimes(1);
    expect(h.onToken).toHaveBeenCalledWith({ text: "Hợp đồng" });
  });

  it("parses_frames_split_at_every_byte", async () => {
    const all = enc.encode(
      'event: status\ndata: {"stage":"searching","docCount":2,"messageId":"m1","scopeRemoved":[]}\r\n\r\n' +
        'event: token\ndata: {"text":"Thời hạn 24 tháng"}\n\n' +
        'event: done\ndata: {"messageId":"m1","citationCount":0,"isNotFound":false,"notFoundReason":null,"notice":null,"stopped":false}\n\n',
    );
    const chunks = Array.from(all, (b) => new Uint8Array([b]));
    fetchMock.mockResolvedValue(sseResponse(chunks));
    const h = handlers();
    await streamPost("/p", {}, h, new AbortController().signal);
    expect(h.onStatus).toHaveBeenCalledTimes(1);
    expect(h.onToken).toHaveBeenCalledWith({ text: "Thời hạn 24 tháng" });
    expect(h.onDone).toHaveBeenCalledTimes(1);
    expect(h.onInterrupted).not.toHaveBeenCalled();
  });

  it("ignores_comments", async () => {
    fetchMock.mockResolvedValue(
      sseResponse([enc.encode(": ping\n\n"), frame("token", { text: "a" }), enc.encode(": ping\n\n")]),
    );
    const h = handlers();
    await streamPost("/p", {}, h, new AbortController().signal);
    expect(h.onToken).toHaveBeenCalledTimes(1);
    expect(h.onStatus).not.toHaveBeenCalled();
    expect(h.onCitation).not.toHaveBeenCalled();
  });

  it("dispatch_all_events", async () => {
    const order: string[] = [];
    const h = handlers();
    h.onStatus.mockImplementation(() => order.push("status"));
    h.onCitation.mockImplementation(() => order.push("citation"));
    h.onToken.mockImplementation(() => order.push("token"));
    h.onDone.mockImplementation(() => order.push("done"));
    fetchMock.mockResolvedValue(
      sseResponse([
        frame("status", { stage: "searching", docCount: 1, messageId: "m", scopeRemoved: [] }),
        frame("citation", { index: 1, docId: "d", docName: "A.pdf", page: 2, snippet: "x" }),
        frame("token", { text: "t [[1]]" }),
        frame("mystery", { a: 1 }),
        frame("done", { messageId: "m", citationCount: 1, isNotFound: false, notFoundReason: null, notice: null, stopped: false }),
      ]),
    );
    await streamPost("/p", {}, h, new AbortController().signal);
    expect(order).toEqual(["status", "citation", "token", "done"]);
    expect(h.onInterrupted).not.toHaveBeenCalled();
  });

  it("error_event_is_terminal", async () => {
    fetchMock.mockResolvedValue(sseResponse([frame("error", { code: "AI_UNAVAILABLE", retryable: true })]));
    const h = handlers();
    await streamPost("/p", {}, h, new AbortController().signal);
    expect(h.onError).toHaveBeenCalledWith({ code: "AI_UNAVAILABLE", retryable: true });
    expect(h.onInterrupted).not.toHaveBeenCalled();
  });

  it("interrupt_before_done", async () => {
    fetchMock.mockResolvedValue(sseResponse([frame("token", { text: "Hợp" })]));
    const h = handlers();
    await streamPost("/p", {}, h, new AbortController().signal);
    expect(h.onToken).toHaveBeenCalledTimes(1);
    expect(h.onInterrupted).toHaveBeenCalledTimes(1);
  });

  it("interrupt_on_read_error", async () => {
    const stream = new ReadableStream<Uint8Array>({
      start(c) {
        c.enqueue(frame("token", { text: "a" }));
        c.error(new TypeError("network"));
      },
    });
    fetchMock.mockResolvedValue(
      new Response(stream, { status: 200, headers: { "Content-Type": "text/event-stream" } }),
    );
    const h = handlers();
    await streamPost("/p", {}, h, new AbortController().signal);
    expect(h.onInterrupted).toHaveBeenCalledTimes(1);
  });

  it("abort_stops_stream", async () => {
    const controller = new AbortController();
    fetchMock.mockResolvedValue(sseResponse([frame("token", { text: "a" }), frame("token", { text: "b" })], { hold: true }));
    const h = handlers();
    h.onToken.mockImplementation(() => controller.abort());
    await streamPost("/p", {}, h, controller.signal);
    expect(h.onToken).toHaveBeenCalledTimes(1);
    expect(h.onInterrupted).not.toHaveBeenCalled();
  });

  it("http_error_before_stream", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ code: "QUESTION_IN_PROGRESS", retryable: true }), {
        status: 409,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const h = handlers();
    const err = await streamPost("/p", {}, h, new AbortController().signal).catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err).toMatchObject({ code: "QUESTION_IN_PROGRESS", retryable: true });
    for (const fn of Object.values(h)) expect(fn).not.toHaveBeenCalled();
  });

  it("sends_post_headers", async () => {
    fetchMock.mockResolvedValue(sseResponse([]));
    await streamPost("/p", { text: "q" }, handlers(), new AbortController().signal);
    const init = fetchMock.mock.calls[0]![1] as RequestInit & { headers: Record<string, string> };
    expect(init.method).toBe("POST");
    expect(init.credentials).toBe("same-origin");
    expect(init.headers["X-Requested-With"]).toBe("cwd");
    expect(init.headers.Accept).toBe("text/event-stream");
    expect(init.body).toBe('{"text":"q"}');
  });

  it("network_failure_before_stream", async () => {
    fetchMock.mockRejectedValue(new TypeError("fail"));
    await expect(streamPost("/p", {}, handlers(), new AbortController().signal)).rejects.toMatchObject({
      code: "NETWORK",
      retryable: true,
    });
  });
});
