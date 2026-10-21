# T-519 · Trang quản trị: người dùng (S-07) và nhật ký (S-08)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-061, US-063 |
| BR | BR-016, BR-018 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-110](T-110-api-quan-ly-allow-list-api-14.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) |
| Mở khóa | — |

## Mục tiêu

Bảng allow-list với thêm và gỡ; bảng nhật ký 4 trường; cả hai đủ 5 trạng thái.

## File cần tạo hoặc sửa

- `frontend/src/views/AdminUsersView.vue`
- `frontend/src/views/AdminAuditView.vue`
- `frontend/src/__tests__/admin.spec.ts`

## Các bước

1. Dựng theo prototype `docs/04-design/UI_UX_design/users.html` và `audit.html`.
2. Thêm người dùng: kiểm tra email và vai trò, báo trùng và vượt 20 người; gỡ có xác nhận.
3. Nhật ký hiển thị người thực hiện, thao tác, tài liệu, thời điểm.
4. Chỉ ADMIN vào được; vai trò khác chuyển S-02.

## Tiêu chí hoàn thành

- [ ] Thêm email X thì X vào được trong ≤ 1 phút (US-061).
- [ ] Bảng nhật ký có đủ 4 trường (AC-018).
- [ ] Email sai báo lỗi tại ô nhập.

## Kiểm thử cần viết

- `add_user_validation`
- `audit_table_columns`
- `admin_only_route`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
