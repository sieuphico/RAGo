# T-105 · Repository hội thoại

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-020, US-041 |
| BR | BR-021 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-102](T-102-migration-002-phien-hoi-thoai-va-tin-nhan.md), [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) |
| Mở khóa | [T-307](T-307-dich-vu-tra-loi-answerservice.md), [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-313](T-313-danh-gia-api-11.md), [T-401](T-401-lich-su-hoi-thoai-api-10-va-het-han-90-ngay.md) |

## Mục tiêu

Truy cập dữ liệu phiên, tin nhắn, trích dẫn; luôn lọc theo chủ phiên.

## File cần tạo hoặc sửa

- `backend/app/models/chat.py`
- `backend/app/modules/chat/repository.py`
- `backend/tests/integration/test_chat_repository.py`

## Chữ ký và giao diện

```python
def create_session(session, user_email: str, first_question: str, scope: list[UUID]) -> ChatSession: ...
def get_session(session, user_email: str, session_id: UUID) -> ChatSession | None: ...
```

## Các bước

1. Mô hình `ChatSession`, `Message`, `Citation`, `Rating`.
2. Các hàm: `create_session`, `add_message`, `update_message`, `add_citations`, `list_sessions(user_email, since)`, `get_session(user_email, session_id)`.
3. Tiêu đề phiên là 60 ký tự đầu của câu hỏi đầu tiên (DEC-002).

## Tiêu chí hoàn thành

- [ ] Người dùng khác không đọc được phiên của người dùng này (trả `None`).
- [ ] `list_sessions` chỉ trả phiên trong `history_days`.
- [ ] Tiêu đề cắt đúng 60 ký tự.

## Kiểm thử cần viết

- `test_get_session_other_user_none`
- `test_list_respects_window`
- `test_title_truncation`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
