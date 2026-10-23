---
description: Sinh test cho một task hoặc module theo bảng "Kiểm thử cần viết"
argument-hint: <T-xxx | đường dẫn module>
---

Viết test cho **$ARGUMENTS**.

1. Nếu là mã task: đọc `docs/05-planning/tasks/$ARGUMENTS-*.md`, lấy bảng "Kiểm thử cần viết". Nếu là đường dẫn: đọc module và test hiện có.
2. Mỗi dòng của bảng thành đúng một test, tên và tình huống khớp bảng, kết quả mong đợi khớp từng chữ. Không thêm test cho AC `[Đề xuất]` hay ngưỡng % (xem AGENTS.md).
3. Đặt test ở `tests/unit/` (không cần CSDL) hoặc `tests/integration/` (dùng fixture `session` trong `tests/conftest.py`, cần `make db-up`). Chỉ sửa trong `tests/`.
4. Dùng bộ nối giả; không gọi dịch vụ ngoài; hàm cần thời gian nhận `now`/`clock`.
5. Chạy `make gate` (hoặc `ruff`, `mypy app tests`, `pytest -q`) và báo kết quả thật. Test mới phải **đỏ trước khi có code** nếu code chưa tồn tại, rồi xanh sau khi code xong.
6. Cập nhật cột "Test" của `docs/traceability.md`.
