# T-606 · Kiểm thử đầu cuối (E2E) luồng P0

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 10 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | BR-033 |
| NFR, EC, cổng | NFR-007, G1 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md), [T-508](T-508-tai-len-vung-keo-tha-kiem-tra-phia-trinh-duyet-trang-thai-tu.md), [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-trich-dan-cac-trang-thai.md), [T-513](T-513-khung-xem-nguon-s-05.md) |
| Mở khóa | [T-612](T-612-ho-tro-uat-va-sua-loi.md) |

## Mục tiêu

Kịch bản tự động chạy trên Chrome và Edge cho các luồng P0.

## File cần tạo hoặc sửa

- `frontend/e2e/login.spec.ts`
- `frontend/e2e/upload.spec.ts`
- `frontend/e2e/ask.spec.ts`
- `frontend/e2e/delete.spec.ts`
- `frontend/playwright.config.ts`

## Các bước

1. Dùng Playwright `[Đề xuất]` với backend và bộ nối giả (AI, OCR, SSO).
2. Kịch bản: đăng nhập và bị chặn khi không có quyền; tải lên tệp hợp lệ và không hợp lệ; hỏi đáp có trích dẫn và mở trang nguồn; xóa tài liệu; "không tìm thấy"; mất kết nối khi nhận câu trả lời. Kịch bản xóa tài liệu (US-016, P1) chỉ chạy khi T-510 đã xong.
3. Chạy ở độ rộng 1280, 1440, 1920 px trên Chrome và Edge (AC-033).

## Tiêu chí hoàn thành

- [ ] 100% kịch bản luồng chính đạt trên Chrome và Edge ở 3 độ rộng (AC-033).
- [ ] Kịch bản không phụ thuộc dịch vụ AI thật.
- [ ] Báo cáo kết quả được lưu cho G1.

## Kiểm thử cần viết

- Các kịch bản E2E

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
