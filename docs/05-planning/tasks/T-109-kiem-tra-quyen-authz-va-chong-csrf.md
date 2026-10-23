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
| Phụ thuộc | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-110](T-110-api-quan-ly-allow-list-api-14.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-202](T-202-danh-sach-tai-lieu-api-03.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md), [T-212](T-212-tai-tep-pdf-cho-khung-xem-nguon-api-06.md), [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-312](T-312-so-lieu-hang-tuan-api-13.md), [T-313](T-313-danh-gia-api-11.md), [T-314](T-314-noi-telemetry-vao-dang-nhap-tai-len-xu-ly-va-xoa.md), [T-401](T-401-lich-su-hoi-thoai-api-10-va-het-han-90-ngay.md), [T-403](T-403-tom-tat-tai-lieu-api-12.md), [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) |

## Mục tiêu

Dependency FastAPI kiểm tra phiên, allow-list và vai trò ở mọi API; thu hồi quyền có hiệu lực ở yêu cầu kế tiếp.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 3 (`AUTH_*`, `CSRF_REJECTED`)
- CONTRACTS mục 4 (quy tắc chung, cột Vai trò)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md) Đăng nhập SSO, phiên và `GET /me` (API-01): `SessionData`, `issue_cookie`, `read_cookie`, `complete_login`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `CurrentUser`, `Role`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/api/deps.py`
- `tests/integration/test_authz.py`

## Chữ ký và giao diện

```python
async def current_user(request: Request, session: AsyncSession = Depends(get_session)) -> CurrentUser: ...
def require_roles(*roles: Role) -> Callable[..., Awaitable[CurrentUser]]: ...
class CsrfMiddleware(BaseHTTPMiddleware): ...
```

## Các bước

1. `current_user(request, session) -> CurrentUser`: đọc `cwd_session` bằng `read_cookie` (T-108); không có hoặc hết hạn → `AppError(AUTH_EXPIRED)`.
2. Tra allow-list **mỗi yêu cầu**, không bộ nhớ đệm; không có → `AppError(AUTH_FORBIDDEN)`.
3. `require_roles(*roles)` trả dependency; sai vai trò → `AUTH_FORBIDDEN`.
4. Middleware CSRF: với `POST`, `PUT`, `PATCH`, `DELETE` dưới `/api/v1`, thiếu tiêu đề `X-Requested-With: cwd` → 403 `CSRF_REJECTED`. `/auth/*` không áp dụng.
5. Viết test ma trận: liệt kê mọi route trong `app.routes` dưới `/api/v1` (trừ `/me`), gọi không cookie, phải nhận 401.

## Tiêu chí hoàn thành

- [ ] Người bị xóa khỏi allow-list bị chặn ở yêu cầu kế tiếp dù cookie còn hạn (US-061, EC-17).
- [ ] Mọi route dưới `/api/v1` trừ `/me` trả 401 khi không có cookie (AC-016).
- [ ] Phương thức ghi thiếu tiêu đề CSRF bị từ chối với `CSRF_REJECTED`; `GET` không cần tiêu đề.
- [ ] Sai vai trò trả 403 `AUTH_FORBIDDEN`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_revoked_user_blocked_next_request` | lan@ đăng nhập; gỡ lan@ khỏi allow-list; gọi một route có `require_roles(BD_USER)` | 403 `AUTH_FORBIDDEN` |
| `test_unauthenticated_all_endpoints` | Lặp mọi route `/api/v1/*` trừ `/me`, không cookie | Tất cả trả 401 `AUTH_EXPIRED` |
| `test_csrf_header_required` | POST route thử có cookie hợp lệ, không tiêu đề `X-Requested-With` | 403 `CSRF_REJECTED`; thêm tiêu đề thì 200 |
| `test_wrong_role` | SPONSOR gọi route `require_roles(ADMIN)` | 403 `AUTH_FORBIDDEN` |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_authz.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Phát `auth_access_denied` (T-314).
- Kiểm thử phân quyền toàn hệ thống (T-609).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
