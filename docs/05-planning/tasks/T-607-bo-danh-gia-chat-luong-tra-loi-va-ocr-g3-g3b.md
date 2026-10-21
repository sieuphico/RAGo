# T-607 · Bộ đánh giá chất lượng trả lời và OCR (G3, G3b)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 10 giờ `[Đề xuất]` |
| Tuần dự kiến | W7–W8 (xem PLAN mục 6) |
| Story | — |
| BR | BR-009, BR-010, BR-011, BR-012, BR-027, BR-030 |
| NFR, EC, cổng | G3, G3b |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md), [T-302](T-302-bo-noi-ai-that-ad-06.md), [T-307](T-307-dich-vu-tra-loi-answerservice.md), [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) |
| Mở khóa | — |

## Mục tiêu

Tập lệnh chạy bộ câu hỏi chuẩn và tính các chỉ số để người chấm đội BD đối chiếu.

## File cần tạo hoặc sửa

- `backend/scripts/eval_answers.py`
- `backend/scripts/eval_ocr.py`
- `docs/05-planning/evidence/eval-method.md`

## Các bước

1. Đọc bộ câu hỏi chuẩn (≥ 50 câu, DEP-003) gồm đáp án, tài liệu và trang kỳ vọng.
2. Chạy từng câu qua `AnswerService`; ghi câu trả lời, trích dẫn, thời gian phản hồi và cờ `isNotFound`.
3. Tính: tỷ lệ "đúng và trích dẫn đúng" (AC-012), tỷ lệ trích dẫn trỏ đúng trang (AC-010), từ chối đúng câu ngoài phạm vi (AC-011), đúng đa tài liệu (AC-009), đúng ngôn ngữ (AC-026), nối tiếp (AC-014).
4. OCR: so văn bản OCR với văn bản chuẩn để tính độ chính xác ký tự (AC-027) và kiểm tra 3 bản kém bị từ chối (AC-030).
5. Xuất tệp CSV cho 2 người chấm độc lập.

## Tiêu chí hoàn thành

- [ ] Có số liệu cho mọi chỉ số G3 và G3b.
- [ ] Kết quả có thể tái lập (cùng dữ liệu cho cùng kết quả).
- [ ] Ghi rõ ngưỡng liên quan đã dùng để chỉnh T-304.

## Kiểm thử cần viết

- Chạy thử trên bộ mẫu nhỏ

## Lưu ý

Bị chặn bởi DEP-003 (hạn 2026-11-27). Chấm điểm cuối cùng do 2 người đội BD thực hiện, công cụ chỉ hỗ trợ.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
