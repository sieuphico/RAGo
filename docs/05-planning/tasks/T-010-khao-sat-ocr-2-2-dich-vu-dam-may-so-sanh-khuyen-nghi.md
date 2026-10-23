# T-010 · Khảo sát OCR (2/2): dịch vụ đám mây, so sánh, khuyến nghị

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
| Phụ thuộc | [T-004](T-004-khao-sat-ocr-1-2-bo-mau-va-tesseract.md) |
| Mở khóa | [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md) |

## Mục tiêu

Đo một dịch vụ OCR đám mây trên cùng bộ mẫu của T-004, so với Tesseract và đưa khuyến nghị công cụ cùng ngưỡng `ocr_min_confidence`.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- docs/05-planning/spikes/ocr-results.csv và ocr-samples/ (kết quả T-004)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-004](T-004-khao-sat-ocr-1-2-bo-mau-va-tesseract.md) Khảo sát OCR (1/2): bộ mẫu và Tesseract: `scripts/ocr_trial.py`, `docs/05-planning/spikes/ocr-samples/README.md`, `docs/05-planning/spikes/ocr-results.csv`

## File cần tạo hoặc sửa

- `docs/05-planning/spikes/OCR-spike.md`
- `docs/05-planning/spikes/ocr-results.csv`
- `scripts/ocr_trial.py`

## Các bước

1. Chọn 1 dịch vụ OCR đám mây có hỗ trợ tiếng Việt; thêm bộ chạy vào `ocr_trial.py` (cùng giao diện dòng lệnh với Tesseract).
2. Chỉ dùng bản quét tự tạo hoặc tài liệu đã được phép dùng ngoài công ty; **không** gửi tài liệu nội bộ khi chưa có DEP-001.
3. Ghi vào `ocr-results.csv` các cột: `file, engine, pages, char_accuracy, sec_per_page, mean_confidence, rejected`.
4. Đo thời gian 100 trang cho mỗi công cụ; đối chiếu NFR-002 (≤ 15 phút, p90).
5. Ghi chi phí ước tính cho 1.000 trang và điều khoản lưu giữ, huấn luyện, vị trí xử lý dữ liệu; đối chiếu CON-005.
6. Viết `OCR-spike.md`: bảng so sánh, khuyến nghị, giá trị `ocr_min_confidence` đề xuất (độ tin cậy trung bình thấp nhất trong các bản rõ nét trừ 0,05), rủi ro.

## Tiêu chí hoàn thành

- [ ] `ocr-results.csv` có dòng cho mọi tệp mẫu với cả hai công cụ.
- [ ] `OCR-spike.md` nêu công cụ khuyến nghị, ngưỡng `ocr_min_confidence` và lý do bằng số đo.
- [ ] Nêu rõ công cụ nào đạt độ chính xác ký tự ≥ 95% (NFR-011); nếu không công cụ nào đạt thì ghi "báo nhà tài trợ" (PR-003).
- [ ] Trưởng đội kỹ thuật ký duyệt khuyến nghị trong file.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Kiểm tra CSV | Mở `ocr-results.csv` | Mỗi tệp mẫu có 2 dòng (Tesseract, dịch vụ đám mây) hoặc ghi rõ lý do thiếu |
| Kiểm tra báo cáo | Mở `OCR-spike.md` | Có bảng so sánh, công cụ khuyến nghị, `ocr_min_confidence` và chữ ký duyệt |

## Lệnh kiểm tra

```bash
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Bộ nối OCR trong ứng dụng (T-209).
- Đánh giá OCR trên bộ mẫu chính thức (T-616).

## Lưu ý

Nếu chưa được dùng dịch vụ đám mây (DEP-001), báo cáo chỉ khuyến nghị Tesseract và ghi rõ phương án đám mây chưa đo.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
