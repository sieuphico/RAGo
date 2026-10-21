# T-310 · Câu hỏi nối tiếp trong phiên

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P1 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-025 |
| BR | BR-014 |
| NFR, EC, cổng | NFR-009 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-307](T-307-dich-vu-tra-loi-answerservice.md) |
| Mở khóa | — |

## Mục tiêu

Đưa các lượt gần nhất của phiên vào truy xuất và prompt để hiểu đại từ.

## File cần tạo hoặc sửa

- `backend/app/modules/answer/history.py`
- `backend/tests/integration/test_followup.py`

## Các bước

1. `recent_turns(session, session_id, n=3) -> list[Turn]`.
2. Viết lại câu hỏi độc lập (`standalone_question`) bằng một lời gọi AI ngắn hoặc ghép lượt trước `[Đề xuất]` trước khi truy xuất.
3. Chỉ dùng lịch sử của chính phiên đó.

## Tiêu chí hoàn thành

- [ ] Hỏi "Thời hạn của nó?" sau câu về hợp đồng X trả lời đúng đối tượng (≥ 8/10 cặp, AC-014 ở T-607).
- [ ] Không dùng lịch sử của phiên khác.
- [ ] Có thể tắt bằng cờ tính năng.

## Kiểm thử cần viết

- `test_followup_uses_previous_turn`
- `test_no_cross_session_history`

## Lưu ý

Thêm một lời gọi AI mỗi lượt nối tiếp: kiểm tra ảnh hưởng chi phí (NFR-009).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
