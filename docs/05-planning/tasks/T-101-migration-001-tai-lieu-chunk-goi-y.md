# T-101 · Migration 001: tài liệu, chunk, gợi ý

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-010, US-015 |
| BR | BR-006 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-03 |
| Phụ thuộc | [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-102](T-102-migration-002-phien-hoi-thoai-va-tin-nhan.md), [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) |

## Mục tiêu

Tạo bảng `document`, `chunk`, `suggestion` và chỉ mục truy xuất theo SAD mục 3.1.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 và 2.1 (`DocumentStatus`, `FailureReason`)
- CONTRACTS mục 7 (`embedding_dim`)
- T-003: hàm `cwd_unaccent`

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md) CSDL phát triển, kết nối và Alembic: `get_session`, `engine`, `SessionLocal`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `DocumentStatus`, `FailureReason`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `migrations/versions/001_documents.py`
- `tests/integration/test_migration_001.py`

## Các bước

1. Bảng `document`: `doc_id uuid pk default gen_random_uuid()`, `name text not null` (≤ 255 ký tự), `uploaded_by text not null` (email), `uploaded_at timestamptz not null default now()`, `size_bytes bigint not null`, `page_count int null`, `status text not null` với `CHECK (status IN ('PROCESSING','OCR_PROCESSING','READY','FAILED','DELETED'))`, `failure_reason text null` với `CHECK` theo `FailureReason`, `used_ocr bool not null default false`, `file_key text not null unique`, `processed_at timestamptz null`, `deleted_at timestamptz null`.
2. Bảng `chunk`: `chunk_id uuid pk`, `doc_id uuid not null references document on delete cascade`, `page int not null check (page >= 1)`, `text text not null`, `embedding vector(<embedding_dim>) not null`, `tsv tsvector generated always as (to_tsvector('simple', cwd_unaccent(text))) stored`, `lang text null`.
3. Bảng `suggestion`: `doc_id uuid pk references document on delete cascade`, `questions jsonb not null` (mảng đúng 3 chuỗi), `created_at timestamptz not null default now()`.
4. Chỉ mục: `ix_chunk_embedding_hnsw` (HNSW, `vector_cosine_ops`); `ix_chunk_tsv_gin` (GIN); `ix_chunk_doc_page` btree `(doc_id, page)`; `ix_document_status_uploaded` btree `(status, uploaded_at desc)`.
5. Số chiều đọc từ `get_settings().embedding_dim` lúc chạy migration; ghi chú trong migration: đổi mô hình nhúng thì phải tạo lại cột và lập chỉ mục lại.
6. Không có giá trị `UPLOADING` hay `INTERRUPTED` (chỉ có ở trình duyệt, CONTRACTS mục 2.1).

## Tiêu chí hoàn thành

- [ ] `upgrade` và `downgrade` đều chạy sạch trên CSDL đã có migration 000.
- [ ] 4 chỉ mục tồn tại đúng tên.
- [ ] Xóa một `document` xóa dây chuyền `chunk` và `suggestion` của nó.
- [ ] Chèn `status='UPLOADING'` bị CSDL từ chối.
- [ ] Cột `tsv` của văn bản "Hợp đồng" khớp truy vấn không dấu "hop dong".

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_upgrade_downgrade` | CSDL ở revision 000; chạy `upgrade 001` rồi `downgrade 000` | Không lỗi; sau downgrade không còn 3 bảng |
| `test_indexes_exist` | Sau upgrade; truy vấn `pg_indexes` | Có đủ 4 tên chỉ mục ở bước 4 |
| `test_cascade_delete` | Chèn 1 document, 2 chunk, 1 suggestion; xóa document | Bảng `chunk` và `suggestion` không còn dòng của tài liệu đó |
| `test_status_check` | Chèn document với `status='UPLOADING'` | `IntegrityError` (vi phạm CHECK) |
| `test_tsv_unaccent` | Chèn chunk `text='Hợp đồng số 12/2026'`; truy vấn `tsv @@ plainto_tsquery('simple', cwd_unaccent('hop dong'))` | Trả đúng chunk đó |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_migration_001.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Mô hình ORM và repository (T-104).
- Bảng hội thoại (T-102), quản trị (T-103).

## Lưu ý

Số chiều vector chưa biết đến khi chốt AD-06 (T-005); dùng giá trị cấu hình, không mã hóa cứng.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
