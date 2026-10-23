// Đọc luồng SSE từ yêu cầu POST bằng fetch (AD-02; không dùng EventSource vì không gửi được thân POST).
import { ApiError, CSRF_HEADER, CSRF_VALUE, notifyAuthError, toApiError } from "./client";
import type { CitationData, DoneData, ErrorData, StatusData, TokenData } from "./types";

export interface StreamHandlers {
  onStatus(d: StatusData): void;
  onToken(d: TokenData): void;
  onCitation(d: CitationData): void;
  onDone(d: DoneData): void;
  onError(d: ErrorData): void;
  onInterrupted(): void;
}

interface Frame {
  event: string;
  data: string;
}

/** Tách một khung SSE (các dòng giữa hai dòng trống). Dòng `:` là chú thích; nhiều dòng `data:` ghép bằng `\n`. */
function parseFrame(raw: string): Frame | null {
  let event = "message";
  const data: string[] = [];
  for (const line of raw.split(/\r?\n/)) {
    if (line === "" || line.startsWith(":")) continue;
    const idx = line.indexOf(":");
    const field = idx === -1 ? line : line.slice(0, idx);
    let value = idx === -1 ? "" : line.slice(idx + 1);
    if (value.startsWith(" ")) value = value.slice(1);
    if (field === "event") event = value;
    else if (field === "data") data.push(value);
  }
  return data.length === 0 ? null : { event, data: data.join("\n") };
}

export async function streamPost(
  path: string,
  body: unknown,
  h: StreamHandlers,
  signal: AbortSignal,
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(path, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        [CSRF_HEADER]: CSRF_VALUE,
        Accept: "text/event-stream",
      },
      body: JSON.stringify(body),
      signal,
    });
  } catch (e) {
    if (signal.aborted || (e instanceof DOMException && e.name === "AbortError")) return;
    throw new ApiError("NETWORK", true);
  }

  const type = res.headers.get("Content-Type") ?? "";
  if (!res.ok || !type.includes("text/event-stream") || !res.body) {
    const err = await toApiError(res);
    notifyAuthError(err);
    throw err;
  }

  const reader = res.body.getReader();
  const onAbort = () => {
    reader.cancel().catch(() => {});
  };
  signal.addEventListener("abort", onAbort, { once: true });

  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  let finished = false; // đã gặp done hoặc error

  const dispatch = (frame: Frame): void => {
    if (signal.aborted) return;
    let payload: unknown;
    try {
      payload = JSON.parse(frame.data);
    } catch {
      return; // khung hỏng: bỏ qua
    }
    switch (frame.event) {
      case "status":
        h.onStatus(payload as StatusData);
        break;
      case "token":
        h.onToken(payload as TokenData);
        break;
      case "citation":
        h.onCitation(payload as CitationData);
        break;
      case "done":
        finished = true;
        h.onDone(payload as DoneData);
        break;
      case "error":
        finished = true;
        h.onError(payload as ErrorData);
        break;
      default:
        break; // tên lạ bỏ qua
    }
  };

  const drain = (flush: boolean): void => {
    const parts = buffer.split(/\r?\n\r?\n/);
    buffer = flush ? "" : (parts.pop() ?? "");
    for (const raw of flush ? parts.filter((p) => p.trim() !== "") : parts) {
      if (finished || signal.aborted) return;
      const frame = parseFrame(raw);
      if (frame) dispatch(frame);
    }
  };

  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (signal.aborted) return;
      if (value) buffer += decoder.decode(value, { stream: true });
      if (done) {
        buffer += decoder.decode();
        drain(true);
        break;
      }
      drain(false);
      if (finished) {
        await reader.cancel().catch(() => {});
        return;
      }
    }
    if (!finished && !signal.aborted) h.onInterrupted();
  } catch {
    if (!signal.aborted && !finished) h.onInterrupted();
  } finally {
    signal.removeEventListener("abort", onAbort);
  }
}
