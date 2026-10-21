# T-515 · Màn hình chào và gợi ý câu hỏi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W10 (xem PLAN mục 6) |
| Story | US-030, US-031 |
| BR | BR-020, BR-035 |
| NFR, EC, cổng | EC-01, EC-02, UX-01 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-402](T-402-goi-y-cau-hoi-mau-api-17.md), [T-511](T-511-trang-hoi-dap-bo-cuc-va-o-nhap-s-03.md) |
| Mở khóa | — |

## Mục tiêu

Màn hình chào lần đầu và khối "Gợi ý câu hỏi" bấm một lần để hỏi.

## File cần tạo hoặc sửa

- `frontend/src/components/WelcomePanel.vue`
- `frontend/src/__tests__/welcome.spec.ts`

## Các bước

1. Hiển thị số tài liệu sẵn sàng và 3 gợi ý lấy từ API-17; bấm gợi ý gửi ngay.
2. Kho trống hiện "Kho chưa có tài liệu." kèm [Tải PDF lên] nếu có quyền, ô nhập bị vô hiệu (EC-01).
3. Tài liệu đang xử lý: "N tài liệu đang được xử lý, chưa dùng để trả lời." (EC-02).

## Tiêu chí hoàn thành

- [ ] Người dùng mới thấy số tài liệu và ≥ 3 gợi ý (AC-035).
- [ ] Kho trống không hiện gợi ý và vô hiệu ô nhập.
- [ ] Bấm gợi ý gửi câu hỏi đúng nội dung.

## Kiểm thử cần viết

- `shows_three_suggestions`
- `empty_library_disables_input`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
