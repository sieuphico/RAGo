# T-202 · Danh sách tài liệu (API-03)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-015 |
| BR | BR-006 |
| NFR, EC, cổng | NFR-004 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) |
| Mở khóa | [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) |

## Mục tiêu

Trả danh sách tài liệu có tìm theo tên và sắp xếp.

## File cần tạo hoặc sửa

- `backend/app/api/documents.py`
- `backend/tests/integration/test_list_documents.py`

## Các bước

1. `GET /api/v1/documents?search=&sort=` trả `{docId, name, pageCount, uploadedBy, uploadedAt, sizeBytes, status, failureReason}`.
2. Sắp xếp theo `name` hoặc `uploadedAt` (tăng/giảm).
3. Không trả tài liệu đã xóa.

## Tiêu chí hoàn thành

- [ ] Kho có 3 tài liệu trả đủ 3 dòng đủ trường (AC-006).
- [ ] Tìm theo tên lọc đúng.
- [ ] Người chưa được cấp quyền nhận lỗi, không thấy tên tài liệu.

## Kiểm thử cần viết

- `test_list_three_documents`
- `test_search_filters`
- `test_list_requires_auth`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
