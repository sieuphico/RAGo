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

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2.2 (quy ước backend)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) Khung mã nguồn backend và công cụ: `create_app`
- [T-002](T-002-nap-cau-hinh-va-bi-mat.md) Nạp cấu hình và bí mật: `Settings`, `get_settings`

## File cần tạo hoặc sửa

- `deploy/compose.dev.yml`
- `backend/app/core/db.py`
- `backend/migrations/env.py`
- `backend/migrations/versions/000_extensions.py`
- `backend/alembic.ini`
- `backend/tests/conftest.py`
- `backend/tests/integration/test_db_connect.py`
- `Makefile`

## Chữ ký và giao diện

```python
engine: AsyncEngine
SessionLocal: async_sessionmaker[AsyncSession]

async def get_session() -> AsyncIterator[AsyncSession]: ...
```

## Các bước

1. Viết `compose.dev.yml` chạy ảnh `pgvector/pgvector:pg16` `[Đề xuất]` ở cổng 5432, có volume dữ liệu.
2. Viết `core/db.py`: `engine = create_async_engine(settings.database_url)`, `SessionLocal = async_sessionmaker(engine, expire_on_commit=False)`, dependency `get_session()`.
3. Khởi tạo Alembic dùng driver đồng bộ `psycopg` (đổi `+asyncpg` thành `+psycopg` trong `env.py`).
4. Migration `000_extensions`: `CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS unaccent;` và hàm bất biến `cwd_unaccent(text)` (xem bước 5).
5. `unaccent()` không phải hàm `IMMUTABLE` nên không dùng được trong cột sinh và chỉ mục; tạo `CREATE FUNCTION cwd_unaccent(text) RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE AS $$ SELECT public.unaccent('public.unaccent', $1) $$;`.
6. Fixture pytest trong `tests/conftest.py`: tạo CSDL thử `cwd_test` một lần mỗi phiên, chạy `alembic upgrade head`, mỗi test chạy trong một giao dịch và rollback khi xong.
7. Thêm đích `db-up`, `db-down`, `migrate`, `db-reset` vào `Makefile`.

## Tiêu chí hoàn thành

- [ ] `make db-up migrate` thành công trên máy sạch.
- [ ] Test tích hợp mở `AsyncSession` và chạy `SELECT 1` được.
- [ ] CSDL có tiện ích `vector`, `unaccent` và hàm `cwd_unaccent`.
- [ ] Dữ liệu ghi trong một test không còn ở test sau.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_db_connects` | CSDL thử đã migrate; khi chạy `SELECT 1` qua `AsyncSession` | Kết quả 1 |
| `test_extensions_installed` | Sau `alembic upgrade head` trên CSDL rỗng; truy vấn `pg_extension` | Có `vector` và `unaccent` |
| `test_cwd_unaccent` | `SELECT cwd_unaccent('Hợp đồng Đà Nẵng')` | `'Hop dong Da Nang'` (bộ quy tắc mặc định của `unaccent` đổi `Đ`/`đ` thành `D`/`d`) |
| `test_rollback_between_tests` | Test 1 chèn một dòng vào bảng tạm; test 2 đếm dòng | Test 2 đếm được 0 |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/conftest.py -q
cd backend && pytest tests/integration/test_db_connect.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Bảng nghiệp vụ (T-101 – T-103).
- Cấu hình CSDL production và sao lưu (T-602, T-603).

## Lưu ý

Quy ước backend ở CONTRACTS mục 2.2: SQLAlchemy 2.0 bất đồng bộ, repository là hàm `async` nhận `AsyncSession` đầu tiên và chỉ `flush`, lớp dịch vụ quyết định `commit`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
