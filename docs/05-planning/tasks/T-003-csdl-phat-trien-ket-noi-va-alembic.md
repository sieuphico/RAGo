# T-003 · CSDL phát triển, kết nối và Alembic

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-03, AD-14 |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md), [T-002](T-002-nap-cau-hinh-va-bi-mat.md) |
| Mở khóa | [T-101](T-101-migration-001-tai-lieu-chunk-goi-y.md), [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) |

## Mục tiêu

Chạy được PostgreSQL có pgvector ở máy phát triển; có engine, session và khung migration.

## File cần tạo hoặc sửa

- `deploy/compose.dev.yml`
- `backend/app/core/db.py`
- `backend/migrations/env.py`
- `backend/alembic.ini`
- `backend/tests/integration/test_db_connect.py`

## Chữ ký và giao diện

```python
def get_session() -> Iterator[Session]: ...
```

## Các bước

1. Viết `compose.dev.yml` chạy PostgreSQL kèm pgvector; các tiện ích `vector`, `unaccent` được tạo khi khởi tạo.
2. Viết `core/db.py`: `engine`, `SessionLocal`, `get_session()` (dependency FastAPI).
3. Khởi tạo Alembic; thêm đích `make db-up`, `make migrate`, `make db-reset`.
4. Viết fixture pytest cung cấp CSDL thử nghiệm sạch cho mỗi phiên test.

## Tiêu chí hoàn thành

- [ ] `make db-up migrate` thành công trên máy sạch.
- [ ] Test tích hợp kết nối và chạy `SELECT 1`.
- [ ] Tiện ích `vector` và `unaccent` có trong CSDL.

## Kiểm thử cần viết

- `test_db_connects`
- `test_extensions_installed`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
