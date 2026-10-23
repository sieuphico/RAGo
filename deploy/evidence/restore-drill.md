# Biên bản buổi thử khôi phục (T-603)

| Mục | Giá trị |
|---|---|
| Ngày | 2026-10-23 |
| Môi trường | Stack `compose.prod.yml` trên máy phát triển (Docker Desktop), **không phải staging** (T-613 chưa làm) |
| Dữ liệu | 3 tài liệu mẫu (1, 12, 100 trang), AI giả (`CWD_AI_PROVIDER=fake`); yêu cầu của task là 20 tài liệu trên staging |
| Bản sao lưu | `backup.sh`: `pg_dump -Fc` + `tar` kho tệp; 7 bản giữ lại |

## Các bước và kết quả
1. Trước: 3 tài liệu `READY`, tải về đúng kích thước (45.209 / 57.186 / 150.292 byte).
2. Sao lưu: thành công (`BACKUP OK`, `db.dump` + `storage.tar`).
3. Phá hủy: `TRUNCATE` bảng tài liệu/hội thoại/tác vụ và xóa toàn bộ `/srv/storage` → danh sách tài liệu rỗng.
4. `restore.sh`: dừng 3 s · `pg_restore --clean` 2 s · nạp kho tệp 2 s · khởi động lại 19 s · **tổng 26 s**.
5. Sau: 3 tài liệu `READY` (100/12/1 trang), tải về đúng kích thước từng tệp; hỏi đáp trả lời có trích dẫn.

Tuổi dữ liệu khôi phục: vừa tạo sao lưu (RPO của buổi thử ≈ 0; mục tiêu NFR-006: RPO ≤ 24 giờ, RTO ≤ 1 ngày làm việc — RTO đo được 26 giây với dữ liệu nhỏ).

## Lỗi tìm thấy khi thử
- Trên Windows (Git Bash), đường dẫn `/srv/storage` bị tự đổi sang đường dẫn Windows làm `tar` lỗi → đã thêm `export MSYS_NO_PATHCONV=1` ở cả hai script. Trên Linux không ảnh hưởng.

## Kiểm thử tự động liên quan
`tests/unit/test_backup_script.py`: sao lưu tạo đủ tệp; lỗi → mã thoát khác 0, tệp `last_failure` và chỉ số lỗi; giữ đúng 7 bản sau 9 lần chạy; thư mục đích chỉ-đọc (chỉ chạy trên POSIX).

## Ngoại lệ BR-029 — cần Bảo mật thông tin duyệt (Q-A3)
Bản sao lưu ≤ 7 ngày có thể còn dữ liệu đã xử lý của tài liệu đã xóa (xóa vật lý chỉ áp dụng cho CSDL đang chạy). **Chưa được duyệt**; không dùng dữ liệu thật trước khi có duyệt.

## Việc còn lại
Lặp lại trên staging với 20 tài liệu và AI thật (T-613); ghi tuổi dữ liệu thật và thời gian tổng.
