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
| Phụ thuộc | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-hang-doi.md) |
| Mở khóa | [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md) |

## Mục tiêu

Mô-đun hàng đợi trong PostgreSQL: đưa vào, nhận, hoàn tất, báo lỗi, giải phóng tác vụ treo.

## File cần tạo hoặc sửa

- `backend/app/modules/jobs/service.py`
- `backend/tests/integration/test_jobs_service.py`

## Chữ ký và giao diện

```python
def claim(session, worker_id: str) -> Job | None: ...
```

## Các bước

1. `enqueue(type, payload, run_after=None)`.
2. `claim(worker_id) -> Job | None` dùng `FOR UPDATE SKIP LOCKED`, tăng `attempts`.
3. `complete(job_id)`, `fail(job_id, error)` (thử lại tối đa N lần với thời gian chờ tăng dần, sau đó `FAILED`).
4. `release_stale(timeout)` trả tác vụ `RUNNING` quá hạn về `QUEUED`.

## Tiêu chí hoàn thành

- [ ] Hai worker không nhận cùng một tác vụ.
- [ ] Tác vụ lỗi quá số lần thử chuyển `FAILED` kèm lý do.
- [ ] Tác vụ treo được giải phóng.

## Kiểm thử cần viết

- `test_exclusive_claim`
- `test_retry_then_failed`
- `test_stale_release`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
