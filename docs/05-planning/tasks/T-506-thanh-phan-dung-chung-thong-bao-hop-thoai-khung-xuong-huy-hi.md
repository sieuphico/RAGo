# T-506 · Thành phần dùng chung: thông báo, hộp thoại, khung xương, huy hiệu

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W1–W2 (xem PLAN mục 6) |
| Story | US-012 |
| BR | — |
| NFR, EC, cổng | UX-03, UX-08, NFR-007 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-502](T-502-token-thiet-ke-khung-ung-dung-dieu-huong-theo-vai-tro.md) |
| Mở khóa | [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-510](T-510-hop-thoai-xoa-va-tep-trung-thao-tac-theo-vai-tro.md), [T-511](T-511-trang-hoi-dap-bo-cuc-va-o-nhap-s-03.md), [T-519](T-519-trang-quan-tri-nguoi-dung-s-07-va-nhat-ky-s-08.md), [T-520](T-520-trang-so-lieu-s-09.md) |

## Mục tiêu

Bộ thành phần giao diện có thể truy cập: toast, dải thông báo, hộp thoại, khung xương, huy hiệu trạng thái.

## File cần tạo hoặc sửa

- `frontend/src/components/ToastHost.vue`
- `frontend/src/components/BannerHost.vue`
- `frontend/src/components/ConfirmDialog.vue`
- `frontend/src/components/SkeletonRows.vue`
- `frontend/src/components/StatusBadge.vue`
- `frontend/src/__tests__/components.spec.ts`

## Các bước

1. Chuyển các mẫu từ `docs/04-design/UI_UX_design/assets/app.js` và `app.css` sang thành phần Vue.
2. Toast: `role="status"`, tự ẩn sau 4 giây, lỗi giữ đến khi đóng. Dải thông báo `role="alert"`.
3. Hộp thoại dùng `<dialog>`: giam focus, `Esc` đóng, trả focus; hộp thoại phá hủy mặc định focus vào "Hủy".
4. `StatusBadge`: 6 trạng thái tài liệu, luôn có chữ và biểu tượng, không chỉ màu (Blueprint 3.5.1).

## Tiêu chí hoàn thành

- [ ] Hộp thoại xóa mặc định focus ở "Hủy" và trả focus khi đóng.
- [ ] Huy hiệu có chữ và biểu tượng cho mọi trạng thái.
- [ ] Toast lỗi không tự ẩn.

## Kiểm thử cần viết

- `dialog_focus_default_cancel`
- `badge_has_text_and_icon`
- `toast_error_persists`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
