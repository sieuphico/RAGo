# T-306 · Kiểm tra và ánh xạ trích dẫn

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-022 |
| BR | BR-010 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-13 |
| Phụ thuộc | [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md), [T-403](T-403-tom-tat-tai-lieu-api-12.md) |

## Mục tiêu

Đổi nhãn `[cN]` trong đầu ra thành trích dẫn; bỏ nhãn không có trong tập chunk đã gửi.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.3 (dấu `[[n]]`)
- CONTRACTS mục 2 (`ChunkRef`, `CitationOut`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `ChunkRef`, `CitationOut`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `backend/app/modules/answer/citations.py`
- `backend/tests/unit/test_citations.py`

## Chữ ký và giao diện

```python
class CitationResolver:
    def __init__(self, label_map: dict[str, ChunkRef]) -> None: ...
    def feed(self, delta: str) -> tuple[str, list[CitationOut]]: ...
    def finish(self) -> tuple[str, list[CitationOut]]: ...
    @property
    def citations(self) -> list[CitationOut]: ...

def resolve(text: str, label_map: dict[str, ChunkRef]) -> tuple[str, list[CitationOut]]: ...
```

## Các bước

1. `CitationResolver(label_map)` xử lý văn bản theo luồng.
2. `feed(delta)` nối vào bộ đệm; tìm nhãn theo biểu thức `\[(c\d+(?:\s*,\s*c\d+)*)\]` (nhận cả `[c1]` và `[c1, c3]`).
3. Nhãn có trong `label_map`: lần đầu gặp thì gán `index` tăng dần từ 1 và tạo `CitationOut(index, doc_id, doc_name, page, snippet)`; thay bằng `[[index]]` (nhãn nhóm thành `[[1]][[2]]`). Nhãn lạ: xóa khỏi văn bản.
4. Nếu bộ đệm kết thúc bằng phần có thể là nhãn dở (khớp `\[(c\d*(\s*,\s*c?\d*)*)?$`) thì giữ lại phần đó, trả phần trước.
5. `feed` trả `(văn_bản_an_toàn, trích_dẫn_mới)`; người gọi gửi trích dẫn mới **trước** văn bản (CONTRACTS mục 4.3).
6. `finish()` trả phần còn lại; nhãn dở ở cuối bị bỏ.
7. `resolve(text, label_map)` gọi `feed` một lần rồi `finish`, tiện cho tóm tắt (T-403).

## Tiêu chí hoàn thành

- [ ] 100% trích dẫn trả về trỏ tới chunk có trong `label_map`.
- [ ] Nhãn bịa không tạo trích dẫn và biến mất khỏi văn bản.
- [ ] Nhãn bị cắt giữa hai lần `feed` vẫn được nhận đúng.
- [ ] Cùng một nhãn dùng lại cho cùng `index`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_valid_labels_resolved` | `label_map` có c1, c2; `resolve("A [c2]. B [c1].")` | Văn bản `"A [[1]]. B [[2]]."`; trích dẫn index 1 = chunk c2, index 2 = chunk c1 |
| `test_unknown_label_dropped` | `resolve("A [c9].")` với `label_map` chỉ có c1 | Văn bản `"A ."`; 0 trích dẫn |
| `test_partial_label_buffered` | `feed("Thời hạn [c")` rồi `feed("1] tháng")` | Lần 1 trả `("Thời hạn ", [])`; lần 2 trả `("[[1]] tháng", [cit1])` |
| `test_group_label` | `resolve("X [c1, c2].")` | `"X [[1]][[2]]."`, 2 trích dẫn |
| `test_repeat_label_same_index` | `resolve("[c1] và [c1]")` | `"[[1]] và [[1]]"`, 1 trích dẫn |
| `test_snippet_limit` | `ChunkRef.snippet` dài 200 | `CitationOut.snippet` dài ≤ 200 |
| `test_dangling_label_at_end` | `feed("kết thúc [c")`; `finish()` | `finish` trả `""` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/unit/test_citations.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Gửi sự kiện SSE (T-307, T-308).
- Hiển thị thẻ trích dẫn (T-512).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
