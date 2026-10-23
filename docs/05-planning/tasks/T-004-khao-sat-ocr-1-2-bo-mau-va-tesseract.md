# T-004 · Khảo sát OCR (1/2): bộ mẫu và Tesseract

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | US-013 |
| BR | BR-027, BR-030 |
| NFR, EC, cổng | NFR-002, NFR-011 |
| Quyết định kiến trúc | AD-05, AD-06 |
| Phụ thuộc | — |
| Mở khóa | [T-010](T-010-khao-sat-ocr-2-2-dich-vu-dam-may-so-sanh-khuyen-nghi.md) |

## Mục tiêu

Chuẩn bị bộ bản quét có văn bản chuẩn, viết script đo và đo Tesseract (chạy tại chỗ, không gửi dữ liệu ra ngoài).

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- NFR-002, NFR-011 và DEP-005 trong BRD
- SAD mục 4.1 dòng "PDF là đầu vào không tin cậy"

## File cần tạo hoặc sửa

- `backend/scripts/ocr_trial.py`
- `docs/05-planning/spikes/ocr-samples/README.md`
- `docs/05-planning/spikes/ocr-results.csv`

## Các bước

1. Lấy ≥ 5 PDF ảnh quét rõ nét (tiếng Việt có dấu và tiếng Anh) và 3 bản kém (mờ, nghiêng 5–10°, 150 dpi). Nếu chưa có DEP-003, tự tạo bằng cách in rồi quét tài liệu công khai; ghi nguồn trong `README.md`.
2. Với mỗi bản quét, gõ văn bản chuẩn của 2 trang vào `ocr-samples/<tên>.txt`.
3. Viết `ocr_trial.py --engine tesseract --input <thư mục> --out <csv>`: chuyển trang thành ảnh 300 dpi, gọi Tesseract `vie+eng`, tính độ chính xác ký tự = `1 - levenshtein(ocr, chuẩn) / len(chuẩn)` sau khi chuẩn hóa khoảng trắng.
4. Ghi cột `file, engine, pages, char_accuracy, sec_per_page, mean_confidence, rejected` vào `ocr-results.csv`.
5. Đo thời gian cho một bản quét 100 trang (nhân bản trang nếu cần).

## Tiêu chí hoàn thành

- [ ] Có ≥ 8 bản quét (5 rõ, 3 kém) kèm văn bản chuẩn.
- [ ] `ocr_trial.py` chạy lại được bằng một lệnh và cho cùng kết quả.
- [ ] `ocr-results.csv` có số đo Tesseract cho mọi tệp và thời gian 100 trang.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Chạy lại script | Chạy `ocr_trial.py` hai lần trên cùng thư mục | Hai tệp CSV giống nhau trừ cột thời gian |
| Kiểm tra bộ mẫu | Mở `ocr-samples/` | 5 bản rõ và 3 bản kém, mỗi bản có tệp `.txt` chuẩn |

## Lệnh kiểm tra

```bash
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Dịch vụ OCR đám mây, so sánh và khuyến nghị (T-010).
- Bộ nối OCR trong ứng dụng (T-209).

## Lưu ý

Bị chặn một phần bởi DEP-003 (hạn 2026-11-27); đã có cách làm tạm ở bước 1.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
