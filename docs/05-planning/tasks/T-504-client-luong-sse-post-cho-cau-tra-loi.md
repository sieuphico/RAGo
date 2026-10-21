# T-504 · Client luồng SSE (POST) cho câu trả lời

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-027 |
| BR | BR-013 |
| NFR, EC, cổng | EC-04 |
| Quyết định kiến trúc | AD-02 |
| Phụ thuộc | [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) |
| Mở khóa | [T-509](T-509-cap-nhat-trang-thai-tai-lieu-theo-thoi-gian-thuc.md), [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-trich-dan-cac-trang-thai.md) |

## Mục tiêu

Đọc luồng SSE từ yêu cầu POST bằng `fetch` (không dùng `EventSource`), hỗ trợ hủy và phát hiện đứt kết nối.

## File cần tạo hoặc sửa

- `frontend/src/api/sse.ts`
- `frontend/src/__tests__/sse.spec.ts`

## Chữ ký và giao diện

```typescript
export function streamPost(path: string, body: unknown, h: StreamHandlers, signal: AbortSignal): Promise<void>
```

## Các bước

1. `streamPost(path, body, handlers, signal)` phân tích khung `event:` và `data:` từ `ReadableStream`.
2. Gọi `onStatus`, `onToken`, `onCitation`, `onDone`, `onError`.
3. Kết nối đóng trước `done` thì gọi `onInterrupted()` (EC-04).
4. Hỗ trợ `AbortController` để dừng.

## Tiêu chí hoàn thành

- [ ] Phân tích đúng khung SSE bị chia cắt ở ranh giới gói.
- [ ] Đứt kết nối trước `done` gọi `onInterrupted`.
- [ ] Hủy dừng ngay việc đọc.

## Kiểm thử cần viết

- `parses_split_frames`
- `interrupt_before_done`
- `abort_stops_stream`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
