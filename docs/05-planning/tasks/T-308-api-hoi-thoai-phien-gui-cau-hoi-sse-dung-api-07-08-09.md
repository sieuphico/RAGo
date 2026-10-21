# T-308 · API hội thoại: phiên, gửi câu hỏi SSE, dừng (API-07/08/09)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | US-020, US-022, US-027 |
| BR | BR-008, BR-013 |
| NFR, EC, cổng | NFR-001, EC-11 |
| Quyết định kiến trúc | AD-02 |
| Phụ thuộc | [T-105](T-105-repository-hoi-thoai.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-307](T-307-dich-vu-tra-loi-answerservice.md) |
| Mở khóa | [T-311](T-311-pham-vi-tai-lieu-trong-api-08-va-ec-15.md), [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-trich-dan-cac-trang-thai.md), [T-609](T-609-kiem-tra-bao-mat-g6.md) |

## Mục tiêu

Mở các API hội thoại: tạo phiên, gửi câu hỏi nhận luồng SSE, dừng câu trả lời.

## File cần tạo hoặc sửa

- `backend/app/api/chat.py`
- `backend/tests/integration/test_chat_api.py`

## Các bước

1. `POST /api/v1/chat/sessions` → `{sessionId}`.
2. `POST /api/v1/chat/sessions/{sid}/messages` body `{text, scopeDocIds[]}` trả `text/event-stream` với các sự kiện `status`, `token`, `citation`, `done`, `error`; kiểm tra câu hỏi trống hoặc > 2.000 ký tự (`QUESTION_EMPTY`, `QUESTION_TOO_LONG`).
3. `POST /api/v1/chat/messages/{mid}/stop`.
4. Chỉ chủ phiên truy cập được phiên của mình.

## Tiêu chí hoàn thành

- [ ] Luồng SSE đúng định dạng và thứ tự sự kiện.
- [ ] Câu hỏi quá dài bị từ chối trước khi gọi AI.
- [ ] Người dùng khác không gửi được vào phiên của người này.

## Kiểm thử cần viết

- `test_sse_event_order`
- `test_question_validation`
- `test_session_ownership`
- `test_stop_endpoint`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
