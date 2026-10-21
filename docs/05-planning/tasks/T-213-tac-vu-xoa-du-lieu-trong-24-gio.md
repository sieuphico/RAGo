# T-213 · Tác vụ xóa dữ liệu trong 24 giờ

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W5–W6 (xem PLAN mục 6) |
| Story | US-064, US-016 |
| BR | BR-029 |
| NFR, EC, cổng | NFR-006 |
| Quyết định kiến trúc | AD-08 |
| Phụ thuộc | [T-203](T-203-xoa-tai-lieu-api-05.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-112](T-112-bo-noi-kho-tep-storageport.md) |
| Mở khóa | — |

## Mục tiêu

Sau khi xóa logic, xóa chunk, gợi ý và tệp gốc trong ≤ 24 giờ và ghi bằng chứng.

## File cần tạo hoặc sửa

- `backend/app/worker/purge.py`
- `backend/tests/integration/test_purge.py`

## Các bước

1. Handler `purge_document(doc_id)`: xóa `chunk`, `suggestion`, tệp gốc qua `StoragePort`, đặt `Document` thành `DELETED` (giữ hàng tối thiểu cho trích dẫn cũ).
2. Scheduler quét tài liệu `deleted_at` quá `purge_hours` mà chưa purge để tránh bỏ sót.
3. Ghi vào `audit` bản ghi `purge` làm bằng chứng cho AC-029.

## Tiêu chí hoàn thành

- [ ] 24 giờ sau khi xóa X, CSDL không còn chunk hay gợi ý gắn với X (AC-029).
- [ ] Tệp gốc bị xóa khỏi kho tệp.
- [ ] Trích dẫn cũ vẫn hiển thị "Tài liệu đã bị xóa" (EC-14).

## Kiểm thử cần viết

- `test_purge_removes_chunks_and_file`
- `test_scheduler_catches_missed_purge`
- `test_audit_purge_record`

## Lưu ý

Bản sao lưu là ngoại lệ đã ghi nhận (Q-A3), chờ Bảo mật thông tin duyệt.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
