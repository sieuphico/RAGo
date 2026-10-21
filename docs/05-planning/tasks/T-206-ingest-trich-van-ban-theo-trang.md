# T-206 · Ingest: trích văn bản theo trang

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-012, US-013 |
| BR | BR-005, BR-027 |
| NFR, EC, cổng | NFR-002, EC-09 |
| Quyết định kiến trúc | AD-05 |
| Phụ thuộc | [T-007](T-007-khao-sat-thu-vien-trich-van-ban-pdf.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md), [T-112](T-112-bo-noi-kho-tep-storageport.md) |
| Mở khóa | [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md), [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) |

## Mục tiêu

Đọc PDF từ kho tệp, trích văn bản từng trang, phát hiện trang không có lớp văn bản và PDF hỏng hay có mật khẩu.

## File cần tạo hoặc sửa

- `backend/app/worker/extract.py`
- `backend/tests/unit/test_extract.py`

## Các bước

1. Dùng thư viện đã chọn ở T-007.
2. `extract_pages(data: bytes) -> list[PageText]` với `PageText(page: int, text: str, has_text_layer: bool)`.
3. PDF có mật khẩu ném `AppError(FILE_ENCRYPTED)`; PDF hỏng ném `AppError(FILE_CORRUPTED)`.
4. Đặt giới hạn bộ nhớ, thời gian và số trang (≤ 300 trang) cho mỗi tệp (PDF là đầu vào không tin cậy).

## Tiêu chí hoàn thành

- [ ] PDF có văn bản trả đúng văn bản theo trang, giữ dấu tiếng Việt.
- [ ] Bản quét trả `has_text_layer=false`.
- [ ] Tệp hỏng và tệp có mật khẩu cho đúng mã lỗi.

## Kiểm thử cần viết

- `test_extract_vietnamese_text`
- `test_detect_scanned_page`
- `test_encrypted_pdf`
- `test_corrupted_pdf`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
