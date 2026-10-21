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
| Phụ thuộc | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) |
| Mở khóa | [T-520](T-520-trang-so-lieu-s-09.md) |

## Mục tiêu

Tổng hợp WAU, số câu hỏi, p50/p90 phản hồi, tỷ lệ 👍 và tỷ lệ "không tìm thấy" theo tuần từ telemetry.

## File cần tạo hoặc sửa

- `backend/app/modules/metrics/service.py`
- `backend/app/api/metrics.py`
- `backend/tests/integration/test_metrics.py`

## Các bước

1. `weekly(session, week_start) -> WeeklyMetrics` gồm `wau_percent`, `wau_count`, `questions`, `latency_p50`, `latency_p90`, `thumbs_up_percent`, `not_found_percent`.
2. `GET /api/v1/metrics/weekly?week=` chỉ ADMIN và SPONSOR; trả danh sách các tuần có dữ liệu để chọn tuần.
3. Dữ liệu cập nhật tối thiểu mỗi 24 giờ (tính khi gọi hoặc bằng tác vụ định kỳ); không có văn bản câu hỏi hay câu trả lời.

## Tiêu chí hoàn thành

- [ ] Có đủ các chỉ số của AC-024.
- [ ] Không chứa nội dung câu hỏi hay câu trả lời.
- [ ] Vai trò khác nhận 403.

## Kiểm thử cần viết

- `test_weekly_aggregation`
- `test_metrics_roles`
- `test_metrics_no_content`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
