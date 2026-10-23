# T-518 · Hộp thoại tóm tắt tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 3 giờ `[Đề xuất]` |
| Tuần dự kiến | W10 (xem PLAN mục 6) |
| Story | US-040 |
| BR | BR-019 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-510](T-510-hop-thoai-xoa-va-tep-trung-thao-tac-theo-vai-tro.md), [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md) |
| Mở khóa | — |

## Mục tiêu

Thao tác "Tóm tắt" ở menu dòng của kho tài liệu, hiển thị bản tóm tắt có trích dẫn.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-12
- CONTRACTS mục 10.4 (`summary.title`)
- API thật do T-403, T-614 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04): `useDocumentsStore`, `truncateMiddle`, `formatDateTime`, `DocumentTable.vue`
- [T-510](T-510-hop-thoai-xoa-va-tep-trung-thao-tac-theo-vai-tro.md) Hộp thoại xóa và tệp trùng, thao tác theo vai trò: `RowMenu.vue`, `DuplicateDialog.vue`
- [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md) Hiển thị tin nhắn: trả lời dần và thẻ trích dẫn: `AnswerPart`, `splitAnswer`, `CitationChip.vue`, `MessageList.vue`

## File cần tạo hoặc sửa

- `frontend/src/components/SummaryDialog.vue`
- `frontend/src/__tests__/summary.spec.ts`

## Chữ ký và giao diện

```typescript
// SummaryDialog.vue
defineProps<{ doc: DocumentOut; open: boolean }>()
defineEmits<{ close: [] }>()
```

## Các bước

1. Thêm mục "Tóm tắt" vào slot của `RowMenu` (T-510), chỉ với tài liệu `READY` và khi cờ `summary` bật.
2. `SummaryDialog` (dùng khung `<dialog>` của T-506, không phá hủy): tiêu đề `summary.title`; khi mở gọi API-12; trong lúc chờ hiện vòng quay và "Đang tạo tóm tắt…"; lỗi → thông báo theo mã + [Thử lại].
3. Nội dung dựng bằng `AnswerBlock`/`splitAnswer` (T-512); bấm thẻ trích dẫn → đóng hộp thoại và điều hướng `/?doc={docId}&page={page}` để mở khung xem nguồn.

## Tiêu chí hoàn thành

- [ ] Chỉ tài liệu sẵn sàng có mục Tóm tắt.
- [ ] Bản tóm tắt có thẻ trích dẫn số trang bấm được.
- [ ] Cờ `summary` tắt thì mục biến mất.
- [ ] Lỗi dịch vụ hiện thông báo tiếng Việt và [Thử lại].

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `summary_only_for_ready` | Menu dòng `READY` và dòng `PROCESSING` | Chỉ dòng `READY` có "Tóm tắt" |
| `renders_summary_with_citations` | API-12 giả trả `text = "Ý 1 [[1]]."`, 1 trích dẫn tr. 3 | Tiêu đề "Tóm tắt do AI tạo cho {tên}"; 1 thẻ trích dẫn "… – tr. 3" |
| `citation_navigates` | Bấm thẻ trích dẫn | Điều hướng tới `/?doc=d1&page=3` |
| `hidden_when_flag_off` | Cờ `summary` tắt | Không có mục "Tóm tắt" |
| `error_retry` | API-12 ném `ApiError("AI_UNAVAILABLE")` | Thông báo "Dịch vụ hỏi đáp tạm thời gián đoạn…" và [Thử lại] |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/summary.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Lưu hay chia sẻ bản tóm tắt (ngoài MVP).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
