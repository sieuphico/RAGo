# T-517 · Thao tác trên câu trả lời: sao chép và đánh giá

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-042, US-050 |
| BR | BR-022, BR-023 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md), [T-521](T-521-telemetry-phia-giao-dien.md) |
| Mở khóa | — |

## Mục tiêu

Nút Sao chép kèm nguồn và 👍/👎 kèm hộp thoại lý do.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-11
- CONTRACTS mục 4.3 (sao chép `[[n]]` → `[n]`)
- CONTRACTS mục 6 (`answer_copied`; `answer_rated` do máy chủ phát)
- Blueprint 4.5 (hộp thoại lý do)
- API thật do T-313, T-614 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md) Hiển thị tin nhắn: trả lời dần và thẻ trích dẫn: `AnswerPart`, `splitAnswer`, `CitationChip.vue`, `MessageList.vue`
- [T-521](T-521-telemetry-phia-giao-dien.md) Telemetry phía giao diện: `track`

## File cần tạo hoặc sửa

- `frontend/src/components/AnswerActions.vue`
- `frontend/src/components/RatingDialog.vue`
- `frontend/src/__tests__/answer_actions.spec.ts`

## Chữ ký và giao diện

```typescript
export function copyText(m: UiMessage): string
// AnswerActions.vue
defineProps<{ message: UiMessage }>()
```

## Các bước

1. `AnswerActions` hiện dưới câu trả lời: [⧉ Sao chép] khi `COMPLETED` (cờ `copy`); [👍] [👎] khi `COMPLETED` hoặc `NOT_FOUND` (cờ `rating`). Nút có `aria-label` "Sao chép câu trả lời", "Câu trả lời hữu ích", "Câu trả lời chưa tốt"; nút đã chọn có `aria-pressed="true"`.
2. Hàm thuần `copyText(message)`: thay `[[n]]` bằng `[n]`, thêm `\n\nNguồn:` và mỗi dòng `[n] {docName}, tr. {page}` theo thứ tự `index`.
3. Sao chép bằng `navigator.clipboard.writeText`; không dùng được thì dùng `<textarea>` tạm + `document.execCommand("copy")`; toast `copy.done`; `track("answer_copied", {question_id})`.
4. 👍 → API-11 `{value: "UP", reasonCode: null}`. 👎 → `RatingDialog`: tiêu đề "Câu trả lời chưa tốt ở điểm nào? (tùy chọn)", 4 lựa chọn radio Sai thông tin (`WRONG_INFO`), Trích dẫn sai (`WRONG_CITATION`), Thiếu ý (`MISSING_INFO`), Khác (`OTHER`); [Bỏ qua] gửi `DOWN` + `null`, [Gửi] gửi `DOWN` + mã đã chọn.
5. Không gửi `answer_rated` từ giao diện (máy chủ phát, Q-C9).

## Tiêu chí hoàn thành

- [ ] Nội dung dán chứa đủ câu trả lời và nguồn (AC-022).
- [ ] Hộp thoại 👎 cho phép bỏ qua lý do và vẫn ghi 👎.
- [ ] Mọi nút có nhãn đọc được bằng trình đọc màn hình.
- [ ] Trình duyệt không có Clipboard API vẫn sao chép được.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `copy_includes_sources` | `text = "Thời hạn 24 tháng [[1]]."`, trích dẫn 1 = HD_ABC_2026.pdf tr. 12 | `"Thời hạn 24 tháng [1].\n\nNguồn:\n[1] HD_ABC_2026.pdf, tr. 12"` |
| `clipboard_fallback` | `navigator.clipboard` là `undefined` | `document.execCommand("copy")` được gọi; toast "Đã sao chép" |
| `rate_up` | Bấm 👍 | API-11 `{value: "UP", reasonCode: null}`; nút có `aria-pressed="true"` |
| `rating_dialog_skip_still_records` | Bấm 👎, rồi [Bỏ qua] | API-11 `{value: "DOWN", reasonCode: null}` |
| `rating_dialog_with_reason` | Bấm 👎, chọn "Trích dẫn sai", [Gửi] | API-11 `{value: "DOWN", reasonCode: "WRONG_CITATION"}` |
| `hidden_while_streaming` | `state=STREAMING` | Không có nút nào |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/answer_actions.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Ghi đánh giá phía máy chủ (T-313).
- Ô nhập lý do tự do (không làm: telemetry cấm văn bản tự do).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
