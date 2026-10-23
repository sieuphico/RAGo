# T-502 · Token thiết kế, khung ứng dụng, điều hướng theo vai trò

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W1–W2 (xem PLAN mục 6) |
| Story | US-001 |
| BR | BR-033 |
| NFR, EC, cổng | UX-06, UX-09, NFR-007 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md), [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) |
| Mở khóa | [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md), [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) |

## Mục tiêu

Chuyển token và bố cục của prototype sang Vue; thanh điều hướng thay đổi theo vai trò.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 10.2 (đường dẫn, vai trò, mục điều hướng)
- `docs/04-design/UI_UX_design/assets/tokens.css`, `docs/04-design/UI_UX_design/chat.html` (thanh trên cùng)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md) Khung mã nguồn frontend và công cụ: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`
- [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) Client API và bảng ánh xạ mã lỗi: `ApiError`, `request`, `setAuthExpiredHandler`, `messageFor`, `t`

## File cần tạo hoặc sửa

- `frontend/src/styles/tokens.css`
- `frontend/src/styles/base.css`
- `frontend/src/components/AppHeader.vue`
- `frontend/src/router/index.ts`
- `frontend/src/__tests__/header.spec.ts`

## Chữ ký và giao diện

```typescript
export interface NavItem { label: string; to: string }
export function navItems(role: Role | null): NavItem[]
```

## Các bước

1. Chép `docs/04-design/UI_UX_design/assets/tokens.css` thành `src/styles/tokens.css` (không đổi giá trị); `base.css` đặt font hệ thống, cỡ chữ gốc 16 px, vòng focus 2 px `var(--color-primary)` cách 2 px.
2. `src/router/nav.ts`: hàm thuần `navItems(role)` trả mục điều hướng đúng bảng CONTRACTS mục 10.2: BD/TN → Hỏi đáp, Kho tài liệu; QT → Hỏi đáp, Kho tài liệu, Số liệu, Quản trị; NTT → Số liệu; `null` → [].
3. `src/router/index.ts`: route cho mọi đường dẫn ở CONTRACTS mục 10.2 với `meta.roles`; component tạm là trang rỗng có tiêu đề (task màn hình thay sau).
4. `AppHeader.vue`: logo "Chat với tài liệu", các mục từ `navItems(auth.me.role)` dạng `RouterLink` (mục đang mở có `aria-current="page"`), tên người dùng bên phải, nút Đăng xuất.
5. Liên kết "Bỏ qua tới nội dung chính" là phần tử focus đầu tiên, trỏ tới `#main`.

## Tiêu chí hoàn thành

- [ ] Mỗi vai trò chỉ thấy mục điều hướng được phép (4 vai trò).
- [ ] Mọi màu, cỡ chữ trong component lấy từ biến của `tokens.css`.
- [ ] Mọi màn hình chính tới được bằng 1 lần bấm từ thanh trên cùng (UX-09).
- [ ] Có đủ route với `meta.roles` đúng bảng.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `header_shows_items_per_role` | `navItems` với `BD_USER`, `TEAM_LEAD`, `ADMIN`, `SPONSOR` | Lần lượt [Hỏi đáp, Kho tài liệu], như trên, [Hỏi đáp, Kho tài liệu, Số liệu, Quản trị], [Số liệu] |
| `router_has_all_routes` | Liệt kê `router.getRoutes()` | Có `/login`, `/denied`, `/`, `/chat/:sessionId`, `/library`, `/admin/users`, `/admin/audit`, `/metrics` với `meta.roles` đúng |
| `skip_link_first` | Mount `AppHeader`, nhấn Tab một lần | Focus ở "Bỏ qua tới nội dung chính" |
| `no_hardcoded_colors` | Tìm `#[0-9a-fA-F]{3,6}` trong `src/components/*.vue` | Không có kết quả |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/header.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Chặn route theo vai trò (T-505).
- Nội dung từng màn hình (các task màn hình).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
