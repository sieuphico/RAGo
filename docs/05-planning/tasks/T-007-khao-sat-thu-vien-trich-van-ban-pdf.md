# T-007 · Khảo sát thư viện trích văn bản PDF

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | US-012, US-013 |
| BR | BR-005, BR-027 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-05 |
| Phụ thuộc | — |
| Mở khóa | [T-206](T-206-ingest-trich-van-ban-theo-trang.md) |

## Mục tiêu

Chọn thư viện trích văn bản theo trang, có phát hiện lớp văn bản, hỗ trợ tiếng Việt và giấy phép phù hợp.

## File cần tạo hoặc sửa

- `docs/05-planning/spikes/PDF-lib.md`

## Các bước

1. So sánh 2–3 thư viện Python: độ đúng chữ có dấu tiếng Việt, phát hiện trang không có lớp văn bản, tốc độ, xử lý PDF có mật khẩu và PDF hỏng.
2. Ghi giấy phép từng thư viện (lưu ý một số thư viện phổ biến dùng AGPL).
3. Đề xuất một thư viện và ghi lý do.

## Tiêu chí hoàn thành

- [ ] Báo cáo có bảng so sánh và đề xuất.
- [ ] Giấy phép đã được ghi và Trưởng đội kỹ thuật chấp nhận.

## Kiểm thử cần viết

- Không có test mã

## Lưu ý

Giải quyết câu hỏi mở Q-A9 của SAD.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
