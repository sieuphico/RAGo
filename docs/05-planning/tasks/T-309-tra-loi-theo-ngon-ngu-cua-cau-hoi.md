# T-309 · Trả lời theo ngôn ngữ của câu hỏi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P1 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 3 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-024 |
| BR | BR-026 |
| NFR, EC, cổng | EC-12 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-305](T-305-dung-prompt-voi-nhan-chunk.md) |
| Mở khóa | — |

## Mục tiêu

Prompt yêu cầu trả lời cùng ngôn ngữ với câu hỏi; ghi chú khi ngôn ngữ ngoài Việt và Anh.

## File cần tạo hoặc sửa

- `backend/app/modules/answer/prompt.py`
- `backend/app/modules/answer/lang.py`
- `backend/tests/unit/test_lang.py`

## Các bước

1. `detect_lang(text: str) -> Literal["vi", "en", "other"]` bằng đoán đơn giản `[Đề xuất]`.
2. Thêm chỉ dẫn ngôn ngữ vào prompt; với `other` thì trả lời tiếng Việt kèm "Hiện chỉ hỗ trợ tốt tiếng Việt và tiếng Anh" (EC-12).

## Tiêu chí hoàn thành

- [ ] Câu hỏi tiếng Anh cho chỉ dẫn trả lời tiếng Anh.
- [ ] Câu hỏi ngôn ngữ khác thêm ghi chú hỗ trợ.
- [ ] Sẵn sàng cho bộ kiểm tra ≥ 19/20 (AC-026) ở T-607.

## Kiểm thử cần viết

- `test_detect_vi_en`
- `test_other_language_note`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
