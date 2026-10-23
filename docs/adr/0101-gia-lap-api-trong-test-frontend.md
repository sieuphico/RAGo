# ADR 0101: Giả lập API trong test frontend bằng fetch giả và vi.mock

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | Đã chấp nhận (chờ Trưởng đội kỹ thuật xác nhận cùng RP-07) |
| Ngày | 2026-10-23 |
| Task / Story | T-501, T-503 (áp dụng cho mọi task Pha 5) |
| Liên quan | CONTRACTS mục 10.6 |

## Bối cảnh
Backend chưa chạy cho frontend; chỉ có `/healthz`, `/auth/*`, `GET /api/v1/me`, `POST /api/v1/documents`, `GET /api/v1/admin/audit-log`. Mọi API khác phải được giả lập theo CONTRACTS mục 4. CONTRACTS 10.6 quy định `vi.mock("@/api/client")`; yêu cầu giao việc cho phép chọn giữa msw và fetch giả.

## Quyết định
- Không thêm `msw`. Dùng hai tầng:
  1. Test của `api/*` (client, SSE, telemetry): thay `globalThis.fetch` bằng `vi.fn()` (`vi.stubGlobal`) trả `Response` thật của jsdom/Node (`new Response(...)`, `ReadableStream` cho SSE).
  2. Test của store, thành phần, trang: `vi.mock("@/api/client")` (và `@/api/sse`, `@/api/telemetry` khi cần) theo CONTRACTS 10.6.
- `EventSource` (T-509) và `XMLHttpRequest` (T-523) được thay bằng lớp giả viết tay trong test (jsdom không có `EventSource`).
- Dùng `vi.useFakeTimers()` cho mọi logic thời gian.

## Lựa chọn đã xét
- `msw`: chặn mạng sát thực tế hơn nhưng thêm một thư viện ngoài danh sách T-501, cần service worker/Node interceptor, và SSE/XHR tiến độ khó mô tả hơn. Không chọn để giữ danh sách thư viện đã duyệt.
- Dev server giả (mock server riêng): thêm mã ngoài phạm vi; chưa cần vì Vite proxy trỏ về backend thật khi có.

## Hệ quả
- Không cần thư viện mới; test chạy nhanh và xác định.
- Hợp đồng chỉ được kiểm ở mức đường dẫn/JSON do test viết tay; tích hợp thật kiểm ở T-606/T-615.
- Chạy dev với API chưa có ở backend sẽ nhận lỗi 404 từ proxy; chưa có chế độ "mock trong trình duyệt" (ghi ở `frontend/OPEN_QUESTIONS.md`).
