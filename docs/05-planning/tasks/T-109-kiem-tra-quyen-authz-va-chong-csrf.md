# T-109 · Kiểm tra quyền (AuthZ) và chống CSRF

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-002, US-061 |
| BR | BR-016 |
| NFR, EC, cổng | NFR-008 |
| Quyết định kiến trúc | AD-09 |
| Phụ thuộc | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md) |
| Mở khóa | [T-110](T-110-api-quan-ly-allow-list-api-14.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-202](T-202-danh-sach-tai-lieu-api-03.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md), [T-212](T-212-tai-tep-pdf-cho-khung-xem-nguon-api-06.md), [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-312](T-312-so-lieu-hang-tuan-api-13.md), [T-313](T-313-danh-gia-api-11.md), [T-401](T-401-lich-su-hoi-thoai-api-10-va-het-han-90-ngay.md) |

## Mục tiêu

Dependency FastAPI kiểm tra phiên, allow-list và vai trò ở mọi API; thu hồi quyền có hiệu lực ở yêu cầu kế tiếp.

## File cần tạo hoặc sửa

- `backend/app/api/deps.py`
- `backend/tests/integration/test_authz.py`

## Chữ ký và giao diện

```python
def require_roles(*roles: Role) -> Callable: ...
```

## Các bước

1. `current_user()` đọc cookie phiên; hết hạn thì `AUTH_EXPIRED` (401).
2. `require_allowed()` kiểm tra allow-list **mỗi yêu cầu** (không dùng bộ nhớ đệm); không có thì `AUTH_FORBIDDEN` (403).
3. `require_roles(*roles)` cho các API theo vai trò.
4. Với phương thức ghi (POST, PUT, DELETE), yêu cầu tiêu đề tùy chỉnh `X-Requested-With` `[Đề xuất]`; thiếu thì từ chối.

## Tiêu chí hoàn thành

- [ ] Người bị xóa khỏi allow-list bị chặn ở yêu cầu kế tiếp dù cookie còn hạn (US-061).
- [ ] Gọi trực tiếp API khi chưa xác thực: 0/10 lần lấy được dữ liệu (AC-016).
- [ ] Phương thức ghi thiếu tiêu đề CSRF bị từ chối.

## Kiểm thử cần viết

- `test_revoked_user_blocked_next_request`
- `test_unauthenticated_all_endpoints`
- `test_csrf_header_required`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
