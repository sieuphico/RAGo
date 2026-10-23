import { describe, it, expect } from "vitest";
import { formatDateTime, formatInt, formatDecimal, normalizeText, truncateMiddle } from "@/utils/format";

describe("format", () => {
  it("truncate_middle", () => {
    const s = "a".repeat(30) + ".pdf";
    const out = truncateMiddle(s, 20);
    expect(out).toHaveLength(20);
    expect(out).toContain("…");
    expect(out.endsWith(".pdf")).toBe(true);
    expect(truncateMiddle("ngan.pdf", 20)).toBe("ngan.pdf");
  });

  it("format_datetime", () => {
    process.env.TZ = "Asia/Ho_Chi_Minh";
    expect(formatDateTime("2026-10-19T02:12:00Z")).toBe("19/10/2026 09:12");
    expect(formatDateTime("không hợp lệ")).toBe("");
  });

  it("normalize_text_and_numbers", () => {
    expect(normalizeText("Hợp đồng ABC")).toBe("hop dong abc");
    expect(normalizeText("ĐIỀU KHOẢN")).toBe("dieu khoan");
    expect(formatInt(2001)).toBe("2.001");
    expect(formatDecimal(6.2, 1)).toBe("6,2");
  });
});
