export const MAX_FILES = 10;
export const MAX_BYTES = 50 * 1024 * 1024;

export interface Rejected {
  file: File;
  code: "FILE_NOT_PDF" | "FILE_TOO_LARGE" | "FILE_TOO_MANY";
}

/**
 * Kiểm tra từng tệp ở trình duyệt (EC-08): không phải `.pdf` → FILE_NOT_PDF; quá cỡ → FILE_TOO_LARGE;
 * nhận tối đa `maxFiles` tệp hợp lệ đầu tiên, tệp hợp lệ thứ 11 trở đi → FILE_TOO_MANY `[Đề xuất]`.
 */
export function validateFiles(
  files: File[],
  limits: { maxFiles: number; maxBytes: number } = { maxFiles: MAX_FILES, maxBytes: MAX_BYTES },
): { accepted: File[]; rejected: Rejected[] } {
  const accepted: File[] = [];
  const rejected: Rejected[] = [];
  for (const file of files) {
    if (!file.name.toLowerCase().endsWith(".pdf")) rejected.push({ file, code: "FILE_NOT_PDF" });
    else if (file.size > limits.maxBytes) rejected.push({ file, code: "FILE_TOO_LARGE" });
    else if (accepted.length >= limits.maxFiles) rejected.push({ file, code: "FILE_TOO_MANY" });
    else accepted.push(file);
  }
  return { accepted, rejected };
}

/** Lý do telemetry `document_upload_rejected` (CONTRACTS mục 6). */
export function telemetryReason(code: Rejected["code"]): "not_pdf" | "too_large" | "too_many" {
  return code === "FILE_NOT_PDF" ? "not_pdf" : code === "FILE_TOO_LARGE" ? "too_large" : "too_many";
}
