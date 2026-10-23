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
| Phụ thuộc | [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md), [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-523](T-523-tai-len-2-2-hang-doi-tien-do-va-thu-lai-tung-tep.md) |
| Mở khóa | [T-518](T-518-hop-thoai-tom-tat-tai-lieu.md) |

## Mục tiêu

Xác nhận xóa tài liệu và cảnh báo tệp trùng; chỉ hiện nút Xóa với người được phép.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-05
- CONTRACTS mục 10.2 (nút Xóa), 10.4 (`delete.*`, `duplicate.title`)
- `docs/04-design/UI_UX_design/library.html` (menu ⋯ và hai hộp thoại)
- Blueprint 4.5 (chép ở bước 2, 3)
- API thật do T-203, T-614 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) Thành phần dùng chung: thông báo, hộp thoại, khung xương, huy hiệu: `useToast`, `useBanner`, `ConfirmDialog.vue`, `StatusBadge.vue`
- [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04): `useDocumentsStore`, `truncateMiddle`, `formatDateTime`, `DocumentTable.vue`
- [T-523](T-523-tai-len-2-2-hang-doi-tien-do-va-thu-lai-tung-tep.md) Tải lên (2/2): hàng đợi, tiến độ và thử lại từng tệp: `UploadItem`, `useUpload`

## File cần tạo hoặc sửa

- `frontend/src/components/RowMenu.vue`
- `frontend/src/components/DuplicateDialog.vue`
- `frontend/src/views/LibraryView.vue`
- `frontend/src/__tests__/row_actions.spec.ts`

## Chữ ký và giao diện

```typescript
// RowMenu.vue
defineProps<{ doc: DocumentOut }>()
defineEmits<{ deleted: [docId: string] }>()
// DuplicateDialog.vue
defineProps<{ file: File; existing: DocumentOut }>()
defineEmits<{ cancel: []; proceed: [] }>()
```

## Các bước

1. `RowMenu` (nút "⋯" có `aria-label="Thao tác với {tên}"`, menu `role="menu"`): mục "Xóa" chỉ khi `doc.canDelete`; có slot cho mục khác (T-518 thêm "Tóm tắt").
2. Xóa: `ConfirmDialog destructive` tiêu đề `delete.title`, nội dung `delete.body` với tên tệp, nút "Hủy" và "Xóa tài liệu". Xác nhận → API-05; `alreadyDeleted=true` → toast `delete.already`; cả hai trường hợp `documentsStore.remove(docId)`; lỗi → toast thông báo của mã.
3. Tệp trùng (EC-10), khi cờ `duplicateCheck` bật: trước khi `enqueue`, với mỗi tệp tìm trong `documentsStore.items` tài liệu cùng `name` và `sizeBytes`; có → `DuplicateDialog` ("{tên}" ({cỡ} MB) trùng tên và kích thước với tài liệu đã tải {ngày}.) với [Hủy] (bỏ tệp đó) và [Vẫn tải lên].
4. Nút Xóa trên dòng `FAILED` hiện trực tiếp (biểu tượng 🗑 có nhãn) theo wireframe.

## Tiêu chí hoàn thành

- [ ] Người dùng không có `canDelete` không thấy mục Xóa (AC-007).
- [ ] Hủy trong hộp thoại xóa không gọi API.
- [ ] Xóa lặp hiện "Tài liệu đã được xóa trước đó." và dòng biến mất (EC-18).
- [ ] Tệp trùng hiện hộp thoại; cả hai lựa chọn hoạt động đúng.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `delete_button_visibility` | Dòng `canDelete=false`; dòng `canDelete=true` | Menu dòng 1 không có "Xóa"; dòng 2 có |
| `cancel_keeps_document` | Mở hộp thoại xóa, bấm "Hủy" | Không gọi `request`; dòng còn |
| `confirm_deletes` | Bấm "Xóa tài liệu"; API giả trả `alreadyDeleted=false` | `DELETE /api/v1/documents/{id}`; dòng biến mất |
| `already_deleted_toast` | API trả `alreadyDeleted=true` | Toast "Tài liệu đã được xóa trước đó."; dòng biến mất |
| `duplicate_dialog_choices` | Kho có "HD.pdf" 4.404.019 byte; thả tệp cùng tên và cỡ | Hiện hộp thoại; [Hủy] → `enqueue` không nhận tệp; [Vẫn tải lên] → `enqueue` nhận tệp |
| `duplicate_flag_off` | Cờ `duplicateCheck` tắt | Không hiện hộp thoại |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/row_actions.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Tóm tắt trong menu (T-518).
- Phát hiện trùng theo nội dung (ngoài MVP).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
