# T-209 · Ingest: đường OCR cho PDF ảnh quét

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W4–W5 (xem PLAN mục 6) |
| Story | US-013 |
| BR | BR-027, BR-030 |
| NFR, EC, cổng | NFR-011, NFR-002, EC-20 |
| Quyết định kiến trúc | AD-05, AD-06 |
| Phụ thuộc | [T-004](T-004-khao-sat-ky-thuat-ocr-dep-005.md), [T-206](T-206-ingest-trich-van-ban-theo-trang.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) |
| Mở khóa | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-va-ocr-g3-g3b.md) |

## Mục tiêu

Với trang không có lớp văn bản: OCR từng trang, so với ngưỡng chất lượng, từ chối khi không đạt.

## File cần tạo hoặc sửa

- `backend/app/worker/ocr_step.py`
- `backend/app/adapters/ocr_<engine>.py`
- `backend/tests/unit/test_ocr_step.py`

## Các bước

1. Dựng bộ nối `OcrPort` thật theo kết luận của T-004; dùng `ocr_fake` trong test.
2. `ocr_pages(ocr: OcrPort, doc_pages, threshold: float) -> list[PageText]`: chỉ OCR các trang `has_text_layer=false`.
3. Nếu độ tin cậy trung bình dưới `threshold` thì ném `AppError(OCR_UNREADABLE)`.
4. Đặt cờ `used_ocr=true` cho tài liệu.

## Tiêu chí hoàn thành

- [ ] Bản quét rõ đạt ngưỡng chuyển `Ready` (AC-027).
- [ ] Bản quét kém (mờ, nghiêng) dẫn tới `Failed` kèm "Không đọc được nội dung" và không bao giờ vào chỉ mục (AC-030).
- [ ] Chỉ trang không có lớp văn bản được OCR.

## Kiểm thử cần viết

- `test_ocr_only_scanned_pages`
- `test_below_threshold_failed`
- `test_used_ocr_flag`

## Lưu ý

Tên bộ nối và ngưỡng chốt sau T-004 (DEP-005). Nếu OCR là dịch vụ đám mây thì cần phê duyệt DEP-001 trước khi dùng dữ liệu thật.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
