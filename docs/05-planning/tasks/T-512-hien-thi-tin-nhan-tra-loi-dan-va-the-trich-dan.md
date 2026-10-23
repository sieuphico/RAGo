# T-512 · Hiển thị tin nhắn: trả lời dần và thẻ trích dẫn

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-020, US-022, US-023, US-027 |
| BR | BR-010, BR-011, BR-013 |
| NFR, EC, cổng | EC-04, EC-06, EC-07, UX-07, UX-10 |
| Quyết định kiến trúc | DD-02, DD-03 |
| Phụ thuộc | [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md), [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md) |
| Mở khóa | [T-513](T-513-khung-xem-nguon-s-05.md), [T-517](T-517-thao-tac-tren-cau-tra-loi-sao-chep-va-danh-gia.md), [T-518](T-518-hop-thoai-tom-tat-tai-lieu.md), [T-522](T-522-ra-soat-kha-nang-tiep-can-va-dap-ung.md), [T-525](T-525-hoi-dap-3-3-trang-thai-cua-cau-tra-loi.md) |

## Mục tiêu

Danh sách tin nhắn hiển thị câu hỏi và câu trả lời hiện dần, thay dấu `[[n]]` bằng thẻ trích dẫn bấm được, và chỉ thông báo cho trình đọc màn hình khi câu trả lời xong.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.3 (dấu `[[n]]`)
- CONTRACTS mục 10.4 (`citation.*`), 10.5 (`UiMessage`)
- Blueprint 3.8.2 dòng "Trình đọc màn hình" và "Giảm chuyển động" (chép ở bước 4, 5)
- `docs/04-design/UI_UX_design/chat.html`

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md) Hỏi đáp (2/3): ô nhập và gửi câu hỏi: `useChatStore`, `Composer.vue`
- [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md) Client luồng SSE (POST) cho câu trả lời: `StreamHandlers`, `streamPost`

## File cần tạo hoặc sửa

- `frontend/src/components/MessageList.vue`
- `frontend/src/components/AnswerBlock.vue`
- `frontend/src/components/CitationChip.vue`
- `frontend/src/utils/answerText.ts`
- `frontend/src/__tests__/answer.spec.ts`

## Chữ ký và giao diện

```typescript
export type AnswerPart = { kind: "text"; value: string } | { kind: "cite"; index: number }
export function splitAnswer(text: string): AnswerPart[]
// CitationChip.vue
defineProps<{ citation: CitationOut }>()
defineEmits<{ open: [c: CitationOut] }>()
// MessageList.vue
defineProps<{ messages: UiMessage[] }>()
defineEmits<{ openCitation: [messageId: string, c: CitationOut] }>()
```

## Các bước

1. Hàm thuần `splitAnswer(text)` tách theo `/\[\[(\d+)\]\]/` thành mảng `{kind: "text", value} | {kind: "cite", index}`.
2. `AnswerBlock` dựng từng phần bằng **nút văn bản** (không bao giờ dùng `v-html`: nội dung do AI tạo là dữ liệu không tin cậy); xuống dòng giữ bằng `white-space: pre-wrap`. `cite` có trong `citations` → `CitationChip`; chưa có → không hiện gì.
3. `CitationChip` là `<button>`: chữ `[{tên rút gọn giữa 24 ký tự} – tr. {page}]`, `aria-label` theo `citation.aria`; tooltip đoạn trích (≤ 200 ký tự) khi di chuột hoặc focus; bấm → emit `open(citation)`; `deleted` → nút `disabled` với chữ `citation.deleted`.
4. `MessageList`: `role="log"`, tin nhắn người dùng căn phải, trợ lý căn trái, tự cuộn xuống khi có token mới nếu người dùng đang ở cuối. Một vùng `aria-live="polite"` ẩn chỉ được cập nhật "Câu trả lời đã xong" khi tin nhắn chuyển `COMPLETED`/`NOT_FOUND` — **không** đọc từng chữ.
5. `prefers-reduced-motion: reduce` → tắt hiệu ứng hiện chữ, chỉ nối chữ.
6. Thanh thao tác (T-517) và trạng thái (T-525) gắn qua slot của `AnswerBlock`.

## Tiêu chí hoàn thành

- [ ] Câu trả lời hiện từng phần và có đủ thẻ trích dẫn (US-022).
- [ ] Không có `v-html` trong các component này (kiểm bằng test).
- [ ] Trình đọc màn hình chỉ nhận thông báo khi câu trả lời xong.
- [ ] Thẻ trích dẫn bấm được bằng bàn phím và có nhãn đầy đủ.
- [ ] Trích dẫn tài liệu đã xóa không bấm được.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `split_answer` | `splitAnswer("A [[1]] B [[2]].")` | `[text "A ", cite 1, text " B ", cite 2, text "."]` |
| `streams_text_and_citations` | Store phát lần lượt token "Thời hạn ", citation 1, token "24 tháng [[1]]" | Văn bản hiển thị "Thời hạn 24 tháng" và 1 nút trích dẫn "[HD_ABC_2026.pdf – tr. 12]" |
| `no_html_injection` | Token `<img src=x onerror=alert(1)>` | Hiển thị nguyên chuỗi dạng văn bản; không có phần tử `img` |
| `announces_only_on_completion` | Phát 5 token rồi `done` | Vùng `aria-live` rỗng trong lúc phát token; sau `done` là "Câu trả lời đã xong" |
| `chip_keyboard_open` | Tab tới thẻ trích dẫn, nhấn Enter | Emit `open` với đúng trích dẫn |
| `deleted_chip_disabled` | Trích dẫn `deleted: true` | Nút `disabled`, chữ "Tài liệu đã bị xóa" |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/answer.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Thông báo đang tìm, chậm, không tìm thấy, dừng, mất kết nối, lỗi (T-525).
- Khung xem nguồn (T-513).
- Sao chép và đánh giá (T-517).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
