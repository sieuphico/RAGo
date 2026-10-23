# Báo cáo khả năng tiếp cận và đáp ứng (T-522)

Ghi tại `frontend/` (không ghi vào `docs/05-planning/evidence/` vì thư mục đó nằm ngoài quyền sửa của nhánh frontend; xem FQ-08).

## Đã kiểm (tự động, jsdom, `src/__tests__/a11y_static.spec.ts`)

| Màn hình | Kiểm tra | Kết quả |
|---|---|---|
| S-01, S-02, S-03 (có trả lời, trích dẫn, khung nguồn), S-04, S-07, S-08, S-09 | Đúng 1 `h1` và 1 `main#main`; mọi nút, ô nhập, liên kết, iframe có tên truy cập được; SVG trang trí `aria-hidden`; biểu đồ `role="img"` có `aria-label`; bảng có `caption` và `th[scope]` | Đạt |
| Toàn bộ mã nguồn | Không `v-html`; không URL `http(s)://` trong mã giao diện | Đạt |
| `base.css`, `tokens.css` | Vòng focus `:focus-visible` dùng `--focus-ring` (2 px primary, cách 2 px); `prefers-reduced-motion: reduce` tắt hoạt ảnh; `.table-wrap` cuộn ngang trong bảng, không cuộn trang | Đạt |
| Component | Hộp thoại `<dialog>` + `aria-modal`, focus mặc định ở "Hủy" khi phá hủy, `Esc` đóng, trả focus; khung nguồn dưới 1280 px là hộp thoại giam focus; vùng `aria-live` chỉ thông báo khi câu trả lời xong | Đạt (test đơn vị) |
| Điều hướng | Liên kết "Bỏ qua tới nội dung chính" là phần tử đầu tiên | Đạt |

Đã sửa trong lượt rà soát: S-03 thiếu `h1` (thêm `h1` ẩn "Hỏi đáp").

## Chưa kiểm được (cần môi trường thật)

- Quét axe (WCAG 2.1 AA, mức serious/critical) trên trình duyệt thật cho 8 trang: khung `frontend/e2e/a11y.spec.ts` đã viết nhưng **chưa chạy** vì cần `@playwright/test`, `@axe-core/playwright` (chưa được duyệt, FQ-07) và môi trường E2E của T-606.
- Không cuộn ngang ở 1024/1280/1440/1920 px; phóng to 200% ở 1280 px: jsdom không dàn trang; có trong khung E2E ở trên. Bố cục dùng lưới CSS theo ba mức độ rộng (≥ 1280, 1024–1279, < 1024) và `min-width: 0` ở các vùng co giãn.
- Tương phản màu: dùng nguyên token của Blueprint đã tính tương phản; chưa đo lại trên trang dựng.
- Trình đọc màn hình thật (NVDA, JAWS, VoiceOver): **chưa kiểm**.
- Luồng bàn phím đầy đủ trên trình duyệt thật (`/`, gõ, Enter, Tab tới thẻ trích dẫn, Enter, Esc, focus về thẻ): từng bước đã có test đơn vị, chưa chạy liền mạch trên trình duyệt.
- Edge, đo hiệu năng (UX-04): chưa đo.
