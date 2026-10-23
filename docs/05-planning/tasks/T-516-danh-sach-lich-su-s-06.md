# T-516 · Danh sách lịch sử (S-06)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W10 (xem PLAN mục 6) |
| Story | US-041 |
| BR | BR-021 |
| NFR, EC, cổng | EC-14 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-511](T-511-hoi-dap-1-3-bo-cuc-trang-va-thanh-ben.md), [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md) |
| Mở khóa | — |

## Mục tiêu

Danh sách phiên nhóm theo Hôm nay, 7 ngày qua, Cũ hơn và mở lại phiên.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-10a, API-10b, 4.2 `SessionSummaryOut`, `SessionDetailOut`
- CONTRACTS mục 10.4 (`history.*`)
- Blueprint 4.9 (S-06)
- API thật do T-401, T-614 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-511](T-511-hoi-dap-1-3-bo-cuc-trang-va-thanh-ben.md) Hỏi đáp (1/3): bố cục trang và thanh bên: `ChatSidebar.vue`
- [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md) Hỏi đáp (2/3): ô nhập và gửi câu hỏi: `useChatStore`, `Composer.vue`

## File cần tạo hoặc sửa

- `frontend/src/components/HistoryList.vue`
- `frontend/src/__tests__/history.spec.ts`

## Chữ ký và giao diện

```typescript
export function groupSessions(items: SessionSummaryOut[], now: Date): { today: SessionSummaryOut[]; last7: SessionSummaryOut[]; older: SessionSummaryOut[] }
```

## Các bước

1. `HistoryList` trong slot thanh bên: gọi API-10a khi mount và sau mỗi câu hỏi đầu tiên của phiên mới.
2. Hàm thuần `groupSessions(items, now)` → `{today, last7, older}` theo `lastMessageAt` và giờ máy: hôm nay; 1–7 ngày trước; cũ hơn. Nhóm rỗng không hiện.
3. Mỗi mục là liên kết `/chat/{sessionId}` hiện `title` (đã ≤ 60 ký tự); mục đang mở có `aria-current="page"`.
4. `chat.open(id)` gọi API-10b và chuyển `messages` thành `UiMessage` (`status` → `state`; trích dẫn giữ `deleted`).
5. Trạng thái: `SkeletonRows rows=3`; `history.empty`; `history.error` + [Thử lại]. Ẩn khi cờ `history` tắt.

## Tiêu chí hoàn thành

- [ ] Mở lại được phiên trước sau khi đăng nhập lại (AC-021).
- [ ] Có đủ trạng thái tải, trống, lỗi.
- [ ] Thẻ trích dẫn của tài liệu đã xóa không mở được.
- [ ] Nhóm theo thời gian đúng.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `groups_by_time` | `now = 2026-12-21 10:00`; phiên lúc 08:00 hôm nay, 3 ngày trước, 30 ngày trước | Mỗi nhóm có 1 phiên: Hôm nay, 7 ngày qua, Cũ hơn |
| `reopens_session_with_citations` | Bấm một phiên; API-10b giả trả 2 tin nhắn, 1 trích dẫn `deleted: true` | Route `/chat/{id}`; store có 2 `UiMessage`; thẻ trích dẫn `disabled` |
| `empty_and_error_states` | API-10a trả `items: []`; rồi ném lỗi | "Chưa có phiên nào"; "Không tải được lịch sử." + [Thử lại] |
| `flag_off_hidden` | Cờ `history` tắt | Không gọi API-10a; không có khối Lịch sử |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/history.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Xóa phiên thủ công (ngoài MVP).
- Hết hạn 90 ngày (T-401).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
