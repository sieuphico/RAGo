import { describe, it, expect } from "vitest";
import { ERROR_MESSAGES, messageFor, GENERIC_ERROR } from "@/api/errors";
import { M, t } from "@/content/messages";

// 27 mã chép từ CONTRACTS mục 3.
const CONTRACT_CODES = [
  "AUTH_EXPIRED", "AUTH_FORBIDDEN", "CSRF_REJECTED", "VALIDATION_ERROR", "NOT_FOUND",
  "FILE_NOT_PDF", "FILE_TOO_LARGE", "FILE_TOO_MANY", "FILE_CORRUPTED", "FILE_ENCRYPTED",
  "OCR_UNREADABLE", "PROCESSING_ERROR", "DOC_NOT_FOUND", "DOC_NOT_READY", "SESSION_NOT_FOUND",
  "QUESTION_EMPTY", "QUESTION_TOO_LONG", "QUESTION_IN_PROGRESS", "MESSAGE_NOT_RATEABLE",
  "EMAIL_INVALID", "USER_EXISTS", "USER_LIMIT_REACHED", "LAST_ADMIN",
  "AI_UNAVAILABLE", "BUDGET_EXCEEDED", "TIMEOUT", "INTERNAL",
];

describe("errors", () => {
  it("every_error_code_has_message", () => {
    expect(CONTRACT_CODES).toHaveLength(27);
    for (const code of CONTRACT_CODES) {
      expect(ERROR_MESSAGES[code], code).toBeTruthy();
      if (code !== "INTERNAL") expect(messageFor(code), code).not.toBe(GENERIC_ERROR);
    }
    expect(messageFor("NETWORK")).toBe(M["net.offline"]);
  });

  it("unknown_code_gets_generic_message", () => {
    expect(messageFor("ABC")).toBe("Đã có lỗi xảy ra. Vui lòng thử lại.");
    expect(messageFor("toString")).toBe(GENERIC_ERROR);
  });

  it("no_technical_terms", () => {
    for (const msg of Object.values(ERROR_MESSAGES)) {
      expect(msg).not.toMatch(/500|timeout|token|error/i);
    }
  });

  it("messages_cover_contract_keys_and_substitute_params", () => {
    expect(t("answer.searching", { N: 125 })).toBe("Đang tìm trong 125 tài liệu…");
    expect(t("delete.body", { tên: "HD.pdf" })).toContain("\"HD.pdf\"");
    expect(t("summary.title", { "tên tài liệu": "A.pdf" })).toBe("Tóm tắt do AI tạo cho A.pdf");
    expect(t("answer.searching")).toContain("{N}");
    expect(Object.keys(M).length).toBeGreaterThanOrEqual(42);
  });
});
