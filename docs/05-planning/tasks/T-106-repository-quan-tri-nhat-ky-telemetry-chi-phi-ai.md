# T-106 · Repository quản trị, nhật ký, telemetry, chi phí AI

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-061, US-063 |
| BR | BR-016, BR-018 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-14 |
| Phụ thuộc | [T-103](T-103-migration-003-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-110](T-110-api-quan-ly-allow-list-api-14.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-312](T-312-so-lieu-hang-tuan-api-13.md) |

## Mục tiêu

Truy cập dữ liệu cho allow-list, nhật ký kiểm toán, telemetry và bộ đếm chi phí AI. Hàng đợi tác vụ thuộc T-204.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 1, 2.2
- CONTRACTS mục 6

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-103](T-103-migration-003-quan-tri-nhat-ky-telemetry-hang-doi.md) Migration 003: quản trị, nhật ký, telemetry, hàng đợi: `migrations/versions/003_admin.py`, `tests/integration/test_migration_003.py`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `Role`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/models/admin.py`
- `app/modules/users/repository.py`
- `app/modules/audit/repository.py`
- `app/modules/telemetry/repository.py`
- `app/modules/usage/repository.py`
- `tests/integration/test_admin_repositories.py`

## Chữ ký và giao diện

```python
# users
async def get_by_email(session: AsyncSession, email: str) -> AllowListEntry | None: ...
async def list_all(session: AsyncSession) -> list[AllowListEntry]: ...
async def add(session: AsyncSession, email: str, role: Role, added_by: str) -> AllowListEntry: ...
async def remove(session: AsyncSession, email: str) -> bool: ...
async def count(session: AsyncSession) -> int: ...
async def count_by_role(session: AsyncSession, role: Role) -> int: ...
async def mark_login(session: AsyncSession, email: str, at: datetime) -> bool: ...  # True nếu là lần đầu
# audit
async def append(session: AsyncSession, actor: str, action: Literal["UPLOAD", "DELETE", "PURGE"], doc_id: UUID | None, doc_name: str | None) -> None: ...
async def list_since(session: AsyncSession, since: datetime, limit: int) -> list[AuditLog]: ...
async def delete_before(session: AsyncSession, cutoff: datetime) -> int: ...
# telemetry
async def append_event(session: AsyncSession, row: TelemetryRow) -> None: ...
async def events_between(session: AsyncSession, names: list[str], start: datetime, end: datetime) -> list[TelemetryEvent]: ...
# usage
async def add_cost(session: AsyncSession, month: date, usd: float) -> None: ...
async def get_cost(session: AsyncSession, month: date) -> float: ...
```

## Các bước

1. Mô hình `AllowListEntry`, `AuditLog`, `TelemetryEvent`, `AiUsage` khớp migration 003.
2. `users`: lưu và tra email ở dạng chữ thường; `count_by_role(role)` dùng cho quy tắc quản trị viên cuối cùng.
3. `audit`: chỉ `append` và `list_since`; **không** có hàm sửa hay xóa lẻ; `delete_before(cutoff)` chỉ dùng cho tác vụ hết hạn.
4. `telemetry`: `append` và các hàm đọc thô cho T-312 (`events_between`).
5. `usage`: `add_cost(month, usd)` cộng dồn nguyên tử (`INSERT ... ON CONFLICT DO UPDATE SET cost_usd = ai_usage.cost_usd + excluded.cost_usd`).

## Tiêu chí hoàn thành

- [ ] Tra `Lan@CongTy.vn` tìm được bản ghi lưu `lan@congty.vn`.
- [ ] Mô-đun `audit` không có hàm cập nhật dữ liệu.
- [ ] Hai lời gọi `add_cost` đồng thời cộng đủ cả hai.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_email_case_insensitive` | `add("Lan@CongTy.vn", BD_USER, ...)`; `get_by_email("lan@congty.vn")` | Tìm thấy; email lưu chữ thường |
| `test_audit_append_only` | Liệt kê hàm công khai của `audit/repository.py` | Chỉ `append`, `list_since`, `delete_before` |
| `test_audit_list_order` | Ghi 3 bản ghi ở 3 thời điểm | `list_since` trả mới nhất trước |
| `test_usage_add_cost_concurrent` | Hai tác vụ đồng thời `add_cost(2026-11-01, 1.5)` | `get_cost` = 3.0 |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_admin_repositories.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Hàng đợi tác vụ (T-204).
- API quản trị (T-110, T-111), số liệu (T-312).

## Lưu ý

Quy ước backend ở CONTRACTS mục 2.2: SQLAlchemy 2.0 bất đồng bộ, repository là hàm `async` nhận `AsyncSession` đầu tiên và chỉ `flush`, lớp dịch vụ quyết định `commit`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
