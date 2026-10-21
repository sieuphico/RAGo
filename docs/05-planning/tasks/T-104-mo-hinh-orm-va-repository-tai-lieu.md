# T-104 · Mô hình ORM và repository tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-010, US-015 |
| BR | BR-005, BR-006 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-101](T-101-migration-001-tai-lieu-chunk-goi-y.md) |
| Mở khóa | [T-105](T-105-repository-hoi-thoai.md), [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-202](T-202-danh-sach-tai-lieu-api-03.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-208](T-208-ingest-nhung-va-lap-chi-muc.md), [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md), [T-212](T-212-tai-tep-pdf-cho-khung-xem-nguon-api-06.md), [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md) |

## Mục tiêu

Mô hình SQLAlchemy và các hàm truy cập dữ liệu cho `document` và `chunk`.

## File cần tạo hoặc sửa

- `backend/app/models/document.py`
- `backend/app/modules/documents/repository.py`
- `backend/tests/integration/test_document_repository.py`

## Chữ ký và giao diện

```python
def add(session, doc: Document) -> Document: ...
def get(session, doc_id: UUID) -> Document | None: ...
def list_documents(session, search: str | None, sort: str) -> list[Document]: ...
def set_status(session, doc_id: UUID, status: DocumentStatus, *, reason: str | None = None) -> None: ...
def soft_delete(session, doc_id: UUID, at: datetime) -> bool: ...
def add_chunks(session, chunks: list[Chunk]) -> None: ...
```

## Các bước

1. Viết mô hình `Document`, `Chunk`, `Suggestion` khớp migration 001.
2. Viết các hàm trong `repository.py` như chữ ký bên dưới; mọi truy vấn danh sách bỏ qua bản ghi có `deleted_at`.
3. Viết fixture tạo dữ liệu mẫu.

## Tiêu chí hoàn thành

- [ ] Danh sách không trả tài liệu đã xóa.
- [ ] Tìm theo tên không phân biệt hoa thường và dấu `[Đề xuất]`.
- [ ] `set_status` kiểm tra chuyển trạng thái hợp lệ (theo sơ đồ trạng thái SAD 5.2), sai thì ném lỗi.

## Kiểm thử cần viết

- `test_list_excludes_deleted`
- `test_search_by_name`
- `test_invalid_status_transition`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
