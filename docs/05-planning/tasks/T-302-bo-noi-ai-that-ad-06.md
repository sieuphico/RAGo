# T-302 · Bộ nối AI thật (AD-06)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 10 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-060, US-020 |
| BR | BR-017, BR-028 |
| NFR, EC, cổng | NFR-001 |
| Quyết định kiến trúc | AD-06 |
| Phụ thuộc | [T-005](T-005-khao-sat-nha-cung-cap-ai-ad-06.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md) |
| Mở khóa | [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-va-ocr-g3-g3b.md) |

## Mục tiêu

Cài đặt `AiPort` với nhà cung cấp đã chọn: nhúng theo lô và sinh câu trả lời dạng luồng.

## File cần tạo hoặc sửa

- `backend/app/adapters/ai_<provider>.py`
- `backend/tests/integration/test_ai_adapter.py`

## Các bước

1. Triển khai `embed` (theo lô) và `generate` (luồng token) với SDK hoặc HTTP của nhà cung cấp.
2. Khóa API chỉ đọc từ cấu hình (`Settings`), không có trong mã.
3. Chỉ gửi văn bản cần thiết; không gửi email, mã người dùng hay tên tệp.
4. Kiểm tra `embedding_dim` khớp với mô hình; không khớp thì dừng khi khởi động.

## Tiêu chí hoàn thành

- [ ] Có test tích hợp (đánh dấu cần khóa thật) chạy được trên môi trường thử.
- [ ] Lời gọi chỉ chứa văn bản câu hỏi hoặc chunk và chỉ dẫn hệ thống.
- [ ] Không có khóa nào trong kho mã hay nhật ký.

## Kiểm thử cần viết

- `test_embed_dimension`
- `test_generate_streams`
- `test_request_has_no_identifiers`

## Lưu ý

Chỉ bắt đầu sau khi chốt AD-06 (kết quả T-005) và có phê duyệt DEP-001 để dùng dữ liệu thật. Trước đó dùng `ai_fake`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
