# ADR 0003: Thư viện bổ sung ngoài danh sách ban đầu

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | Đã chấp nhận (python-multipart, pypdf); đề xuất (reportlab) |
| Ngày | 2026-10-23 |
| Task / Story | T-201, T-206, T-605 · US-010 |
| Liên quan | PLAN RP-07, Q-A9 |

## Bối cảnh
Danh sách thư viện được xác nhận (RP-07) chưa gồm gói nhận tệp tải lên và gói đọc PDF. AGENTS.md cấm thêm thư viện ngoài danh sách mà chưa hỏi.

## Quyết định
- **python-multipart**: FastAPI bắt buộc để nhận `multipart/form-data` (`UploadFile`). Không có phương án thay; thêm vào phụ thuộc chạy.
- **pypdf** (BSD, thuần Python): người dùng chọn ngày 2026-10-23 để trích văn bản theo trang ở T-206; thêm khi làm T-206. T-007 (khảo sát) đo lại sau.
- **reportlab** (cho T-605, sinh PDF mẫu có font tiếng Việt): **chưa thêm**, chờ xác nhận. Test T-201 dùng PDF tối thiểu tạo bằng mã thuần trong `tests/fixtures/pdfs.py`.

## Lựa chọn đã xét
Tự ghi bộ phân tích multipart (rủi ro bảo mật, không đáng); PyMuPDF (AGPL, cần Pháp chế).

## Hệ quả
`pyproject.toml` thêm `python-multipart`. Việc thêm `pypdf` và quyết định về `reportlab` ghi lại ở đây khi xảy ra.
