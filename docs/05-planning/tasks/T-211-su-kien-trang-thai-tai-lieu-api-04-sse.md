# T-211 · Sự kiện trạng thái tài liệu (API-04, SSE)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-012 |
| BR | BR-005 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-02 |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) |
| Mở khóa | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-509](T-509-cap-nhat-trang-thai-tai-lieu-theo-thoi-gian-thuc.md) |

## Mục tiêu

Đẩy thay đổi trạng thái tài liệu tới giao diện qua SSE, không cần tải lại trang.

## File cần tạo hoặc sửa

- `backend/app/modules/documents/events.py`
- `backend/app/api/document_events.py`
- `backend/tests/integration/test_document_events.py`

## Các bước

1. `publish_status(doc_id, status, reason=None)` gửi qua PostgreSQL `NOTIFY` `[Đề xuất]` để worker (tiến trình khác) báo được cho API.
2. `GET /api/v1/documents/events` giữ kết nối SSE, nhận `LISTEN` và chuyển thành sự kiện `{docId, status, reason}`.
3. Gửi `ping` định kỳ để giữ kết nối; hỗ trợ giao diện tự hỏi lại mỗi 3 giây khi SSE không dùng được.

## Tiêu chí hoàn thành

- [ ] Đổi trạng thái ở worker xuất hiện ở client SSE trong vài giây.
- [ ] Người chưa xác thực không nhận được luồng.
- [ ] Ngắt kết nối giải phóng tài nguyên.

## Kiểm thử cần viết

- `test_status_event_delivered`
- `test_events_require_auth`
- `test_disconnect_cleanup`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
