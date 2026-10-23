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
| Phụ thuộc | [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md), [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) |
| Mở khóa | — |

## Mục tiêu

Danh sách chọn một hay nhiều tài liệu để giới hạn câu hỏi.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-08 (`scopeDocIds`), 5.2 (`scopeRemoved`)
- CONTRACTS mục 10.4 (`scope.*`)
- API thật do T-311, T-614 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md) Hỏi đáp (2/3): ô nhập và gửi câu hỏi: `useChatStore`, `Composer.vue`
- [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04): `useDocumentsStore`, `truncateMiddle`, `formatDateTime`, `DocumentTable.vue`

## File cần tạo hoặc sửa

- `frontend/src/components/ScopePicker.vue`
- `frontend/src/__tests__/scope_picker.spec.ts`

## Chữ ký và giao diện

```typescript
// ScopePicker.vue
defineProps<{ modelValue: string[] }>()
defineEmits<{ "update:modelValue": [ids: string[]] }>()
```

## Các bước

1. `ScopePicker` là nút "Phạm vi: …" mở danh sách `role="listbox" aria-multiselectable="true"` gồm tài liệu `READY` (từ `documentsStore`), có ô lọc theo tên và mục "Tất cả tài liệu".
2. Nhãn nút: không chọn gì → `scope.all`; chọn N → `scope.some` với N.
3. Bàn phím: mũi tên lên/xuống di chuyển, `Space` chọn/bỏ, `Esc` đóng và trả focus về nút.
4. Giá trị lưu ở `chat.scope` và gửi trong `scopeDocIds` (T-524). Chọn "Tất cả tài liệu" → `[]`.
5. Sự kiện `status` có `scopeRemoved` khác rỗng: bỏ các mã đó khỏi `chat.scope` và hiện toast `scope.removed` (EC-15).
6. Ẩn khi cờ `scope` tắt.

## Tiêu chí hoàn thành

- [ ] Chọn tài liệu A thì câu hỏi gửi `scopeDocIds = [A]`.
- [ ] Chọn "Tất cả tài liệu" gửi `[]` và nhãn về "Phạm vi: Tất cả tài liệu".
- [ ] Thông báo EC-15 hiển thị và phạm vi được cập nhật.
- [ ] Dùng được hoàn toàn bằng bàn phím.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `sends_selected_scope` | Chọn A trong danh sách; gửi câu hỏi | Thân API-08 có `scopeDocIds: ["A"]`; nhãn "Đang hỏi trong 1 tài liệu" |
| `select_all_resets` | Đang chọn A, B; chọn "Tất cả tài liệu" | `chat.scope = []`; nhãn "Phạm vi: Tất cả tài liệu" |
| `removed_doc_notice` | `status.scopeRemoved = ["B"]` khi đang chọn A, B | Toast "Một tài liệu trong phạm vi đã bị xóa và được bỏ khỏi phạm vi."; `chat.scope = ["A"]` |
| `keyboard_navigation` | Mở bằng Enter, ↓, Space, Esc | Mục thứ nhất được chọn; danh sách đóng; focus về nút |
| `only_ready_listed` | Store có 1 `READY`, 1 `PROCESSING` | Danh sách có 1 tài liệu |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/scope_picker.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Lọc phạm vi phía máy chủ (T-311).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
