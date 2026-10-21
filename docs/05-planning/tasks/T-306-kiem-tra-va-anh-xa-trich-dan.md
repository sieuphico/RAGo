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
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) |
| Mở khóa | [T-307](T-307-dich-vu-tra-loi-answerservice.md), [T-403](T-403-tom-tat-tai-lieu-api-12.md) |

## Mục tiêu

Đổi nhãn `[cN]` trong đầu ra thành trích dẫn; bỏ nhãn không có trong tập chunk đã gửi.

## File cần tạo hoặc sửa

- `backend/app/modules/answer/citations.py`
- `backend/tests/unit/test_citations.py`

## Các bước

1. `resolve(text: str, label_map: dict[str, ChunkRef]) -> ResolvedAnswer` với `ResolvedAnswer(text, citations: list[Citation])`.
2. Nhãn hợp lệ → `Citation(index, doc_id, doc_name, page, snippet[:200])`; nhãn lạ bị bỏ và ý đó không được tính là có căn cứ.
3. Hàm xử lý được nhãn bị cắt giữa luồng (`[c1` chưa đóng) bằng bộ đệm.

## Tiêu chí hoàn thành

- [ ] 100% trích dẫn trả về trỏ tới chunk đã gửi.
- [ ] Nhãn bịa không tạo trích dẫn.
- [ ] Snippet không dài quá 200 ký tự.

## Kiểm thử cần viết

- `test_valid_labels_resolved`
- `test_unknown_label_dropped`
- `test_partial_label_buffered`
- `test_snippet_limit`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
