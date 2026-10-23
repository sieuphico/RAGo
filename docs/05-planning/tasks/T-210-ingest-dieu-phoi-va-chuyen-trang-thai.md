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
| Phụ thuộc | [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-206](T-206-ingest-trich-van-ban-theo-trang.md), [T-207](T-207-ingest-chia-chunk-theo-trang.md), [T-208](T-208-ingest-nhung-va-lap-chi-muc.md), [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md), [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md), [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-204](T-204-hang-doi-tac-vu-jobs.md) |
| Mở khóa | [T-314](T-314-noi-telemetry-vao-dang-nhap-tai-len-xu-ly-va-xoa.md), [T-402](T-402-goi-y-cau-hoi-mau-api-17.md), [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md), [T-608](T-608-thu-tai-g4.md) |

## Mục tiêu

Handler tác vụ `ingest` ghép trích văn bản, OCR, chia chunk, nhúng; cập nhật trạng thái và phát sự kiện.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2.1 (chuyển trạng thái)
- CONTRACTS mục 8 (`ingest`, `suggest`)
- Sơ đồ hoạt động: SAD mục 5.2 (chép ở bước 2 dưới đây)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md) Worker: vòng lặp xử lý và scheduler: `run_worker`, `run_scheduler`
- [T-206](T-206-ingest-trich-van-ban-theo-trang.md) Ingest: trích văn bản theo trang: `ExtractError`, `extract_pages`
- [T-207](T-207-ingest-chia-chunk-theo-trang.md) Ingest: chia chunk theo trang: `split`
- [T-208](T-208-ingest-nhung-va-lap-chi-muc.md) Ingest: nhúng và lập chỉ mục: `index_document`, `EmbedFn`
- [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md) Ingest: đường OCR cho PDF ảnh quét: `ocr_pages`, `TesseractOcr`
- [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md) Sự kiện trạng thái tài liệu (API-04, SSE): `publish_status`, `StatusHub`
- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-204](T-204-hang-doi-tac-vu-jobs.md) Hàng đợi tác vụ (jobs): `enqueue`, `claim`, `complete`, `fail`, `release_stale`

## File cần tạo hoặc sửa

- `app/worker/ingest.py`
- `tests/integration/test_ingest_flow.py`

## Chữ ký và giao diện

```python
async def handle_ingest(job: Job) -> None: ...
```

## Các bước

1. `handle_ingest(job)` đăng ký với `register("ingest", handle_ingest)`.
2. Trình tự: đọc `Document`; nếu đã có `deleted_at` thì kết thúc ngay. Đọc tệp qua `StoragePort`; `extract_pages`; nếu có trang `has_text_layer=False` thì `set_status(OCR_PROCESSING)` + `publish_status`, gọi `ocr_pages`; `split`; kiểm tra lại `deleted_at` (Q-C5); `index_document`; `set_status(READY, page_count=len(pages), used_ocr=...)` + `publish_status`.
3. `ExtractError` → `set_status(FAILED, reason=e.reason)` + `publish_status`, **không** ném lại (lỗi do tệp, thử lại vô ích). Lỗi khác → ném lại để T-204 thử lại; lần cuối cùng (attempts = max) đặt `FAILED` với `PROCESSING_ERROR`.
4. Khi `READY` và `"suggestions" in settings.features`: `enqueue("suggest", {"docId"})`.
5. Mỗi lần đổi trạng thái gọi `publish_status(doc_id, status, reason, page_count)` (T-211).

## Tiêu chí hoàn thành

- [ ] `text_12p.pdf` đi `PROCESSING → READY`, có chunk, `page_count = 12`.
- [ ] `corrupted.pdf` và `encrypted.pdf` kết thúc `FAILED` với lý do đúng, tác vụ `DONE` (không thử lại) (AC-005).
- [ ] `scan_1p.pdf` qua `OCR_PROCESSING` rồi `READY` với `used_ocr=True` (dùng `OcrFake`).
- [ ] Mỗi chuyển trạng thái phát đúng một `publish_status`.
- [ ] Tài liệu bị xóa giữa chừng không có chunk nào được ghi.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_text_pdf_reaches_ready` | Tải `text_12p.pdf`, chạy `handle_ingest` với `AiFake` | `status=READY`, `page_count=12`, số chunk > 0; `publish_status` gọi 1 lần với `READY` |
| `test_corrupted_pdf_failed` | `corrupted.pdf` | `FAILED`, `failure_reason=FILE_CORRUPTED`; tác vụ `DONE` |
| `test_encrypted_pdf_failed` | `encrypted.pdf` | `FAILED`, `FILE_ENCRYPTED` |
| `test_scanned_pdf_uses_ocr_state` | `scan_1p.pdf`, `OcrFake(0.95)` | `publish_status` lần lượt `OCR_PROCESSING`, `READY`; `used_ocr=True` |
| `test_deleted_midway_no_chunks` | Đặt `deleted_at` sau bước `split` (monkeypatch) | 0 chunk; trạng thái không đổi thành `READY` |
| `test_transient_error_retried` | `embed` ném `ProviderError` ở lần 1, thành công lần 2 | Lần 1 tác vụ về `QUEUED`; lần 2 `READY` |
| `test_suggest_enqueued` | `features` có `suggestions` | Có 1 tác vụ `suggest` sau `READY`; không có khi tắt |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_ingest_flow.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Sự kiện telemetry xử lý xong hay thất bại (T-314).
- Tạo gợi ý (T-402).
- Thông báo "Xử lý lâu bất thường" sau 15 phút (giao diện, T-509).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
