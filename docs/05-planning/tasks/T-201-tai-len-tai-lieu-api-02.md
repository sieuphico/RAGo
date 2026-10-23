# T-201 · Tải lên tài liệu (API-02)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-010, US-011, US-014 |
| BR | BR-001, BR-002, BR-003, BR-004 |
| NFR, EC, cổng | NFR-004, EC-08 |
| Quyết định kiến trúc | DD-05 |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-112](T-112-bo-noi-kho-tep-storageport.md), [T-204](T-204-hang-doi-tac-vu-jobs.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-314](T-314-noi-telemetry-vao-dang-nhap-tai-len-xu-ly-va-xoa.md), [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md), [T-609](T-609-kiem-tra-bao-mat-g6.md) |

## Mục tiêu

Nhận 1–10 tệp, kiểm tra lại ở máy chủ, lưu tệp, tạo bản ghi `Processing`, đưa tác vụ xử lý vào hàng đợi, trả 202.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-02, 4.2 `UploadResultOut`
- CONTRACTS mục 3 (`FILE_*`)
- CONTRACTS mục 8 (`ingest`)
- CONTRACTS mục 11 (file riêng `documents_upload.py`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md) Hợp đồng lỗi và bộ xử lý ngoại lệ: `ErrorCode`, `AppError`, `install_error_handlers`, `ERROR_DEFAULTS`
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md) Mô-đun nhật ký kiểm toán (API-15): `record`, `expire`
- [T-112](T-112-bo-noi-kho-tep-storageport.md) Bộ nối kho tệp (StoragePort): `FsStorage`, `new_file_key`
- [T-204](T-204-hang-doi-tac-vu-jobs.md) Hàng đợi tác vụ (jobs): `enqueue`, `claim`, `complete`, `fail`, `release_stale`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `CurrentUser`, `UploadResult`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/modules/documents/upload.py`
- `app/api/documents_upload.py`
- `tests/integration/test_upload_api.py`

## Chữ ký và giao diện

```python
async def upload_documents(session: AsyncSession, storage: StoragePort, files: list[UploadFile], actor: CurrentUser, settings: Settings) -> list[UploadResult]: ...
```

## Các bước

1. `POST /api/v1/documents` (multipart, trường `files`), `require_roles(TEAM_LEAD)`.
2. 0 tệp hoặc > `max_files` tệp → 400 `FILE_TOO_MANY`, không lưu gì.
3. Với từng tệp, theo thứ tự: tên không kết thúc `.pdf` (không phân biệt hoa thường) → `FILE_NOT_PDF`; đọc theo khối 1 MB, vượt `max_upload_mb` MB → `FILE_TOO_LARGE`; 5 byte đầu khác `%PDF-` → `FILE_NOT_PDF`.
4. Tệp hợp lệ: `key = new_file_key()`, `storage.save`, `documents.add(...)` (trạng thái `PROCESSING`), `jobs.enqueue("ingest", {"docId": ...})`, `audit.record(actor, "UPLOAD", doc_id, name)`; cả bốn trong một giao dịch, lỗi thì xóa tệp đã lưu.
5. Trả 202 `{"results": [...]}` theo đúng thứ tự tệp gửi lên; tệp bị từ chối có `docId=null`, `status=null`, `error=<mã>`.
6. Tên tệp lưu nguyên văn để hiển thị, cắt còn 255 ký tự; không dùng tên tệp làm đường dẫn.

## Tiêu chí hoàn thành

- [ ] Tệp `.docx`, `.xlsx`, `.png` bị từ chối, kho không đổi (AC-003).
- [ ] PDF 51 MB bị từ chối `FILE_TOO_LARGE`, PDF 49 MB được nhận (AC-004).
- [ ] Tệp `.pdf` có nội dung PNG bị từ chối `FILE_NOT_PDF`.
- [ ] Lô 3 tệp gồm 2 hợp lệ và 1 sai: 202, 2 tài liệu mới, 1 lỗi.
- [ ] Người không phải TEAM_LEAD nhận 403.
- [ ] Mỗi tài liệu được nhận có đúng 1 tác vụ `ingest` và 1 bản ghi nhật ký `UPLOAD`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_upload_valid_pdf_202` | TEAM_LEAD gửi `text_1p.pdf` | 202; `results[0].status == "PROCESSING"`; bảng `job` có 1 `ingest` đúng `docId`; `audit_log` có 1 `UPLOAD` |
| `test_reject_non_pdf_extension` | Gửi `a.docx`, `b.png` | 202; cả hai `error == "FILE_NOT_PDF"`; bảng `document` không đổi |
| `test_reject_non_pdf_magic` | Gửi `not_pdf.pdf` (nội dung PNG) | `error == "FILE_NOT_PDF"` |
| `test_reject_oversize` | Gửi `big_51mb.pdf` và một PDF 49 MB | Tệp 51 MB `FILE_TOO_LARGE`; tệp 49 MB `PROCESSING` |
| `test_too_many_files` | Gửi 11 tệp PDF hợp lệ | 400 `FILE_TOO_MANY`; không tài liệu nào được tạo |
| `test_batch_partial_valid` | Gửi `[text_1p.pdf, a.png, text_12p.pdf]` | Thứ tự kết quả giữ nguyên; 2 `PROCESSING`, 1 lỗi |
| `test_non_team_lead_forbidden` | BD_USER và ADMIN gửi `text_1p.pdf` | Cả hai 403 `AUTH_FORBIDDEN` |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_upload_api.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Phát hiện tệp trùng (giao diện, T-510).
- Sự kiện `document_upload_rejected` phía máy chủ (T-314).
- Xử lý nội dung tệp (T-206 – T-210).
- Giới hạn kích thước thân yêu cầu ở máy chủ web (T-602).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
