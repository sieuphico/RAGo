# T-403 · Tóm tắt tài liệu (API-12)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 4 Tính năng P1 phía máy chủ |
| Ưu tiên | P1 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-040 |
| BR | BR-019 |
| NFR, EC, cổng | NFR-009 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-306](T-306-kiem-tra-va-anh-xa-trich-dan.md) |
| Mở khóa | [T-518](T-518-hop-thoai-tom-tat-tai-lieu.md) |

## Mục tiêu

Tạo bản tóm tắt một tài liệu có trích dẫn số trang.

## File cần tạo hoặc sửa

- `backend/app/modules/summary/service.py`
- `backend/app/api/summary.py`
- `backend/tests/integration/test_summary.py`

## Các bước

1. `POST /api/v1/documents/{id}/summary` lấy chunk của tài liệu theo trang, gọi AI theo cơ chế nhãn như T-305/T-306.
2. Tài liệu chưa `READY` trả lỗi rõ ràng.
3. Giới hạn số chunk gửi đi để kiểm soát chi phí.

## Tiêu chí hoàn thành

- [ ] Bản tóm tắt có trích dẫn số trang (US-040).
- [ ] Tài liệu chưa sẵn sàng bị từ chối.
- [ ] Nội dung gửi tới AI không chứa tên tệp.

## Kiểm thử cần viết

- `test_summary_has_citations`
- `test_summary_not_ready_rejected`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
