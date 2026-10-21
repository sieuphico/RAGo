# T-603 · Sao lưu, khôi phục và buổi thử khôi phục

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-064 |
| BR | BR-032, BR-029 |
| NFR, EC, cổng | NFR-006 |
| Quyết định kiến trúc | AD-08 |
| Phụ thuộc | [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) |
| Mở khóa | [T-611](T-611-so-tay-van-hanh-va-ghi-chu-phat-hanh.md) |

## Mục tiêu

Sao lưu hằng ngày cho CSDL và kho tệp; thử khôi phục thành công để đạt G10.

## File cần tạo hoặc sửa

- `deploy/backup/backup.sh`
- `deploy/backup/restore.sh`
- `docs/05-planning/evidence/restore-drill.md`

## Các bước

1. Viết kịch bản sao lưu PostgreSQL và ảnh chụp kho tệp, chạy mỗi 24 giờ, giữ số bản theo chính sách.
2. Viết kịch bản khôi phục và ghi thời gian thực hiện.
3. Thực hiện một buổi thử: dữ liệu cũ nhất không quá 24 giờ, hoàn tất ≤ 1 ngày làm việc.
4. Ghi lại ngoại lệ sao lưu của BR-029 (bản sao lưu có thể chứa tài liệu đã xóa) để Bảo mật thông tin duyệt (Q-A3).

## Tiêu chí hoàn thành

- [ ] Buổi thử khôi phục thành công và có biên bản (AC-032, G10).
- [ ] Kịch bản chạy tự động hằng ngày.
- [ ] Ngoại lệ sao lưu được ghi nhận bằng văn bản.

## Kiểm thử cần viết

- Biên bản buổi thử khôi phục

## Lưu ý

Cần Bảo mật thông tin duyệt ngoại lệ (Q-A3) trước khi dùng dữ liệu thật.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
