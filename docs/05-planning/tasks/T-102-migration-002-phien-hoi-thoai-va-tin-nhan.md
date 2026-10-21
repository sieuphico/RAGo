# T-102 · Migration 002: phiên hội thoại và tin nhắn

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-020, US-041 |
| BR | BR-021 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-101](T-101-migration-001-tai-lieu-chunk-goi-y.md) |
| Mở khóa | [T-103](T-103-migration-003-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-105](T-105-repository-hoi-thoai.md) |

## Mục tiêu

Tạo bảng `chat_session`, `message`, `citation`, `rating`.

## File cần tạo hoặc sửa

- `backend/migrations/versions/002_chat.py`
- `backend/tests/integration/test_migration_002.py`

## Các bước

1. `chat_session`: `session_id uuid pk`, `user_email`, `title`, `created_at`, `scope_doc_ids uuid[]`.
2. `message`: `message_id uuid pk`, `session_id fk`, `role`, `text`, `status` (enum SEARCHING, STREAMING, COMPLETED, NOT_FOUND, STOPPED, INTERRUPTED, FAILED), `is_not_found bool`, `stopped bool`, `created_at`.
3. `citation`: `message_id fk`, `idx int`, `doc_id`, `page int`, `snippet` (≤ 200 ký tự, ràng buộc CHECK); khóa chính `(message_id, idx)`.
4. `rating`: `message_id pk fk`, `value` (UP, DOWN), `reason_code null`.
5. Chỉ mục: `chat_session(user_email, created_at desc)`, `message(session_id, created_at)`.

## Tiêu chí hoàn thành

- [ ] `upgrade` và `downgrade` sạch.
- [ ] Snippet dài hơn 200 ký tự bị từ chối.
- [ ] Xóa phiên xóa dây chuyền tin nhắn, trích dẫn và đánh giá.

## Kiểm thử cần viết

- `test_upgrade_downgrade`
- `test_snippet_length_check`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
