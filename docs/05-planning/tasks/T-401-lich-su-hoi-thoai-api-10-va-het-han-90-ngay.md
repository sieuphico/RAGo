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
| Phụ thuộc | [T-105](T-105-repository-hoi-thoai.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-614](T-614-co-tinh-nang-cho-phan-p1.md) |
| Mở khóa | — |

## Mục tiêu

Liệt kê phiên theo nhóm thời gian, mở lại phiên và xóa dữ liệu quá 90 ngày.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-10a, API-10b, 4.2 `SessionSummaryOut`, `SessionDetailOut`
- CONTRACTS mục 8 (`history_expire`)
- CONTRACTS mục 6 (`history_session_opened`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-105](T-105-repository-hoi-thoai.md) Repository hội thoại: `create_session`, `set_title_if_empty`, `get_session`, `list_sessions`, `add_message`, `update_message` …
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) Telemetry: lược đồ sự kiện và API-16: `anon_id`, `emit`, `EVENTS`, `CLIENT_EVENTS`
- [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md) Worker: vòng lặp xử lý và scheduler: `run_worker`, `run_scheduler`
- [T-614](T-614-co-tinh-nang-cho-phan-p1.md) Cờ tính năng cho phần P1: `is_enabled`, `require_feature`, `ALL_P1`

## File cần tạo hoặc sửa

- `app/api/chat_history.py`
- `app/worker/expire_history.py`
- `tests/integration/test_history.py`

## Chữ ký và giao diện

```python
async def expire_history(session: AsyncSession, now: datetime) -> int: ...
```

## Các bước

1. `GET /api/v1/chat/sessions` (API-10a): phiên của người gọi có `last_message_at >= now - history_days`, mới nhất trước; `require_feature("history")`.
2. `GET /api/v1/chat/sessions/{sid}` (API-10b): không phải chủ phiên → 404 `SESSION_NOT_FOUND`; trả tin nhắn theo thời gian, kèm trích dẫn và `rating`; trích dẫn tới tài liệu có `deleted_at` → `deleted: true`. Phát `history_session_opened {session_age_days}`.
3. `expire_history(session, now)`: xóa phiên có `last_message_at < now - history_days` (dây chuyền xóa tin nhắn); thêm `daily("history_expire", "02:30", ...)` vào `worker/registry.py`.

## Tiêu chí hoàn thành

- [ ] Đăng nhập lại mở được phiên trước; phiên 91 ngày tuổi không còn (AC-021).
- [ ] Người dùng chỉ thấy phiên của mình.
- [ ] Trích dẫn tới tài liệu đã xóa có `deleted: true`.
- [ ] Cờ `history` tắt thì API trả 404 `NOT_FOUND`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_history_own_sessions_only` | lan@ có 2 phiên, minh@ có 1 | lan@ gọi API-10a nhận 2 mục |
| `test_open_other_user_session` | minh@ gọi API-10b với phiên của lan@ | 404 `SESSION_NOT_FOUND` |
| `test_session_detail_shape` | Phiên có 1 câu hỏi và 1 câu trả lời 2 trích dẫn, 👍 | Đúng dạng `SessionDetailOut`; `rating="UP"`; có `history_session_opened` |
| `test_deleted_doc_flag` | Một trích dẫn trỏ tài liệu đã `soft_delete` | Trích dẫn đó `deleted: true`, trích dẫn kia `false` |
| `test_expired_sessions_removed` | Phiên 91 ngày và 89 ngày tuổi; `expire_history(now)` | Còn phiên 89 ngày; tin nhắn của phiên 91 ngày bị xóa |
| `test_flag_off` | Cờ `history` tắt | API-10a 404 |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_history.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Danh sách lịch sử ở giao diện (T-516).
- Cho PM/QA xem bản ẩn danh (PQ-003, ngoài MVP).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
