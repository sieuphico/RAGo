# T-509 · Cập nhật trạng thái tài liệu theo thời gian thực

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W6–W7 (xem PLAN mục 6) |
| Story | US-012 |
| BR | BR-005 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-02 |
| Phụ thuộc | [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md), [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) |
| Mở khóa | — |

## Mục tiêu

Huy hiệu tự đổi trạng thái qua SSE, không tải lại trang.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 5.1 (khung SSE API-04)
- CONTRACTS mục 10.3 ("Xử lý lâu bất thường")
- API thật do T-211 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md) Client luồng SSE (POST) cho câu trả lời: `StreamHandlers`, `streamPost`
- [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04): `useDocumentsStore`, `truncateMiddle`, `formatDateTime`, `DocumentTable.vue`

## File cần tạo hoặc sửa

- `frontend/src/composables/useDocumentEvents.ts`
- `frontend/src/__tests__/document_events.spec.ts`

## Chữ ký và giao diện

```typescript
export function useDocumentEvents(): { mode: Ref<"sse" | "polling"> }
```

## Các bước

1. `useDocumentEvents()` mở `new EventSource("/api/v1/documents/events")` khi mount `LibraryView`; khung `status` → `documentsStore.applyEvent` (đổi `status`, `failureReason`, `pageCount`; `DELETED` → xóa khỏi danh sách).
2. `onerror` 2 lần liên tiếp → đóng `EventSource`, hỏi lại API-03 mỗi 3 giây; thử mở lại SSE sau 60 giây.
3. Vùng `aria-live="polite"` ẩn: thông báo "{tên}: Sẵn sàng" hoặc "{tên}: Thất bại – {lý do}" khi một tài liệu chuyển `READY` hoặc `FAILED`.
4. Mỗi 60 giây đánh dấu tài liệu `OCR_PROCESSING` có `uploadedAt` cũ hơn 15 phút để `StatusBadge` thêm "Xử lý lâu bất thường" (EC-20).
5. Unmount → đóng `EventSource` và hủy bộ hẹn giờ.

## Tiêu chí hoàn thành

- [ ] Đổi trạng thái ở máy chủ hiện ra không cần tải lại trang (US-012).
- [ ] SSE hỏng thì chuyển sang hỏi lại mỗi 3 giây.
- [ ] Rời trang đóng kết nối và bộ hẹn giờ.
- [ ] Có thông báo cho trình đọc màn hình khi tài liệu sẵn sàng hoặc thất bại.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `updates_badge_on_event` | `EventSource` giả phát `status {docId: d1, status: "READY", pageCount: 12}` | Dòng d1 hiện "Sẵn sàng", cột Trang = 12; vùng `aria-live` có "…: Sẵn sàng" |
| `falls_back_to_polling` | `EventSource` giả gọi `onerror` 2 lần; tiến đồng hồ giả 9 giây | `request` tới API-03 được gọi 3 lần |
| `slow_ocr_flag` | Tài liệu `OCR_PROCESSING`, `uploadedAt` cách 16 phút; tiến 60 giây | Huy hiệu có "Xử lý lâu bất thường" |
| `closes_on_unmount` | Unmount | `EventSource.close` được gọi; không còn bộ hẹn giờ |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/document_events.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Phía máy chủ gửi sự kiện (T-211).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
