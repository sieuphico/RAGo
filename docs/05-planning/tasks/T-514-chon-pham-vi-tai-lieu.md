# T-514 · Chọn phạm vi tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-026 |
| BR | BR-015 |
| NFR, EC, cổng | EC-15 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-311](T-311-pham-vi-tai-lieu-trong-api-08-va-ec-15.md), [T-511](T-511-trang-hoi-dap-bo-cuc-va-o-nhap-s-03.md) |
| Mở khóa | — |

## Mục tiêu

Danh sách chọn một hay nhiều tài liệu để giới hạn câu hỏi.

## File cần tạo hoặc sửa

- `frontend/src/components/ScopePicker.vue`
- `frontend/src/__tests__/scope_picker.spec.ts`

## Các bước

1. Chỉ liệt kê tài liệu `Sẵn sàng`; nhãn "Phạm vi: Tất cả tài liệu" hoặc "Đang hỏi trong N tài liệu".
2. Gửi `scopeDocIds` theo API-08; hiện thông báo khi máy chủ loại tài liệu đã xóa khỏi phạm vi (EC-15).
3. Điều khiển bằng bàn phím; `Esc` đóng.

## Tiêu chí hoàn thành

- [ ] Chọn tài liệu A thì câu hỏi gửi kèm đúng `scopeDocIds`.
- [ ] Chọn tất cả quay về "Tất cả tài liệu".
- [ ] Thông báo EC-15 hiển thị đúng.

## Kiểm thử cần viết

- `sends_selected_scope`
- `removed_doc_notice`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
