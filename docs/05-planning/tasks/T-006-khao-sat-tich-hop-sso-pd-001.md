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

## File cần tạo hoặc sửa

- `docs/05-planning/spikes/SSO-spike.md`

## Các bước

1. Lấy tài liệu và môi trường thử của dịch vụ xác thực công ty từ đội IT.
2. Xác nhận giao thức, địa chỉ chuyển hướng, trường chứa email, thời hạn phiên.
3. Thử luồng đăng nhập và đăng xuất bằng một ứng dụng thử.
4. Ghi kết quả và định nghĩa giao diện `IdpPort` cần có.

## Tiêu chí hoàn thành

- [ ] Có báo cáo nêu giao thức, claim email và vòng đời phiên.
- [ ] Có môi trường thử hoặc ghi rõ chưa có để báo nhà tài trợ (DEC-011).

## Kiểm thử cần viết

- Không có test mã

## Lưu ý

Không có phương án dự phòng được duyệt (DEC-011). Nếu SSO trễ, báo nhà tài trợ ngay.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
