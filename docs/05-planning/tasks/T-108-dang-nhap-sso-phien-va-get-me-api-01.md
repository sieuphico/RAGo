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
| Phụ thuộc | [T-002](T-002-nap-cau-hinh-va-bi-mat.md), [T-006](T-006-khao-sat-tich-hop-sso-pd-001.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md), [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md) |
| Mở khóa | [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md) |

## Mục tiêu

Luồng đăng nhập qua `IdpPort`, cookie phiên và API-01 trả người dùng, vai trò, trạng thái được cấp quyền.

## File cần tạo hoặc sửa

- `backend/app/modules/auth/service.py`
- `backend/app/api/auth.py`
- `backend/app/api/me.py`
- `backend/tests/integration/test_auth_flow.py`

## Chữ ký và giao diện

```python
def complete_login(session, idp: IdpPort, params: dict[str, str]) -> SessionCookie: ...
```

## Các bước

1. `GET /auth/login` chuyển hướng tới IdP; `GET /auth/callback` hoàn tất, ghi cookie phiên đã ký, `HttpOnly`, `Secure`, `SameSite=Lax` `[Đề xuất]` có hạn dùng.
2. `GET /api/v1/me` trả `{email, role, allowed}`: chưa đăng nhập thì 401 `AUTH_EXPIRED`; đã đăng nhập nhưng không có trong allow-list thì 200 với `allowed=false`, `role=null`.
3. Ghi `auth_login_succeeded` (`is_first_login`) và `auth_access_denied` qua telemetry (nối ở T-314).
4. Dùng `idp_fake` trong test.

## Tiêu chí hoàn thành

- [ ] Người dùng trong allow-list đăng nhập và nhận `allowed=true` (US-001).
- [ ] Người không trong danh sách nhận `allowed=false`, không có tên tài liệu hay dữ liệu nào (US-002).
- [ ] Cookie có đủ cờ bảo mật.

## Kiểm thử cần viết

- `test_login_allowed_user`
- `test_login_not_in_allowlist`
- `test_me_without_cookie_401`

## Lưu ý

Giao thức thật (OIDC hay SAML) và bộ nối `idp_*` phụ thuộc T-006; làm với bộ nối giả trước.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
