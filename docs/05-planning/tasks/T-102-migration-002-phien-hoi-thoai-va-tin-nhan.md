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
| Phụ thuộc | [T-101](T-101-migration-001-tai-lieu-chunk-goi-y.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-103](T-103-migration-003-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-105](T-105-repository-hoi-thoai.md) |

## Mục tiêu

Tạo bảng `chat_session`, `message`, `citation`, `rating`.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`MessageStatus`)
- CONTRACTS mục 12, Q-C7 (tiêu đề phiên)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-101](T-101-migration-001-tai-lieu-chunk-goi-y.md) Migration 001: tài liệu, chunk, gợi ý: `backend/migrations/versions/001_documents.py`, `backend/tests/integration/test_migration_001.py`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `MessageStatus`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `backend/migrations/versions/002_chat.py`
- `backend/tests/integration/test_migration_002.py`

## Các bước

1. `chat_session`: `session_id uuid pk`, `user_email text not null`, `title text null` (≤ 60 ký tự, đặt ở câu hỏi đầu), `created_at timestamptz not null default now()`, `last_message_at timestamptz not null default now()`, `scope_doc_ids uuid[] not null default '{}'`.
2. `message`: `message_id uuid pk`, `session_id uuid not null references chat_session on delete cascade`, `role text not null check (role in ('user','assistant'))`, `text text not null default ''`, `status text not null` với CHECK theo `MessageStatus`, `is_not_found bool not null default false`, `latency_ms int null`, `error_code text null`, `created_at timestamptz not null default now()`.
3. `citation`: `message_id uuid references message on delete cascade`, `idx int not null`, `doc_id uuid not null references document` (không cascade: tài liệu đã xóa vẫn giữ hàng, EC-14), `page int not null`, `snippet text not null check (char_length(snippet) <= 200)`; khóa chính `(message_id, idx)`.
4. `rating`: `message_id uuid pk references message on delete cascade`, `value text not null check (value in ('UP','DOWN'))`, `reason_code text null check (reason_code in ('WRONG_INFO','WRONG_CITATION','MISSING_INFO','OTHER'))`, `created_at timestamptz not null default now()`.
5. Chỉ mục: `chat_session(user_email, last_message_at desc)`, `message(session_id, created_at)`.

## Tiêu chí hoàn thành

- [ ] `upgrade` và `downgrade` sạch.
- [ ] Snippet 201 ký tự bị từ chối, 200 ký tự được nhận.
- [ ] Xóa phiên xóa dây chuyền tin nhắn, trích dẫn và đánh giá.
- [ ] `role='system'` bị từ chối.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_upgrade_downgrade` | CSDL ở revision 001; `upgrade 002` rồi `downgrade 001` | Không lỗi |
| `test_snippet_length_check` | Chèn citation với snippet 200 rồi 201 ký tự | 200 ký tự được nhận; 201 ký tự `IntegrityError` |
| `test_session_cascade` | Phiên có 2 tin nhắn, 1 trích dẫn, 1 đánh giá; xóa phiên | Ba bảng con không còn dòng của phiên |
| `test_role_check` | Chèn message `role='system'` | `IntegrityError` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_migration_002.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Repository hội thoại (T-105).
- Hết hạn 90 ngày (T-401).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
