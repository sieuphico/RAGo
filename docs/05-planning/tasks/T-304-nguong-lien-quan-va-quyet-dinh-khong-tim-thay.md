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
| Phụ thuộc | [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md) |
| Mở khóa | [T-307](T-307-dich-vu-tra-loi-answerservice.md) |

## Mục tiêu

Quyết định có đủ bằng chứng để gọi AI hay trả "không tìm thấy" ngay.

## File cần tạo hoặc sửa

- `backend/app/modules/answer/relevance.py`
- `backend/tests/unit/test_relevance.py`

## Các bước

1. `has_enough_evidence(chunks: list[ScoredChunk], threshold: float) -> bool`.
2. Không có tài liệu `READY` thì trả `NO_READY_DOCS` (không gọi AI, US-023).
3. Ngưỡng lấy từ cấu hình; ghi chú cách chỉnh bằng bộ câu hỏi chuẩn (DEP-003).

## Tiêu chí hoàn thành

- [ ] Không có chunk nào vượt ngưỡng thì `False` và không có lời gọi AI.
- [ ] Kho không có tài liệu sẵn sàng cho kết quả riêng để giao diện hiện "Kho chưa có tài liệu sẵn sàng".
- [ ] Ngưỡng đổi được bằng cấu hình.

## Kiểm thử cần viết

- `test_below_threshold_not_enough`
- `test_no_ready_docs`
- `test_threshold_configurable`

## Lưu ý

Ngưỡng ban đầu `[TBD]`, chỉnh sau khi có bộ câu hỏi chuẩn (RA-06).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
