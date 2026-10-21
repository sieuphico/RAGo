# T-212 · Tải tệp PDF cho khung xem nguồn (API-06)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-022 |
| BR | BR-010 |
| NFR, EC, cổng | EC-14 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-112](T-112-bo-noi-kho-tep-storageport.md) |
| Mở khóa | [T-513](T-513-khung-xem-nguon-s-05.md) |

## Mục tiêu

Trả PDF (hỗ trợ khoảng byte) sau khi kiểm tra quyền.

## File cần tạo hoặc sửa

- `backend/app/api/document_file.py`
- `backend/tests/integration/test_document_file.py`

## Các bước

1. `GET /api/v1/documents/{id}/file` hỗ trợ tiêu đề `Range`, trả 206 khi có.
2. Kiểm tra phiên và allow-list như mọi API; tài liệu đã xóa trả `DOC_NOT_FOUND`.
3. Đặt `Content-Type: application/pdf`, `Content-Disposition: inline`, `Cache-Control: private`.

## Tiêu chí hoàn thành

- [ ] Người không có quyền không tải được tệp (AC-016).
- [ ] Yêu cầu `Range` trả đúng khoảng byte.
- [ ] Tài liệu đã xóa trả `DOC_NOT_FOUND` (EC-14).

## Kiểm thử cần viết

- `test_file_requires_auth`
- `test_range_request_206`
- `test_deleted_file_404`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
