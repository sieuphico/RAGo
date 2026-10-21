# T-522 · Rà soát khả năng tiếp cận và đáp ứng

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | BR-033 |
| NFR, EC, cổng | UX-03, UX-05, NFR-007 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-trich-dan-cac-trang-thai.md), [T-513](T-513-khung-xem-nguon-s-05.md) |
| Mở khóa | — |

## Mục tiêu

Kiểm tra và sửa theo WCAG 2.1 AA, bàn phím, độ rộng 1024 – 1920 px.

## File cần tạo hoặc sửa

- `frontend/src/__tests__/a11y.spec.ts`
- `docs/05-planning/evidence/a11y-report.md`

## Các bước

1. Quét tự động (axe) các trang chính; sửa mọi lỗi Serious và Critical.
2. Kiểm tra bằng bàn phím luồng hỏi đáp: Tab theo thứ tự trực quan, vòng focus luôn thấy, `Esc` đóng viewer và hộp thoại.
3. Kiểm tra bố cục ở 1024, 1280, 1440, 1920 px: không cuộn ngang.
4. Kiểm tra `prefers-reduced-motion` và phóng to 200%.

## Tiêu chí hoàn thành

- [ ] 0 lỗi mức Serious hay Critical khi quét tự động (UX-03).
- [ ] Không cuộn ngang ở các độ rộng yêu cầu (UX-05).
- [ ] Báo cáo ghi rõ phần chưa kiểm bằng trình đọc màn hình thật.

## Kiểm thử cần viết

- `axe scan of main views`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
