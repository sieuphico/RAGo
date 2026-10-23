# ADR 0001: Mã backend ở gốc kho (`app/`, `tests/`)

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | Đã chấp nhận |
| Ngày | 2026-10-23 |
| Task / Story | T-001 |
| Liên quan | PLAN mục 3.1 |

## Bối cảnh
PLAN 3.1 đặt backend trong `backend/`. Người dùng yêu cầu `app/`, `tests/` ở gốc kho.

## Quyết định
`app/`, `tests/`, `migrations/`, `pyproject.toml` ở gốc. Frontend sau này ở `frontend/`.

## Lựa chọn đã xét
Giữ `backend/` theo PLAN: chừa chỗ rõ cho `frontend/`, nhưng trái yêu cầu.

## Hệ quả
PLAN 3.1 và đường dẫn trong file task đã được cập nhật cùng lúc (trước khi có quy tắc baseline). Từ nay docs baseline không sửa bằng agent.
