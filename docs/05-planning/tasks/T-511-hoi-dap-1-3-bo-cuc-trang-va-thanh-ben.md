# T-511 · Hỏi đáp (1/3): bố cục trang và thanh bên

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-020 |
| BR | BR-008, BR-013 |
| NFR, EC, cổng | EC-05, EC-11, UX-08 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md), [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md), [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) |
| Mở khóa | [T-513](T-513-khung-xem-nguon-s-05.md), [T-516](T-516-danh-sach-lich-su-s-06.md), [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md) |

## Mục tiêu

Bố cục ba vùng của S-03 (thanh bên, hội thoại, khung xem nguồn) theo độ rộng màn hình, và thanh bên có Phiên mới cùng tóm tắt kho.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- `docs/04-design/UI_UX_design/chat.html`
- Blueprint 3.8.3 (bố cục theo độ rộng, chép ở bước 2)
- CONTRACTS mục 10.2 (S-03, S-05, S-06)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md) Kho trạng thái đăng nhập, bảo vệ route, S-01 và S-02: `useAuthStore`, `installGuards`
- [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) Thành phần dùng chung: thông báo, hộp thoại, khung xương, huy hiệu: `useToast`, `useBanner`, `ConfirmDialog.vue`, `StatusBadge.vue`
- [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04): `useDocumentsStore`, `truncateMiddle`, `formatDateTime`, `DocumentTable.vue`

## File cần tạo hoặc sửa

- `frontend/src/views/ChatView.vue`
- `frontend/src/components/ChatSidebar.vue`
- `frontend/src/__tests__/chat_layout.spec.ts`

## Chữ ký và giao diện

```typescript
// ChatSidebar.vue
defineEmits<{ newSession: [] }>()
```

## Các bước

1. Dựng `ChatView` theo `docs/04-design/UI_UX_design/chat.html`: lưới CSS 3 cột — thanh bên 240 px, hội thoại co giãn, khung xem nguồn 480 px chỉ hiện khi có `?doc=`.
2. ≥ 1280 px như trên; 1024–1279 px: thanh bên thu thành cột biểu tượng 56 px, khung xem nguồn là lớp phủ toàn khung; < 1024 px: một cột, thanh bên thành nút menu.
3. `ChatSidebar`: nút "+ Phiên mới" (gọi `chat.newSession()` và về `/`), khối "Lịch sử" (slot cho T-516), khối "Kho tài liệu" hiện "{N} tài liệu" từ `documentsStore` và liên kết "Mở kho →".
4. Vùng hội thoại `id="main"` chứa slot cho danh sách tin nhắn (T-512) và ô nhập (T-524).
5. Route `/` và `/chat/:sessionId` cùng dùng `ChatView`; đổi `sessionId` gọi `chat.open(id)` (T-524/T-516).

## Tiêu chí hoàn thành

- [ ] Ở 1280 px có 3 vùng đúng độ rộng; ở 1100 px thanh bên là cột biểu tượng.
- [ ] Không có cuộn ngang ở 1024, 1280, 1440, 1920 px (UX-05).
- [ ] "+ Phiên mới" xóa hội thoại hiện tại và về `/`.
- [ ] Thanh bên hiện đúng số tài liệu.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `three_columns_at_1280` | Đặt `window.innerWidth = 1280`, mount có `?doc=d1` | Có 3 vùng `[data-testid=sidebar]`, `[data-testid=conversation]`, `[data-testid=viewer-slot]` |
| `collapsed_sidebar_1100` | `innerWidth = 1100` | Thanh bên có lớp `collapsed` |
| `new_session_resets` | Store có 2 tin nhắn; bấm "+ Phiên mới" | `chat.newSession` được gọi; route là `/` |
| `sidebar_doc_count` | `documentsStore.items` có 125 tài liệu | Thấy "125 tài liệu" |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/chat_layout.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Ô nhập và gửi câu hỏi (T-524).
- Danh sách tin nhắn (T-512), trạng thái câu trả lời (T-525).
- Danh sách lịch sử (T-516), khung xem nguồn (T-513).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
