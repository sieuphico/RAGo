# T-112 · Bộ nối kho tệp (StoragePort)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-010, US-022 |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-11 |
| Phụ thuộc | [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) |
| Mở khóa | [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-206](T-206-ingest-trich-van-ban-theo-trang.md), [T-212](T-212-tai-tep-pdf-cho-khung-xem-nguon-api-06.md), [T-213](T-213-tac-vu-xoa-du-lieu-trong-24-gio.md) |

## Mục tiêu

Lưu, đọc theo khoảng byte và xóa tệp PDF trên đĩa; an toàn với đường dẫn.

## File cần tạo hoặc sửa

- `backend/app/adapters/storage_fs.py`
- `backend/tests/unit/test_storage_fs.py`

## Các bước

1. Triển khai `StoragePort` với thư mục gốc `storage_root`.
2. Tạo khóa tệp bằng UUID, không dùng tên tệp người dùng; từ chối khóa chứa `..` hoặc đường dẫn tuyệt đối.
3. `read(key, start, end)` đọc đúng khoảng byte (phục vụ API-06).
4. Ghi tệp nguyên tử (ghi tạm rồi đổi tên).

## Tiêu chí hoàn thành

- [ ] Không thể đọc hay ghi ngoài `storage_root`.
- [ ] Đọc theo khoảng byte trả đúng nội dung.
- [ ] Xóa tệp không tồn tại không ném lỗi.

## Kiểm thử cần viết

- `test_path_traversal_rejected`
- `test_range_read`
- `test_delete_missing_ok`

## Lưu ý

Kho tệp là đĩa mã hóa hay NAS vẫn là câu hỏi Q-A8; bộ nối chỉ cần thư mục gắn sẵn.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
