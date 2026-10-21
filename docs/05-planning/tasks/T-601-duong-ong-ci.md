# T-601 · Đường ống CI

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | G7 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md), [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md) |
| Mở khóa | — |

## Mục tiêu

Mỗi thay đổi tự chạy lint, kiểm tra kiểu, test và build cho cả backend và frontend.

## File cần tạo hoặc sửa

- `ci/pipeline.yml`
- `Makefile`

## Các bước

1. Viết đường ống chạy `make lint type test` cho backend và `npm run lint type-check test build` cho frontend.
2. Đường ống dùng CSDL thử nghiệm dùng một lần cho test tích hợp.
3. Chặn gộp khi có kiểm tra bắt buộc thất bại; xuất báo cáo coverage.

## Tiêu chí hoàn thành

- [ ] Đường ống chạy xanh trên nhánh chính.
- [ ] Báo cáo coverage có sẵn để kiểm G7 (≥ 70% ở logic xử lý tài liệu và trích dẫn).
- [ ] Không có bí mật trong tệp cấu hình.

## Kiểm thử cần viết

- Kiểm bằng một lần chạy thật

## Lưu ý

Hệ thống CI tại chỗ chưa xác định `[TBD]`; hỏi đội IT. Có thể chỉ là một kịch bản chạy cục bộ nếu chưa có CI.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
