# T-511 · Trang Hỏi đáp: bố cục và ô nhập (S-03)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 10 giờ `[Đề xuất]` |
| Tuần dự kiến | W4–W5 (xem PLAN mục 6) |
| Story | US-020 |
| BR | BR-008, BR-013 |
| NFR, EC, cổng | EC-05, EC-11, UX-08 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md), [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) |
| Mở khóa | [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-trich-dan-cac-trang-thai.md), [T-514](T-514-chon-pham-vi-tai-lieu.md), [T-515](T-515-man-hinh-chao-va-goi-y-cau-hoi.md), [T-516](T-516-danh-sach-lich-su-s-06.md) |

## Mục tiêu

Bố cục ba vùng và ô nhập: Enter gửi, Shift+Enter xuống dòng, bộ đếm, nút Gửi/Dừng, bản nháp.

## File cần tạo hoặc sửa

- `frontend/src/views/ChatView.vue`
- `frontend/src/components/Composer.vue`
- `frontend/src/components/ChatSidebar.vue`
- `frontend/src/stores/chat.ts`
- `frontend/src/__tests__/composer.spec.ts`

## Các bước

1. Dựng theo prototype `docs/04-design/UI_UX_design/chat.html` và Blueprint 4.1.
2. Ô nhập: Enter gửi, Shift+Enter xuống dòng, phím `/` đưa con trỏ vào ô, bộ đếm `n/2.000` đổi màu cảnh báo khi vượt.
3. Nút Gửi vô hiệu khi trống hoặc quá dài; đổi thành [■ Dừng] khi đang tạo.
4. Bản nháp lưu `sessionStorage`, giữ khi mất mạng; dải "Mất kết nối" (EC-05).
5. Dòng nhắc "Câu trả lời do AI tạo – hãy kiểm tra trích dẫn với thông tin quan trọng." luôn hiện.

## Tiêu chí hoàn thành

- [ ] Ô trống hoặc chỉ khoảng trắng: Enter không gửi (AC US-020).
- [ ] Quá 2.000 ký tự: nút Gửi bị vô hiệu và bộ đếm cảnh báo (EC-11).
- [ ] Mất mạng: dải thông báo hiện, nội dung đang gõ được giữ (EC-05).

## Kiểm thử cần viết

- `enter_sends_shift_enter_newline`
- `blocks_empty_and_overlong`
- `keeps_draft_on_offline`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
