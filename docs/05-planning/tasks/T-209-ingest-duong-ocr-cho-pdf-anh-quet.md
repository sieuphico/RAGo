# T-209 · Ingest: đường OCR cho PDF ảnh quét

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-013 |
| BR | BR-027, BR-030 |
| NFR, EC, cổng | NFR-011, NFR-002, EC-20 |
| Quyết định kiến trúc | AD-05, AD-06 |
| Phụ thuộc | [T-010](T-010-khao-sat-ocr-2-2-dich-vu-dam-may-so-sanh-khuyen-nghi.md), [T-206](T-206-ingest-trich-van-ban-theo-trang.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) |
| Mở khóa | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-616](T-616-danh-gia-chat-luong-ocr-g3b.md) |

## Mục tiêu

Với trang không có lớp văn bản: OCR từng trang, so với ngưỡng chất lượng, từ chối khi không đạt.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`PageText`, `OcrResult`, `FailureReason`)
- CONTRACTS mục 7 (`ocr_engine`, `ocr_min_confidence`)
- docs/05-planning/spikes/OCR-spike.md (kết quả T-010)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-010](T-010-khao-sat-ocr-2-2-dich-vu-dam-may-so-sanh-khuyen-nghi.md) Khảo sát OCR (2/2): dịch vụ đám mây, so sánh, khuyến nghị: `docs/05-planning/spikes/OCR-spike.md`, `docs/05-planning/spikes/ocr-results.csv`, `backend/scripts/ocr_trial.py`
- [T-206](T-206-ingest-trich-van-ban-theo-trang.md) Ingest: trích văn bản theo trang: `ExtractError`, `extract_pages`
- [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) Cổng (ports) và bộ nối giả (fake adapters): `ProviderError`, `ProviderTimeout`, `AiPort`, `OcrPort`, `StoragePort`, `IdpPort`

## File cần tạo hoặc sửa

- `backend/app/worker/ocr_step.py`
- `backend/app/adapters/ocr_tesseract.py`
- `backend/tests/unit/test_ocr_step.py`
- `backend/tests/integration/test_ocr_tesseract.py`

## Chữ ký và giao diện

```python
async def ocr_pages(ocr: OcrPort, pdf: bytes, pages: list[PageText], threshold: float) -> tuple[list[PageText], float]: ...

class TesseractOcr:
    async def recognize(self, image_png: bytes, lang: str = "vie+eng") -> OcrResult: ...
```

## Các bước

1. `ocr_tesseract.py`: bộ nối `OcrPort` gọi Tesseract cục bộ (`vie+eng`), trả độ tin cậy trung bình các từ (0–1). Luôn làm bộ nối này vì chạy tại chỗ, không cần DEP-001.
2. Nếu T-010 khuyến nghị dịch vụ đám mây thì thêm bộ nối thứ hai **sau khi** có DEP-001; ghi vào `wiring.build_ocr`.
3. `ocr_pages(ocr, pdf, pages, threshold)`: chỉ xử lý `PageText` có `has_text_layer=False`; dựng trang thành PNG 300 dpi bằng thư viện của T-007; gọi `ocr.recognize`; thay văn bản trang bằng kết quả OCR.
4. Độ tin cậy trung bình các trang đã OCR < `threshold` → `ExtractError(OCR_UNREADABLE)`.
5. Trả `(pages_mới, mean_confidence)`; T-210 đặt `used_ocr=True` khi có ít nhất một trang được OCR.

## Tiêu chí hoàn thành

- [ ] Chỉ trang không có lớp văn bản được OCR.
- [ ] Bản quét rõ đạt ngưỡng cho văn bản OCR (AC-027 đo ở T-616).
- [ ] Độ tin cậy dưới ngưỡng ném `OCR_UNREADABLE`, không trả văn bản nào (AC-030).
- [ ] Bộ nối Tesseract chạy được trên `scan_1p.pdf`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_ocr_only_scanned_pages` | 3 trang, trang 2 `has_text_layer=False`; `OcrFake` đếm lần gọi | `recognize` được gọi 1 lần; trang 1 và 3 giữ nguyên văn bản |
| `test_below_threshold_failed` | `OcrFake(confidence=0.5)`, `threshold=0.8` | `ExtractError`, `reason == OCR_UNREADABLE` |
| `test_returns_mean_confidence` | 2 trang quét, độ tin cậy 0,9 và 0,8 | Trả `mean_confidence == 0.85` |
| `test_tesseract_adapter` | `scan_1p.pdf` qua `ocr_tesseract` (đánh dấu `@pytest.mark.ocr`, cần Tesseract trên máy) | Văn bản không rỗng, `0 <= confidence <= 1` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/unit/test_ocr_step.py -q
cd backend && pytest tests/integration/test_ocr_tesseract.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đổi trạng thái `OCR_PROCESSING`, `used_ocr` (T-210).
- Đo độ chính xác OCR trên bộ mẫu chính thức (T-616).

## Lưu ý

Ngưỡng `ocr_min_confidence` chốt từ T-010. Dịch vụ OCR đám mây chỉ dùng với dữ liệu thật sau DEP-001.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
