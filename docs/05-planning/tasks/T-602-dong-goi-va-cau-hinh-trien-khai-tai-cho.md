# T-602 · Đóng gói và cấu hình triển khai tại chỗ

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | NFR-008, NFR-005 |
| Quyết định kiến trúc | AD-11 |
| Phụ thuộc | [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md), [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md) |
| Mở khóa | [T-603](T-603-sao-luu-khoi-phuc-va-buoi-thu-khoi-phuc.md), [T-604](T-604-giam-sat-suc-khoe-chi-so-va-canh-bao.md), [T-613](T-613-dung-moi-truong-staging.md) |

## Mục tiêu

Ảnh container và cấu hình cho máy chủ web, ứng dụng, worker, CSDL theo physical view.

## File cần tạo hoặc sửa

- `deploy/Dockerfile.backend`
- `deploy/compose.prod.yml`
- `deploy/web/`
- `deploy/.env.template`
- `docs/05-planning/evidence/deploy-notes.md`

## Các bước

1. Dockerfile backend (một ảnh dùng cho API và worker, khác lệnh khởi động).
2. Cấu hình máy chủ web: TLS 1.2+, phục vụ tệp tĩnh frontend, chuyển tiếp API và SSE (tắt bộ đệm cho SSE).
3. Mẫu biến môi trường; bí mật nạp từ kho bí mật hoặc tệp quyền hạn chế, không đưa vào ảnh.
4. Quy tắc đầu ra chỉ tới SSO và dịch vụ AI/OCR đã duyệt (phối hợp đội mạng).

## Tiêu chí hoàn thành

- [ ] `compose.prod.yml` khởi động đủ các dịch vụ trên máy sạch.
- [ ] SSE không bị bộ đệm của máy chủ web chặn.
- [ ] Không có bí mật trong ảnh hay kho mã.

## Kiểm thử cần viết

- Kiểm bằng triển khai thử trên staging (T-613)

## Lưu ý

Cỡ máy, hệ điều hành, cổng nội bộ và kho tệp (Q-A8) còn `[TBD]`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
