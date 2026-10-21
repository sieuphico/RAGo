# T-516 · Danh sách lịch sử (S-06)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W10 (xem PLAN mục 6) |
| Story | US-041 |
| BR | BR-021 |
| NFR, EC, cổng | EC-14 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-401](T-401-lich-su-hoi-thoai-api-10-va-het-han-90-ngay.md), [T-511](T-511-trang-hoi-dap-bo-cuc-va-o-nhap-s-03.md) |
| Mở khóa | — |

## Mục tiêu

Danh sách phiên nhóm theo Hôm nay, 7 ngày qua, Cũ hơn và mở lại phiên.

## File cần tạo hoặc sửa

- `frontend/src/components/HistoryList.vue`
- `frontend/src/__tests__/history.spec.ts`

## Các bước

1. Gọi API-10; nhóm theo thời gian; tiêu đề là 60 ký tự đầu của câu hỏi đầu.
2. Mở phiên nạp lại câu hỏi, câu trả lời, trích dẫn; trích dẫn tới tài liệu đã xóa hiện "Tài liệu đã bị xóa".
3. Trạng thái: khung xương 3 dòng, "Chưa có phiên nào", "Không tải được lịch sử. [Thử lại]".

## Tiêu chí hoàn thành

- [ ] Mở lại được phiên trước sau khi đăng nhập lại (AC-021).
- [ ] Có đủ trạng thái trống, tải, lỗi.
- [ ] Thẻ trích dẫn tài liệu đã xóa không mở được.

## Kiểm thử cần viết

- `groups_by_time`
- `reopens_session_with_citations`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
