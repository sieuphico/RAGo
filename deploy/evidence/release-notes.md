# Ghi chú phát hành — MVP "Chat với tài liệu" (bản thí điểm)

## Đã có
- Đăng nhập qua IdP, danh sách người được cấp quyền, 4 vai trò; chặn ở máy chủ, thu hồi quyền có hiệu lực ngay (US-001, US-002, US-061).
- Trưởng nhóm BD tải PDF (≤ 50 MB, tới 10 tệp), thấy trạng thái cập nhật không cần tải lại trang; PDF lỗi/có mật khẩu báo lý do rõ (US-010–US-014).
- Danh sách tài liệu có tìm kiếm và sắp xếp; xóa tài liệu (xóa vật lý dữ liệu đã xử lý trong ≤ 24 giờ) (US-015, US-016, US-062, US-064).
- Hỏi đáp tiếng Việt/Anh có trích dẫn `[Tên – tr. N]`, bấm trích dẫn mở đúng trang PDF, báo "không tìm thấy", hiển thị dần và Dừng (US-020–US-023, US-027).
- Số liệu hàng tuần cho nhà tài trợ, nhật ký tải lên/xóa, telemetry chỉ siêu dữ liệu (US-051, US-063).
- AI chạy nội bộ bằng Ollama (Qwen3 1.7B sinh, qwen3-embedding:0.6b nhúng); dữ liệu không rời máy chủ.

## P1 đang bật bằng cờ (`CWD_FEATURES`; mặc định bật hết, tắt từng mục khi cần cắt phạm vi)
`suggestions` (câu hỏi mẫu), `summary` (tóm tắt), `history` (lịch sử 90 ngày), `rating` (👍/👎), `copy`, `scope` (giới hạn tài liệu), `followup` (câu nối tiếp), `duplicateCheck` (cảnh báo tệp trùng). Thứ tự cắt khi trễ: gợi ý → tóm tắt → lịch sử → sao chép.

## Giới hạn đã biết
- **OCR PDF ảnh quét (US-013) chưa dùng được thật:** luồng, trạng thái và ngưỡng đã có nhưng chưa có bộ nối Tesseract/bộ dựng ảnh trang; tệp quét sẽ báo lỗi xử lý. Chờ khảo sát T-004/T-010.
- **Hiệu năng AI trên CPU:** câu hỏi đầu cuối ~17–23 giây, chưa đạt NFR-001 (p90 ≤ 15 giây). Cần GPU, giảm `CWD_RETRIEVAL_K` hoặc mô hình nhanh hơn; đo bằng bộ câu hỏi chuẩn (T-607) và thử tải (T-608).
- Chất lượng Qwen3 1.7B (trích dẫn đúng trang, từ chối câu ngoài phạm vi, tiếng Việt) chưa đo bằng bộ câu hỏi chuẩn (DEP-003 chưa có); ngưỡng liên quan mặc định 0,0.
- SSO thật chưa tích hợp (T-006): đang dùng IdP giả cho phát triển; **không dùng IdP giả ở môi trường có dữ liệu thật**.
- Danh sách tài liệu không phân trang (tối đa 500).
- Ngôn ngữ ngoài Việt/Anh: trả lời tiếng Việt kèm thông báo.
- Bản sao lưu ≤ 7 ngày có thể còn dữ liệu tài liệu đã xóa (ngoại lệ BR-029, chờ Bảo mật thông tin duyệt).
- Một số AC `[Đề xuất]` ở giao diện đã làm theo tiêu chí của task nhưng chưa được PM/PO duyệt (xem `frontend/OPEN_QUESTIONS.md`, FQ-09).

## Điểm cần kiểm khi thí điểm
1. Tải 5 PDF mẫu của đội BD, đo thời gian tới `Sẵn sàng`.
2. Chạy bộ câu hỏi chuẩn: đúng trang ≥ 90% (AC-010), "không tìm thấy" đúng ≥ 9/10 (AC-011), p90 ≤ 15 giây (AC-013).
3. Thử thu hồi quyền một người đang đăng nhập; kiểm tra khôi phục từ bản sao lưu.
4. Theo dõi `cwd_ai_cost_usd_month` và cảnh báo.
