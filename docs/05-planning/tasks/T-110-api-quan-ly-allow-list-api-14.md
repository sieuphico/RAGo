# T-110 · API quản lý allow-list (API-14)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-061 |
| BR | BR-016 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | — |

## Mục tiêu

Thêm, liệt kê và gỡ người dùng được cấp quyền; chỉ Quản trị viên.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-14a/b/c, 4.2 `UserOut`
- CONTRACTS mục 3 (`EMAIL_INVALID`, `USER_EXISTS`, `USER_LIMIT_REACHED`, `LAST_ADMIN`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md) Repository quản trị, nhật ký, telemetry, chi phí AI: `get_by_email`, `list_all`, `add`, `remove`, `count`, `count_by_role` …
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `Role`, `CurrentUser`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/modules/users/service.py`
- `app/api/admin_users.py`
- `app/cli.py`
- `tests/integration/test_admin_users.py`
- `Makefile`

## Chữ ký và giao diện

```python
async def add_user(session: AsyncSession, email: str, role: Role, actor: CurrentUser) -> AllowListEntry: ...
async def remove_user(session: AsyncSession, email: str, actor: CurrentUser) -> None: ...
def main(argv: list[str] | None = None) -> int: ...  # app/cli.py
```

## Các bước

1. Ba route API-14a/b/c, `require_roles(ADMIN)`; mô hình vào/ra theo CONTRACTS mục 4.2 (`alias_generator=to_camel`).
2. Kiểm tra email bằng biểu thức `^[^@\s]+@[^@\s]+\.[^@\s]+$`, chuyển chữ thường.
3. Đã có 20 người → `USER_LIMIT_REACHED`; trùng → `USER_EXISTS`; gỡ ADMIN cuối cùng (kể cả tự gỡ) → `LAST_ADMIN`.
4. Lệnh tạo quản trị viên đầu tiên: `python -m app.cli add-admin <email>` và đích `make add-admin EMAIL=...`; chạy lại với email đã có thì không lỗi.
5. Mỗi lần thêm hoặc gỡ ghi nhật ký ứng dụng dạng `user_added`/`user_removed` (không ghi vào `audit_log`, vì BR-018 chỉ yêu cầu tải lên và xóa tài liệu).

## Tiêu chí hoàn thành

- [ ] Chỉ ADMIN gọi được ba route; vai trò khác nhận 403.
- [ ] Thêm email xong, người đó gọi `/me` ngay được `allowed=true` (US-061).
- [ ] Người thứ 21 bị từ chối với 409 `USER_LIMIT_REACHED`.
- [ ] Không gỡ được ADMIN cuối cùng.
- [ ] `make add-admin` tạo được ADMIN đầu tiên trên CSDL trống.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_admin_only` | BD_USER gọi `GET /api/v1/admin/users` | 403 `AUTH_FORBIDDEN` |
| `test_add_user_201` | ADMIN POST `{"email":"Lan@CongTy.vn","role":"BD_USER"}` | 201, `email` = `lan@congty.vn`; `/me` của lan@ trả `allowed=true` |
| `test_add_duplicate_rejected` | Thêm lan@ lần hai | 409 `USER_EXISTS` |
| `test_email_invalid` | POST `{"email":"lan@","role":"BD_USER"}` | 400 `EMAIL_INVALID` |
| `test_limit_20` | Đã có 20 người; thêm người thứ 21 | 409 `USER_LIMIT_REACHED` |
| `test_last_admin` | Chỉ 1 ADMIN; DELETE chính email đó | 409 `LAST_ADMIN` |
| `test_cli_add_admin` | CSDL trống; chạy `add-admin quantri@congty.vn` hai lần | Có đúng 1 bản ghi ADMIN; lần hai mã thoát 0 |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_admin_users.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Trang S-07 (T-519).
- Đồng bộ người dùng từ danh bạ công ty (ngoài MVP).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
