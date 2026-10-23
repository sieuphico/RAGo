# T-524 · Hỏi đáp (2/3): ô nhập và gửi câu hỏi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-020, US-027 |
| BR | BR-008, BR-013 |
| NFR, EC, cổng | EC-05, EC-11, UX-08 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-511](T-511-hoi-dap-1-3-bo-cuc-trang-va-thanh-ben.md), [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md) |
| Mở khóa | [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md), [T-514](T-514-chon-pham-vi-tai-lieu.md), [T-515](T-515-man-hinh-chao-va-goi-y-cau-hoi.md), [T-516](T-516-danh-sach-lich-su-s-06.md) |

## Mục tiêu

Ô nhập câu hỏi và store hội thoại: tạo phiên khi cần, gửi câu hỏi qua API-08, cập nhật tin nhắn theo luồng, dừng, giữ bản nháp.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-07, API-08, API-09
- CONTRACTS mục 5.2
- CONTRACTS mục 10.4 (`composer.*`, `net.offline`), 10.5 (`useChatStore`, `UiMessage`)
- Chữ ký `streamPost` ở T-504
- API thật do T-308 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-511](T-511-hoi-dap-1-3-bo-cuc-trang-va-thanh-ben.md) Hỏi đáp (1/3): bố cục trang và thanh bên: `ChatSidebar.vue`
- [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md) Client luồng SSE (POST) cho câu trả lời: `StreamHandlers`, `streamPost`

## File cần tạo hoặc sửa

- `frontend/src/stores/chat.ts`
- `frontend/src/components/Composer.vue`
- `frontend/src/composables/useOnline.ts`
- `frontend/src/__tests__/composer.spec.ts`
- `frontend/src/__tests__/chat_store.spec.ts`

## Chữ ký và giao diện

```typescript
export const useChatStore = defineStore("chat", () => { /* sessionId, messages, draft, busy, scope, libraryEmpty */
  return { send(text: string): Promise<void>, stop(): Promise<void>, newSession(): void, open(sessionId: string): Promise<void> } })
// Composer.vue
defineEmits<{ submit: [text: string]; stop: [] }>()
```

## Các bước

1. `useChatStore`: trạng thái và hành động như CONTRACTS mục 10.5. `send(text)`: chưa có `sessionId` thì gọi API-07; thêm `UiMessage` người dùng và `UiMessage` trợ lý `SUBMITTING`; gọi `streamPost` (T-504) tới API-08 với `{text, scopeDocIds: scope}`.
2. Bộ xử lý luồng: `status` → `SEARCHING`, lưu `messageId`, `docCount`; `citation` → thêm vào `citations`; `token` → nối `text`, `STREAMING`; `done` → `stopped` ? `STOPPED` : `isNotFound` ? `NOT_FOUND` : `COMPLETED`, lưu `notFoundReason`, `notice`; `error` → `FAILED` + `errorCode`; `onInterrupted` → `INTERRUPTED`.
3. Lỗi trước luồng (`ApiError`): `QUESTION_IN_PROGRESS` → toast thông báo của mã, bỏ tin nhắn vừa thêm; mã khác → `FAILED`.
4. `stop()`: gọi API-09 với `messageId`; nếu sau 2 giây luồng chưa kết thúc thì `abort()` và đặt `STOPPED`.
5. `Composer.vue`: `Enter` gửi, `Shift+Enter` xuống dòng, phím `/` khi focus không ở ô nhập thì focus ô nhập; bộ đếm `n/2.000` đổi sang màu cảnh báo khi > 2.000; nút Gửi vô hiệu khi trống, chỉ khoảng trắng, quá dài, mất mạng hoặc `libraryEmpty`; khi `busy` nút thành [■ Dừng].
6. Bản nháp lưu `sessionStorage["cwd_draft"]` mỗi lần gõ (bọc `try/catch`), khôi phục khi mở trang, xóa khi gửi thành công.
7. `useOnline()` theo dõi `navigator.onLine` và sự kiện `online`/`offline`; mất mạng thì hiện dải `net.offline` (EC-05).
8. Dòng nhắc `composer.disclaimer` luôn hiện dưới ô nhập.

## Tiêu chí hoàn thành

- [ ] Ô trống hoặc chỉ khoảng trắng: `Enter` không gửi (US-020).
- [ ] 2.001 ký tự: nút Gửi vô hiệu, bộ đếm cảnh báo (EC-11).
- [ ] Mất mạng: dải thông báo hiện, nội dung đang gõ được giữ (EC-05).
- [ ] Gửi câu hỏi tạo phiên đúng một lần rồi gửi API-08.
- [ ] Bấm Dừng gọi API-09 với đúng `messageId`.
- [ ] Tải lại trang giữ bản nháp.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `enter_sends_shift_enter_newline` | Gõ "abc", nhấn `Enter`; gõ "x", nhấn `Shift+Enter` | Lần 1 emit `submit("abc")`; lần 2 ô nhập có xuống dòng, không emit |
| `blocks_empty_and_overlong` | Ô nhập "   "; ô nhập 2.001 ký tự | Nút Gửi `disabled` cả hai; lần 2 bộ đếm "2.001/2.000" có lớp cảnh báo |
| `keeps_draft_on_offline` | Gõ "câu dở"; phát sự kiện `offline` | Dải "Mất kết nối. Đang thử kết nối lại…" hiện; ô nhập vẫn "câu dở"; nút Gửi `disabled` |
| `draft_restored` | `sessionStorage.cwd_draft = "nháp"`; mount | Ô nhập là "nháp" |
| `send_creates_session_once` | Chưa có phiên; gửi 2 câu liên tiếp (câu 1 xong mới gửi câu 2) | API-07 gọi 1 lần; API-08 gọi 2 lần |
| `stream_updates_message` | `streamPost` giả phát `status{docCount:3,messageId:m1}`, `citation`, `token`, `done` | Tin nhắn trợ lý qua `SEARCHING` → `STREAMING` → `COMPLETED`, có 1 trích dẫn, `messageId = m1` |
| `stop_calls_api09` | Đang `STREAMING` với `messageId = m1`; bấm [■ Dừng] | `POST /api/v1/chat/messages/m1/stop` |
| `question_in_progress_toast` | `streamPost` ném `ApiError("QUESTION_IN_PROGRESS")` | Toast "Đang trả lời câu hỏi trước. Hãy chờ hoặc bấm Dừng."; tin nhắn vừa thêm bị bỏ |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/composer.spec.ts
cd frontend && npx vitest run src/__tests__/chat_store.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Hiển thị nội dung tin nhắn và thẻ trích dẫn (T-512).
- Thông báo trạng thái câu trả lời (T-525).
- Chọn phạm vi (T-514).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
