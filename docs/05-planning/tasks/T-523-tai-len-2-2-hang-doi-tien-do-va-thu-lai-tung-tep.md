# T-523 · Tải lên (2/2): hàng đợi, tiến độ và thử lại từng tệp

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-010, US-014 |
| BR | BR-001, BR-003, BR-004 |
| NFR, EC, cổng | EC-03, UX-02 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-508](T-508-tai-len-1-2-vung-keo-tha-va-kiem-tra-o-trinh-duyet.md), [T-521](T-521-telemetry-phia-giao-dien.md) |
| Mở khóa | [T-510](T-510-hop-thoai-xoa-va-tep-trung-thao-tac-theo-vai-tro.md), [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) |

## Mục tiêu

Gửi từng tệp đã được chấp nhận lên API-02, hiển thị tiến độ, xử lý gián đoạn và thử lại riêng từng tệp.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-02, 4.2 `UploadResultOut`
- CONTRACTS mục 10.3 (`UPLOADING`, `INTERRUPTED`)
- CONTRACTS mục 6 (`document_upload_started`)
- API thật do T-201 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-508](T-508-tai-len-1-2-vung-keo-tha-va-kiem-tra-o-trinh-duyet.md) Tải lên (1/2): vùng kéo thả và kiểm tra ở trình duyệt: `validateFiles`, `DropZone.vue`
- [T-521](T-521-telemetry-phia-giao-dien.md) Telemetry phía giao diện: `track`

## File cần tạo hoặc sửa

- `frontend/src/composables/useUpload.ts`
- `frontend/src/components/UploadQueue.vue`
- `frontend/src/__tests__/use_upload.spec.ts`

## Chữ ký và giao diện

```typescript
export interface UploadItem { id: string; file: File; state: "UPLOADING" | "INTERRUPTED" | "DONE" | "REJECTED"; progress: number; errorCode?: string }
export function useUpload(): { items: Ref<UploadItem[]>; enqueue(files: File[]): void; retry(id: string): void }
```

## Các bước

1. `useUpload()` giữ hàng đợi `UploadItem { id, file, state: "UPLOADING" | "INTERRUPTED" | "DONE" | "REJECTED", progress, errorCode? }`.
2. Mỗi tệp gửi bằng **một** yêu cầu `XMLHttpRequest` riêng `[Đề xuất]` (để có tiến độ và thử lại từng tệp): `POST /api/v1/documents`, `FormData` trường `files`, tiêu đề `X-Requested-With: cwd`, `withCredentials`. Tối đa 2 yêu cầu song song.
3. `xhr.upload.onprogress` cập nhật `progress` (0–100). Phản hồi 202: `results[0].error` khác `null` → `REJECTED` kèm mã; ngược lại `DONE` và gọi `documentsStore.upsert` với tài liệu `PROCESSING` (tên, kích thước, người tải là người dùng hiện tại).
4. Lỗi mạng hoặc hủy → `INTERRUPTED`; `retry(id)` gửi lại đúng tệp đó; các tệp khác không bị ảnh hưởng (EC-03). HTTP 401 → luồng hết phiên (T-505).
5. Đầu mỗi lô gọi `track("document_upload_started", {file_count, total_size_mb})` (T-521).
6. `UploadQueue.vue` hiển thị các tệp đang tải ở đầu bảng kho với nhãn "Đang tải lên ({p}%)" hoặc "Tải lên bị gián đoạn" + [Thử lại] (CONTRACTS mục 10.3).

## Tiêu chí hoàn thành

- [ ] Chọn 10 tệp hợp lệ trong một thao tác: cả 10 được gửi và chuyển `DONE` (AC-002).
- [ ] Một tệp lỗi mạng chuyển `INTERRUPTED`, các tệp khác vẫn `DONE`; [Thử lại] gửi lại đúng tệp đó.
- [ ] Máy chủ từ chối một tệp (`FILE_NOT_PDF`) thì dòng đó hiện lý do tiếng Việt.
- [ ] Mỗi lô ghi đúng một `document_upload_started`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `uploads_each_file` | `enqueue` 3 tệp; XHR giả trả 202 thành công | 3 yêu cầu, tối đa 2 cùng lúc; cả 3 `DONE`; `documentsStore.upsert` gọi 3 lần với `status=PROCESSING` |
| `progress_updates` | XHR giả phát `progress` 50% | `progress == 50`; dòng hiện "Đang tải lên (50%)" |
| `network_error_interrupted` | Tệp 2 nhận `onerror` | Tệp 2 `INTERRUPTED`; tệp 1, 3 `DONE` |
| `retry_single_failed_file` | `retry(id của tệp 2)` | Chỉ 1 yêu cầu mới, cho tệp 2 |
| `server_rejection_shown` | Phản hồi `results[0].error = "FILE_NOT_PDF"` | `REJECTED`; dòng hiện "Chỉ hỗ trợ tệp PDF." |
| `upload_started_tracked` | `enqueue` 2 tệp 1,5 MB và 2,5 MB | `track` gọi 1 lần với `{file_count: 2, total_size_mb: 4}` |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/use_upload.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Kiểm tra tệp ở trình duyệt (T-508).
- Trạng thái sau khi máy chủ nhận (T-509).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
