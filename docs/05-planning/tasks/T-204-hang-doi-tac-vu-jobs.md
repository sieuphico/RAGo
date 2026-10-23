# T-204 · Hàng đợi tác vụ (jobs)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W3–W4 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-14 |
| Phụ thuộc | [T-103](T-103-migration-003-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md), [T-002](T-002-nap-cau-hinh-va-bi-mat.md) |
| Mở khóa | [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-213](T-213-tac-vu-xoa-du-lieu-trong-24-gio.md), [T-604](T-604-giam-sat-suc-khoe-chi-so-va-canh-bao.md) |

## Mục tiêu

Mô-đun hàng đợi trong PostgreSQL: đưa vào, nhận, hoàn tất, báo lỗi, giải phóng tác vụ treo.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 8
- CONTRACTS mục 7 (`job_max_attempts`, `job_stale_after_s`)
- CONTRACTS mục 2.2

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-103](T-103-migration-003-quan-tri-nhat-ky-telemetry-hang-doi.md) Migration 003: quản trị, nhật ký, telemetry, hàng đợi: `backend/migrations/versions/003_admin.py`, `backend/tests/integration/test_migration_003.py`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `Job`, `assert_transition`, `InvalidTransition`
- [T-002](T-002-nap-cau-hinh-va-bi-mat.md) Nạp cấu hình và bí mật: `Settings`, `get_settings`

## File cần tạo hoặc sửa

- `backend/app/models/job.py`
- `backend/app/modules/jobs/repository.py`
- `backend/app/modules/jobs/service.py`
- `backend/tests/integration/test_jobs_service.py`

## Chữ ký và giao diện

```python
async def enqueue(session: AsyncSession, type: str, payload: dict, run_after: datetime | None = None) -> UUID: ...
async def claim(session: AsyncSession, worker_id: str, now: datetime) -> Job | None: ...
async def complete(session: AsyncSession, job_id: UUID) -> None: ...
async def fail(session: AsyncSession, job_id: UUID, error: BaseException, now: datetime) -> None: ...
async def release_stale(session: AsyncSession, now: datetime) -> int: ...
```

## Các bước

1. Mô hình `JobRow` khớp bảng `job` (migration 003).
2. `enqueue(type, payload, run_after=None)` tạo `QUEUED`.
3. `claim(worker_id, now)`: `SELECT ... WHERE status='QUEUED' AND run_after <= now ORDER BY run_after FOR UPDATE SKIP LOCKED LIMIT 1`, đặt `RUNNING`, `locked_at=now`, `locked_by`, `attempts += 1`; trả `Job` (T-009) hoặc `None`.
4. `complete(job_id)` → `DONE`. `fail(job_id, error, now)`: nếu `attempts < job_max_attempts` thì về `QUEUED` với `run_after = now + [30, 120][attempts-1]` giây, ngược lại `FAILED`; `last_error` chỉ lưu tên lớp lỗi, tối đa 200 ký tự.
5. `release_stale(now)`: `RUNNING` có `locked_at < now - job_stale_after_s` về `QUEUED`.
6. Mọi hàm nhận `now` để test không phụ thuộc đồng hồ thật.

## Tiêu chí hoàn thành

- [ ] Hai worker gọi `claim` đồng thời không nhận cùng một tác vụ.
- [ ] Tác vụ lỗi 3 lần chuyển `FAILED`; lần 1 và 2 được hẹn lại sau 30 và 120 giây.
- [ ] Tác vụ `RUNNING` quá 1.800 giây được trả về `QUEUED`.
- [ ] Tác vụ có `run_after` ở tương lai không bị nhận.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_exclusive_claim` | 1 tác vụ; hai `AsyncSession` gọi `claim` đồng thời | Một bên nhận được, bên kia `None` |
| `test_retry_then_failed` | `fail` 3 lần ở `now = T` | Sau lần 1 `run_after = T+30s`; lần 2 `T+120s`; lần 3 `status = FAILED`, `last_error` = tên lớp lỗi |
| `test_stale_release` | Tác vụ `RUNNING`, `locked_at = T-1801s`; `release_stale(T)` | Về `QUEUED`; tác vụ `locked_at = T-100s` giữ nguyên |
| `test_future_not_claimed` | Tác vụ `run_after = T+60s`; `claim(w, T)` | `None` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_jobs_service.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Vòng lặp worker và tác vụ định kỳ (T-205).
- Xử lý từng loại tác vụ (T-210, T-213, T-402).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
