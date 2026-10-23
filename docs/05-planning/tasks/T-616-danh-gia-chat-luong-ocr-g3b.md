# T-616 · Đánh giá chất lượng OCR (G3b)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W8–W9 (xem PLAN mục 6) |
| Story | US-013 |
| BR | BR-027, BR-030 |
| NFR, EC, cổng | NFR-011, G3b |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md), [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-g3.md) |
| Mở khóa | — |

## Mục tiêu

Đo độ chính xác ký tự của OCR trên bộ bản quét chính thức, kiểm tra bản kém bị từ chối và tổng hợp kết quả câu hỏi về bản quét.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- `ocr_trial.py` và cách tính độ chính xác ký tự ở T-004
- Kết quả `eval-answers.csv` của T-607

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md) Ingest: đường OCR cho PDF ảnh quét: `ocr_pages`, `TesseractOcr`
- [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-g3.md) Bộ đánh giá chất lượng trả lời (G3): `backend/scripts/eval_answers.py`, `backend/eval/README.md`, `docs/05-planning/evidence/eval-method.md`

## File cần tạo hoặc sửa

- `backend/scripts/eval_ocr.py`
- `docs/05-planning/evidence/eval-ocr.md`

## Các bước

1. Đọc `eval/scans.jsonl`: mỗi dòng `{file, ground_truth_file, quality: "clear" | "poor"}` (DEP-003, ≥ 5 bản rõ, 3 bản kém).
2. Chạy đúng đường xử lý của worker (`extract_pages` → `ocr_pages`) với bộ nối OCR đã chọn; tính độ chính xác ký tự như T-004 cho mỗi bản rõ.
3. Bản kém: ghi có bị từ chối với `OCR_UNREADABLE` hay không.
4. Lấy từ kết quả T-607 các câu hỏi có `expected_doc` là bản quét; tính tỷ lệ trả lời đúng (chấm của 2 người, AC-027).
5. Viết `eval-ocr.md`: bảng từng tệp, trung bình, 3/3 bản kém, tỷ lệ câu hỏi đúng, ngưỡng `ocr_min_confidence` đã dùng.

## Tiêu chí hoàn thành

- [ ] Có độ chính xác ký tự cho ≥ 5 bản rõ; đối chiếu NFR-011 (≥ 95%).
- [ ] Ghi rõ 3/3 bản kém bị từ chối hay không (AC-030).
- [ ] Có tỷ lệ câu hỏi về bản quét được trả lời đúng (≥ 80%, AC-027).
- [ ] Chạy lại cho cùng số liệu.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Chạy bộ OCR | Bộ 8 bản quét (5 rõ, 3 kém) | `eval-ocr.md` có 8 dòng, trung bình độ chính xác bản rõ, kết quả 3 bản kém |
| Tái lập | Chạy hai lần | Cùng số liệu |

## Lệnh kiểm tra

```bash
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đổi công cụ OCR (quyết định của Trưởng đội kỹ thuật nếu không đạt NFR-011).

## Lưu ý

Bị chặn bởi DEP-003 (hạn 2026-11-27). Chấm cuối cùng do 2 người đội BD.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
