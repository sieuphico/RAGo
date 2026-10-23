# T-508 · Tải lên (1/2): vùng kéo thả và kiểm tra ở trình duyệt

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-010, US-011, US-014 |
| BR | BR-001, BR-002, BR-003, BR-004 |
| NFR, EC, cổng | EC-03, EC-08, UX-02 |
| Quyết định kiến trúc | DD-05 |
| Phụ thuộc | [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-521](T-521-telemetry-phia-giao-dien.md) |
| Mở khóa | [T-523](T-523-tai-len-2-2-hang-doi-tien-do-va-thu-lai-tung-tep.md) |

## Mục tiêu

Vùng kéo thả và nút chọn tệp cho Trưởng nhóm BD; kiểm tra từng tệp trước khi gửi và nêu lý do riêng cho tệp bị từ chối.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 3 (`FILE_*`)
- CONTRACTS mục 6 (`document_upload_rejected`)
- `docs/04-design/UI_UX_design/library.html` (vùng kéo thả)
- EC-08 (PRD mục 4.2)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04): `useDocumentsStore`, `truncateMiddle`, `formatDateTime`, `DocumentTable.vue`
- [T-521](T-521-telemetry-phia-giao-dien.md) Telemetry phía giao diện: `track`

## File cần tạo hoặc sửa

- `frontend/src/components/DropZone.vue`
- `frontend/src/utils/validateFiles.ts`
- `frontend/src/views/LibraryView.vue`
- `frontend/src/__tests__/upload.spec.ts`

## Chữ ký và giao diện

```typescript
export function validateFiles(files: File[], limits: { maxFiles: number; maxBytes: number }): { accepted: File[]; rejected: { file: File; code: string }[] }
// DropZone.vue
defineEmits<{ accepted: [files: File[]] }>()
```

## Các bước

1. Hàm thuần `validateFiles(files, {maxFiles: 10, maxBytes: 50 * 1024 * 1024})`: tên không kết thúc `.pdf` (không phân biệt hoa thường) → `FILE_NOT_PDF`; `size > maxBytes` → `FILE_TOO_LARGE`; nhận tối đa 10 tệp hợp lệ đầu tiên, tệp hợp lệ thứ 11 trở đi → `FILE_TOO_MANY` `[Đề xuất]`.
2. `DropZone.vue`: vùng kéo thả có viền đứt, chữ "Kéo thả tệp PDF vào đây hoặc [Chọn tệp] · tối đa 10 tệp, mỗi tệp ≤ 50 MB"; nút "Chọn tệp" mở `<input type="file" multiple accept="application/pdf,.pdf">`; vùng nhận `dragover`/`drop`; dùng được bằng bàn phím (nút là phần tử focus được).
3. Sau kiểm tra: emit `accepted(files)`; mỗi tệp bị từ chối hiện một dòng "<tên> – <thông báo của mã>" và gọi `track("document_upload_rejected", {reason})` với `not_pdf`/`too_large`/`too_many`.
4. Gắn `DropZone` vào `LibraryView` chỉ khi `auth.me.role === "TEAM_LEAD"`; `accepted` chuyển cho `useUpload().enqueue` (T-523).

## Tiêu chí hoàn thành

- [ ] Tệp không phải PDF và tệp > 50 MB bị chặn ngay ở trình duyệt, mỗi tệp một lý do riêng (EC-08).
- [ ] Tệp hợp lệ trong cùng lô vẫn được chuyển đi.
- [ ] Vùng kéo thả không có với BD_USER, ADMIN, SPONSOR.
- [ ] Thao tác được bằng bàn phím.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `rejects_non_pdf_and_oversize` | `validateFiles([a.docx, b.pdf(51 MB), c.pdf(1 MB)])` | `accepted=[c.pdf]`; `rejected` có `a.docx: FILE_NOT_PDF`, `b.pdf: FILE_TOO_LARGE` |
| `too_many_files` | 12 tệp PDF 1 MB | 10 tệp đầu `accepted`; 2 tệp cuối `FILE_TOO_MANY` |
| `keeps_valid_files_in_batch` | Thả `[x.png, y.pdf]` vào `DropZone` | Emit `accepted` với `[y.pdf]`; hiện dòng "x.png – Chỉ hỗ trợ tệp PDF."; `track` gọi với `reason: "not_pdf"` |
| `hidden_for_non_team_lead` | Mount `LibraryView` với `BD_USER`, `ADMIN` | Không có `[data-testid=dropzone]` |
| `keyboard_choose_file` | Tab tới nút "Chọn tệp", nhấn Enter | `input[type=file]` nhận `click()` |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/upload.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Gửi tệp, tiến độ, thử lại (T-523).
- Cảnh báo tệp trùng (T-510).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
