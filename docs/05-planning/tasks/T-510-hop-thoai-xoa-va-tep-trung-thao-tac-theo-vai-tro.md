# T-510 · Hộp thoại xóa và tệp trùng, thao tác theo vai trò

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-016, US-017, US-062 |
| BR | BR-007, BR-001 |
| NFR, EC, cổng | EC-10, EC-18 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-203](T-203-xoa-tai-lieu-api-05.md), [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md), [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) |
| Mở khóa | — |

## Mục tiêu

Xác nhận xóa tài liệu và cảnh báo tệp trùng; chỉ hiện nút Xóa với người được phép.

## File cần tạo hoặc sửa

- `frontend/src/components/RowMenu.vue`
- `frontend/src/components/DuplicateDialog.vue`
- `frontend/src/__tests__/row_actions.spec.ts`

## Các bước

1. Nút Xóa chỉ hiện với người tải lên hoặc quản trị viên.
2. Hộp thoại "Xóa tài liệu?" nêu tên tệp và hậu quả ("Dữ liệu được xóa trong 24 giờ"), nút phá hủy bên phải, mặc định focus "Hủy".
3. Hộp thoại "Tài liệu này có thể đã có trong kho" khi trùng tên và kích thước; [Vẫn tải lên] hoặc [Hủy].
4. Xóa lặp (EC-18) hiện "Tài liệu đã được xóa trước đó" và làm mới danh sách.

## Tiêu chí hoàn thành

- [ ] Người dùng thường không thấy nút Xóa (AC-007).
- [ ] Hủy trong hộp thoại xóa không thay đổi gì.
- [ ] Tệp trùng hiện hộp thoại và cả hai lựa chọn hoạt động.

## Kiểm thử cần viết

- `delete_button_visibility`
- `cancel_keeps_document`
- `duplicate_dialog_choices`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
