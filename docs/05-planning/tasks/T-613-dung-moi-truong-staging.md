# T-613 · Dựng môi trường staging

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | G4, G8 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) |
| Mở khóa | [T-608](T-608-thu-tai-g4.md), [T-609](T-609-kiem-tra-bao-mat-g6.md), [T-610](T-610-kiem-tra-telemetry-tren-staging-g8.md) |

## Mục tiêu

Môi trường staging tại chỗ cùng cấu trúc với production, dữ liệu mẫu.

## File cần tạo hoặc sửa

- `docs/05-planning/evidence/staging-setup.md`

## Các bước

1. Triển khai gói từ T-602 lên máy staging; nạp bộ tài liệu mẫu ≥ 200 tài liệu (DEP-003).
2. Kết nối SSO môi trường thử; dịch vụ AI thật chỉ khi đã có DEP-001, nếu chưa thì dùng bộ nối giả.
3. Ghi lại địa chỉ, tài khoản kiểm thử và cách đặt lại dữ liệu.

## Tiêu chí hoàn thành

- [ ] Có thể chạy toàn bộ luồng P0 trên staging.
- [ ] Có ≥ 200 tài liệu mẫu cho thử tải.
- [ ] Không dùng tài liệu thật của công ty.

## Kiểm thử cần viết

- Smoke test luồng tải lên → hỏi đáp

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
