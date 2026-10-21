# T-201 · Tải lên tài liệu (API-02)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-010, US-011, US-014 |
| BR | BR-001, BR-002, BR-003, BR-004 |
| NFR, EC, cổng | NFR-004, EC-08 |
| Quyết định kiến trúc | DD-05 |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-112](T-112-bo-noi-kho-tep-storageport.md), [T-204](T-204-hang-doi-tac-vu-jobs.md) |
| Mở khóa | [T-314](T-314-noi-telemetry-vao-cac-luong-chinh.md), [T-508](T-508-tai-len-vung-keo-tha-kiem-tra-phia-trinh-duyet-trang-thai-tu.md), [T-609](T-609-kiem-tra-bao-mat-g6.md) |

## Mục tiêu

Nhận 1–10 tệp, kiểm tra lại ở máy chủ, lưu tệp, tạo bản ghi `Processing`, đưa tác vụ xử lý vào hàng đợi, trả 202.

## File cần tạo hoặc sửa

- `backend/app/modules/documents/service.py`
- `backend/app/api/documents.py`
- `backend/tests/integration/test_upload_api.py`

## Chữ ký và giao diện

```python
async def upload_documents(files: list[UploadFile], actor: User) -> list[UploadResult]: ...
```

## Các bước

1. `POST /api/v1/documents` (multipart) chỉ cho vai trò TEAM_LEAD (BRU-007).
2. Kiểm tra từng tệp: đuôi `.pdf`, ≤ 50 MB, nội dung bắt đầu bằng `%PDF-` (không chỉ tin đuôi); > 10 tệp trả `FILE_TOO_MANY`.
3. Tệp hợp lệ: lưu qua `StoragePort`, tạo `Document(status=PROCESSING, size_bytes)`, `enqueue("ingest", doc_id)`, ghi nhật ký `upload`.
4. Phản hồi 202 gồm danh sách `{docId, name, status}` và lỗi riêng từng tệp không hợp lệ (tệp hợp lệ vẫn được nhận).

## Tiêu chí hoàn thành

- [ ] Tệp `.docx`, `.xlsx`, `.png` bị từ chối, kho không đổi (AC-003).
- [ ] PDF 51 MB bị từ chối, PDF 49 MB được nhận (AC-004).
- [ ] Tệp đổi đuôi `.pdf` nhưng không phải PDF bị từ chối với `FILE_NOT_PDF`.
- [ ] Người dùng không phải TEAM_LEAD nhận 403.

## Kiểm thử cần viết

- `test_upload_valid_pdf_202`
- `test_reject_non_pdf_magic`
- `test_reject_oversize`
- `test_batch_partial_valid`
- `test_non_team_lead_forbidden`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
