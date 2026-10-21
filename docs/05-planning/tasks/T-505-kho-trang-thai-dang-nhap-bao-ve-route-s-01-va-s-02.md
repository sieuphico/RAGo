# T-505 · Kho trạng thái đăng nhập, bảo vệ route, S-01 và S-02

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-001, US-002 |
| BR | BR-016 |
| NFR, EC, cổng | EC-16, EC-17, UX-07 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) |
| Mở khóa | [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-511](T-511-trang-hoi-dap-bo-cuc-va-o-nhap-s-03.md), [T-606](T-606-kiem-thu-dau-cuoi-e2e-luong-p0.md) |

## Mục tiêu

Tải `/me`, chuyển hướng đăng nhập khi hết phiên (giữ bản nháp), trang S-01 và S-02.

## File cần tạo hoặc sửa

- `frontend/src/stores/auth.ts`
- `frontend/src/router/guards.ts`
- `frontend/src/views/LoginView.vue`
- `frontend/src/views/DeniedView.vue`
- `frontend/src/__tests__/auth.spec.ts`

## Các bước

1. `useAuthStore`: `load()` gọi API-01; trạng thái `unauthenticated | denied | allowed(role)`.
2. Guard: chưa đăng nhập → S-01; đã xác thực nhưng `allowed=false` → S-02; vai trò không phù hợp → S-02.
3. `AUTH_EXPIRED` giữ bản nháp trong `sessionStorage`, chuyển tới đăng nhập, quay lại đúng màn hình (US-001).
4. S-01 và S-02 theo prototype `docs/04-design/UI_UX_design/login.html`, `denied.html`; S-02 không hiển thị tên tài liệu.

## Tiêu chí hoàn thành

- [ ] Hết phiên: bản nháp giữ nguyên và khôi phục sau đăng nhập (EC-16).
- [ ] Người ngoài danh sách thấy "Bạn chưa được cấp quyền. Liên hệ quản trị viên." (US-002).
- [ ] Bị thu hồi quyền thấy "Quyền truy cập của bạn đã bị thu hồi" (EC-17).

## Kiểm thử cần viết

- `guard_redirects_unauthenticated`
- `denied_page_shows_no_documents`
- `draft_survives_reauth`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
