# T-509 · Cập nhật trạng thái tài liệu theo thời gian thực

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | US-012 |
| BR | BR-005 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-02 |
| Phụ thuộc | [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md), [T-504](T-504-client-luong-sse-post-cho-cau-tra-loi.md), [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) |
| Mở khóa | — |

## Mục tiêu

Huy hiệu tự đổi trạng thái qua SSE, không tải lại trang.

## File cần tạo hoặc sửa

- `frontend/src/composables/useDocumentEvents.ts`
- `frontend/src/__tests__/document_events.spec.ts`

## Các bước

1. Mở kết nối tới API-04 khi vào trang kho; cập nhật store theo sự kiện.
2. Khi SSE không dùng được, hỏi lại danh sách mỗi 3 giây.
3. Phát thông báo `aria-live` khi tài liệu chuyển `Sẵn sàng` hoặc `Thất bại`.

## Tiêu chí hoàn thành

- [ ] Đổi trạng thái ở máy chủ hiện ra không cần tải lại trang (AC của US-012).
- [ ] Có phương án hỏi lại khi SSE hỏng.
- [ ] Rời trang đóng kết nối.

## Kiểm thử cần viết

- `updates_badge_on_event`
- `falls_back_to_polling`
- `closes_on_unmount`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
