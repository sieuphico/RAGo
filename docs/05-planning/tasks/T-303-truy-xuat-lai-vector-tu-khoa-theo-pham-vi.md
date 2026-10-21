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
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) |
| Mở khóa | [T-304](T-304-nguong-lien-quan-va-quyet-dinh-khong-tim-thay.md), [T-403](T-403-tom-tat-tai-lieu-api-12.md) |

## Mục tiêu

Truy xuất top-k chunk bằng vector và từ khóa, hợp nhất thứ hạng, lọc theo phạm vi tài liệu.

## File cần tạo hoặc sửa

- `backend/app/modules/retrieval/service.py`
- `backend/app/modules/retrieval/queries.py`
- `backend/tests/integration/test_retrieval.py`

## Chữ ký và giao diện

```python
async def retrieve(session, gateway: AiGateway, query: str, scope: set[UUID], k: int = 8) -> list[ScoredChunk]: ...
```

## Các bước

1. `retrieve(session, gateway, query, scope_doc_ids, k) -> list[ScoredChunk]`.
2. Nhúng `query` qua cổng AI; truy vấn vector (khoảng cách cosine) và truy vấn `tsv` (`plainto_tsquery('simple', unaccent(query))`) đều lọc `deleted_at is null`, tài liệu `READY` và `doc_id in scope`.
3. Hợp nhất bằng reciprocal rank fusion; trả `ScoredChunk(chunk, score)`.
4. Phạm vi rỗng nghĩa là tất cả tài liệu `READY`.

## Tiêu chí hoàn thành

- [ ] Câu hỏi có mã hợp đồng chính xác tìm ra đúng chunk nhờ truy vấn từ khóa.
- [ ] Câu hỏi diễn đạt khác vẫn tìm ra nhờ vector.
- [ ] Tài liệu đã xóa hoặc chưa sẵn sàng không bao giờ xuất hiện.

## Kiểm thử cần viết

- `test_keyword_finds_contract_number`
- `test_vector_finds_paraphrase`
- `test_scope_filter`
- `test_excludes_deleted_and_not_ready`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
