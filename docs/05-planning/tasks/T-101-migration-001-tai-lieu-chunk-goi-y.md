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
| Phụ thuộc | [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md) |
| Mở khóa | [T-102](T-102-migration-002-phien-hoi-thoai-va-tin-nhan.md), [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) |

## Mục tiêu

Tạo bảng `document`, `chunk`, `suggestion` và chỉ mục truy xuất theo SAD mục 3.1.

## File cần tạo hoặc sửa

- `backend/migrations/versions/001_documents.py`
- `backend/tests/integration/test_migration_001.py`

## Các bước

1. Bảng `document`: `doc_id uuid pk`, `name`, `uploaded_by`, `uploaded_at`, `size_bytes bigint`, `page_count int null`, `status` (enum UPLOADING, INTERRUPTED, PROCESSING, OCR_PROCESSING, READY, FAILED, DELETED), `failure_reason null`, `used_ocr bool`, `file_key`, `deleted_at null`.
2. Bảng `chunk`: `chunk_id uuid pk`, `doc_id fk`, `page int`, `text`, `embedding vector(embedding_dim)`, `tsv tsvector` (cột tạo từ `text` với cấu hình `simple` và `unaccent`), `lang`.
3. Bảng `suggestion`: `doc_id pk fk`, `questions jsonb`, `created_at`.
4. Chỉ mục: HNSW trên `embedding`; GIN trên `tsv`; btree trên `chunk(doc_id, page)` và `document(status, uploaded_at)`.
5. Số chiều vector lấy từ `Settings.embedding_dim`; ghi chú trong migration rằng đổi mô hình nhúng phải lập chỉ mục lại.

## Tiêu chí hoàn thành

- [ ] `upgrade` và `downgrade` đều chạy sạch.
- [ ] Các chỉ mục tồn tại (kiểm bằng truy vấn catalog).
- [ ] Xóa `document` xóa dây chuyền `chunk` và `suggestion`.

## Kiểm thử cần viết

- `test_upgrade_downgrade`
- `test_indexes_exist`
- `test_cascade_delete`

## Lưu ý

Số chiều vector chưa biết đến khi chốt AD-06 (T-005); dùng giá trị cấu hình, không mã hóa cứng.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
