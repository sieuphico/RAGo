# T-513 · Khung xem nguồn (S-05)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 7 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-022 |
| BR | BR-010 |
| NFR, EC, cổng | EC-14, EC-19, UX-05 |
| Quyết định kiến trúc | AD-07 |
| Phụ thuộc | [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md), [T-511](T-511-hoi-dap-1-3-bo-cuc-trang-va-thanh-ben.md), [T-521](T-521-telemetry-phia-giao-dien.md) |
| Mở khóa | [T-522](T-522-ra-soat-kha-nang-tiep-can-va-dap-ung.md), [T-615](T-615-kiem-thu-dau-cuoi-2-2-hoi-dap-xem-nguon-cac-trang-thai.md) |

## Mục tiêu

Mở đúng trang PDF khi bấm thẻ trích dẫn; chuyển trang; `Esc` đóng; lớp phủ dưới 1280 px.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-06
- CONTRACTS mục 10.2 (tham số `?doc=&page=`), 10.4 (`viewer.error`, `citation.deleted`)
- CONTRACTS mục 6 (`citation_clicked`)
- `docs/04-design/UI_UX_design/chat.html` (khung xem nguồn)
- API thật do T-212 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md) Hiển thị tin nhắn: trả lời dần và thẻ trích dẫn: `AnswerPart`, `splitAnswer`, `CitationChip.vue`, `MessageList.vue`
- [T-511](T-511-hoi-dap-1-3-bo-cuc-trang-va-thanh-ben.md) Hỏi đáp (1/3): bố cục trang và thanh bên: `ChatSidebar.vue`
- [T-521](T-521-telemetry-phia-giao-dien.md) Telemetry phía giao diện: `track`

## File cần tạo hoặc sửa

- `frontend/src/components/SourceViewer.vue`
- `frontend/src/__tests__/source_viewer.spec.ts`

## Chữ ký và giao diện

```typescript
// SourceViewer.vue
defineProps<{ docId: string; docName: string; page: number; pageCount?: number | null }>()
defineEmits<{ close: []; page: [n: number] }>()
```

## Các bước

1. `SourceViewer` props `docId`, `docName`, `page`, `pageCount?`; dùng trình xem PDF của trình duyệt: `<iframe src="/api/v1/documents/{docId}/file#page={page}" title="Trang nguồn: {docName}, trang {page}">` (AD-07); không thêm thư viện PDF.
2. Trước khi gắn iframe, gọi `fetch` với `Range: bytes=0-0` tới API-06: 404 → hiện `citation.deleted`; lỗi khác → `viewer.error` + [Thử lại]; thành công → hiện iframe. Trong lúc chờ hiện vòng quay.
3. Đầu khung: tên tệp, "◀ Trang {page} / {pageCount}" và nút ▶ (đổi `page`, cập nhật `?page=` bằng `router.replace`), nút ✕.
4. `Esc` hoặc ✕ đóng: xóa `doc`, `page` khỏi URL, trả focus cho phần tử đã mở (thẻ trích dẫn).
5. < 1280 px: khung là lớp phủ `role="dialog" aria-modal="true"` toàn khung, giam focus (EC-19).
6. `ChatView` mở khung khi nhận `openCitation`: đặt `?doc=&page=` và gọi `track("citation_clicked", {question_id: messageId, doc_id, page})`. URL không chứa nội dung câu hỏi.

## Tiêu chí hoàn thành

- [ ] Bấm trích dẫn mở đúng tài liệu và đúng trang (đo ≤ 3 giây ở T-615) (US-022).
- [ ] `Esc` đóng và trả focus về thẻ trích dẫn.
- [ ] Dưới 1280 px là lớp phủ, không cuộn ngang (UX-05).
- [ ] Tài liệu đã xóa hiện "Tài liệu đã bị xóa"; lỗi mạng hiện "Không mở được trang." + [Thử lại].
- [ ] Mỗi lần mở ghi một `citation_clicked`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `opens_at_cited_page` | Props `docId=d1`, `page=12`; `fetch` giả trả 206 | `iframe.src` kết thúc bằng `/api/v1/documents/d1/file#page=12` |
| `next_page_updates_url` | Bấm ▶ | `iframe.src` có `#page=13`; `router.replace` với `page=13` |
| `esc_closes_and_restores_focus` | Mở từ một nút trích dẫn; nhấn `Escape` | Emit `close`; focus về nút trích dẫn; URL không còn `doc` |
| `deleted_document` | `fetch` giả trả 404 | Thấy "Tài liệu đã bị xóa"; không có iframe |
| `load_error_retry` | `fetch` giả lỗi mạng rồi thành công | Thấy "Không mở được trang."; bấm [Thử lại] thì có iframe |
| `overlay_below_1280` | `innerWidth = 1100` | Phần tử gốc có `role="dialog"` và `aria-modal="true"` |
| `tracks_citation_clicked` | `ChatView` nhận `openCitation(m1, {docId: d1, page: 12})` | `track` gọi với `{question_id: "m1", doc_id: "d1", page: 12}` |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/source_viewer.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Phía máy chủ trả tệp theo khoảng byte (T-212).
- Đánh dấu đoạn trích trên trang PDF (ngoài MVP).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
