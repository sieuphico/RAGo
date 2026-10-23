# T-504 · Client luồng SSE (POST) cho câu trả lời

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W2–W3 (xem PLAN mục 6) |
| Story | US-027 |
| BR | BR-013 |
| NFR, EC, cổng | EC-04 |
| Quyết định kiến trúc | AD-02 |
| Phụ thuộc | [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) |
| Mở khóa | [T-509](T-509-cap-nhat-trang-thai-tai-lieu-theo-thoi-gian-thuc.md), [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md), [T-524](T-524-hoi-dap-2-3-o-nhap-va-gui-cau-hoi.md) |

## Mục tiêu

Đọc luồng SSE từ yêu cầu POST bằng `fetch` (không dùng `EventSource`), hỗ trợ hủy và phát hiện đứt kết nối.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 5 (định dạng khung SSE, sự kiện API-08)
- Chữ ký `request`, `ApiError` ở T-503

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) Client API và bảng ánh xạ mã lỗi: `ApiError`, `request`, `setAuthExpiredHandler`, `messageFor`, `t`

## File cần tạo hoặc sửa

- `frontend/src/api/sse.ts`
- `frontend/src/__tests__/sse.spec.ts`

## Chữ ký và giao diện

```typescript
export interface StreamHandlers {
  onStatus(d: StatusData): void; onToken(d: TokenData): void; onCitation(d: CitationData): void
  onDone(d: DoneData): void; onError(d: ErrorData): void; onInterrupted(): void
}
export function streamPost(path: string, body: unknown, h: StreamHandlers, signal: AbortSignal): Promise<void>
```

## Các bước

1. `streamPost(path, body, h, signal)`: `fetch` POST với `credentials: "same-origin"`, `Content-Type: application/json`, `X-Requested-With: cwd`, `Accept: text/event-stream`.
2. Phản hồi không phải 200 hoặc `Content-Type` không phải `text/event-stream` → đọc JSON lỗi và ném `ApiError` (chưa gọi handler nào).
3. Đọc `body.getReader()` qua `TextDecoder` (`stream: true`); tách khung theo `\n\n` (chấp nhận cả `\r\n\r\n`); dòng bắt đầu bằng `:` bỏ qua; ghép nhiều dòng `data:` của một khung bằng `\n`.
4. `event` → handler: `status` → `onStatus`, `token` → `onToken`, `citation` → `onCitation`, `done` → `onDone`, `error` → `onError`; tên lạ bỏ qua.
5. Luồng kết thúc (hoặc `read()` lỗi) mà chưa gặp `done`/`error` → `onInterrupted()` (EC-04). `signal` bị hủy → dừng đọc, không gọi `onInterrupted`.

## Tiêu chí hoàn thành

- [ ] Phân tích đúng khung bị chia cắt ở bất kỳ vị trí byte nào, kể cả giữa ký tự UTF-8 nhiều byte.
- [ ] Đứt kết nối trước `done` gọi `onInterrupted` đúng 1 lần.
- [ ] Hủy dừng đọc ngay.
- [ ] Lỗi HTTP trước luồng thành `ApiError`, không gọi handler.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `parses_split_frames` | Luồng giả gồm `event: token\ndata: {"text":"Hợ` và `p đồng"}\n\n` (cắt giữa ký tự `ợ`) | `onToken` nhận `{text: "Hợp đồng"}` đúng 1 lần |
| `ignores_comments` | Luồng có dòng `: ping\n\n` giữa hai khung | Không handler nào được gọi cho dòng đó |
| `dispatch_all_events` | Khung `status`, `citation`, `token`, `done` | 4 handler được gọi đúng thứ tự |
| `interrupt_before_done` | Luồng kết thúc sau `token`, không có `done` | `onInterrupted` gọi 1 lần |
| `abort_stops_stream` | Gọi `controller.abort()` sau khung đầu | Không handler nào được gọi thêm; không gọi `onInterrupted` |
| `http_error_before_stream` | Phản hồi 409 JSON `QUESTION_IN_PROGRESS` | Ném `ApiError("QUESTION_IN_PROGRESS", true)` |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/sse.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Cập nhật tin nhắn trong store (T-524).
- Luồng trạng thái tài liệu dùng `EventSource` (T-509).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
