# T-605 · Dữ liệu mẫu và fixture kiểm thử

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | — |
| BR | BR-001, BR-027 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) |
| Mở khóa | [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md), [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-va-ocr-g3-g3b.md) |

## Mục tiêu

Sinh PDF mẫu (có lớp văn bản, nhiều trang, tiếng Việt có dấu, bản ảnh quét giả) để test tích hợp và thử tải.

## File cần tạo hoặc sửa

- `backend/scripts/make_sample_data.py`
- `backend/tests/fixtures/README.md`

## Các bước

1. Viết script tạo các PDF mẫu: 1 trang, 12 trang, 100 trang có văn bản; 1 bản ảnh quét (ảnh chứa chữ, không có lớp văn bản); 1 tệp hỏng; 1 tệp có mật khẩu.
2. Văn bản chứa nội dung biết trước (số hiệu hợp đồng, ngày, số tiền) để kiểm tra truy xuất và trích dẫn.
3. Thêm đích `make sample-data`.

## Tiêu chí hoàn thành

- [ ] Chạy script tạo đủ các loại tệp trong thư mục tạm.
- [ ] Mỗi tệp có nội dung chuẩn đi kèm để đối chiếu.
- [ ] Không dùng tài liệu thật của công ty.

## Kiểm thử cần viết

- `test_sample_files_generated`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
