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
| Phụ thuộc | [T-102](T-102-migration-002-phien-hoi-thoai-va-tin-nhan.md), [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md), [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-310](T-310-cau-hoi-noi-tiep-trong-phien.md), [T-313](T-313-danh-gia-api-11.md), [T-401](T-401-lich-su-hoi-thoai-api-10-va-het-han-90-ngay.md) |

## Mục tiêu

Truy cập dữ liệu phiên, tin nhắn, trích dẫn; luôn lọc theo chủ phiên.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`MessageStatus`, `CitationOut`)
- CONTRACTS mục 4.2 (`SessionDetailOut`)
- CONTRACTS mục 12, Q-C7

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-102](T-102-migration-002-phien-hoi-thoai-va-tin-nhan.md) Migration 002: phiên hội thoại và tin nhắn: `backend/migrations/versions/002_chat.py`, `backend/tests/integration/test_migration_002.py`
- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `MessageStatus`, `CitationOut`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `backend/app/models/chat.py`
- `backend/app/modules/chat/repository.py`
- `backend/tests/integration/test_chat_repository.py`

## Chữ ký và giao diện

```python
async def create_session(session: AsyncSession, user_email: str, scope: list[UUID] | None = None) -> ChatSession: ...
async def set_title_if_empty(session: AsyncSession, session_id: UUID, question: str) -> None: ...
async def get_session(session: AsyncSession, user_email: str, session_id: UUID) -> ChatSession | None: ...  # nạp kèm messages, citations, rating
async def list_sessions(session: AsyncSession, user_email: str, since: datetime) -> list[ChatSession]: ...
async def add_message(session: AsyncSession, session_id: UUID, role: Literal["user", "assistant"], text: str, status: MessageStatus) -> Message: ...
async def update_message(session: AsyncSession, message_id: UUID, *, text: str | None = None, status: MessageStatus | None = None,
                         is_not_found: bool | None = None, latency_ms: int | None = None, error_code: str | None = None) -> None: ...
async def add_citations(session: AsyncSession, message_id: UUID, citations: list[CitationOut]) -> None: ...
async def get_message_for_user(session: AsyncSession, user_email: str, message_id: UUID) -> Message | None: ...
async def has_running_message(session: AsyncSession, user_email: str) -> bool: ...
```

## Các bước

1. Mô hình `ChatSession`, `Message`, `Citation`, `Rating` khớp migration 002.
2. Viết các hàm đúng chữ ký; mọi hàm đọc nhận `user_email` và lọc theo chủ phiên.
3. `create_session` tạo phiên với `title=None`; `set_title_if_empty` đặt `title = question.strip()[:60]` chỉ khi đang `None` (DEC-002).
4. `has_running_message(user_email)` trả `True` nếu người đó có tin nhắn `assistant` ở `SEARCHING` hoặc `STREAMING`.
5. `add_message` cập nhật `chat_session.last_message_at`.

## Tiêu chí hoàn thành

- [ ] Người dùng khác gọi `get_session` nhận `None`.
- [ ] `list_sessions` chỉ trả phiên có `last_message_at >= since`, mới nhất trước.
- [ ] Câu hỏi 75 ký tự cho tiêu đề đúng 60 ký tự đầu; gọi lần hai không đổi tiêu đề.
- [ ] `has_running_message` phản ánh đúng trạng thái.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_get_session_other_user_none` | Phiên của lan@; `get_session("minh@...", sid)` | `None` |
| `test_list_respects_window` | Phiên A `last_message_at` 10 ngày trước, B 100 ngày trước; `since` = 90 ngày trước | Chỉ A |
| `test_title_truncation` | `set_title_if_empty(sid, "x" * 75)` rồi gọi lại với "y" | Tiêu đề = 60 ký tự "x" |
| `test_has_running_message` | Tin nhắn assistant `STREAMING` của lan@ | `True`; sau `update_message(status=COMPLETED)` thì `False` |
| `test_add_citations_roundtrip` | `add_citations(mid, [CitationOut(1, d, "A.pdf", 3, "…")])`; `get_session` | Tin nhắn có 1 trích dẫn đúng `page=3` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_chat_repository.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- API hội thoại (T-308), lịch sử (T-401), đánh giá (T-313).
- Xóa phiên quá 90 ngày (T-401).

## Lưu ý

Quy ước backend ở CONTRACTS mục 2.2: SQLAlchemy 2.0 bất đồng bộ, repository là hàm `async` nhận `AsyncSession` đầu tiên và chỉ `flush`, lớp dịch vụ quyết định `commit`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
