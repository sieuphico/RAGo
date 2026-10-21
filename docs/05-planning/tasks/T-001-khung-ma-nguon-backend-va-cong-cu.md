# T-001 · Khung mã nguồn backend và công cụ

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | NFR-008 |
| Quyết định kiến trúc | — |
| Phụ thuộc | — |
| Mở khóa | [T-002](T-002-nap-cau-hinh-va-bi-mat.md), [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-207](T-207-ingest-chia-chunk-theo-trang.md), [T-305](T-305-dung-prompt-voi-nhan-chunk.md), [T-306](T-306-kiem-tra-va-anh-xa-trich-dan.md), [T-601](T-601-duong-ong-ci.md), [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) |

## Mục tiêu

Tạo cây thư mục `backend/` theo PLAN mục 3; lint, kiểm tra kiểu và test chạy được bằng một lệnh.

## File cần tạo hoặc sửa

- `backend/pyproject.toml`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/tests/unit/test_health.py`
- `Makefile`
- `.gitignore`
- `backend/.env.example`

## Chữ ký và giao diện

```python
def create_app() -> FastAPI: ...
```

## Các bước

1. Tạo `pyproject.toml`: Python 3.12 `[Đề xuất]`, fastapi, uvicorn, pydantic, pytest, httpx, ruff, mypy.
2. Viết `create_app() -> FastAPI` trong `app/main.py` với `GET /healthz` trả `{"status": "ok"}`.
3. Thêm `Makefile` với các đích `lint`, `type`, `test`, `run`.
4. Thêm test `test_health_returns_ok`.

## Tiêu chí hoàn thành

- [ ] `make lint type test` đều đạt.
- [ ] `GET /healthz` trả 200 và `{"status": "ok"}`.
- [ ] Không có bí mật nào trong kho mã; `.env.example` chỉ có tên biến.

## Kiểm thử cần viết

- `test_health_returns_ok`

## Lưu ý

Thư viện ngoài ba công nghệ đã chốt (FastAPI, Vue, PostgreSQL) là đề xuất mặc định, cần Trưởng đội kỹ thuật xác nhận ở tuần 1.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
