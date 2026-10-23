# ADR 0002: Engine CSDL tạo lười và CSDL dev ở cổng 5433

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | Đã chấp nhận |
| Ngày | 2026-10-23 |
| Task / Story | T-003 |
| Liên quan | CONTRACTS mục 2.2 |

## Bối cảnh
T-003 yêu cầu `engine` và `SessionLocal` ở cấp module và PostgreSQL dev ở cổng 5432. Tạo engine lúc nhập cần `Settings` đầy đủ, làm hỏng test đơn vị không có biến môi trường. Máy phát triển có PostgreSQL cài sẵn giữ cổng 5432.

## Quyết định
- `engine`, `SessionLocal` tạo lười qua `__getattr__` của module `app.core.db`; `get_session()` không đổi.
- `deploy/compose.dev.yml` ánh xạ cổng 5433; test mặc định dùng `localhost:5433` (`CWD_TEST_DATABASE_URL` đổi được).

## Lựa chọn đã xét
Tạo engine ngay khi nhập (đúng chữ task nhưng ép mọi test có đủ cấu hình); dừng PostgreSQL cài sẵn của người dùng (không được phép).

## Hệ quả
Chữ ký công khai không đổi. Task T-003 trong docs ghi 5432; sai lệch này chỉ có ở ADR, chờ người duyệt cập nhật docs.
