# T-203 · Xóa tài liệu (API-05)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-016, US-062 |
| BR | BR-007, BR-018 |
| NFR, EC, cổng | EC-18 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md) |
| Mở khóa | [T-213](T-213-tac-vu-xoa-du-lieu-trong-24-gio.md), [T-510](T-510-hop-thoai-xoa-va-tep-trung-thao-tac-theo-vai-tro.md) |

## Mục tiêu

Xóa logic ngay, ghi nhật ký, chỉ người tải lên hoặc quản trị viên; xóa lặp không báo lỗi.

## File cần tạo hoặc sửa

- `backend/app/modules/documents/service.py`
- `backend/app/api/documents.py`
- `backend/tests/integration/test_delete_document.py`

## Các bước

1. `DELETE /api/v1/documents/{id}`: người tải lên hoặc ADMIN; người khác nhận 403.
2. Đặt `deleted_at`, ngừng truy xuất ngay (retrieval lọc `deleted_at is null`), ghi `audit` `delete`, enqueue tác vụ purge (T-213).
3. Xóa tài liệu đã xóa trả 200 với thông điệp đã xóa trước đó (EC-18).

## Tiêu chí hoàn thành

- [ ] Người tải lên xóa được X; người dùng khác không xóa được (AC-007).
- [ ] Sau khi xóa, câu hỏi chỉ X có đáp án nhận "không tìm thấy".
- [ ] Hai yêu cầu xóa liên tiếp: yêu cầu thứ hai không lỗi.

## Kiểm thử cần viết

- `test_owner_can_delete`
- `test_other_user_forbidden`
- `test_admin_can_delete_any`
- `test_double_delete_idempotent`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
