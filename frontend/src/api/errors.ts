// Bảng ánh xạ mã lỗi → thông báo tiếng Việt (CONTRACTS mục 3, cột cuối). Nơi duy nhất; giao diện không hiển thị chuỗi do máy chủ gửi.
import { M } from "@/content/messages";

export const GENERIC_ERROR = "Đã có lỗi xảy ra. Vui lòng thử lại.";

/** Chú thích đi kèm `OCR_UNREADABLE` (CONTRACTS mục 3). */
export const OCR_UNREADABLE_HINT = "Thử tải bản quét rõ nét hơn.";

export const ERROR_MESSAGES: Record<string, string> = {
  AUTH_EXPIRED: "Phiên đã hết hạn. Đang chuyển tới trang đăng nhập…",
  // Chưa cấp quyền; trường hợp bị thu hồi dùng `M["denied.revoked"]` (xem T-505).
  AUTH_FORBIDDEN: M["denied.title"],
  CSRF_REJECTED: "Không thực hiện được thao tác. Hãy tải lại trang rồi thử lại.",
  VALIDATION_ERROR: "Dữ liệu gửi lên không hợp lệ.",
  NOT_FOUND: "Không tìm thấy nội dung yêu cầu.",
  FILE_NOT_PDF: "Chỉ hỗ trợ tệp PDF.",
  FILE_TOO_LARGE: "Tệp vượt quá 50 MB.",
  FILE_TOO_MANY: "Chỉ tải tối đa 10 tệp mỗi lần.",
  FILE_CORRUPTED: "Tệp bị hỏng.",
  FILE_ENCRYPTED: "Tệp có mật khẩu.",
  OCR_UNREADABLE: "Không đọc được nội dung.",
  PROCESSING_ERROR: "Không xử lý được tài liệu.",
  DOC_NOT_FOUND: "Tài liệu đã bị xóa.",
  DOC_NOT_READY: "Tài liệu chưa sẵn sàng.",
  SESSION_NOT_FOUND: "Không tìm thấy phiên hội thoại.",
  QUESTION_EMPTY: "Hãy nhập câu hỏi.",
  QUESTION_TOO_LONG: "Câu hỏi vượt quá 2.000 ký tự.",
  QUESTION_IN_PROGRESS: "Đang trả lời câu hỏi trước. Hãy chờ hoặc bấm Dừng.",
  MESSAGE_NOT_RATEABLE: "Chỉ đánh giá được câu trả lời đã hoàn tất.",
  EMAIL_INVALID: "Email không hợp lệ.",
  USER_EXISTS: "Người dùng này đã có trong danh sách.",
  USER_LIMIT_REACHED: "Đã đạt giới hạn 20 người dùng.",
  LAST_ADMIN: "Không thể gỡ quản trị viên cuối cùng.",
  AI_UNAVAILABLE: "Dịch vụ hỏi đáp tạm thời gián đoạn. Vui lòng thử lại sau ít phút.",
  BUDGET_EXCEEDED: "Dịch vụ hỏi đáp tạm thời gián đoạn. Vui lòng thử lại sau ít phút.",
  TIMEOUT: "Không thể trả lời lúc này.",
  INTERNAL: GENERIC_ERROR,
  // Mã chỉ có ở giao diện: lỗi mạng.
  NETWORK: M["net.offline"],
};

/** Thông báo cho một mã lỗi; mã lạ dùng thông báo của `INTERNAL`. */
export function messageFor(code: string): string {
  return Object.prototype.hasOwnProperty.call(ERROR_MESSAGES, code)
    ? ERROR_MESSAGES[code]!
    : ERROR_MESSAGES.INTERNAL!;
}
