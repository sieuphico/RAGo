# T-501 · Khung mã nguồn frontend và công cụ

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | NFR-007, NFR-008 |
| Quyết định kiến trúc | — |
| Phụ thuộc | — |
| Mở khóa | [T-502](T-502-token-thiet-ke-khung-ung-dung-dieu-huong-theo-vai-tro.md), [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md), [T-601](T-601-duong-ong-ci.md), [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) |

## Mục tiêu

Tạo `frontend/` bằng Vue 3 và TypeScript; lint, kiểm tra kiểu và test chạy được.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 10.6 (quy ước giao diện)
- PLAN.md mục 3.1

## File cần tạo hoặc sửa

- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/src/main.ts`
- `frontend/src/App.vue`
- `frontend/src/__tests__/app.spec.ts`

## Chữ ký và giao diện

```typescript
// src/main.ts
createApp(App).use(createPinia()).use(router).mount("#app")
```

## Các bước

1. Khởi tạo bằng Vite + Vue 3 + TypeScript; cài Vue Router, Pinia, Vitest, `@vue/test-utils`, `jsdom`, ESLint (cấu hình `@vue/eslint-config-typescript`) `[Đề xuất]`.
2. `vite.config.ts`: alias `@` → `src`; máy chủ phát triển chuyển tiếp `/api` và `/auth` tới `http://localhost:8000`.
3. Chỉ dùng thư viện chạy cục bộ; không tải font hay script từ bên thứ ba; dùng font hệ thống.
4. Thêm script `lint`, `type-check` (`vue-tsc --noEmit`), `test` (`vitest run`), `build`.
5. `main.ts` gắn Pinia, router (rỗng tạm thời) và `App.vue`.

## Tiêu chí hoàn thành

- [ ] `npm run lint type-check test build` đều trả mã 0.
- [ ] Thư mục `dist/` không chứa URL `http://` hay `https://` tới tên miền ngoài.
- [ ] Không có bí mật trong mã.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| app mounts | `mount(App)` với Pinia và router thử | Không lỗi; có phần tử `#app` con |
| Kiểm tra gói | Sau `npm run build`, tìm `https?://` trong `dist/**/*.js` | Không có kết quả trừ chú thích giấy phép |
| Kiểm tra lệnh | Máy sạch: `npm ci && npm run lint type-check test build` | Mã 0 |

## Lệnh kiểm tra

```bash
cd frontend && npx vitest run src/__tests__/app.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Token và khung ứng dụng (T-502).
- Client API (T-503).
- CI (T-601).

## Lưu ý

Pinia, Vue Router, Vitest, ESLint là đề xuất mặc định; Trưởng đội kỹ thuật xác nhận ở tuần 1.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
