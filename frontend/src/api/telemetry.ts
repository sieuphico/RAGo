// Telemetry phía giao diện (T-521, AD-10): chỉ siêu dữ liệu, không có văn bản tự do.
// 6 sự kiện nguồn "giao diện" ở CONTRACTS mục 6; sự kiện khác, thiếu/thừa thuộc tính, sai kiểu → bỏ.
import { CSRF_HEADER, CSRF_VALUE } from "./client";

export type ClientEvent =
  | "onboarding_viewed"
  | "document_upload_started"
  | "document_upload_rejected"
  | "suggestion_clicked"
  | "citation_clicked"
  | "answer_copied";

type Rule =
  | { type: "int"; min?: number; max?: number }
  | { type: "float"; min?: number }
  | { type: "uuid" }
  | { type: "enum"; values: readonly string[] };

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const CLIENT_SCHEMA: Record<ClientEvent, Record<string, Rule>> = {
  onboarding_viewed: { doc_count: { type: "int", min: 0 } },
  document_upload_started: { file_count: { type: "int", min: 1, max: 10 }, total_size_mb: { type: "float", min: 0 } },
  document_upload_rejected: {
    reason: { type: "enum", values: ["not_pdf", "too_large", "too_many", "invalid_pdf"] },
  },
  suggestion_clicked: { suggestion_index: { type: "int", min: 0, max: 2 } },
  citation_clicked: { question_id: { type: "uuid" }, doc_id: { type: "uuid" }, page: { type: "int", min: 1 } },
  answer_copied: { question_id: { type: "uuid" } },
};

function valid(rule: Rule, v: unknown): boolean {
  switch (rule.type) {
    case "int":
      return (
        typeof v === "number" && Number.isInteger(v) && (rule.min === undefined || v >= rule.min) && (rule.max === undefined || v <= rule.max)
      );
    case "float":
      return typeof v === "number" && Number.isFinite(v) && (rule.min === undefined || v >= rule.min);
    case "uuid":
      return typeof v === "string" && UUID_RE.test(v);
    case "enum":
      return typeof v === "string" && rule.values.includes(v);
  }
}

/** Trả về `true` nếu sự kiện đúng lược đồ. */
export function isValidEvent(event: string, props: Record<string, unknown>): boolean {
  if (!Object.prototype.hasOwnProperty.call(CLIENT_SCHEMA, event)) return false;
  const schema = CLIENT_SCHEMA[event as ClientEvent];
  const keys = Object.keys(props);
  if (keys.length !== Object.keys(schema).length) return false;
  return keys.every((k) => Object.prototype.hasOwnProperty.call(schema, k) && valid(schema[k]!, props[k]));
}

export function track(event: ClientEvent, props: Record<string, string | number | boolean>): void {
  if (!isValidEvent(event, props)) {
    if (import.meta.env.DEV) console.warn(`telemetry: bỏ sự kiện không hợp lệ "${String(event)}"`);
    return;
  }
  try {
    void fetch("/api/v1/telemetry/events", {
      method: "POST",
      keepalive: true,
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", [CSRF_HEADER]: CSRF_VALUE },
      body: JSON.stringify({ event, props }),
    }).catch(() => {});
  } catch {
    /* nuốt lỗi: telemetry không bao giờ làm hỏng giao diện */
  }
}
