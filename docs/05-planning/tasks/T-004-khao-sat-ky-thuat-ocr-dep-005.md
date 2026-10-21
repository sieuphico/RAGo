# T-004 · Khảo sát kỹ thuật OCR (DEP-005)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 12 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | US-013 |
| BR | BR-027, BR-030 |
| NFR, EC, cổng | NFR-002, NFR-011 |
| Quyết định kiến trúc | AD-05, AD-06 |
| Phụ thuộc | — |
| Mở khóa | [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md) |

## Mục tiêu

Chọn công cụ OCR và ngưỡng chất lượng dựa trên số đo thật trên bộ mẫu; kết quả quyết định AD-05, AD-06 và OQ-018.

## File cần tạo hoặc sửa

- `docs/05-planning/spikes/OCR-spike.md`
- `backend/scripts/ocr_trial.py`

## Các bước

1. Lấy ≥ 5 PDF ảnh quét rõ nét (tiếng Việt có dấu và tiếng Anh) và 3 bản kém (mờ, nghiêng, sai độ phân giải) từ bộ mẫu DEP-003.
2. Chạy Tesseract (vi+en) và một dịch vụ OCR đám mây ứng viên; ghi độ chính xác ký tự so với văn bản chuẩn, thời gian mỗi trang, hành vi với bản kém.
3. Đo thời gian cho một bản quét 100 trang, đối chiếu NFR-002 (≤ 15 phút, p90).
4. Ghi chi phí và điều khoản lưu trữ dữ liệu của dịch vụ đám mây, đối chiếu CON-005.
5. Viết báo cáo: bảng số liệu, khuyến nghị công cụ, ngưỡng đề xuất cho NFR-011.

## Tiêu chí hoàn thành

- [ ] Có báo cáo với số đo thật cho cả hai phương án.
- [ ] Có khuyến nghị công cụ và ngưỡng chất lượng, kèm rủi ro.
- [ ] Báo cáo nêu rõ nếu OCR tiếng Việt không đạt 95% để báo nhà tài trợ (PR-003).

## Kiểm thử cần viết

- Không có test mã; kiểm tra bằng báo cáo được Trưởng đội kỹ thuật duyệt

## Lưu ý

Bị chặn bởi DEP-003 (bộ tài liệu mẫu, hạn 2026-11-27). Nếu chưa có bộ mẫu, dùng tạm 5–8 bản quét do đội BD cung cấp riêng và ghi rõ giới hạn.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
