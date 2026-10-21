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
| Mở khóa | [T-502](T-502-token-thiet-ke-khung-ung-dung-dieu-huong-theo-vai-tro.md), [T-601](T-601-duong-ong-ci.md), [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) |

## Mục tiêu

Tạo `frontend/` bằng Vue 3 và TypeScript; lint, kiểm tra kiểu và test chạy được.

## File cần tạo hoặc sửa

- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/src/main.ts`
- `frontend/src/App.vue`
- `frontend/src/__tests__/app.spec.ts`

## Các bước

1. Khởi tạo bằng Vite, Vue 3, TypeScript, Vue Router, Pinia, Vitest, ESLint `[Đề xuất]`.
2. Chỉ dùng thư viện chạy cục bộ; không tải font hay script từ bên thứ ba (riêng tư).
3. Thêm script `lint`, `type-check`, `test`, `build`.
4. Một test mount `App.vue`.

## Tiêu chí hoàn thành

- [ ] `npm run lint type-check test build` đều đạt.
- [ ] Gói tạo ra là tệp tĩnh không phụ thuộc CDN ngoài.
- [ ] Không có bí mật trong mã.

## Kiểm thử cần viết

- `app mounts`

## Lưu ý

Pinia, Vue Router, Vitest, ESLint là đề xuất mặc định; Trưởng đội kỹ thuật xác nhận ở tuần 1.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
