# T-506 · Thành phần dùng chung: thông báo, hộp thoại, khung xương, huy hiệu

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-012 |
| BR | — |
| NFR, EC, cổng | UX-03, UX-08, NFR-007 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-502](T-502-token-thiet-ke-khung-ung-dung-dieu-huong-theo-vai-tro.md) |
| Mở khóa | [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-510](T-510-hop-thoai-xoa-va-tep-trung-thao-tac-theo-vai-tro.md), [T-511](T-511-hoi-dap-1-3-bo-cuc-trang-va-thanh-ben.md), [T-519](T-519-trang-quan-tri-nguoi-dung-s-07-va-nhat-ky-s-08.md), [T-520](T-520-trang-so-lieu-s-09.md) |

## Mục tiêu

Bộ thành phần giao diện có thể truy cập: toast, dải thông báo, hộp thoại, khung xương, huy hiệu trạng thái.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 10.3 (nhãn và biểu tượng trạng thái)
- `docs/04-design/UI_UX_design/assets/app.js`, `app.css` (mẫu toast, dải, hộp thoại)
- Blueprint 3.8.2 (chép ở bước 3)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-502](T-502-token-thiet-ke-khung-ung-dung-dieu-huong-theo-vai-tro.md) Token thiết kế, khung ứng dụng, điều hướng theo vai trò: `NavItem`, `navItems`

## File cần tạo hoặc sửa

- `frontend/src/components/ToastHost.vue`
- `frontend/src/components/BannerHost.vue`
- `frontend/src/components/ConfirmDialog.vue`
- `frontend/src/components/SkeletonRows.vue`
- `frontend/src/components/StatusBadge.vue`
- `frontend/src/__tests__/components.spec.ts`

## Chữ ký và giao diện

```typescript
// ConfirmDialog.vue
defineProps<{ open: boolean; title: string; confirmLabel: string; destructive?: boolean }>()
defineEmits<{ confirm: []; cancel: [] }>()
// StatusBadge.vue
defineProps<{ status: DocumentStatus | ClientUploadState; progress?: number; failureReason?: FailureReason | null }>()
export function useToast(): { show(text: string, kind?: "info" | "success" | "error"): void }
export function useBanner(): { show(text: string): void; hide(): void }
```

## Các bước

1. Chuyển các mẫu từ `docs/04-design/UI_UX_design/assets/app.js` và `app.css` sang thành phần Vue; giữ tên lớp CSS khi có thể.
2. `ToastHost` + `useToast()`: `show(text, kind)`; `role="status"`; loại `info`/`success` tự ẩn sau 4 giây; `error` giữ tới khi bấm đóng. `BannerHost` + `useBanner()`: một dải đầu trang `role="alert"`.
3. `ConfirmDialog` dùng `<dialog>` + `showModal()`: `aria-modal="true"`, tiêu đề nối `aria-labelledby`; giam focus; `Esc` đóng; khi đóng trả focus về phần tử đã mở; prop `destructive` → focus mặc định vào "Hủy", nút phá hủy bên phải.
4. `SkeletonRows` prop `rows`, `aria-busy="true"`, tôn trọng `prefers-reduced-motion`.
5. `StatusBadge` prop `status: DocumentStatus | ClientUploadState`, `progress?`, `failureReason?`: nhãn, biểu tượng, tông đúng CONTRACTS mục 10.3; luôn có chữ (không chỉ màu).

## Tiêu chí hoàn thành

- [ ] Hộp thoại phá hủy mặc định focus ở "Hủy" và trả focus khi đóng.
- [ ] Huy hiệu có chữ và biểu tượng cho đủ 8 giá trị trạng thái.
- [ ] Toast lỗi không tự ẩn; toast thường ẩn sau 4 giây.
- [ ] `Esc` đóng hộp thoại.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `dialog_focus_default_cancel` | Mở `ConfirmDialog destructive` từ một nút | `document.activeElement` là nút "Hủy"; đóng xong focus về nút đã mở |
| `dialog_esc_closes` | Mở hộp thoại, gửi phím `Escape` | Emit `cancel`; hộp thoại đóng |
| `badge_has_text_and_icon` | Mount `StatusBadge` với từng giá trị trong 8 trạng thái | Mỗi lần có văn bản đúng CONTRACTS mục 10.3 và một phần tử biểu tượng `aria-hidden="true"` |
| `badge_failed_reason` | `status=FAILED`, `failureReason=OCR_UNREADABLE` | "Thất bại – Không đọc được nội dung." |
| `toast_error_persists` | `show("x", "error")`, tiến đồng hồ giả 10 giây | Toast còn hiển thị; toast `info` biến mất sau 4 giây |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/components.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Nội dung cụ thể của từng hộp thoại (T-510, T-517, T-518, T-519).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
