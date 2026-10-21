# T-210 · Ingest: điều phối và chuyển trạng thái

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-012, US-013 |
| BR | BR-005, BR-027 |
| NFR, EC, cổng | NFR-002 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-206](T-206-ingest-trich-van-ban-theo-trang.md), [T-208](T-208-ingest-nhung-va-lap-chi-muc.md), [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md), [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md) |
| Mở khóa | [T-314](T-314-noi-telemetry-vao-cac-luong-chinh.md), [T-402](T-402-goi-y-cau-hoi-mau-api-17.md), [T-608](T-608-thu-tai-g4.md) |

## Mục tiêu

Handler tác vụ `ingest` ghép trích văn bản, OCR, chia chunk, nhúng; cập nhật trạng thái và phát sự kiện.

## File cần tạo hoặc sửa

- `backend/app/worker/ingest.py`
- `backend/tests/integration/test_ingest_flow.py`

## Các bước

1. `handle_ingest(job)` đọc tệp, gọi `extract_pages`, `ocr_pages` khi cần, `split`, `index_document`.
2. Đặt trạng thái: `PROCESSING` → `OCR_PROCESSING` (khi có trang quét) → `READY`; lỗi thì `FAILED` kèm `failure_reason` đúng (FILE_CORRUPTED, FILE_ENCRYPTED, OCR_UNREADABLE).
3. Mỗi lần đổi trạng thái gọi `publish_status(doc_id, status)` (T-211).
4. Khi `READY`, đưa tác vụ tạo gợi ý (T-402) nếu tính năng bật.

## Tiêu chí hoàn thành

- [ ] PDF có văn bản đi từ `PROCESSING` tới `READY` và có chunk.
- [ ] PDF hỏng và PDF có mật khẩu kết thúc `FAILED` với lý do cụ thể (AC-005).
- [ ] Mỗi chuyển trạng thái phát một sự kiện.

## Kiểm thử cần viết

- `test_text_pdf_reaches_ready`
- `test_corrupted_pdf_failed`
- `test_scanned_pdf_uses_ocr_state`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
