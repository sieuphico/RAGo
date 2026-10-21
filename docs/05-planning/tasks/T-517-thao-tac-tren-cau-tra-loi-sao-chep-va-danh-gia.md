# T-517 · Thao tác trên câu trả lời: sao chép và đánh giá

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-042, US-050 |
| BR | BR-022, BR-023 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-313](T-313-danh-gia-api-11.md), [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-trich-dan-cac-trang-thai.md) |
| Mở khóa | — |

## Mục tiêu

Nút Sao chép kèm nguồn và 👍/👎 kèm hộp thoại lý do.

## File cần tạo hoặc sửa

- `frontend/src/components/AnswerActions.vue`
- `frontend/src/components/RatingDialog.vue`
- `frontend/src/__tests__/answer_actions.spec.ts`

## Các bước

1. Sao chép văn bản thuần kèm "Nguồn: [1] Tên tài liệu, tr. N"; có phương án thay khi `navigator.clipboard` không dùng được; toast "Đã sao chép".
2. 👍 gửi ngay; 👎 mở hộp thoại lý do tùy chọn (Sai thông tin, Trích dẫn sai, Thiếu ý, Khác) với [Bỏ qua] và [Gửi]; cả hai đều ghi nhận 👎.
3. Ghi sự kiện `answer_copied` và `answer_rated` qua T-521.

## Tiêu chí hoàn thành

- [ ] Nội dung dán chứa đủ câu trả lời và trích dẫn (AC-022).
- [ ] Hộp thoại 👎 cho phép bỏ qua lý do.
- [ ] Nút có nhãn đọc được bằng trình đọc màn hình.

## Kiểm thử cần viết

- `copy_includes_sources`
- `rating_dialog_skip_still_records`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
