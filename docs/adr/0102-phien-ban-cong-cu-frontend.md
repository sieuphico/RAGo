# ADR 0102: Phiên bản công cụ frontend

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | Đã chấp nhận (chờ Trưởng đội kỹ thuật xác nhận cùng RP-07) |
| Ngày | 2026-10-23 |
| Task / Story | T-501 |
| Liên quan | PLAN RP-07, CONTRACTS mục 10.6 |

## Bối cảnh
T-501 nêu danh sách thư viện (Vue 3, Vite, TypeScript, Pinia, Vue Router, Vitest, `@vue/test-utils`, `jsdom`, ESLint, `vue-tsc`) nhưng không nêu phiên bản. Kho npm có các bản mới hơn (TypeScript 7, Vite 8, Vitest 5, ESLint 10) chưa được đội kiểm chứng.

## Quyết định
Ghim dòng phiên bản đã quen dùng: Vue 3.5, Vue Router 4, Pinia 3, Vite 7, Vitest 3, TypeScript 5.9, ESLint 9 (cấu hình phẳng, `@vue/eslint-config-typescript`), `vue-tsc` 3, `jsdom` 26. Thêm `@types/node` (chỉ kiểu, cho `vite.config.ts`). Không thêm Prettier (T-501 không nêu). `npm run build` chạy thêm `scripts/check-dist.mjs` để thực hiện kiểm tra gói của T-501 (không có URL ngoài trong `dist/`; chỉ cho phép URL không gian tên w3.org và liên kết tài liệu trong chuỗi lỗi của Vue).

## Lựa chọn đã xét
Dùng bản mới nhất của mọi gói: rủi ro không tương thích giữa các công cụ và chưa có bằng chứng lợi ích cho MVP.

## Hệ quả
Nâng phiên bản chính là một thay đổi riêng, kèm chạy lại bốn cổng. Script `esbuild` postinstall bị npm 12 chặn mặc định; xây dựng vẫn chạy được vì gói nhị phân theo nền tảng được cài sẵn.
