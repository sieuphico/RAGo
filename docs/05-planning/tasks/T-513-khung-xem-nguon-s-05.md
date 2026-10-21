# T-513 · Khung xem nguồn (S-05)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 7 giờ `[Đề xuất]` |
| Tuần dự kiến | W7–W8 (xem PLAN mục 6) |
| Story | US-022 |
| BR | BR-010 |
| NFR, EC, cổng | EC-14, EC-19, UX-05 |
| Quyết định kiến trúc | AD-07 |
| Phụ thuộc | [T-212](T-212-tai-tep-pdf-cho-khung-xem-nguon-api-06.md), [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-trich-dan-cac-trang-thai.md) |
| Mở khóa | [T-522](T-522-ra-soat-kha-nang-tiep-can-va-dap-ung.md), [T-606](T-606-kiem-thu-dau-cuoi-e2e-luong-p0.md) |

## Mục tiêu

Mở đúng trang PDF khi bấm thẻ trích dẫn; chuyển trang; `Esc` đóng; lớp phủ dưới 1280 px.

## File cần tạo hoặc sửa

- `frontend/src/components/SourceViewer.vue`
- `frontend/src/__tests__/source_viewer.spec.ts`

## Các bước

1. Dùng trình xem PDF của trình duyệt mở tại trang N (`#page=N`) trên API-06 (AD-07, đã xác nhận); không thêm thư viện PDF.
2. Có nút trang trước/sau, đóng và `Esc`; trả focus cho thẻ trích dẫn đã mở.
3. Dưới 1280 px hiển thị dạng lớp phủ toàn khung (EC-19).
4. Trạng thái lỗi "Không mở được trang. [Thử lại]"; tài liệu đã xóa: "Tài liệu đã bị xóa" (EC-14).

## Tiêu chí hoàn thành

- [ ] Bấm trích dẫn mở đúng tài liệu và đúng trang trong ≤ 3 giây (US-022).
- [ ] `Esc` đóng và trả focus.
- [ ] Dưới 1280 px thành lớp phủ, không cuộn ngang (UX-05).

## Kiểm thử cần viết

- `opens_at_cited_page`
- `esc_closes_and_restores_focus`
- `overlay_below_1280`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
