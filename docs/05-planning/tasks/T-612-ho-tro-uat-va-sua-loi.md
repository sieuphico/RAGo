# T-612 · Hỗ trợ UAT và sửa lỗi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 16 giờ `[Đề xuất]` |
| Tuần dự kiến | W8–W9 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | G7, G9, UX-01, UX-02, UX-10 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-606](T-606-kiem-thu-dau-cuoi-e2e-luong-p0.md), [T-608](T-608-thu-tai-g4.md), [T-609](T-609-kiem-tra-bao-mat-g6.md), [T-610](T-610-kiem-tra-telemetry-tren-staging-g8.md) |
| Mở khóa | — |

## Mục tiêu

Hỗ trợ UAT với ≥ 5 thành viên BD và sửa lỗi trước ngày thí điểm.

## File cần tạo hoặc sửa

- `docs/05-planning/evidence/uat-log.md`

## Các bước

1. Chuẩn bị môi trường và tài khoản cho buổi UAT; ghi lỗi và mức độ.
2. Sửa mọi lỗi Sev-1 và Sev-2; ghi các lỗi hoãn kèm chủ sở hữu.
3. Chạy lại các kiểm tra bị ảnh hưởng và cập nhật báo cáo.

## Tiêu chí hoàn thành

- [ ] Không còn lỗi Sev-1 hoặc Sev-2 đang mở (G7).
- [ ] Biên bản UAT không có vấn đề chặn luồng chính (G9).
- [ ] Mọi kiểm tra bị ảnh hưởng đã chạy lại.

## Kiểm thử cần viết

- Chạy lại bộ kiểm tra liên quan

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
