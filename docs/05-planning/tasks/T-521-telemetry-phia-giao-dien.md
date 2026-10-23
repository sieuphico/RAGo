# T-521 · Telemetry phía giao diện

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-051 |
| BR | — |
| NFR, EC, cổng | NFR-008 |
| Quyết định kiến trúc | AD-10 |
| Phụ thuộc | [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) |
| Mở khóa | [T-508](T-508-tai-len-1-2-vung-keo-tha-va-kiem-tra-o-trinh-duyet.md), [T-513](T-513-khung-xem-nguon-s-05.md), [T-515](T-515-man-hinh-chao-va-goi-y-cau-hoi.md), [T-517](T-517-thao-tac-tren-cau-tra-loi-sao-chep-va-danh-gia.md), [T-523](T-523-tai-len-2-2-hang-doi-tien-do-va-thu-lai-tung-tep.md), [T-610](T-610-kiem-tra-telemetry-tren-staging-g8.md) |

## Mục tiêu

Gửi các sự kiện phía giao diện qua API-16, chỉ siêu dữ liệu.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 6 (6 sự kiện nguồn "giao diện")
- CONTRACTS mục 4.1 API-16
- API thật do T-113 làm; task này test bằng API giả theo CONTRACTS, tích hợp thật kiểm ở T-606/T-615

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) Client API và bảng ánh xạ mã lỗi: `ApiError`, `request`, `setAuthExpiredHandler`, `messageFor`, `t`

## File cần tạo hoặc sửa

- `frontend/src/api/telemetry.ts`
- `frontend/src/__tests__/telemetry.spec.ts`

## Chữ ký và giao diện

```typescript
export function track(event: ClientEvent, props: Record<string, string | number | boolean>): void
```

## Các bước

1. `CLIENT_SCHEMA` mô tả 6 sự kiện nguồn "giao diện" ở CONTRACTS mục 6: tên thuộc tính, kiểu (`int`, `float`, `uuid`, `enum`), giá trị cho phép.
2. `track(event, props)`: sự kiện không có trong lược đồ, thiếu hoặc thừa thuộc tính, sai kiểu → bỏ và `console.warn` ở chế độ phát triển; không gửi.
3. Gửi bằng `fetch("/api/v1/telemetry/events", {method: "POST", keepalive: true, credentials: "same-origin", headers: {"Content-Type": "application/json", "X-Requested-With": "cwd"}})`. **Không** dùng `navigator.sendBeacon` vì không gắn được tiêu đề CSRF.
4. Lỗi gửi bị nuốt; không hiển thị gì cho người dùng; không thử lại.

## Tiêu chí hoàn thành

- [ ] Không sự kiện nào chứa văn bản câu hỏi, câu trả lời hay tên tệp (lược đồ không có trường chuỗi tự do).
- [ ] Sự kiện sai lược đồ bị loại ở giao diện.
- [ ] Lỗi mạng không hiện lỗi cho người dùng.
- [ ] Yêu cầu có tiêu đề `X-Requested-With: cwd`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `rejects_free_text_props` | `track("citation_clicked", {question_id: "m1", doc_id: "d1", page: 3, text: "abc"})` | `fetch` không được gọi |
| `rejects_unknown_event` | `track("answer_completed", {...})` (sự kiện máy chủ) | `fetch` không được gọi |
| `sends_valid_event` | `track("answer_copied", {question_id: "<uuid>"})` | `fetch` gọi 1 lần với `keepalive: true`, tiêu đề `X-Requested-With: cwd`, thân `{"event":"answer_copied","props":{...}}` |
| `failure_is_silent` | `fetch` giả ném lỗi | `track` không ném; không có toast |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/telemetry.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Lược đồ và ghi phía máy chủ (T-113).
- Gọi `track` ở từng màn hình (T-508, T-513, T-515, T-517, T-523).

## Lưu ý

Quy ước giao diện ở CONTRACTS mục 10.6: `<script setup lang="ts">`, store Pinia kiểu setup, mọi chuỗi hiển thị lấy từ `content/messages.ts`, test bằng Vitest + `@vue/test-utils`, giả lập API bằng `vi.mock("@/api/client")`, phần tử test dùng `data-testid`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
