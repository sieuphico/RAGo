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
| Phụ thuộc | [T-105](T-105-repository-hoi-thoai.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md), [T-316](T-316-dich-vu-tra-loi-2-2-dung-dut-ket-noi-loi-va-het-gio.md) |
| Mở khóa | [T-311](T-311-pham-vi-tai-lieu-trong-api-08-va-ec-15.md), [T-608](T-608-thu-tai-g4.md), [T-609](T-609-kiem-tra-bao-mat-g6.md), [T-615](T-615-kiem-thu-dau-cuoi-2-2-hoi-dap-xem-nguon-cac-trang-thai.md) |

## Mục tiêu

Mở các API hội thoại: tạo phiên, gửi câu hỏi nhận luồng SSE, dừng câu trả lời.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-07, API-08, API-09
- CONTRACTS mục 5.2 (khung SSE)
- CONTRACTS mục 3 (`QUESTION_*`, `SESSION_NOT_FOUND`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-105](T-105-repository-hoi-thoai.md) Repository hội thoại: `create_session`, `set_title_if_empty`, `get_session`, `list_sessions`, `add_message`, `update_message` …
- [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md) Hợp đồng lỗi và bộ xử lý ngoại lệ: `ErrorCode`, `AppError`, `install_error_handlers`, `ERROR_DEFAULTS`
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) Dịch vụ trả lời (1/2): luồng chính có trích dẫn: `AnswerService`, `detect_lang`
- [T-316](T-316-dich-vu-tra-loi-2-2-dung-dut-ket-noi-loi-va-het-gio.md) Dịch vụ trả lời (2/2): dừng, đứt kết nối, lỗi và hết giờ: `RunningAnswers`

## File cần tạo hoặc sửa

- `app/api/chat.py`
- `tests/integration/test_chat_api.py`

## Chữ ký và giao diện

```python
@router.post("/api/v1/chat/sessions", status_code=201)
async def create_session_api(...) -> SessionCreatedOut: ...
@router.post("/api/v1/chat/sessions/{session_id}/messages")
async def ask_api(session_id: UUID, body: AskIn, request: Request, user: CurrentUser = Depends(...)) -> StreamingResponse: ...
@router.post("/api/v1/chat/messages/{message_id}/stop")
async def stop_api(message_id: UUID, user: CurrentUser = Depends(...)) -> StopOut: ...

def to_sse_frame(event: AnswerEvent) -> bytes: ...
```

## Các bước

1. `POST /api/v1/chat/sessions` (API-07): `create_session(user.email)`; 201 `{sessionId, title: null, createdAt}`.
2. `POST /api/v1/chat/sessions/{sid}/messages` (API-08), thân `{text: str, scopeDocIds: list[UUID] = []}` (tối đa 50 phần tử). Kiểm tra theo thứ tự, trả JSON lỗi **trước** khi mở luồng: `text.strip()` rỗng → 400 `QUESTION_EMPTY`; > `max_question_chars` → 400 `QUESTION_TOO_LONG`; phiên không thuộc người gọi → 404 `SESSION_NOT_FOUND`; `has_running_message` → 409 `QUESTION_IN_PROGRESS`.
3. Kiểm tra câu hỏi đang chạy trong giao dịch có `pg_advisory_xact_lock(hashtext(email))` để hai yêu cầu đồng thời không cùng lọt.
4. Trả `StreamingResponse(media_type="text/event-stream")`, tiêu đề `Cache-Control: no-cache`, `X-Accel-Buffering: no`. Mỗi `AnswerEvent` thành một khung `event: <tên>\ndata: <json>\n\n` (`json.dumps(..., ensure_ascii=False, separators=(",", ":"))`, khóa camelCase theo CONTRACTS mục 5.2). Khi chưa có sự kiện mới quá 10 giây, gửi `: ping`.
5. Client ngắt kết nối → đóng trình lặp của `ask` (T-316 lưu `INTERRUPTED`).
6. `POST /api/v1/chat/messages/{mid}/stop` (API-09): `get_message_for_user` không có → 404 `NOT_FOUND`; gọi `running.stop(mid)`; trả 200 `{messageId, status}` với trạng thái hiện tại.

## Tiêu chí hoàn thành

- [ ] Mỗi khung SSE có dạng `event: <tên>\ndata: <JSON một dòng>\n\n` như CONTRACTS mục 5.2; `status` là khung đầu tiên và có đúng một khung kết thúc.
- [ ] Câu hỏi trống hoặc 2.001 ký tự bị từ chối bằng JSON trước khi gọi AI.
- [ ] Người khác gửi vào phiên của người này nhận 404 `SESSION_NOT_FOUND`.
- [ ] Câu hỏi thứ hai khi câu thứ nhất chưa xong nhận 409 `QUESTION_IN_PROGRESS`.
- [ ] API-09 dừng câu trả lời đang chạy và trả `STOPPED`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_create_session` | BD_USER POST API-07 | 201; `title` là `null` |
| `test_sse_event_order` | Phiên của lan@, tài liệu `READY`, `AiFake`; POST API-08 | `Content-Type: text/event-stream`; khung đầu `event: status`; khung cuối `event: done`; mọi `data` là JSON hợp lệ một dòng |
| `test_question_validation` | `text="   "`; `text="a" * 2001` | 400 `QUESTION_EMPTY`; 400 `QUESTION_TOO_LONG`; gateway giả không được gọi |
| `test_session_ownership` | minh@ POST vào phiên của lan@ | 404 `SESSION_NOT_FOUND` |
| `test_question_in_progress` | lan@ gửi câu 1 (`AiFake(delay_s=2)`), gửi câu 2 trong lúc câu 1 chạy | Câu 2 nhận 409 `QUESTION_IN_PROGRESS`, `retryable: true` |
| `test_stop_endpoint` | Đang chạy câu trả lời `mid`; POST API-09 | 200 `{"messageId": mid, "status": "STOPPED"}` (chờ tối đa 1 giây); luồng kết thúc bằng `done` có `stopped: true` |
| `test_stop_other_user_404` | minh@ POST API-09 với `mid` của lan@ | 404 `NOT_FOUND` |
| `test_csrf_on_stream` | POST API-08 không có `X-Requested-With` | 403 `CSRF_REJECTED` |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_chat_api.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Lịch sử và mở lại phiên (T-401).
- Phạm vi tài liệu: loại tài liệu đã xóa (T-311).
- Client đọc luồng (T-504).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
