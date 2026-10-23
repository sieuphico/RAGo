# T-312 · Số liệu hàng tuần (API-13)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-051 |
| BR | BR-024 |
| NFR, EC, cổng | NFR-001 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) |
| Mở khóa | — |

## Mục tiêu

Tổng hợp WAU, số câu hỏi, p50/p90 phản hồi, tỷ lệ 👍 và tỷ lệ "không tìm thấy" theo tuần từ telemetry.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-13, 4.2 `WeeklyMetricsOut`
- PRD mục 5.2 bảng "Chỉ số theo dõi sau ra mắt" (công thức chép ở bước 2)
- CONTRACTS mục 7 (`timezone`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md) Repository quản trị, nhật ký, telemetry, chi phí AI: `get_by_email`, `list_all`, `add`, `remove`, `count`, `count_by_role` …
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) Telemetry: lược đồ sự kiện và API-16: `anon_id`, `emit`, `EVENTS`, `CLIENT_EVENTS`

## File cần tạo hoặc sửa

- `app/modules/metrics/service.py`
- `app/api/metrics.py`
- `tests/integration/test_metrics.py`

## Chữ ký và giao diện

```python
async def weekly(session: AsyncSession, week_start: date, tz: ZoneInfo) -> WeeklyMetricsOut: ...
```

## Các bước

1. Tuần tính từ thứ Hai 00:00 tới thứ Hai kế tiếp theo `settings.timezone` (mặc định `Asia/Ho_Chi_Minh`).
2. Công thức: `wauCount` = số `anon_user_id` khác nhau có `question_submitted` trong tuần; `allowedCount` = số người trong allow-list trừ SPONSOR; `wauPercent = wauCount / allowedCount × 100`; `questions` = số `question_submitted`; `latencyP50Ms`, `latencyP90Ms` = `percentile_cont(0.5/0.9)` của `answer_completed.latency_ms`; `thumbsUpPercent` = `rating=up` ÷ số `answer_rated`; `notFoundPercent` = `is_not_found=true` ÷ số `answer_completed`. Mẫu số 0 → `null`.
3. `weeks` = các thứ Hai có ≥ 1 sự kiện, mới nhất trước; `series` = 8 tuần gần nhất; `updatedAt` = thời điểm tính.
4. Tính khi gọi API và giữ bộ nhớ đệm 1 giờ theo `week` `[Đề xuất]` (đáp ứng "cập nhật tối thiểu mỗi 24 giờ").
5. `GET /api/v1/metrics/weekly`, `require_roles(ADMIN, SPONSOR)`; `week` không phải thứ Hai → 422.

## Tiêu chí hoàn thành

- [ ] Có đủ 8 chỉ số của AC-024 theo `WeeklyMetricsOut`.
- [ ] Kết quả không có văn bản câu hỏi hay câu trả lời.
- [ ] BD_USER và TEAM_LEAD nhận 403.
- [ ] Tuần không có dữ liệu trả `null` cho tỷ lệ, không lỗi chia cho 0.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_weekly_aggregation` | Tuần 2026-12-21: 18 người được cấp quyền (+1 SPONSOR); 13 người gửi tổng 241 `question_submitted`; 200 `answer_completed` với latency 1..200 × 100 ms, 36 `is_not_found`; 50 `answer_rated`, 38 `up` | `wauCount=13`, `wauPercent≈72.2`, `questions=241`, `latencyP50Ms≈10050`, `latencyP90Ms≈18010`, `notFoundPercent=18.0`, `thumbsUpPercent=76.0` |
| `test_metrics_roles` | BD_USER, TEAM_LEAD, SPONSOR, ADMIN gọi API-13 | 403, 403, 200, 200 |
| `test_metrics_no_content` | Chuỗi JSON trả về | Không chứa giá trị nào từ `props` ngoài số và mã |
| `test_empty_week` | Tuần không có sự kiện | `questions=0`, `thumbsUpPercent=null`, `notFoundPercent=null` |
| `test_week_must_be_monday` | `week=2026-12-22` | 422 `VALIDATION_ERROR` |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_metrics.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Trang S-09 (T-520).
- Chi phí AI theo tuần (đọc từ bảng chi phí của nhà cung cấp, ngoài hệ thống).

## Lưu ý

Thêm khóa `timezone: str = "Asia/Ho_Chi_Minh"` vào `Settings` (CONTRACTS mục 7).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
