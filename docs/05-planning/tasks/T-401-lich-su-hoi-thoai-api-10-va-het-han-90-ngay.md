# T-401 · Lịch sử hội thoại (API-10) và hết hạn 90 ngày

| Thuộc tính | Giá trị |
|---|---|
| Pha | 4 Tính năng P1 phía máy chủ |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-041 |
| BR | BR-021 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-12 |
| Phụ thuộc | [T-105](T-105-repository-hoi-thoai.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) |
| Mở khóa | [T-516](T-516-danh-sach-lich-su-s-06.md) |

## Mục tiêu

Liệt kê phiên theo nhóm thời gian, mở lại phiên và xóa dữ liệu quá 90 ngày.

## File cần tạo hoặc sửa

- `backend/app/api/chat_history.py`
- `backend/app/worker/expire_history.py`
- `backend/tests/integration/test_history.py`

## Các bước

1. `GET /api/v1/chat/sessions` trả phiên của người gọi (id, title, createdAt); `GET /api/v1/chat/sessions/{sid}` trả đầy đủ tin nhắn và trích dẫn.
2. Trích dẫn tới tài liệu đã xóa trả cờ `deleted=true` để giao diện hiện "Tài liệu đã bị xóa".
3. Tác vụ định kỳ xóa phiên quá `history_days`.

## Tiêu chí hoàn thành

- [ ] Đăng nhập lại mở được phiên trước, phiên quá 90 ngày không còn (AC-021).
- [ ] Người dùng chỉ thấy phiên của mình.
- [ ] Trích dẫn tới tài liệu bị xóa trả cờ xóa.

## Kiểm thử cần viết

- `test_history_own_sessions_only`
- `test_expired_sessions_removed`
- `test_deleted_doc_flag`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
