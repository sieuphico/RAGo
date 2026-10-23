# T-104 · Mô hình ORM và repository tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-010, US-015 |
| BR | BR-005, BR-006 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-101](T-101-migration-001-tai-lieu-chunk-goi-y.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-105](T-105-repository-hoi-thoai.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-202](T-202-danh-sach-tai-lieu-api-03.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-208](T-208-ingest-nhung-va-lap-chi-muc.md), [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md), [T-212](T-212-tai-tep-pdf-cho-khung-xem-nguon-api-06.md), [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md), [T-311](T-311-pham-vi-tai-lieu-trong-api-08-va-ec-15.md), [T-402](T-402-goi-y-cau-hoi-mau-api-17.md), [T-403](T-403-tom-tat-tai-lieu-api-12.md) |

## Mục tiêu

Mô hình SQLAlchemy và các hàm truy cập dữ liệu cho `document` và `chunk`.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2, 2.1, 2.2
- CONTRACTS mục 4.1 API-03 (giá trị `sort`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-101](T-101-migration-001-tai-lieu-chunk-goi-y.md) Migration 001: tài liệu, chunk, gợi ý: `migrations/versions/001_documents.py`, `tests/integration/test_migration_001.py`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `DocumentStatus`, `FailureReason`, `ChunkDraft`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/models/document.py`
- `app/modules/documents/repository.py`
- `tests/integration/test_document_repository.py`

## Chữ ký và giao diện

```python
DocumentSort = Literal["uploadedAt_desc", "uploadedAt_asc", "name_asc", "name_desc"]

async def add(session: AsyncSession, *, name: str, uploaded_by: str, size_bytes: int, file_key: str) -> Document: ...  # status=PROCESSING
async def get(session: AsyncSession, doc_id: UUID, *, include_deleted: bool = False) -> Document | None: ...
async def list_documents(session: AsyncSession, search: str | None, sort: DocumentSort) -> list[Document]: ...
async def set_status(session: AsyncSession, doc_id: UUID, status: DocumentStatus, *, reason: FailureReason | None = None,
                     page_count: int | None = None, used_ocr: bool | None = None) -> Document: ...
async def soft_delete(session: AsyncSession, doc_id: UUID, at: datetime) -> bool: ...
async def add_chunks(session: AsyncSession, doc_id: UUID, chunks: list[ChunkDraft], embeddings: list[list[float]]) -> int: ...
async def delete_chunks(session: AsyncSession, doc_id: UUID) -> int: ...
async def ready_doc_ids(session: AsyncSession, scope: set[UUID] | None = None) -> set[UUID]: ...
```

## Các bước

1. Viết mô hình `Document`, `Chunk`, `Suggestion` (SQLAlchemy 2.0, `Mapped[...]`) khớp migration 001; cột `status` ánh xạ sang `DocumentStatus`.
2. Viết các hàm trong `repository.py` đúng chữ ký; mọi hàm đọc danh sách bỏ qua `deleted_at is not null`.
3. `list_documents`: `search` lọc `cwd_unaccent(lower(name)) LIKE cwd_unaccent(lower('%' || :q || '%'))`, thoát ký tự `%` và `_` trong `search`; `sort` theo bảng API-03.
4. `set_status` đọc trạng thái hiện tại, gọi `assert_transition` (T-009), ghi trạng thái mới; khi sang `READY` hoặc `FAILED` thì đặt `processed_at = now()`.
5. `soft_delete` trả `False` nếu đã có `deleted_at` (EC-18), ngược lại đặt `deleted_at` và trả `True`.
6. Fixture `make_document(session, **kw)` trong `tests/fixtures/documents.py` để task khác dùng.

## Tiêu chí hoàn thành

- [ ] Danh sách không trả tài liệu có `deleted_at`.
- [ ] Tìm "hop dong" ra tài liệu tên "Hợp đồng ABC.pdf"; tìm "50%" không khớp mọi tên.
- [ ] `set_status` sai chuyển trạng thái ném `InvalidTransition` và không ghi.
- [ ] `soft_delete` lần hai trả `False`.
- [ ] `add_chunks` ghi đúng số dòng và vector.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_list_excludes_deleted` | 3 tài liệu, 1 đã `soft_delete` | `list_documents(None, "uploadedAt_desc")` trả 2 |
| `test_search_unaccent` | Tài liệu "Hợp đồng ABC.pdf" và "Báo cáo.pdf"; `search="hop dong"` | Chỉ trả "Hợp đồng ABC.pdf" |
| `test_search_escapes_wildcards` | Tài liệu "a.pdf", "b.pdf"; `search="%"` | Trả rỗng |
| `test_sort_name_asc` | Tên "b.pdf", "a.pdf"; `sort="name_asc"` | Thứ tự a.pdf, b.pdf |
| `test_invalid_status_transition` | Tài liệu `READY`; `set_status(..., PROCESSING)` | `InvalidTransition`; trạng thái vẫn `READY` |
| `test_soft_delete_twice` | Gọi `soft_delete` hai lần | Lần 1 `True`, lần 2 `False` |
| `test_add_chunks` | `add_chunks(doc_id, [2 ChunkDraft], [2 vector])` | Trả 2; bảng `chunk` có 2 dòng đúng `page` |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_document_repository.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- API danh sách (T-202), tải lên (T-201), xóa (T-203).
- Truy xuất chunk (T-303).

## Lưu ý

Quy ước backend ở CONTRACTS mục 2.2: SQLAlchemy 2.0 bất đồng bộ, repository là hàm `async` nhận `AsyncSession` đầu tiên và chỉ `flush`, lớp dịch vụ quyết định `commit`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
