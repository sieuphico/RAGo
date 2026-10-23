# T-603 · Sao lưu, khôi phục và buổi thử khôi phục

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | US-064 |
| BR | BR-032, BR-029 |
| NFR, EC, cổng | NFR-006 |
| Quyết định kiến trúc | AD-08 |
| Phụ thuộc | [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) |
| Mở khóa | [T-611](T-611-so-tay-van-hanh-va-ghi-chu-phat-hanh.md) |

## Mục tiêu

Sao lưu hằng ngày cho CSDL và kho tệp; thử khôi phục thành công để đạt G10.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- SAD mục 4.2 dòng "Sao lưu": RPO ≤ 24 giờ, RTO ≤ 1 ngày làm việc
- AD-08, Q-A3 (bản sao lưu là ngoại lệ của xóa 24 giờ)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) Đóng gói và cấu hình triển khai tại chỗ: `deploy/Dockerfile.backend`, `deploy/compose.prod.yml`, `deploy/web/`

## File cần tạo hoặc sửa

- `deploy/backup/backup.sh`
- `deploy/backup/restore.sh`
- `docs/05-planning/evidence/restore-drill.md`

## Các bước

1. `backup.sh`: `pg_dump -Fc` CSDL và `tar` (hoặc ảnh chụp ổ) kho tệp vào thư mục sao lưu có ngày giờ; chạy 01:00 hằng ngày (cron hoặc systemd timer); giữ 7 bản gần nhất `[Đề xuất]`; ghi nhật ký và mã thoát.
2. Sao lưu thất bại → mã thoát khác 0 và tệp `last_failure` để T-604 tạo cảnh báo.
3. `restore.sh <thư mục bản sao lưu>`: dừng `api`, `worker`; `pg_restore --clean`; giải nén kho tệp; khởi động lại; in thời gian từng bước.
4. Buổi thử trên staging: tạo dữ liệu, sao lưu, xóa CSDL và kho tệp, khôi phục, kiểm tra tài liệu và hỏi đáp; ghi tuổi dữ liệu và tổng thời gian vào `restore-drill.md`.
5. Ghi ngoại lệ BR-029 (bản sao lưu ≤ 7 ngày có thể còn tài liệu đã xóa) để Bảo mật thông tin duyệt (Q-A3).

## Tiêu chí hoàn thành

- [ ] Buổi thử khôi phục thành công và có biên bản (AC-032, G10).
- [ ] Kịch bản chạy tự động hằng ngày.
- [ ] Dữ liệu khôi phục cũ nhất không quá 24 giờ; tổng thời gian ≤ 1 ngày làm việc.
- [ ] Ngoại lệ sao lưu được ghi nhận bằng văn bản.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Buổi thử khôi phục | Staging có 20 tài liệu; chạy `backup.sh`; xóa volume; chạy `restore.sh` | 20 tài liệu `READY`; một câu hỏi trả lời có trích dẫn; biên bản có thời gian |
| Sao lưu lỗi | Đặt thư mục đích chỉ đọc; chạy `backup.sh` | Mã thoát khác 0; có tệp `last_failure` |
| Giữ 7 bản | Chạy 9 lần với ngày giả | Còn 7 thư mục |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Sao lưu ra ngoài máy chủ hay ra nơi khác (theo chính sách IT, chưa có).
- Xóa tài liệu đã xóa khỏi bản sao lưu (ngoại lệ Q-A3).

## Lưu ý

Cần Bảo mật thông tin duyệt ngoại lệ (Q-A3) trước khi dùng dữ liệu thật.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
