# T-205 · Worker: vòng lặp xử lý và scheduler

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-01, AD-14 |
| Phụ thuộc | [T-002](T-002-nap-cau-hinh-va-bi-mat.md), [T-204](T-204-hang-doi-tac-vu-jobs.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md) |
| Mở khóa | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-213](T-213-tac-vu-xoa-du-lieu-trong-24-gio.md), [T-401](T-401-lich-su-hoi-thoai-api-10-va-het-han-90-ngay.md), [T-402](T-402-goi-y-cau-hoi-mau-api-17.md), [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) |

## Mục tiêu

Tiến trình worker nhận tác vụ theo loại và chạy các tác vụ định kỳ.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 8 (đăng ký, chu kỳ)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-002](T-002-nap-cau-hinh-va-bi-mat.md) Nạp cấu hình và bí mật: `Settings`, `get_settings`
- [T-204](T-204-hang-doi-tac-vu-jobs.md) Hàng đợi tác vụ (jobs): `enqueue`, `claim`, `complete`, `fail`, `release_stale`
- [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md) Mô-đun nhật ký kiểm toán (API-15): `record`, `expire`

## File cần tạo hoặc sửa

- `app/worker/__main__.py`
- `app/worker/main.py`
- `app/worker/scheduler.py`
- `app/worker/registry.py`
- `tests/integration/test_worker_loop.py`

## Chữ ký và giao diện

```python
async def run_worker(worker_id: str, stop: asyncio.Event) -> None: ...
async def run_scheduler(clock: Callable[[], datetime], stop: asyncio.Event) -> None: ...
```

## Các bước

1. `registry.py`: `register`, `every`, `daily` như CONTRACTS mục 8; lưu vào bảng trong bộ nhớ.
2. `main.py`: `run_worker(worker_id, stop: asyncio.Event)` lặp: `claim` → gọi handler theo `job.type` → `complete`; ngoại lệ → `fail`; không có tác vụ thì chờ 1 giây. `type` không có handler → `fail` với lỗi `UnknownJobType`.
3. `scheduler.py`: `run_scheduler(clock, stop)` mỗi giây kiểm tra tác vụ định kỳ đến hạn; chạy mỗi tác vụ trong `asyncio.create_task`, một tác vụ lỗi không chặn tác vụ khác.
4. Đăng ký sẵn: `every("release_stale_jobs", 60, ...)` và `daily("audit_expire", "02:00", audit.expire)` (T-111).
5. `python -m app.worker` chạy cả hai vòng lặp; SIGTERM đặt `stop`, chờ tác vụ đang chạy xong tối đa 30 giây rồi thoát.

## Tiêu chí hoàn thành

- [ ] Handler được gọi đúng theo `type`; `type` lạ thành lỗi có tên.
- [ ] SIGTERM khi đang chạy tác vụ: tác vụ hoàn tất rồi mới thoát (≤ 30 giây).
- [ ] Với đồng hồ giả, tác vụ `every(60)` chạy đúng 3 lần trong 180 giây; `daily("02:00")` chạy 1 lần mỗi ngày.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_dispatch_by_type` | Đăng ký handler `"t1"`; enqueue `t1`; chạy một vòng | Handler nhận đúng `Job`; tác vụ `DONE` |
| `test_unknown_type_fails` | Enqueue `"khong_co"` | Tác vụ được `fail` với `last_error = "UnknownJobType"` |
| `test_graceful_stop` | Handler chờ 2 giây; đặt `stop` sau 0,5 giây | Handler hoàn tất; tác vụ `DONE`; hàm trả về trong ≤ 3 giây |
| `test_scheduler_every` | Đồng hồ giả tiến 180 giây theo bước 1 giây | Hàm `every(60)` được gọi 3 lần |
| `test_scheduler_daily` | Đồng hồ giả từ 01:59 ngày 1 tới 02:01 ngày 2 | Hàm `daily("02:00")` được gọi 2 lần |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_worker_loop.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Handler `ingest`, `purge`, `suggest` (T-210, T-213, T-402).
- Tác vụ `purge_sweep` (T-213), `history_expire` (T-401) — task đó tự thêm một dòng đăng ký vào `registry.py`.
- Chạy worker trong container (T-602).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
