# T-316 · Dịch vụ trả lời (2/2): dừng, đứt kết nối, lỗi và hết giờ

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | US-027, US-020 |
| BR | BR-013 |
| NFR, EC, cổng | EC-04, EC-06, EC-07 |
| Quyết định kiến trúc | AD-02, AD-04 |
| Phụ thuộc | [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) |
| Mở khóa | [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-g3.md) |

## Mục tiêu

Bổ sung cho `AnswerService.ask` các nhánh dừng theo yêu cầu, đứt kết nối, lỗi AI và quá thời gian; luôn giữ phần đã sinh.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`DoneEvent.stopped`, `ErrorEvent`)
- CONTRACTS mục 5.2
- CONTRACTS mục 6 (`question_failed`, `answer_stopped`)
- CONTRACTS mục 3 (`TIMEOUT`, `AI_UNAVAILABLE`, `BUDGET_EXCEEDED`, `INTERNAL`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) Dịch vụ trả lời (1/2): luồng chính có trích dẫn: `AnswerService`, `detect_lang`

## File cần tạo hoặc sửa

- `app/modules/answer/running.py`
- `app/modules/answer/service.py`
- `tests/integration/test_answer_interrupts.py`

## Chữ ký và giao diện

```python
class RunningAnswers:
    def start(self, message_id: UUID) -> asyncio.Event: ...
    def stop(self, message_id: UUID) -> bool: ...
    def finish(self, message_id: UUID) -> None: ...
```

## Các bước

1. `RunningAnswers` (một thể hiện trong tiến trình API): `start(message_id) -> asyncio.Event`, `stop(message_id) -> bool`, `finish(message_id)`.
2. Trong vòng đọc token, chờ đồng thời token kế tiếp và sự kiện dừng (`asyncio.wait(..., return_when=FIRST_COMPLETED)`) để dừng trong ≤ 1 giây kể cả khi AI đang im.
3. Dừng theo yêu cầu: `aclose()` luồng AI, lưu phần đã có, trạng thái `STOPPED`, gửi `DoneEvent(..., stopped=True)`, phát `answer_stopped {question_id, elapsed_ms}`.
4. Client đóng kết nối (`GeneratorExit` hoặc `CancelledError` trong `ask`): lưu phần đã có, trạng thái `INTERRUPTED`, phát `question_failed {reason: "network"}`; ghi CSDL bằng phiên mới, bọc `asyncio.shield`.
5. `AppError` `TIMEOUT`, `AI_UNAVAILABLE`, `BUDGET_EXCEEDED` → `ErrorEvent(code, retryable)`, trạng thái `FAILED`, `error_code` lưu mã; phát `question_failed` với `reason` lần lượt `timeout`, `provider_error`, `budget`.
6. Ngoại lệ khác → `ErrorEvent("INTERNAL", False)`, `FAILED`, ghi nhật ký kèm mã yêu cầu (không ghi nội dung).

## Tiêu chí hoàn thành

- [ ] Gọi `stop` khi đang sinh: luồng kết thúc trong ≤ 1 giây, phần đã có được lưu, trạng thái `STOPPED`.
- [ ] Đóng kết nối giữa chừng: tin nhắn lưu `INTERRUPTED` với phần đã có.
- [ ] AI lỗi cho đúng một `ErrorEvent(AI_UNAVAILABLE, true)` và không còn sự kiện nào sau đó.
- [ ] Quá 60 giây cho `ErrorEvent(TIMEOUT, true)`.
- [ ] Sau mọi nhánh, `RunningAnswers` không còn `message_id` đó.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_stop_keeps_partial` | `AiFake(delay_s=0.3)`; sau token thứ 2 gọi `running.stop(mid)` | Trong ≤ 1 giây nhận `done(stopped=True)`; tin nhắn `STOPPED`, văn bản = 2 token đầu; có `answer_stopped` |
| `test_stop_while_ai_silent` | `AiFake(delay_s=5)` (im 5 giây trước token đầu); gọi `stop` sau 0,2 giây | Kết thúc trong ≤ 1 giây |
| `test_disconnect_marks_interrupted` | Đọc 1 token rồi `aclose()` trình lặp của `ask` | Tin nhắn `INTERRUPTED` với 1 token; có `question_failed(reason="network")` |
| `test_ai_error_event` | `AiFake(fail_mode="error")` | Sự kiện cuối là `error{code:"AI_UNAVAILABLE",retryable:true}`; tin nhắn `FAILED`, `error_code="AI_UNAVAILABLE"`; `question_failed(reason="provider_error")` |
| `test_timeout_event` | `AiFake(delay_s=2)`, `ai_timeout_s=1` | `error{code:"TIMEOUT",retryable:true}`; `question_failed(reason="timeout")` |
| `test_budget_event` | `ai_usage` đã vượt ngân sách | `error{code:"BUDGET_EXCEEDED",retryable:false}` |
| `test_registry_cleaned` | Sau mỗi test trên | `running` không còn `mid` |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_answer_interrupts.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đường API-09 và kiểm tra quyền sở hữu tin nhắn (T-308).
- Hiển thị trạng thái ở giao diện (T-525).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
