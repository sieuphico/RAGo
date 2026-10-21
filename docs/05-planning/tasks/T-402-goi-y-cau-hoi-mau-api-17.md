# T-402 · Gợi ý câu hỏi mẫu (API-17)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 4 Tính năng P1 phía máy chủ |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-031, US-030 |
| BR | BR-020, BR-035 |
| NFR, EC, cổng | NFR-009 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-hang-doi.md) |
| Mở khóa | [T-515](T-515-man-hinh-chao-va-goi-y-cau-hoi.md) |

## Mục tiêu

Tạo 3 gợi ý một lần khi tài liệu `READY` và trả ngẫu nhiên 3 gợi ý.

## File cần tạo hoặc sửa

- `backend/app/worker/suggest.py`
- `backend/app/api/suggestions.py`
- `backend/tests/integration/test_suggestions.py`

## Các bước

1. Handler `generate_suggestions(doc_id)`: lấy vài chunk đại diện, nhờ AI đề xuất 3 câu hỏi, lưu vào `suggestion` (DEC-018: tạo một lần, không cần duyệt).
2. `GET /api/v1/suggestions` trả ngẫu nhiên 3 gợi ý từ các tài liệu `READY`; trả rỗng khi chưa có tài liệu sẵn sàng.
3. Xóa gợi ý khi tài liệu bị xóa (T-213).

## Tiêu chí hoàn thành

- [ ] Kho có tài liệu sẵn sàng thì có ≥ 3 gợi ý (AC-020).
- [ ] Kho trống hoặc chưa có tài liệu sẵn sàng trả rỗng.
- [ ] Chi phí AI chỉ phát sinh một lần cho mỗi tài liệu.

## Kiểm thử cần viết

- `test_three_suggestions`
- `test_empty_when_no_ready`
- `test_generated_once`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
