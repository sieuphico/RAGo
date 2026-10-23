# T-303 · Truy xuất lai (vector + từ khóa) theo phạm vi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-020, US-021 |
| BR | BR-008, BR-009, BR-015 |
| NFR, EC, cổng | NFR-001 |
| Quyết định kiến trúc | AD-03 |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-304](T-304-nguong-lien-quan-va-quyet-dinh-khong-tim-thay.md), [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) |

## Mục tiêu

Truy xuất top-k chunk bằng vector và từ khóa, hợp nhất thứ hạng, lọc theo phạm vi tài liệu.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`ScoredChunk`)
- CONTRACTS mục 7 (`retrieval_k`)
- Migration 001 (T-101): cột `embedding`, `tsv`, hàm `cwd_unaccent`

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md) Cổng AI (AiGateway): thời hạn, hạn mức, ghi nhận: `AiGateway`
- [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) Dữ liệu mẫu và fixture kiểm thử: `scripts/make_sample_data.py`, `tests/fixtures/README.md`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `ScoredChunk`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/modules/retrieval/service.py`
- `app/modules/retrieval/queries.py`
- `tests/integration/test_retrieval.py`

## Chữ ký và giao diện

```python
async def retrieve(session: AsyncSession, embed: EmbedFn, query: str, scope: set[UUID], k: int = 8) -> list[ScoredChunk]: ...
```

## Các bước

1. `retrieve(session, embed, query, scope, k)`; `embed` là `AiGateway.embed` trong mã chạy thật.
2. Lọc chung: `document.status = 'READY' AND document.deleted_at IS NULL AND (scope rỗng OR chunk.doc_id = ANY(:scope))`.
3. Nhánh vector: `ORDER BY chunk.embedding <=> :qvec LIMIT 2k`; `similarity = 1 - (embedding <=> :qvec)`.
4. Nhánh từ khóa: `WHERE chunk.tsv @@ plainto_tsquery('simple', cwd_unaccent(:q)) ORDER BY ts_rank_cd(tsv, query) DESC LIMIT 2k`.
5. Hợp nhất RRF: `score = Σ 1/(60 + rank)` trên hai nhánh (rank bắt đầu từ 1); `keyword_hit = True` nếu chunk có ở nhánh từ khóa; `similarity = None` nếu chỉ có ở nhánh từ khóa.
6. Trả `k` phần tử điểm cao nhất, kèm `doc_name`.

## Tiêu chí hoàn thành

- [ ] Câu hỏi chứa mã "HD-2026-012" tìm ra đúng chunk nhờ nhánh từ khóa.
- [ ] Câu hỏi có vector gần chunk B nhất (vector dựng tay) tìm ra B dù không trùng từ.
- [ ] Tài liệu đã xóa hoặc chưa `READY` không bao giờ xuất hiện.
- [ ] Phạm vi `{A}` chỉ trả chunk của A.
- [ ] Với 500 tài liệu × 50 chunk, một truy vấn chạy ≤ 500 ms trên máy phát triển.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_keyword_finds_contract_number` | Chunk X chứa "HD-2026-012", 20 chunk khác; `embed` giả trả vector ngẫu nhiên; truy vấn "hợp đồng HD-2026-012" | X ở vị trí 1, `keyword_hit=True` |
| `test_vector_finds_paraphrase` | Chunk B có `embedding = e1`, chunk khác vector trực giao; `embed` giả trả `e1` cho truy vấn không trùng từ nào với B | B ở vị trí 1, `similarity ≈ 1.0`, `keyword_hit=False` |
| `test_scope_filter` | Chunk ở tài liệu A và B; `scope={A}` | Chỉ chunk của A |
| `test_excludes_deleted_and_not_ready` | Tài liệu C `PROCESSING`, D đã `soft_delete`, cả hai có chunk khớp từ khóa | Không có chunk của C, D |
| `test_rrf_merge` | Chunk xuất hiện ở cả hai nhánh, hạng 1 và 2 | `score == 1/61 + 1/62` |
| `test_retrieval_perf` | 25.000 chunk (dùng script chèn hàng loạt) | ≤ 500 ms mỗi truy vấn (ghi số đo vào mô tả thay đổi) |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_retrieval.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Quyết định có đủ bằng chứng (T-304).
- Chỉnh `k` và ngưỡng theo bộ câu hỏi chuẩn (T-607).

## Lưu ý

Vector của `AiFake` lấy từ băm văn bản nên không có nghĩa ngữ nghĩa; test nhánh vector phải dựng vector bằng tay như bảng kiểm thử.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
