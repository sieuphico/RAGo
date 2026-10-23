# T-505 · Kho trạng thái đăng nhập, bảo vệ route, S-01 và S-02

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-001, US-002 |
| BR | BR-016 |
| NFR, EC, cổng | EC-16, EC-17, UX-07 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md), [T-502](T-502-token-thiet-ke-khung-ung-dung-dieu-huong-theo-vai-tro.md) |
| Mở khóa | [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-511](T-511-hoi-dap-1-3-bo-cuc-trang-va-thanh-ben.md), [T-519](T-519-trang-quan-tri-nguoi-dung-s-07-va-nhat-ky-s-08.md), [T-520](T-520-trang-so-lieu-s-09.md), [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) |

## Mục tiêu

Tải `/me`, chuyển hướng đăng nhập khi hết phiên (giữ bản nháp), trang S-01 và S-02.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.0, 4.1 API-01
- CONTRACTS mục 10.2, 10.4 (`login.*`, `denied.*`), 10.5 (`useAuthStore`, `useFeaturesStore`)
- Blueprint 3.5.3 (trạng thái phiên): hết hạn giữ màn hình và bản nháp; thu hồi → S-02
- API thật do T-108, T-614 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) Client API và bảng ánh xạ mã lỗi: `ApiError`, `request`, `setAuthExpiredHandler`, `messageFor`, `t`
- [T-502](T-502-token-thiet-ke-khung-ung-dung-dieu-huong-theo-vai-tro.md) Token thiết kế, khung ứng dụng, điều hướng theo vai trò: `NavItem`, `navItems`

## File cần tạo hoặc sửa

- `frontend/src/stores/auth.ts`
- `frontend/src/stores/features.ts`
- `frontend/src/router/guards.ts`
- `frontend/src/views/LoginView.vue`
- `frontend/src/views/DeniedView.vue`
- `frontend/src/__tests__/auth.spec.ts`

## Chữ ký và giao diện

```typescript
export const useAuthStore = defineStore("auth", () => { /* status, me */ return { load(): Promise<void>, login(next: string): void, logout(): Promise<void> } })
export function installGuards(router: Router): void
```

## Các bước

1. `useAuthStore.load()`: gọi API-01; 401 → `unauthenticated`; `allowed=false` → `denied`; ngược lại `allowed` + `me`.
2. `login(next)` chuyển trình duyệt tới `/auth/login?next=<next>`; `logout()` POST `/auth/logout` rồi về `/login`.
3. `setAuthExpiredHandler`: lưu `router.currentRoute.fullPath` vào `sessionStorage["cwd_return_to"]`, đặt `unauthenticated`, chuyển `/login?expired=1`. Bản nháp do T-524 giữ trong `sessionStorage`.
4. Nhận `AUTH_FORBIDDEN` khi đang `allowed` → `revoked`, chuyển `/denied`.
5. Guard `beforeEach`: chưa `load` thì `await load()`; `unauthenticated` → `/login` (trừ khi đang ở `/login`); `denied`/`revoked` → `/denied`; vai trò không có trong `meta.roles` → `/denied`; SPONSOR vào `/` → `/metrics`.
6. `LoginView` theo `docs/04-design/UI_UX_design/login.html`: nút `login.button` gọi `login(return_to ?? "/")`; có `?expired=1` thì hiện `login.expired`. `DeniedView` theo `denied.html`: `denied.title` hoặc `denied.revoked`, nút Đăng xuất; không hiện tên tài liệu nào.
7. `useFeaturesStore.load()` gọi `GET /api/v1/features` sau khi `allowed`.

## Tiêu chí hoàn thành

- [ ] Hết phiên: chuyển tới đăng nhập, sau đăng nhập về đúng đường dẫn cũ; bản nháp còn nguyên (EC-16).
- [ ] Người ngoài danh sách thấy "Bạn chưa được cấp quyền. Liên hệ quản trị viên." (US-002).
- [ ] Bị thu hồi quyền thấy "Quyền truy cập của bạn đã bị thu hồi." (EC-17).
- [ ] BD_USER vào `/admin/users` bị chuyển `/denied`.
- [ ] S-02 không gọi API danh sách tài liệu.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `guard_redirects_unauthenticated` | API-01 giả trả 401; điều hướng tới `/library` | Kết thúc ở `/login` |
| `guard_role_denied` | `me.role = BD_USER`; điều hướng `/admin/users` | Kết thúc ở `/denied` |
| `sponsor_home_is_metrics` | `me.role = SPONSOR`; điều hướng `/` | Kết thúc ở `/metrics` |
| `denied_page_shows_no_documents` | `allowed=false`; mount `DeniedView` | Có "Bạn chưa được cấp quyền"; `request` giả không được gọi với `/api/v1/documents` |
| `revoked_message` | Đang `allowed`, một yêu cầu trả 403 `AUTH_FORBIDDEN` | Ở `/denied` với "Quyền truy cập của bạn đã bị thu hồi." |
| `draft_survives_reauth` | Ở `/chat/abc`, `sessionStorage.cwd_draft = "câu hỏi dở"`; một yêu cầu trả 401 | `cwd_return_to = "/chat/abc"`; `/login?expired=1` hiện `login.expired`; `cwd_draft` còn nguyên |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/auth.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Màn hình đăng nhập SSO thật (do IdP hiển thị).
- Giữ bản nháp câu hỏi (T-524).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
