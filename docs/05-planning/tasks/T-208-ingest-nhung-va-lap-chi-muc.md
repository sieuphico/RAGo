# T-208 · Ingest: nhúng và lập chỉ mục

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-020 |
| BR | BR-008 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-03 |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-207](T-207-ingest-chia-chunk-theo-trang.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) |
| Mở khóa | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) |

## Mục tiêu

Nhúng các chunk theo lô qua `AiPort` và ghi chunk cùng vector, `tsv` vào CSDL.

## File cần tạo hoặc sửa

- `backend/app/worker/indexer.py`
- `backend/tests/integration/test_indexer.py`

## Các bước

1. `index_document(session, ai: AiPort, doc_id, chunks: list[ChunkDraft]) -> int`.
2. Gọi `ai.embed` theo lô (kích thước lô cấu hình được); gặp lỗi tạm thời thì thử lại với backoff.
3. Ghi `Chunk` (kèm `lang` nếu đoán được); cột `tsv` tự tạo từ migration.
4. Ghi lại số chunk.

## Tiêu chí hoàn thành

- [ ] Sau khi chạy, số dòng `chunk` bằng số chunk đầu vào.
- [ ] Vector có đúng số chiều cấu hình.
- [ ] Lỗi giữa chừng không để lại chunk dở dang (dùng giao dịch).

## Kiểm thử cần viết

- `test_index_writes_chunks`
- `test_dim_mismatch_raises`
- `test_partial_failure_rolls_back`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
