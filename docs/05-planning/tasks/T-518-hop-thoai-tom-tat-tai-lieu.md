# T-518 · Hộp thoại tóm tắt tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 3 giờ `[Đề xuất]` |
| Tuần dự kiến | W10 (xem PLAN mục 6) |
| Story | US-040 |
| BR | BR-019 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-403](T-403-tom-tat-tai-lieu-api-12.md), [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) |
| Mở khóa | — |

## Mục tiêu

Thao tác "Tóm tắt" ở menu dòng của kho tài liệu, hiển thị bản tóm tắt có trích dẫn.

## File cần tạo hoặc sửa

- `frontend/src/components/SummaryDialog.vue`
- `frontend/src/__tests__/summary.spec.ts`

## Các bước

1. Mục "Tóm tắt" chỉ có với tài liệu `Sẵn sàng`; gọi API-12.
2. Hiển thị "Tóm tắt do AI tạo cho {tên tài liệu}", trạng thái đang tạo và lỗi; thẻ trích dẫn bấm được.
3. Ẩn khi cờ tính năng `summary` tắt.

## Tiêu chí hoàn thành

- [ ] Chỉ tài liệu sẵn sàng có mục Tóm tắt.
- [ ] Bản tóm tắt có thẻ trích dẫn số trang.
- [ ] Cờ tắt thì mục biến mất.

## Kiểm thử cần viết

- `summary_only_for_ready`
- `hidden_when_flag_off`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
