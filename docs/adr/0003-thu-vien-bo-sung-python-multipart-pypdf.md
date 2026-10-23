# ADR 0003: Thư viện bổ sung ngoài danh sách ban đầu

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | Đã chấp nhận (python-multipart, pypdf); reportlab chỉ cho dev, chờ người duyệt xác nhận |
| Ngày | 2026-10-23 |
| Task / Story | T-201, T-206, T-605 · US-010 |
| Liên quan | PLAN RP-07, Q-A9 |

## Bối cảnh
Danh sách thư viện được xác nhận (RP-07) chưa gồm gói nhận tệp tải lên và gói đọc PDF. AGENTS.md cấm thêm thư viện ngoài danh sách mà chưa hỏi.

## Quyết định
- **python-multipart**: FastAPI bắt buộc để nhận `multipart/form-data` (`UploadFile`). Không có phương án thay; thêm vào phụ thuộc chạy.
- **pypdf** (BSD, thuần Python): người dùng chọn ngày 2026-10-23 để trích văn bản theo trang ở T-206; thêm khi làm T-206. T-007 (khảo sát) đo lại sau.
- **reportlab** (BSD): chỉ trong `dev`, cho T-605 sinh PDF mẫu có font tiếng Việt (task T-605 tự đề xuất). Không vào ảnh chạy. Thêm 2026-10-23 để không chặn T-206; người duyệt có thể thay bằng thư viện khác. Test T-201 vẫn dùng PDF tối thiểu trong `tests/fixtures/pdfs.py`.

## Lựa chọn đã xét
Tự ghi bộ phân tích multipart (rủi ro bảo mật, không đáng); PyMuPDF (AGPL, cần Pháp chế).

## Hệ quả
`pyproject.toml` thêm `python-multipart`. `pyproject.toml` thêm `pypdf` (chạy) và `reportlab` (dev). PDF mẫu cần một font TTF hỗ trợ tiếng Việt trên máy chạy (Arial hoặc DejaVu Sans).
