# T-610 · Kiểm tra telemetry trên staging (G8)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | US-051 |
| BR | — |
| NFR, EC, cổng | G8 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-314](T-314-noi-telemetry-vao-cac-luong-chinh.md), [T-521](T-521-telemetry-phia-giao-dien.md), [T-613](T-613-dung-moi-truong-staging.md) |
| Mở khóa | [T-612](T-612-ho-tro-uat-va-sua-loi.md) |

## Mục tiêu

Danh sách kiểm tra mọi sự kiện P0 bắn đúng tên và thuộc tính, không có nội dung.

## File cần tạo hoặc sửa

- `docs/05-planning/evidence/telemetry-checklist.md`

## Các bước

1. Với mỗi sự kiện P0 ở PRD mục 5.2, thực hiện thao tác tương ứng trên staging và đối chiếu bản ghi.
2. Kiểm thử gói tin: không trường văn bản tự do.
3. Kiểm tra bảng số liệu US-051 hiển thị đúng theo dữ liệu vừa tạo.

## Tiêu chí hoàn thành

- [ ] 100% sự kiện P0 bắn đúng (G8).
- [ ] Bảng số liệu hoạt động.
- [ ] Danh sách kiểm tra được PM ký nhận.

## Kiểm thử cần viết

- Danh sách kiểm tra

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
