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
| Mở khóa | [T-002](T-002-nap-cau-hinh-va-bi-mat.md), [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-601](T-601-duong-ong-ci.md), [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) |

## Mục tiêu

Tạo cây thư mục backend (`app/`, `tests/` ở gốc kho) theo PLAN mục 3; lint, kiểm tra kiểu và test chạy được bằng một lệnh.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- PLAN.md mục 3.1 (cây thư mục)
- CONTRACTS mục 2.2 (quy ước backend)
- CONTRACTS mục 11 (file dùng chung)

## File cần tạo hoặc sửa

- `pyproject.toml`
- `app/__init__.py`
- `app/main.py`
- `app/api/__init__.py`
- `app/api/health.py`
- `tests/unit/test_health.py`
- `Makefile`
- `.gitignore`
- `.env.example`

## Chữ ký và giao diện

```python
def create_app() -> FastAPI: ...
```

## Các bước

1. Tạo `pyproject.toml`: Python 3.12 `[Đề xuất]`; phụ thuộc chạy: fastapi, uvicorn, pydantic, pydantic-settings, sqlalchemy[asyncio], asyncpg, alembic, psycopg[binary]; phụ thuộc phát triển: pytest, pytest-asyncio, httpx, ruff, mypy.
2. Tạo các gói rỗng có `__init__.py`: `app/core`, `app/api`, `app/domain`, `app/modules`, `app/ports`, `app/adapters`, `app/models`, `app/worker`.
3. Viết `api/health.py` với router `GET /healthz` trả `{"status": "ok"}` (T-604 mở rộng sau).
4. Viết `create_app() -> FastAPI` trong `app/main.py`, gắn router health.
5. Thêm `Makefile` với các đích `install`, `lint` (ruff), `type` (mypy app), `test` (pytest), `run` (uvicorn).
6. Cấu hình pytest `asyncio_mode = "auto"`; ruff và mypy đọc từ `pyproject.toml`.

## Tiêu chí hoàn thành

- [ ] `make install lint type test` đều trả mã 0 trên máy sạch.
- [ ] `GET /healthz` trả 200 và đúng `{"status": "ok"}`.
- [ ] Có đủ 8 gói trong `app/` như bước 2.
- [ ] `.env.example` chỉ có tên biến, không có giá trị.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_health_returns_ok` | Cho ứng dụng từ `create_app()`; khi gọi `GET /healthz` bằng `httpx.AsyncClient` | Mã 200, thân đúng `{"status": "ok"}` |
| Kiểm tra lệnh | Trên bản sao kho mã sạch, chạy `make install lint type test` | Cả bốn đích trả mã 0 |
| Kiểm tra bí mật | Mở `.env.example` | Mỗi dòng có dạng `TEN=` với giá trị trống |
| `test_app_packages_exist` | Liệt kê thư mục con của `app` | Có đủ `core`, `api`, `domain`, `modules`, `ports`, `adapters`, `models`, `worker`, mỗi thư mục có `__init__.py` |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_health.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Cấu hình và biến môi trường cụ thể (T-002).
- Kết nối CSDL (T-003).
- Đường ống CI (T-601).
- Kiểm tra CSDL trong `/healthz` (T-604).

## Lưu ý

Thư viện ngoài ba công nghệ đã chốt (FastAPI, Vue, PostgreSQL) là đề xuất mặc định, cần Trưởng đội kỹ thuật xác nhận ở tuần 1.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
