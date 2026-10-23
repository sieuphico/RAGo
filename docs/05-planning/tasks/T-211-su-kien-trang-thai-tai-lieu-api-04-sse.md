# T-211 · Sự kiện trạng thái tài liệu (API-04, SSE)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-012 |
| BR | BR-005 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-02 |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) |

## Mục tiêu

Đẩy thay đổi trạng thái tài liệu tới giao diện qua SSE, không cần tải lại trang.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 5.1 (định dạng SSE API-04)
- CONTRACTS mục 4.1 API-04

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `DocumentStatus`, `FailureReason`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/modules/documents/events.py`
- `app/api/document_events.py`
- `tests/integration/test_document_events.py`

## Chữ ký và giao diện

```python
async def publish_status(session: AsyncSession, doc_id: UUID, status: DocumentStatus, reason: FailureReason | None = None, page_count: int | None = None) -> None: ...

class StatusHub:
    async def start(self, dsn: str) -> None: ...
    def subscribe(self) -> asyncio.Queue[dict]: ...
    def unsubscribe(self, q: asyncio.Queue[dict]) -> None: ...
```

## Các bước

1. `publish_status(session, doc_id, status, reason=None, page_count=None)`: `SELECT pg_notify('doc_status', :json)` trong cùng giao dịch với việc đổi trạng thái (thông báo chỉ đi khi `commit`).
2. `StatusHub` trong tiến trình API: một kết nối `asyncpg` riêng `LISTEN doc_status`; mỗi client SSE là một `asyncio.Queue(maxsize=100)`; nhận thông báo thì đẩy vào mọi hàng đợi (đầy thì bỏ thông báo cũ nhất).
3. `GET /api/v1/documents/events`: `require_roles(BD_USER, TEAM_LEAD, ADMIN)`; trả `StreamingResponse` `text/event-stream`, tiêu đề `Cache-Control: no-cache`, `X-Accel-Buffering: no`; khung đúng CONTRACTS mục 5.1; `: ping` mỗi 15 giây.
4. Client ngắt kết nối (`request.is_disconnected()` hoặc `CancelledError`) → gỡ hàng đợi khỏi `StatusHub` trong ≤ 1 giây.

## Tiêu chí hoàn thành

- [ ] Đổi trạng thái ở worker (tiến trình khác) xuất hiện ở client SSE trong ≤ 2 giây.
- [ ] Người chưa xác thực nhận 401 và không mở luồng.
- [ ] Sau khi client ngắt, số hàng đợi trong `StatusHub` giảm về như trước trong ≤ 1 giây.
- [ ] Khung dữ liệu là JSON một dòng đúng 4 khóa `docId`, `status`, `failureReason`, `pageCount`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_status_event_delivered` | Mở luồng SSE; ở phiên CSDL khác gọi `publish_status(d, READY, page_count=3)` rồi `commit` | Trong ≤ 2 giây nhận `event: status` với `{"docId":"d","status":"READY","failureReason":null,"pageCount":3}` |
| `test_no_notify_without_commit` | `publish_status` rồi `rollback` | Không nhận khung nào trong 2 giây |
| `test_events_require_auth` | Mở luồng không cookie | 401 JSON, không phải `text/event-stream` |
| `test_disconnect_cleanup` | Mở rồi đóng luồng | `len(hub.subscribers)` về 0 trong ≤ 1 giây |
| `test_ping` | Mở luồng với chu kỳ ping 0,1 giây (cấu hình test) | Nhận dòng `: ping` |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_document_events.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Cập nhật huy hiệu và hỏi lại mỗi 3 giây ở giao diện (T-509).
- Tắt bộ đệm SSE ở máy chủ web (T-602).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
