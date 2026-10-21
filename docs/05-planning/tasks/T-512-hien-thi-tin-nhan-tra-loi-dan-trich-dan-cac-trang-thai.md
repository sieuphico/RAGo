# T-512 · Hiển thị tin nhắn: trả lời dần, trích dẫn, các trạng thái

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 10 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | US-020, US-022, US-023, US-027 |
| BR | BR-010, BR-011, BR-013 |
| NFR, EC, cổng | EC-04, EC-06, EC-07, UX-07, UX-10 |
| Quyết định kiến trúc | DD-02, DD-03 |
| Phụ thuộc | [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md), [T-511](T-511-trang-hoi-dap-bo-cuc-va-o-nhap-s-03.md) |
| Mở khóa | [T-513](T-513-khung-xem-nguon-s-05.md), [T-517](T-517-thao-tac-tren-cau-tra-loi-sao-chep-va-danh-gia.md), [T-522](T-522-ra-soat-kha-nang-tiep-can-va-dap-ung.md), [T-606](T-606-kiem-thu-dau-cuoi-e2e-luong-p0.md) |

## Mục tiêu

Bong bóng câu hỏi, câu trả lời hiện dần với thẻ trích dẫn, và các trạng thái đang tìm, không tìm thấy, đã dừng, mất kết nối, lỗi.

## File cần tạo hoặc sửa

- `frontend/src/components/MessageList.vue`
- `frontend/src/components/AnswerBlock.vue`
- `frontend/src/components/CitationChip.vue`
- `frontend/src/components/AnswerState.vue`
- `frontend/src/__tests__/answer.spec.ts`

## Các bước

1. "Đang tìm trong N tài liệu…" trong ≤ 300 ms phía giao diện; sau 15 giây thêm "Câu hỏi đang mất nhiều thời gian hơn bình thường…"; sau 60 giây "Không thể trả lời lúc này" kèm [Thử lại].
2. Thẻ trích dẫn `[Tên tài liệu – tr. N]` là `button`, rút gọn giữa, tooltip hiện đoạn trích ≤ 200 ký tự khi di chuột hoặc focus.
3. "Không tìm thấy" dùng giao diện trung tính, không màu đỏ, kèm gợi ý; đứt giữa chừng giữ phần đã nhận kèm "Mất kết nối – câu trả lời chưa đầy đủ" và [Hỏi lại]; lỗi dịch vụ dùng thông báo từ bảng lỗi.
4. Danh sách `role="log"`; **không** đọc từng chữ, chỉ thông báo khi câu trả lời xong (Blueprint 3.8.2).

## Tiêu chí hoàn thành

- [ ] Câu trả lời có trích dẫn hiện từng phần và có đủ thẻ trích dẫn (US-022).
- [ ] "Không tìm thấy" không dùng màu đỏ (DD-03).
- [ ] Đứt kết nối giữ phần đã nhận và có [Hỏi lại] (UX-07).

## Kiểm thử cần viết

- `streams_text_and_citations`
- `not_found_is_neutral`
- `interrupted_keeps_partial`
- `announces_only_on_completion`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
