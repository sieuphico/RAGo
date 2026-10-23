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
| Phụ thuộc | [T-007](T-007-khao-sat-thu-vien-trich-van-ban-pdf.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md), [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) |
| Mở khóa | [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md), [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) |

## Mục tiêu

Đọc PDF từ kho tệp, trích văn bản từng trang, phát hiện trang không có lớp văn bản và PDF hỏng hay có mật khẩu.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`PageText`, `FailureReason`)
- docs/05-planning/spikes/PDF-lib.md (kết quả T-007)
- CONTRACTS mục 7 (`max_pages`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-007](T-007-khao-sat-thu-vien-trich-van-ban-pdf.md) Khảo sát thư viện trích văn bản PDF: `docs/05-planning/spikes/PDF-lib.md`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `FailureReason`, `PageText`, `assert_transition`, `InvalidTransition`
- [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) Dữ liệu mẫu và fixture kiểm thử: `backend/scripts/make_sample_data.py`, `backend/tests/fixtures/README.md`

## File cần tạo hoặc sửa

- `backend/app/worker/extract.py`
- `backend/tests/unit/test_extract.py`

## Chữ ký và giao diện

```python
class ExtractError(Exception):
    def __init__(self, reason: FailureReason) -> None: ...
    reason: FailureReason

def extract_pages(data: bytes, *, max_pages: int) -> list[PageText]: ...
```

## Các bước

1. Dùng thư viện đã chọn ở T-007.
2. `extract_pages(data, max_pages)`: mở PDF từ byte; có mật khẩu → `ExtractError(FILE_ENCRYPTED)`; không mở được hoặc lỗi khi đọc trang → `ExtractError(FILE_CORRUPTED)`; số trang > `max_pages` → `ExtractError(PROCESSING_ERROR)`.
3. Mỗi trang: chuẩn hóa Unicode NFC, gộp khoảng trắng liên tiếp; `has_text_layer = len(text.strip()) >= 20` `[Đề xuất]`.
4. Chạy trích văn bản trong tiến trình con (`concurrent.futures.ProcessPoolExecutor`, 1 worker) với thời hạn 120 giây; quá hạn → `ExtractError(PROCESSING_ERROR)` (PDF là đầu vào không tin cậy, SAD 4.1).
5. `ExtractError` đặt trong `worker/extract.py`, có thuộc tính `reason: FailureReason`.

## Tiêu chí hoàn thành

- [ ] `text_12p.pdf` cho 12 `PageText`, trang 12 chứa "HD-2026-012" và giữ đúng dấu tiếng Việt.
- [ ] `scan_1p.pdf` cho `has_text_layer=False`.
- [ ] `encrypted.pdf` → `FILE_ENCRYPTED`; `corrupted.pdf` → `FILE_CORRUPTED`.
- [ ] PDF 301 trang → `PROCESSING_ERROR`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_extract_vietnamese_text` | `text_12p.pdf` (T-605) | 12 phần tử; `pages[11].page == 12`; chứa "Hợp đồng số HD-2026-012" đúng dấu |
| `test_detect_scanned_page` | `scan_1p.pdf` | 1 phần tử, `has_text_layer is False` |
| `test_encrypted_pdf` | `encrypted.pdf` | `ExtractError`, `reason == FILE_ENCRYPTED` |
| `test_corrupted_pdf` | `corrupted.pdf` | `ExtractError`, `reason == FILE_CORRUPTED` |
| `test_too_many_pages` | PDF 301 trang trống, `max_pages=300` | `ExtractError`, `reason == PROCESSING_ERROR` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/unit/test_extract.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- OCR cho trang không có lớp văn bản (T-209).
- Chia chunk (T-207).
- Đọc tệp từ kho và đổi trạng thái tài liệu (T-210).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
