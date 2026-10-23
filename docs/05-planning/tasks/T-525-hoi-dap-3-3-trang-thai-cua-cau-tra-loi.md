# T-525 · Hỏi đáp (3/3): trạng thái của câu trả lời

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-023, US-027, US-020 |
| BR | BR-011, BR-013 |
| NFR, EC, cổng | EC-04, EC-06, EC-07, EC-12, UX-07 |
| Quyết định kiến trúc | DD-03 |
| Phụ thuộc | [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md) |
| Mở khóa | [T-522](T-522-ra-soat-kha-nang-tiep-can-va-dap-ung.md), [T-615](T-615-kiem-thu-dau-cuoi-2-2-hoi-dap-xem-nguon-cac-trang-thai.md) |

## Mục tiêu

Hiển thị đúng 8 trạng thái của một câu trả lời (Blueprint 3.5.2) cùng thông báo chậm, không tìm thấy, đã dừng, mất kết nối, lỗi và ghi chú ngôn ngữ.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 10.4 (`answer.*`), 10.5 (`UiMessage`)
- Blueprint 3.5.2 (bảng trạng thái câu trả lời, chép ở các bước)
- `docs/04-design/UI_UX_design/chat.html` (4 trạng thái mẫu)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md) Hiển thị tin nhắn: trả lời dần và thẻ trích dẫn: `AnswerPart`, `splitAnswer`, `CitationChip.vue`, `MessageList.vue`

## File cần tạo hoặc sửa

- `frontend/src/components/AnswerState.vue`
- `frontend/src/__tests__/answer_state.spec.ts`

## Chữ ký và giao diện

```typescript
defineProps<{ message: UiMessage }>()
defineEmits<{ retry: []; stop: [] }>()
```

## Các bước

1. Prop `message: UiMessage`; emit `retry` (gửi lại cùng câu hỏi) và `stop`.
2. `SUBMITTING`/`SEARCHING`: "Đang tìm trong {N} tài liệu…" (N từ `docCount`, chưa có thì bỏ số) kèm vòng quay và [■ Dừng]; sau 15 giây kể từ lúc gửi thêm `answer.slow`. Sau 65 giây không có sự kiện kết thúc, đặt `FAILED` với `TIMEOUT` `[Đề xuất: dự phòng khi máy chủ không gửi]`.
3. `NOT_FOUND`: khối nền trung tính (token `color.surface-muted`, **không** dùng token lỗi), biểu tượng kính lúp, `answer.notFound` + `answer.notFoundHint`; `notFoundReason = "NO_READY_DOCS"` thì hiện `answer.noReadyDocs`.
4. `STOPPED`: giữ văn bản, nhãn `answer.stopped`, nút [Hỏi lại]. `INTERRUPTED`: giữ văn bản, biểu tượng cảnh báo, `answer.interrupted`, nút [Hỏi lại].
5. `FAILED`: thông báo theo `errorCode` từ `errors.ts`, nút [Thử lại]; không bao giờ hiện mã lỗi.
6. `notice = "LANG_UNSUPPORTED"`: dòng ghi chú `answer.langNotice` dưới câu trả lời.

## Tiêu chí hoàn thành

- [ ] Có đủ 8 trạng thái với đúng nội dung ở CONTRACTS mục 10.4.
- [ ] "Không tìm thấy" không dùng màu đỏ hay token lỗi (DD-03).
- [ ] Đứt kết nối giữ phần đã nhận và có [Hỏi lại] (UX-07).
- [ ] Sau 15 giây chờ hiện thông báo chậm (EC-06).

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `searching_with_count` | `state=SEARCHING`, `docCount=125` | "Đang tìm trong 125 tài liệu…" và nút Dừng |
| `slow_notice_after_15s` | `SEARCHING`; tiến đồng hồ giả 15 giây | Thêm "Câu hỏi đang mất nhiều thời gian hơn bình thường…" |
| `client_timeout_fallback` | `SEARCHING`; tiến 65 giây không có sự kiện | `FAILED`, thông báo "Không thể trả lời lúc này." và [Thử lại] |
| `not_found_is_neutral` | `state=NOT_FOUND`, `notFoundReason=NO_EVIDENCE` | Có `answer.notFound` và `answer.notFoundHint`; phần tử không có lớp `tone-danger` hay biến `--color-danger` |
| `no_ready_docs_text` | `NOT_FOUND`, `notFoundReason=NO_READY_DOCS` | "Kho chưa có tài liệu sẵn sàng. Hãy tải PDF lên để bắt đầu." |
| `interrupted_keeps_partial` | `state=INTERRUPTED`, `text="Hợp đồng có thời hạn 24"` | Văn bản còn nguyên; có "Mất kết nối – câu trả lời chưa đầy đủ." và [Hỏi lại] emit `retry` |
| `stopped_label` | `state=STOPPED` | "Đã dừng" và [Hỏi lại] |
| `failed_uses_error_table` | `state=FAILED`, `errorCode=AI_UNAVAILABLE` | "Dịch vụ hỏi đáp tạm thời gián đoạn. Vui lòng thử lại sau ít phút."; không có chữ "AI_UNAVAILABLE" |
| `lang_notice` | `COMPLETED`, `notice=LANG_UNSUPPORTED` | Có "Hiện chỉ hỗ trợ tốt tiếng Việt và tiếng Anh." |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/answer_state.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Văn bản và thẻ trích dẫn (T-512).
- Thời hạn 60 giây phía máy chủ (T-316).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
