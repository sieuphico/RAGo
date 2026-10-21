# T-110 · API quản lý allow-list (API-14)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-061 |
| BR | BR-016 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) |
| Mở khóa | [T-519](T-519-trang-quan-tri-nguoi-dung-s-07-va-nhat-ky-s-08.md) |

## Mục tiêu

Thêm, liệt kê và gỡ người dùng được cấp quyền; chỉ Quản trị viên.

## File cần tạo hoặc sửa

- `backend/app/modules/users/service.py`
- `backend/app/api/admin_users.py`
- `backend/tests/integration/test_admin_users.py`

## Các bước

1. `GET /api/v1/admin/users`, `POST` (body `{email, role}`), `DELETE /api/v1/admin/users/{email}`.
2. Kiểm tra email hợp lệ; trùng email trả lỗi; tối đa 20 người dùng (ASM-002).
3. Không cho quản trị viên gỡ chính mình nếu là quản trị viên cuối cùng `[Đề xuất]`.

## Tiêu chí hoàn thành

- [ ] Chỉ vai trò ADMIN gọi được.
- [ ] Thêm email xong, người đó đăng nhập được trong ≤ 1 phút (thực tế ngay lập tức).
- [ ] Vượt 20 người dùng bị từ chối với thông báo rõ.

## Kiểm thử cần viết

- `test_admin_only`
- `test_add_duplicate_rejected`
- `test_limit_20`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
