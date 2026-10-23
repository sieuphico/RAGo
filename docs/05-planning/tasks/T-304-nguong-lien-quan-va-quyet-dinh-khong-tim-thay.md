# T-304 · Ngưỡng liên quan và quyết định "không tìm thấy"

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-023 |
| BR | BR-011 |
| NFR, EC, cổng | EC-01, EC-13 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) |

## Mục tiêu

Quyết định có đủ bằng chứng để gọi AI hay trả "không tìm thấy" ngay.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`ScoredChunk`, `DoneEvent.not_found_reason`)
- CONTRACTS mục 7 (`relevance_threshold`)
- CONTRACTS mục 12, Q-C8

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md) Truy xuất lai (vector + từ khóa) theo phạm vi: `retrieve`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `ScoredChunk`, `DoneEvent`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/modules/answer/relevance.py`
- `tests/unit/test_relevance.py`

## Chữ ký và giao diện

```python
Decision = Literal["ANSWER", "NO_READY_DOCS", "NO_EVIDENCE"]

def decide(chunks: list[ScoredChunk], ready_doc_count: int, threshold: float) -> Decision: ...
def filter_evidence(chunks: list[ScoredChunk], threshold: float) -> list[ScoredChunk]: ...
```

## Các bước

1. `decide(chunks, ready_doc_count, threshold)`: `ready_doc_count == 0` → `"NO_READY_DOCS"`; không chunk nào đạt (đạt = `keyword_hit` hoặc `similarity >= threshold`) → `"NO_EVIDENCE"`; còn lại → `"ANSWER"`.
2. `filter_evidence(chunks, threshold)` trả các chunk đạt, giữ thứ tự; chỉ các chunk này được đưa vào prompt.
3. Ngưỡng lấy từ `settings.relevance_threshold` (mặc định 0,0: mọi chunk tìm được đều đạt). Ghi chú trong mã: chỉnh bằng bộ câu hỏi chuẩn ở T-607.

## Tiêu chí hoàn thành

- [ ] Không chunk nào đạt → `NO_EVIDENCE`.
- [ ] Kho không có tài liệu sẵn sàng → `NO_READY_DOCS` dù có chunk.
- [ ] Đổi `relevance_threshold` qua cấu hình làm đổi kết quả.
- [ ] Danh sách rỗng → `NO_EVIDENCE`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_below_threshold_not_enough` | 2 chunk `similarity` 0,3 và 0,4, `keyword_hit=False`; `threshold=0.5` | `"NO_EVIDENCE"`; `filter_evidence` trả `[]` |
| `test_keyword_hit_passes` | 1 chunk `similarity=None`, `keyword_hit=True`; `threshold=0.9` | `"ANSWER"` |
| `test_no_ready_docs` | `ready_doc_count=0`, có chunk đạt | `"NO_READY_DOCS"` |
| `test_threshold_configurable` | Cùng chunk `similarity=0.6`; `threshold` 0,5 rồi 0,7 | `"ANSWER"` rồi `"NO_EVIDENCE"` |
| `test_empty_list` | `chunks=[]`, `ready_doc_count=3` | `"NO_EVIDENCE"` |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_relevance.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Gửi `done` với `notFoundReason` (T-307).
- Chọn giá trị ngưỡng thật (T-607).

## Lưu ý

Ngưỡng ban đầu 0,0 (mọi chunk đều đạt) để không chặn luồng; giá trị thật chỉnh sau khi có bộ câu hỏi chuẩn (RA-06, T-607).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
