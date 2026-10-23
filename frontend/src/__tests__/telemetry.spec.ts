import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { track, isValidEvent, type ClientEvent } from "@/api/telemetry";

const U1 = "11111111-1111-4111-8111-111111111111";
const U2 = "22222222-2222-4222-8222-222222222222";

describe("telemetry", () => {
  const fetchMock = vi.fn();
  beforeEach(() => {
    fetchMock.mockReset();
    fetchMock.mockImplementation(() => Promise.resolve(new Response(null, { status: 204 })));
    vi.stubGlobal("fetch", fetchMock);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("rejects_free_text_props", () => {
    track("citation_clicked", { question_id: U1, doc_id: U2, page: 3, text: "abc" });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects_unknown_event", () => {
    track("answer_completed" as ClientEvent, { question_id: U1 });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("sends_valid_event", () => {
    track("answer_copied", { question_id: U1 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit & { headers: Record<string, string> }];
    expect(url).toBe("/api/v1/telemetry/events");
    expect(init.keepalive).toBe(true);
    expect(init.method).toBe("POST");
    expect(init.headers["X-Requested-With"]).toBe("cwd");
    expect(JSON.parse(init.body as string)).toEqual({ event: "answer_copied", props: { question_id: U1 } });
  });

  it("failure_is_silent", async () => {
    fetchMock.mockImplementation(() => Promise.reject(new TypeError("net")));
    expect(() => track("onboarding_viewed", { doc_count: 3 })).not.toThrow();
    await Promise.resolve();
    fetchMock.mockImplementation(() => {
      throw new Error("sync");
    });
    expect(() => track("onboarding_viewed", { doc_count: 3 })).not.toThrow();
  });

  it("validates_types_and_ranges", () => {
    expect(isValidEvent("document_upload_started", { file_count: 2, total_size_mb: 4 })).toBe(true);
    expect(isValidEvent("document_upload_started", { file_count: 11, total_size_mb: 4 })).toBe(false);
    expect(isValidEvent("document_upload_started", { file_count: 0, total_size_mb: 4 })).toBe(false);
    expect(isValidEvent("document_upload_started", { file_count: 2, total_size_mb: -1 })).toBe(false);
    expect(isValidEvent("document_upload_started", { file_count: 2 })).toBe(false);
    expect(isValidEvent("document_upload_rejected", { reason: "not_pdf" })).toBe(true);
    expect(isValidEvent("document_upload_rejected", { reason: "HD.docx" })).toBe(false);
    expect(isValidEvent("suggestion_clicked", { suggestion_index: 3 })).toBe(false);
    expect(isValidEvent("suggestion_clicked", { suggestion_index: 2 })).toBe(true);
    expect(isValidEvent("citation_clicked", { question_id: "m1", doc_id: U2, page: 3 })).toBe(false);
    expect(isValidEvent("onboarding_viewed", { doc_count: 1.5 })).toBe(false);
    expect(isValidEvent("toString", {})).toBe(false);
  });
});
