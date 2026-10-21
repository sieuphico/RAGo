# T-314 · Nối telemetry vào các luồng chính

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | US-051 |
| BR | — |
| NFR, EC, cổng | NFR-001 |
| Quyết định kiến trúc | AD-10 |
| Phụ thuộc | [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-307](T-307-dich-vu-tra-loi-answerservice.md) |
| Mở khóa | [T-610](T-610-kiem-tra-telemetry-tren-staging-g8.md) |

## Mục tiêu

Phát đúng sự kiện P0 ở PRD mục 5.2 từ các luồng đăng nhập, tải lên, xử lý, hỏi đáp.

## File cần tạo hoặc sửa

- `backend/app/modules/telemetry/wiring.py`
- `backend/tests/integration/test_telemetry_wiring.py`

## Các bước

1. Gọi `emit` tại: đăng nhập, từ chối truy cập, bắt đầu tải lên, từ chối tải lên, xử lý xong và thất bại, câu hỏi gửi, chữ đầu tiên, câu trả lời xong, câu hỏi lỗi.
2. Không truyền văn bản tự do; chỉ các thuộc tính trong lược đồ (độ dài, ngôn ngữ, số trích dẫn, độ trễ, mã lý do).
3. Sự kiện phía giao diện (`citation_clicked`, `answer_copied`…) đến từ API-16 ở T-521.

## Tiêu chí hoàn thành

- [ ] Mọi sự kiện P0 phía máy chủ được ghi đúng tên và thuộc tính (G8).
- [ ] Không có sự kiện nào chứa nội dung.
- [ ] Lỗi ghi telemetry không làm hỏng luồng chính.

## Kiểm thử cần viết

- `test_events_emitted_for_upload_and_answer`
- `test_telemetry_failure_does_not_break_flow`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
