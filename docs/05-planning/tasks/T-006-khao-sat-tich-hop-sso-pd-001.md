# T-006 · Khảo sát tích hợp SSO (PD-001)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | US-001 |
| BR | BR-016 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-09 |
| Phụ thuộc | — |
| Mở khóa | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md) |

## Mục tiêu

Xác nhận giao thức SSO (OIDC hay SAML), thông tin nhận được (email), thời hạn phiên và đăng xuất.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- Chữ ký `IdpPort` ở mục "Chữ ký và giao diện" của task này
- CONTRACTS mục 2 (`IdpIdentity`), 4.0 (luồng đăng nhập), 7 (`session_ttl_s`)
- DEC-011 trong BRD (SSO là cách đăng nhập duy nhất)

## File cần tạo hoặc sửa

- `docs/05-planning/spikes/SSO-spike.md`

## Chữ ký và giao diện

```python
class IdpPort(Protocol):
    def login_url(self, redirect_uri: str, state: str, login_hint: str | None = None) -> str: ...
    async def complete(self, params: dict[str, str]) -> IdpIdentity: ...
```

## Các bước

1. Lấy tài liệu và môi trường thử của dịch vụ xác thực công ty từ đội IT.
2. Xác nhận: giao thức (OIDC hay SAML), địa chỉ chuyển hướng cần đăng ký, claim chứa email, thời hạn phiên của IdP, có đăng xuất tập trung không.
3. Thử luồng đăng nhập và đăng xuất bằng một ứng dụng thử nhỏ; chụp lại các tham số nhận được (che giá trị bí mật).
4. Đề xuất giá trị `session_ttl_s` và ghi vào báo cáo.
5. Đối chiếu với `IdpPort` bên dưới; nếu cần thêm tham số thì ghi đề xuất sửa trong báo cáo (không tự sửa T-008).

## Tiêu chí hoàn thành

- [ ] `SSO-spike.md` nêu giao thức, claim email, địa chỉ chuyển hướng, thời hạn phiên, cách đăng xuất.
- [ ] Có giá trị đề xuất cho `session_ttl_s`.
- [ ] Có môi trường thử dùng được, hoặc ghi rõ chưa có và ngày đã báo nhà tài trợ (DEC-011).

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Kiểm tra báo cáo | Mở `SSO-spike.md` | Có đủ 5 mục ở bước 2 và giá trị `session_ttl_s` |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Bộ nối IdP thật trong ứng dụng (làm trong T-108 khi có kết quả).
- Phân quyền theo vai trò (T-109).

## Lưu ý

Không có phương án dự phòng được duyệt (DEC-011). Nếu SSO trễ, báo nhà tài trợ ngay.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
