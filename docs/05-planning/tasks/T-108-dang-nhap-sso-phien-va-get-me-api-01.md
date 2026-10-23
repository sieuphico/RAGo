# T-108 · Đăng nhập SSO, phiên và `GET /me` (API-01)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-001, US-002 |
| BR | BR-016 |
| NFR, EC, cổng | NFR-008 |
| Quyết định kiến trúc | AD-09 |
| Phụ thuộc | [T-002](T-002-nap-cau-hinh-va-bi-mat.md), [T-006](T-006-khao-sat-tich-hop-sso-pd-001.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md), [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-314](T-314-noi-telemetry-vao-dang-nhap-tai-len-xu-ly-va-xoa.md), [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) |

## Mục tiêu

Luồng đăng nhập qua `IdpPort`, cookie phiên và API-01 trả người dùng, vai trò, trạng thái được cấp quyền.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.0 (đăng nhập), 4.1 API-01
- CONTRACTS mục 7 (`session_secret`, `session_ttl_s`, `idp`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-002](T-002-nap-cau-hinh-va-bi-mat.md) Nạp cấu hình và bí mật: `Settings`, `get_settings`
- [T-006](T-006-khao-sat-tich-hop-sso-pd-001.md) Khảo sát tích hợp SSO (PD-001): `IdpPort`
- [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) Cổng (ports) và bộ nối giả (fake adapters): `ProviderError`, `ProviderTimeout`, `AiPort`, `OcrPort`, `StoragePort`, `IdpPort`
- [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md) Repository quản trị, nhật ký, telemetry, chi phí AI: `get_by_email`, `list_all`, `add`, `remove`, `count`, `count_by_role` …
- [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md) Hợp đồng lỗi và bộ xử lý ngoại lệ: `ErrorCode`, `AppError`, `install_error_handlers`, `ERROR_DEFAULTS`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/modules/auth/service.py`
- `app/modules/auth/cookies.py`
- `app/api/auth.py`
- `app/api/me.py`
- `tests/integration/test_auth_flow.py`

## Chữ ký và giao diện

```python
@dataclass(frozen=True)
class SessionData:
    email: str
    sid: str
    issued_at: datetime

def issue_cookie(email: str, settings: Settings) -> str: ...
def read_cookie(value: str, settings: Settings) -> SessionData | None: ...
async def complete_login(session: AsyncSession, idp: IdpPort, params: dict[str, str]) -> tuple[str, bool]: ...  # (giá trị cookie, is_first_login)
```

## Các bước

1. `cookies.py`: ký cookie bằng `itsdangerous.URLSafeTimedSerializer(session_secret, salt="cwd-session")` `[Đề xuất]`; nội dung `{"email", "sid", "iat"}` với `sid` là chuỗi ngẫu nhiên 16 byte; `read_cookie` trả `None` khi sai chữ ký hoặc quá `session_ttl_s`.
2. `GET /auth/login?next=&login_hint=`: tạo `state` ngẫu nhiên, lưu trong cookie tạm `cwd_state` (10 phút), 302 tới `idp.login_url(redirect_uri, state, login_hint)`. `next` phải bắt đầu bằng `/` và không bắt đầu bằng `//`; sai thì dùng `/`.
3. `GET /auth/callback`: kiểm tra `state` khớp `cwd_state` (sai → 400 `VALIDATION_ERROR`); gọi `idp.complete(params)`; email chuyển chữ thường; đặt cookie `cwd_session` với cờ ở CONTRACTS mục 4.0; nếu email có trong allow-list thì gọi `users.mark_login` để biết lần đầu; 302 tới `next`.
4. `POST /auth/logout`: xóa cookie, 204.
5. `GET /api/v1/me`: không có cookie hợp lệ → 401 `AUTH_EXPIRED`; có cookie nhưng không trong allow-list → 200 `{email, role: null, allowed: false}`; có → 200 `{email, role, allowed: true}`.
6. Dùng `IdpFake` qua `wiring.build_idp` trong test; bộ nối thật (`idp_oidc.py` hoặc `idp_saml.py`) làm sau khi T-006 có kết quả, cùng task này hoặc task bổ sung.

## Tiêu chí hoàn thành

- [ ] Người trong allow-list đăng nhập xong gọi `/me` nhận `allowed=true` và đúng vai trò (US-001).
- [ ] Người ngoài allow-list nhận `allowed=false`, `role=null`, không có dữ liệu nào khác (US-002).
- [ ] Cookie có `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`.
- [ ] `next=//evil.com` bị thay bằng `/`.
- [ ] Cookie sửa một ký tự bị coi là không hợp lệ (401).

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_login_allowed_user` | allow-list có lan@ (BD_USER); đi `/auth/login` → `/auth/callback?email=lan@...&state=<đúng>`; gọi `/api/v1/me` | 200 `{"email":"lan@congty.vn","role":"BD_USER","allowed":true}` |
| `test_login_not_in_allowlist` | Như trên với x@congty.vn không có trong allow-list | 200 `{"email":"x@congty.vn","role":null,"allowed":false}` |
| `test_me_without_cookie_401` | Gọi `/api/v1/me` không cookie | 401 `AUTH_EXPIRED` |
| `test_cookie_flags` | Đọc tiêu đề `Set-Cookie` sau callback | Có `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`, `Max-Age=28800` |
| `test_state_mismatch` | Callback với `state` khác cookie `cwd_state` | 400 `VALIDATION_ERROR`, không đặt cookie phiên |
| `test_open_redirect_blocked` | `/auth/login?next=//evil.com` rồi callback | 302 tới `/` |
| `test_tampered_cookie` | Sửa một ký tự của `cwd_session`; gọi `/me` | 401 `AUTH_EXPIRED` |
| `test_first_login_flag` | Đăng nhập lan@ hai lần | Lần 1 `mark_login` trả `True`, lần 2 `False` |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_auth_flow.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Kiểm tra allow-list và vai trò cho các API khác (T-109).
- Phát sự kiện `auth_login_succeeded` (T-314).
- Màn hình đăng nhập (T-505).

## Lưu ý

Giao thức thật (OIDC hay SAML) phụ thuộc T-006. Làm toàn bộ với `IdpFake` trước; khi có kết quả T-006, thêm bộ nối thật và một test tích hợp đánh dấu `@pytest.mark.idp` chạy trên môi trường thử.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
