# T-311 · Phạm vi tài liệu trong API-08 và EC-15

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P1 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | US-026 |
| BR | BR-015 |
| NFR, EC, cổng | EC-15 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md) |
| Mở khóa | [T-514](T-514-chon-pham-vi-tai-lieu.md) |

## Mục tiêu

Giới hạn truy xuất theo `scopeDocIds`; tự loại tài liệu đã xóa và báo người dùng.

## File cần tạo hoặc sửa

- `backend/app/modules/answer/scope.py`
- `backend/tests/integration/test_scope.py`

## Các bước

1. `normalize_scope(session, scope) -> ScopeResult(effective: set[UUID], removed: set[UUID])`.
2. Tài liệu đã xóa hoặc không `READY` bị loại và đưa vào `removed`; phát sự kiện `status` kèm `scopeRemoved`.
3. Phạm vi rỗng sau khi loại thì quay về tất cả tài liệu.

## Tiêu chí hoàn thành

- [ ] Giới hạn vào A thì câu trả lời chỉ trích dẫn A (AC-015).
- [ ] Tài liệu bị xóa khỏi phạm vi được báo cho người dùng (EC-15).
- [ ] Phạm vi trống quay về "Tất cả tài liệu".

## Kiểm thử cần viết

- `test_scope_only_cites_selected`
- `test_deleted_doc_removed_from_scope`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
