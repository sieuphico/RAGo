# T-503 · Client API và bảng ánh xạ mã lỗi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | UX-06 |
| Quyết định kiến trúc | DD-06 |
| Phụ thuộc | [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md) |
| Mở khóa | [T-502](T-502-token-thiet-ke-khung-ung-dung-dieu-huong-theo-vai-tro.md), [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md), [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md), [T-521](T-521-telemetry-phia-giao-dien.md) |

## Mục tiêu

Một client gọi API; mã lỗi `{code}` ánh xạ sang thông báo tiếng Việt ở một nơi duy nhất.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2, 4.2, 5 (kiểu cần chép sang TS)
- CONTRACTS mục 3 (mã lỗi và thông báo)
- CONTRACTS mục 10.1, 10.4
- API thật do T-107 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md) Khung mã nguồn frontend và công cụ: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`

## File cần tạo hoặc sửa

- `frontend/src/api/types.ts`
- `frontend/src/api/client.ts`
- `frontend/src/api/errors.ts`
- `frontend/src/content/messages.ts`
- `frontend/src/__tests__/errors.spec.ts`
- `frontend/src/__tests__/client.spec.ts`

## Chữ ký và giao diện

```typescript
export class ApiError extends Error { constructor(public code: string, public retryable: boolean, public status?: number) }
export function request<T>(path: string, opts?: { method?: string; body?: unknown; signal?: AbortSignal }): Promise<T>
export function setAuthExpiredHandler(fn: () => void): void
export function messageFor(code: string): string
export function t(key: keyof typeof M, params?: Record<string, string | number>): string
```

## Các bước

1. `types.ts`: chép các kiểu ở CONTRACTS mục 10.1 (khóa camelCase đúng như JSON).
2. `messages.ts`: hằng `M` gồm đúng các khóa ở CONTRACTS mục 10.4; hàm `t(key, params?)` thay `{N}`, `{tên}`…
3. `errors.ts`: bảng `ERROR_MESSAGES: Record<string, string>` chép cột cuối CONTRACTS mục 3; thêm mã chỉ có ở giao diện `NETWORK` → `net.offline`; `messageFor(code)` trả thông báo, mã lạ → thông báo của `INTERNAL`.
4. `client.ts`: `request<T>(path, {method, body, signal})` gọi `fetch` với `credentials: "same-origin"`, JSON; phương thức khác `GET` thêm `X-Requested-With: cwd`; phản hồi lỗi đọc `{code, retryable}` thành `ApiError`; lỗi mạng → `ApiError("NETWORK", true)`; 204 trả `undefined`.
5. `setAuthExpiredHandler(fn)`: `request` gọi `fn()` khi nhận `AUTH_EXPIRED` (T-505 đăng ký; tránh nhập vòng).

## Tiêu chí hoàn thành

- [ ] Mọi mã ở CONTRACTS mục 3 có thông báo tiếng Việt (test liệt kê).
- [ ] Thêm mã lỗi mới chỉ cần sửa `errors.ts` (QA-04).
- [ ] Không thông báo nào chứa mã hay thuật ngữ kỹ thuật.
- [ ] `POST` có `X-Requested-With`, `GET` không có.
- [ ] Lỗi máy chủ thành `ApiError` đúng `code`, `retryable`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `every_error_code_has_message` | Danh sách 27 mã chép từ CONTRACTS mục 3 | `messageFor(code)` khác thông báo mặc định cho từng mã |
| `unknown_code_gets_generic_message` | `messageFor("ABC")` | "Đã có lỗi xảy ra. Vui lòng thử lại." |
| `no_technical_terms` | Mọi giá trị của `ERROR_MESSAGES` | Không chứa "500", "timeout", "token", "error" |
| `post_has_csrf_header` | `fetch` giả; `request("/x", {method: "POST", body: {}})` | Tiêu đề có `X-Requested-With: cwd`; với `GET` thì không |
| `error_body_to_api_error` | `fetch` giả trả 409 `{"code":"QUESTION_IN_PROGRESS","retryable":true}` | Ném `ApiError` có `code` và `retryable` đúng |
| `auth_expired_calls_handler` | Đăng ký handler; `fetch` giả trả 401 `AUTH_EXPIRED` | Handler được gọi 1 lần |
| `network_error` | `fetch` giả ném `TypeError` | `ApiError("NETWORK", true)` |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/errors.spec.ts
cd frontend && npx vitest run src/__tests__/client.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đọc luồng SSE (T-504).
- Luồng đăng nhập lại khi hết phiên (T-505).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
