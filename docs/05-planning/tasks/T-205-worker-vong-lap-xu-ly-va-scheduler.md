# T-205 · Worker: vòng lặp xử lý và scheduler

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-01, AD-14 |
| Phụ thuộc | [T-002](T-002-nap-cau-hinh-va-bi-mat.md), [T-204](T-204-hang-doi-tac-vu-jobs.md) |
| Mở khóa | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-213](T-213-tac-vu-xoa-du-lieu-trong-24-gio.md) |

## Mục tiêu

Tiến trình worker nhận tác vụ theo loại và chạy các tác vụ định kỳ.

## File cần tạo hoặc sửa

- `backend/app/worker/main.py`
- `backend/app/worker/scheduler.py`
- `backend/tests/integration/test_worker_loop.py`

## Chữ ký và giao diện

```python
def register(job_type: str, handler: Callable[[Job], Awaitable[None]]) -> None: ...
```

## Các bước

1. `worker/main.py`: vòng lặp `claim` → gọi handler theo `type` → `complete` hoặc `fail`; dừng êm khi nhận tín hiệu.
2. `scheduler.py`: đăng ký tác vụ định kỳ (purge 24 giờ, xóa nhật ký 90 ngày, xóa lịch sử 90 ngày).
3. Cơ chế đăng ký handler: `register(type, fn)`.

## Tiêu chí hoàn thành

- [ ] Handler được gọi đúng theo loại.
- [ ] Worker dừng êm không bỏ dở tác vụ.
- [ ] Scheduler chạy đúng chu kỳ (dùng đồng hồ giả trong test).

## Kiểm thử cần viết

- `test_dispatch_by_type`
- `test_graceful_stop`
- `test_scheduler_runs_due_tasks`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
