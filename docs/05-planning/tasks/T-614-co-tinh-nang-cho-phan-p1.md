# T-614 · Cờ tính năng cho phần P1

| Thuộc tính | Giá trị |
|---|---|
| Pha | 4 Tính năng P1 phía máy chủ |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | DD-08 |
| Phụ thuộc | [T-002](T-002-nap-cau-hinh-va-bi-mat.md) |
| Mở khóa | — |

## Mục tiêu

Bật tắt từng tính năng P1 mà không phá luồng P0 (DD-08, RSK-005).

## File cần tạo hoặc sửa

- `backend/app/core/features.py`
- `backend/app/api/features.py`
- `backend/tests/unit/test_features.py`

## Các bước

1. `Settings.features` gồm: `suggestions`, `summary`, `history`, `rating`, `copy`, `scope`, `followup`, `audit_ui`.
2. `GET /api/v1/features` trả cờ cho giao diện.
3. Router của tính năng tắt trả 404; worker bỏ qua tác vụ của tính năng tắt.

## Tiêu chí hoàn thành

- [ ] Tắt một cờ ẩn route tương ứng và không ảnh hưởng luồng P0.
- [ ] Giao diện đọc được cờ.
- [ ] Cờ cấu hình bằng biến môi trường.

## Kiểm thử cần viết

- `test_disabled_feature_404`
- `test_features_endpoint`

## Lưu ý

Thứ tự cắt khi trễ theo BRD: BR-020 (gợi ý) → BR-019 (tóm tắt) → BR-021 (lịch sử) → BR-022 (sao chép).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
