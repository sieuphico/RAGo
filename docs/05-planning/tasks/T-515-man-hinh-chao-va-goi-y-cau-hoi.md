# T-515 · Màn hình chào và gợi ý câu hỏi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W10 (xem PLAN mục 6) |
| Story | US-030, US-031 |
| BR | BR-020, BR-035 |
| NFR, EC, cổng | EC-01, EC-02, UX-01 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md), [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-521](T-521-telemetry-phia-giao-dien.md) |
| Mở khóa | — |

## Mục tiêu

Màn hình chào lần đầu và khối "Gợi ý câu hỏi" bấm một lần để hỏi.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-17
- CONTRACTS mục 10.4 (`chat.emptyLibrary`, `library.processingCount`, `suggest.title`)
- CONTRACTS mục 6 (`onboarding_viewed`, `suggestion_clicked`)
- `docs/04-design/UI_UX_design/chat.html` (màn hình chào)
- EC-01, EC-02 (PRD mục 4.2)
- API thật do T-402, T-614 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md) Hỏi đáp (2/3): ô nhập và gửi câu hỏi: `useChatStore`, `Composer.vue`
- [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04): `useDocumentsStore`, `truncateMiddle`, `formatDateTime`, `DocumentTable.vue`
- [T-521](T-521-telemetry-phia-giao-dien.md) Telemetry phía giao diện: `track`

## File cần tạo hoặc sửa

- `frontend/src/components/WelcomePanel.vue`
- `frontend/src/__tests__/welcome.spec.ts`

## Chữ ký và giao diện

```typescript
// WelcomePanel.vue
defineProps<{ userName: string }>()
```

## Các bước

1. `WelcomePanel` hiện khi phiên hiện tại chưa có tin nhắn: "Xin chào {tên}! Kho đang có {N} tài liệu." (N = số `READY`).
2. Khi cờ `suggestions` bật và N > 0: gọi API-17, hiện tiêu đề `suggest.title` và tối đa 3 nút gợi ý; bấm gợi ý thứ i → `chat.send(text)` và `track("suggestion_clicked", {suggestion_index: i})`.
3. N = 0 và không có tài liệu nào (EC-01): hiện `chat.emptyLibrary`, nút [Tải PDF lên] (liên kết `/library`) chỉ với TEAM_LEAD; đặt `chat.libraryEmpty = true` để ô nhập bị vô hiệu.
4. Có tài liệu đang `PROCESSING`/`OCR_PROCESSING` (EC-02): dòng `library.processingCount` với số đó; ô nhập vẫn dùng được.
5. Lần đầu hiện màn hình chào trên trình duyệt này: `track("onboarding_viewed", {doc_count: N})` và ghi `localStorage["cwd_onboarded"] = "1"` (bọc `try/catch`).

## Tiêu chí hoàn thành

- [ ] Người dùng mới thấy số tài liệu và 3 gợi ý (AC-035).
- [ ] Kho trống không hiện gợi ý và vô hiệu ô nhập (EC-01).
- [ ] Bấm gợi ý gửi đúng nội dung gợi ý.
- [ ] `onboarding_viewed` chỉ ghi một lần mỗi trình duyệt.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `shows_three_suggestions` | 125 tài liệu `READY`; API-17 trả 3 gợi ý | "Kho đang có 125 tài liệu." và 3 nút gợi ý |
| `click_suggestion_sends` | Bấm gợi ý thứ 2 | `chat.send` nhận đúng văn bản gợi ý 2; `track` với `suggestion_index: 1` |
| `empty_library_disables_input` | Store không có tài liệu; vai trò TEAM_LEAD | Thấy "Kho chưa có tài liệu." và [Tải PDF lên]; `chat.libraryEmpty === true`; API-17 không được gọi |
| `processing_count` | 2 `READY`, 3 `PROCESSING` | Thấy "3 tài liệu đang được xử lý, chưa dùng để trả lời." |
| `onboarding_once` | Mount hai lần | `track("onboarding_viewed")` gọi 1 lần |
| `flag_off_no_suggestions` | Cờ `suggestions` tắt | Không gọi API-17; không có khối gợi ý |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/welcome.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Tạo gợi ý phía máy chủ (T-402).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
