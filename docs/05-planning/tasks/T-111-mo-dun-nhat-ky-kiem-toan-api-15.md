# T-111 · Mô-đun nhật ký kiểm toán (API-15)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-063, US-062 |
| BR | BR-018 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-12 |
| Phụ thuộc | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) |
| Mở khóa | [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-213](T-213-tac-vu-xoa-du-lieu-trong-24-gio.md) |

## Mục tiêu

Ghi nhật ký tải lên và xóa; API đọc cho Quản trị viên; xóa bản ghi quá 90 ngày.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-15, 4.2 `AuditOut`
- CONTRACTS mục 8 (`audit_expire`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md) Repository quản trị, nhật ký, telemetry, chi phí AI: `get_by_email`, `list_all`, `add`, `remove`, `count`, `count_by_role` …
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`

## File cần tạo hoặc sửa

- `backend/app/modules/audit/service.py`
- `backend/app/api/admin_audit.py`
- `backend/tests/integration/test_audit.py`

## Chữ ký và giao diện

```python
async def record(session: AsyncSession, actor: str, action: Literal["UPLOAD", "DELETE", "PURGE"], doc_id: UUID | None, doc_name: str | None) -> None: ...
async def expire(session: AsyncSession, now: datetime) -> int: ...
```

## Các bước

1. `record(session, actor, action, doc_id, doc_name)` gọi `audit.append`; được gọi từ T-201 (UPLOAD), T-203 (DELETE), T-213 (PURGE, `actor="system"`).
2. `GET /api/v1/admin/audit-log?since=&limit=`: `require_roles(ADMIN)`; `since` mặc định now − `audit_days`; `limit` 1–500, mặc định 100; trả `{"items": AuditOut[]}`.
3. `async def expire(session, now)` xóa bản ghi có `at < now - audit_days`; T-205 đăng ký chạy hằng ngày 02:00.

## Tiêu chí hoàn thành

- [ ] Sau 3 lần `record` UPLOAD và 1 DELETE, API trả đúng 4 bản ghi có đủ `actor`, `action`, `docName`, `at` (AC-018).
- [ ] Không có route sửa hoặc xóa lẻ bản ghi.
- [ ] Chỉ ADMIN đọc được.
- [ ] `expire` xóa bản ghi 91 ngày tuổi và giữ bản ghi 89 ngày tuổi.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_four_records_after_ops` | Gọi `record` 3 lần UPLOAD, 1 lần DELETE; ADMIN gọi API-15 | 200, 4 mục, mỗi mục có đủ 4 trường, mới nhất trước |
| `test_audit_admin_only` | TEAM_LEAD gọi API-15 | 403 |
| `test_limit_bounds` | `limit=0` và `limit=501` | 422 `VALIDATION_ERROR` |
| `test_expire_90_days` | Bản ghi 91 ngày và 89 ngày tuổi; `expire(now)` | Còn bản ghi 89 ngày |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_audit.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Gọi `record` trong luồng tải lên, xóa, purge (T-201, T-203, T-213).
- Đăng ký tác vụ hằng ngày (T-205).
- Trang S-08 (T-519).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
