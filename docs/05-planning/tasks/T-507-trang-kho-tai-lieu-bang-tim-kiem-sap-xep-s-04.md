# T-507 · Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-015 |
| BR | BR-006 |
| NFR, EC, cổng | UX-11, NFR-004 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md), [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) |
| Mở khóa | [T-508](T-508-tai-len-1-2-vung-keo-tha-va-kiem-tra-o-trinh-duyet.md), [T-509](T-509-cap-nhat-trang-thai-tai-lieu-theo-thoi-gian-thuc.md), [T-510](T-510-hop-thoai-xoa-va-tep-trung-thao-tac-theo-vai-tro.md), [T-511](T-511-hoi-dap-1-3-bo-cuc-trang-va-thanh-ben.md), [T-514](T-514-chon-pham-vi-tai-lieu.md), [T-515](T-515-man-hinh-chao-va-goi-y-cau-hoi.md), [T-518](T-518-hop-thoai-tom-tat-tai-lieu.md), [T-522](T-522-ra-soat-kha-nang-tiep-can-va-dap-ung.md) |

## Mục tiêu

Hiển thị danh sách tài liệu với 5 trạng thái màn hình (đang tải, trống, dữ liệu, lỗi, hạn chế quyền).

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-03, 4.2 `DocumentOut`
- CONTRACTS mục 10.2, 10.3, 10.4 (`library.*`), 10.5 (`useDocumentsStore`)
- `docs/04-design/UI_UX_design/library.html`
- Blueprint 3.2.4 dòng S-04 (5 trạng thái, chép ở bước 5)
- API thật do T-202 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md) Kho trạng thái đăng nhập, bảo vệ route, S-01 và S-02: `useAuthStore`, `installGuards`
- [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) Thành phần dùng chung: thông báo, hộp thoại, khung xương, huy hiệu: `useToast`, `useBanner`, `ConfirmDialog.vue`, `StatusBadge.vue`

## File cần tạo hoặc sửa

- `frontend/src/views/LibraryView.vue`
- `frontend/src/stores/documents.ts`
- `frontend/src/components/DocumentTable.vue`
- `frontend/src/utils/format.ts`
- `frontend/src/__tests__/library.spec.ts`
- `frontend/src/__tests__/format.spec.ts`

## Chữ ký và giao diện

```typescript
export const useDocumentsStore = defineStore("documents", () => { /* items, loading, error */
  return { fetch(): Promise<void>, upsert(d: DocumentOut): void, applyEvent(e: StatusData): void, remove(docId: string): void, filtered(search: string, sort: DocumentSort): DocumentOut[] } })
// DocumentTable.vue
defineProps<{ rows: DocumentOut[]; sort: DocumentSort }>()
defineEmits<{ sort: [s: DocumentSort] }>()
export function truncateMiddle(s: string, max: number): string
export function formatDateTime(iso: string): string
```

## Các bước

1. Dựng `LibraryView` theo `docs/04-design/UI_UX_design/library.html`: tiêu đề "Kho tài liệu ({total})", ô "Tìm theo tên", chỗ cho vùng tải lên (T-508 gắn vào), bảng.
2. `useDocumentsStore.fetch()` gọi API-03 một lần khi vào trang; tìm kiếm và sắp xếp làm **ở trình duyệt** trên danh sách đã tải (≤ 500 dòng) `[Đề xuất]`; so khớp không dấu: `normalize("NFD")`, bỏ dấu, `đ→d`, chữ thường.
3. `DocumentTable` cột: Tên (rút gọn giữa còn 40 ký tự, đầy đủ ở `title`), Trang (`—` khi `null`), Người tải, Thời điểm `dd/MM/yyyy HH:mm`, Trạng thái (`StatusBadge`), Thao tác (chỗ cho T-510). Tiêu đề Tên và Thời điểm bấm được để sắp xếp, có `aria-sort`.
4. Người không phải TEAM_LEAD: thay vùng tải lên bằng dòng `library.uploadNotAllowed`.
5. Trạng thái: đang tải → `SkeletonRows rows=5`; rỗng → `library.empty` (TN) hoặc `library.emptyNoUpload`; lỗi → `library.loadError` + [Thử lại]; có dữ liệu → bảng.
6. Hàm thuần `truncateMiddle(s, max)` và `formatDateTime(iso)` ở `src/utils/format.ts`.

## Tiêu chí hoàn thành

- [ ] Kho có 3 tài liệu hiển thị 3 dòng với đủ 6 cột (AC-006).
- [ ] Có đủ 4 trạng thái màn hình và dòng hạn chế quyền.
- [ ] BD_USER thấy dòng "Chỉ Trưởng nhóm BD tải được tài liệu lên."
- [ ] Gõ "hop dong" lọc ra "Hợp đồng ABC.pdf" ngay, không gọi lại API.
- [ ] Bấm tiêu đề Tên đổi thứ tự và `aria-sort`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `renders_rows_with_fields` | API-03 giả trả 3 tài liệu | 3 dòng; dòng đầu có tên, số trang, người tải, `19/10/2026 09:12`, huy hiệu |
| `search_filters_by_name` | Gõ "hop dong" | Còn 1 dòng; `request` giả chỉ được gọi 1 lần |
| `sort_by_name` | Bấm tiêu đề Tên | Thứ tự a→z; `aria-sort="ascending"` |
| `shows_empty_and_error_states` | API trả `items: []`; API ném lỗi | Thấy `library.emptyNoUpload` (BD_USER); thấy `library.loadError` và nút [Thử lại] gọi lại API |
| `upload_not_allowed_line` | `role=BD_USER` | Thấy "Chỉ Trưởng nhóm BD tải được tài liệu lên." |
| `truncate_middle` | `truncateMiddle("a".repeat(30) + ".pdf", 20)` | Dài 20 ký tự, có `…` ở giữa, kết thúc bằng `.pdf` |
| `format_datetime` | `formatDateTime("2026-10-19T02:12:00Z")` với múi giờ `Asia/Ho_Chi_Minh` | `"19/10/2026 09:12"` |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/library.spec.ts
cd frontend && npx vitest run src/__tests__/format.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Vùng tải lên (T-508, T-523).
- Cập nhật trạng thái theo thời gian thực (T-509).
- Menu thao tác Xóa, Tóm tắt (T-510, T-518).
- Ảo hóa danh sách (chỉ làm nếu 500 dòng cuộn không mượt).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
