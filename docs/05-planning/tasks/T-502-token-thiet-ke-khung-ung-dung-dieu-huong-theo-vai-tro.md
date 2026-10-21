# T-502 · Token thiết kế, khung ứng dụng, điều hướng theo vai trò

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | US-001 |
| BR | BR-033 |
| NFR, EC, cổng | UX-06, UX-09, NFR-007 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md) |
| Mở khóa | [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md), [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) |

## Mục tiêu

Chuyển token và bố cục của prototype sang Vue; thanh điều hướng thay đổi theo vai trò.

## File cần tạo hoặc sửa

- `frontend/src/styles/tokens.css`
- `frontend/src/styles/base.css`
- `frontend/src/components/AppHeader.vue`
- `frontend/src/router/index.ts`
- `frontend/src/__tests__/header.spec.ts`

## Các bước

1. Sao chép token từ `docs/04-design/UI_UX_design/assets/tokens.css` (nguồn: Blueprint 3.6).
2. Viết `AppHeader.vue`: Hỏi đáp, Kho tài liệu, Số liệu (QT, NTT), Quản trị (QT) theo bảng vai trò Blueprint 3.2.2.
3. Cấu hình router cho S-01 … S-09 (đường dẫn theo Blueprint 3.2.3).
4. Thêm liên kết "Bỏ qua tới nội dung chính".

## Tiêu chí hoàn thành

- [ ] Mỗi vai trò chỉ thấy các mục điều hướng được phép (test cho 4 vai trò).
- [ ] Tất cả màu, cỡ chữ lấy từ token.
- [ ] Điều hướng tới mọi màn hình chính ≤ 1 lần bấm (UX-09).

## Kiểm thử cần viết

- `header_shows_items_per_role`
- `router_has_all_routes`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
