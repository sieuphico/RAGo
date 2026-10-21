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
| Phụ thuộc | [T-105](T-105-repository-hoi-thoai.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) |
| Mở khóa | [T-517](T-517-thao-tac-tren-cau-tra-loi-sao-chep-va-danh-gia.md) |

## Mục tiêu

Ghi đánh giá cho một câu trả lời kèm lý do tùy chọn.

## File cần tạo hoặc sửa

- `backend/app/api/rating.py`
- `backend/tests/integration/test_rating.py`

## Các bước

1. `POST /api/v1/chat/messages/{mid}/rating` body `{value: UP|DOWN, reasonCode?}`.
2. Chỉ chủ phiên đánh giá; gửi lại thì ghi đè.
3. Ghi sự kiện `answer_rated` (chỉ mã lý do, không văn bản).

## Tiêu chí hoàn thành

- [ ] Đánh giá xuất hiện trong số liệu (AC-023).
- [ ] Người không phải chủ phiên bị từ chối.
- [ ] Lý do chỉ nhận mã có trong danh sách.

## Kiểm thử cần viết

- `test_rate_up`
- `test_rate_down_with_reason`
- `test_rate_other_user_forbidden`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
