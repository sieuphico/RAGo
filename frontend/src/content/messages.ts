// Vi nội dung dùng chung (CONTRACTS mục 10.4). Thành phần không viết chuỗi cứng.
// Chỉ thêm khóa; không đổi nội dung khóa đã có mà chưa cập nhật CONTRACTS mục 10.4.

export const M = {
  "composer.placeholder": "Hỏi về nội dung tài liệu…",
  "composer.disclaimer": "Câu trả lời do AI tạo – hãy kiểm tra trích dẫn với thông tin quan trọng.",
  "composer.counter": "{n}/2.000",
  "answer.searching": "Đang tìm trong {N} tài liệu…",
  "answer.slow": "Câu hỏi đang mất nhiều thời gian hơn bình thường…",
  "answer.notFound": "Không tìm thấy thông tin này trong các tài liệu hiện có.",
  "answer.notFoundHint": "Thử diễn đạt khác, hoặc kiểm tra tài liệu đã được tải lên chưa.",
  "answer.noReadyDocs": "Kho chưa có tài liệu sẵn sàng. Hãy tải PDF lên để bắt đầu.",
  "answer.stopped": "Đã dừng",
  "answer.interrupted": "Mất kết nối – câu trả lời chưa đầy đủ.",
  "answer.langNotice": "Hiện chỉ hỗ trợ tốt tiếng Việt và tiếng Anh.",
  "net.offline": "Mất kết nối. Đang thử kết nối lại…",
  "library.empty": "Chưa có tài liệu. Kéo thả PDF vào đây.",
  "library.emptyNoUpload": "Chưa có tài liệu.",
  "library.loadError": "Không tải được danh sách.",
  "library.uploadNotAllowed": "Chỉ Trưởng nhóm BD tải được tài liệu lên.",
  "library.processingCount": "{N} tài liệu đang được xử lý, chưa dùng để trả lời.",
  "chat.emptyLibrary": "Kho chưa có tài liệu.",
  "scope.all": "Phạm vi: Tất cả tài liệu",
  "scope.some": "Đang hỏi trong {N} tài liệu",
  "scope.removed": "Một tài liệu trong phạm vi đã bị xóa và được bỏ khỏi phạm vi.",
  "citation.deleted": "Tài liệu đã bị xóa",
  "citation.aria": "Trích dẫn: {tên tài liệu}, trang {N}, mở trang nguồn",
  "viewer.error": "Không mở được trang.",
  "copy.done": "Đã sao chép",
  "delete.title": "Xóa tài liệu?",
  "delete.body": "Bạn sắp xóa \"{tên}\". Cả đội sẽ không thể hỏi về tài liệu này nữa. Dữ liệu được xóa trong 24 giờ.",
  "delete.already": "Tài liệu đã được xóa trước đó.",
  "duplicate.title": "Tài liệu này có thể đã có trong kho",
  "summary.title": "Tóm tắt do AI tạo cho {tên tài liệu}",
  "suggest.title": "Gợi ý câu hỏi",
  "history.empty": "Chưa có phiên nào",
  "history.error": "Không tải được lịch sử.",
  "denied.title": "Bạn chưa được cấp quyền. Liên hệ quản trị viên.",
  "denied.revoked": "Quyền truy cập của bạn đã bị thu hồi.",
  "login.button": "Đăng nhập bằng tài khoản công ty",
  "login.expired": "Phiên đã hết hạn. Đăng nhập lại để tiếp tục.",
  "metrics.empty": "Chưa có dữ liệu. Số liệu xuất hiện sau tuần sử dụng đầu tiên.",
  "users.empty": "Chưa có người dùng nào được cấp quyền",
  "audit.empty": "Chưa có hoạt động nào",
  "action.retry": "Thử lại",
  "action.askAgain": "Hỏi lại",

  // ---- Khóa thêm bởi các task giao diện (chỉ thêm; không thuộc bảng CONTRACTS 10.4)
  "app.name": "Chat với tài liệu",
  "app.skipToMain": "Bỏ qua tới nội dung chính",
  "nav.aria": "Điều hướng chính",
  "nav.chat": "Hỏi đáp",
  "nav.library": "Kho tài liệu",
  "nav.metrics": "Số liệu",
  "nav.admin": "Quản trị",
  "auth.logout": "Đăng xuất",
  "role.BD_USER": "Người dùng BD",
  "role.TEAM_LEAD": "Trưởng nhóm BD",
  "role.ADMIN": "Quản trị viên",
  "role.SPONSOR": "Nhà tài trợ",
} as const;

export type MessageKey = keyof typeof M;

/** Lấy chuỗi theo khóa và thay `{N}`, `{n}`, `{tên}`… bằng tham số; tham số thiếu giữ nguyên chỗ giữ. */
export function t(key: MessageKey, params?: Record<string, string | number>): string {
  const raw: string = M[key];
  if (!params) return raw;
  return raw.replace(/\{([^}]+)\}/g, (whole, name: string) =>
    Object.prototype.hasOwnProperty.call(params, name) ? String(params[name]) : whole,
  );
}
