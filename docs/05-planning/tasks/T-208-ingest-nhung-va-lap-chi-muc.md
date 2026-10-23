# T-208 · Ingest: nhúng và lập chỉ mục

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W4–W5 (xem PLAN mục 6) |
| Story | US-020 |
| BR | BR-008 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-03 |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-207](T-207-ingest-chia-chunk-theo-trang.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) |
| Mở khóa | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) |

## Mục tiêu

Nhúng các chunk theo lô qua `AiPort` và ghi chunk cùng vector, `tsv` vào CSDL.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`ChunkDraft`)
- CONTRACTS mục 7 (`embed_batch_size`, `embedding_dim`)
- Chữ ký `add_chunks` ở T-104

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-207](T-207-ingest-chia-chunk-theo-trang.md) Ingest: chia chunk theo trang: `split`
- [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) Cổng (ports) và bộ nối giả (fake adapters): `ProviderError`, `ProviderTimeout`, `AiPort`, `OcrPort`, `StoragePort`, `IdpPort`

## File cần tạo hoặc sửa

- `backend/app/worker/indexer.py`
- `backend/tests/integration/test_indexer.py`

## Chữ ký và giao diện

```python
EmbedFn = Callable[[list[str]], Awaitable[list[list[float]]]]

async def index_document(session: AsyncSession, embed: EmbedFn, doc_id: UUID, chunks: list[ChunkDraft], *, batch_size: int, dim: int) -> int: ...
```

## Các bước

1. `index_document(session, embed, doc_id, chunks, batch_size)`: chia `chunks` thành lô `batch_size`, gọi `embed([c.text for c in lô])` cho từng lô.
2. Kiểm tra mỗi vector có độ dài `embedding_dim`; sai → `ValueError("embedding dim")`.
3. Ghi toàn bộ bằng `documents.delete_chunks(doc_id)` rồi `documents.add_chunks(...)` trong cùng giao dịch (chạy lại an toàn).
4. `embed` là hàm truyền vào (wiring chọn `AiGateway.embed` sau T-301, hoặc `AiFake.embed`); task này **không** tự thử lại — thử lại do cổng AI làm (T-301).
5. Trả số chunk đã ghi.

## Tiêu chí hoàn thành

- [ ] Sau khi chạy, số dòng `chunk` của tài liệu bằng số chunk đầu vào.
- [ ] Chạy lại lần hai không nhân đôi chunk.
- [ ] Vector sai số chiều làm dừng và không ghi chunk nào.
- [ ] Lỗi ở lô thứ hai không để lại chunk của lô thứ nhất.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_index_writes_chunks` | 70 chunk, `batch_size=32`, `embed` giả đếm lần gọi | Trả 70; `embed` được gọi 3 lần; 70 dòng `chunk` |
| `test_reindex_idempotent` | Gọi hai lần với cùng 5 chunk | Vẫn 5 dòng |
| `test_dim_mismatch_raises` | `embed` trả vector dài 10 khi `embedding_dim=384` | `ValueError`; 0 dòng |
| `test_partial_failure_rolls_back` | `embed` ném lỗi ở lô 2 | Ngoại lệ lan ra; 0 dòng sau rollback |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_indexer.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Thử lại, thời hạn và hạn mức khi gọi AI (T-301).
- Đổi trạng thái tài liệu (T-210).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
