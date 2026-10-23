# T-313 · Đánh giá 👍/👎 (API-11)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 3 giờ `[Đề xuất]` |
| Tuần dự kiến | W8–W9 (xem PLAN mục 6) |
| Story | US-050 |
| BR | BR-023 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-105](T-105-repository-hoi-thoai.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-614](T-614-co-tinh-nang-cho-phan-p1.md) |
| Mở khóa | — |

## Mục tiêu

Ghi đánh giá cho một câu trả lời kèm lý do tùy chọn.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-11
- CONTRACTS mục 6 (`answer_rated`)
- CONTRACTS mục 3 (`MESSAGE_NOT_RATEABLE`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-105](T-105-repository-hoi-thoai.md) Repository hội thoại: `create_session`, `set_title_if_empty`, `get_session`, `list_sessions`, `add_message`, `update_message` …
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) Telemetry: lược đồ sự kiện và API-16: `anon_id`, `emit`, `EVENTS`, `CLIENT_EVENTS`
- [T-614](T-614-co-tinh-nang-cho-phan-p1.md) Cờ tính năng cho phần P1: `is_enabled`, `require_feature`, `ALL_P1`

## File cần tạo hoặc sửa

- `backend/app/api/rating.py`
- `backend/tests/integration/test_rating.py`

## Chữ ký và giao diện

```python
@router.post("/api/v1/chat/messages/{message_id}/rating", status_code=204)
async def rate_api(message_id: UUID, body: RatingIn, user: CurrentUser = Depends(...)) -> None: ...
```

## Các bước

1. `POST /api/v1/chat/messages/{mid}/rating`, thân `{value: "UP"|"DOWN", reasonCode: null|"WRONG_INFO"|"WRONG_CITATION"|"MISSING_INFO"|"OTHER"}`; `require_feature("rating")`.
2. `get_message_for_user` không có → 404 `NOT_FOUND`; tin nhắn không phải `assistant` hoặc trạng thái khác `COMPLETED`/`NOT_FOUND` → 409 `MESSAGE_NOT_RATEABLE`; `UP` kèm `reasonCode` → 422.
3. Ghi đè bằng `INSERT ... ON CONFLICT (message_id) DO UPDATE`; trả 204.
4. Phát `answer_rated {question_id: mid, rating: "up"|"down", reason_code}`.

## Tiêu chí hoàn thành

- [ ] Đánh giá được lưu và xuất hiện trong số liệu tuần (AC-023).
- [ ] Người không phải chủ phiên nhận 404.
- [ ] Lý do lạ bị từ chối; gửi lại ghi đè.
- [ ] Không đánh giá được tin nhắn đang `STREAMING`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_rate_up` | Tin nhắn `COMPLETED` của lan@; POST `{"value":"UP","reasonCode":null}` | 204; bảng `rating` có `UP`; có sự kiện `answer_rated` `rating="up"` |
| `test_rate_down_with_reason` | POST `{"value":"DOWN","reasonCode":"WRONG_CITATION"}` | 204; `reason_code=WRONG_CITATION` |
| `test_rate_overwrite` | POST UP rồi DOWN | Còn 1 dòng, `value=DOWN` |
| `test_rate_other_user_forbidden` | minh@ đánh giá tin nhắn của lan@ | 404 `NOT_FOUND` |
| `test_rate_streaming_rejected` | Tin nhắn `STREAMING` | 409 `MESSAGE_NOT_RATEABLE` |
| `test_bad_reason` | `reasonCode="ABC"`; `value=UP` kèm `reasonCode` | 422; 422 |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_rating.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Nút 👍/👎 và hộp thoại lý do (T-517).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
