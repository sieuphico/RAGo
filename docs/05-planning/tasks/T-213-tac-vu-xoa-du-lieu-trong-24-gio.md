# T-213 · Tác vụ xóa dữ liệu trong 24 giờ

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-064, US-016 |
| BR | BR-029 |
| NFR, EC, cổng | NFR-006 |
| Quyết định kiến trúc | AD-08 |
| Phụ thuộc | [T-203](T-203-xoa-tai-lieu-api-05.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-112](T-112-bo-noi-kho-tep-storageport.md), [T-204](T-204-hang-doi-tac-vu-jobs.md) |
| Mở khóa | — |

## Mục tiêu

Sau khi xóa logic, xóa chunk, gợi ý và tệp gốc trong ≤ 24 giờ và ghi bằng chứng.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 8 (`purge`, `purge_sweep`)
- CONTRACTS mục 2.1 (`DELETED`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-203](T-203-xoa-tai-lieu-api-05.md) Xóa tài liệu (API-05): `delete_document`
- [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md) Worker: vòng lặp xử lý và scheduler: `run_worker`, `run_scheduler`
- [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md) Mô-đun nhật ký kiểm toán (API-15): `record`, `expire`
- [T-112](T-112-bo-noi-kho-tep-storageport.md) Bộ nối kho tệp (StoragePort): `FsStorage`, `new_file_key`
- [T-204](T-204-hang-doi-tac-vu-jobs.md) Hàng đợi tác vụ (jobs): `enqueue`, `claim`, `complete`, `fail`, `release_stale`

## File cần tạo hoặc sửa

- `app/worker/purge.py`
- `tests/integration/test_purge.py`

## Chữ ký và giao diện

```python
async def purge_document(job: Job) -> None: ...
async def purge_sweep(now: datetime) -> int: ...
```

## Các bước

1. `purge_document(job)` đăng ký `register("purge", ...)`: đọc tài liệu; không có `deleted_at` → bỏ qua (đã khôi phục hoặc lỗi dữ liệu, ghi cảnh báo).
2. Trong một giao dịch: xóa `chunk` và `suggestion` của tài liệu; `set_status(DELETED)`; `audit.record("system", "PURGE", doc_id, name)`. Sau `commit`, `storage.delete(file_key)`.
3. Giữ hàng `document` (tên, trạng thái `DELETED`) để trích dẫn cũ hiển thị "Tài liệu đã bị xóa" (EC-14).
4. `purge_sweep(now)`: tìm tài liệu có `deleted_at < now - purge_hours + 1 giờ` mà `status != DELETED`, enqueue `purge` cho từng tài liệu chưa có tác vụ `purge` đang `QUEUED`/`RUNNING`; đăng ký `every("purge_sweep", 3600, ...)` trong `registry.py`.

## Tiêu chí hoàn thành

- [ ] Sau khi tác vụ chạy, CSDL không còn chunk hay gợi ý của tài liệu (AC-029).
- [ ] Tệp gốc không còn trong kho tệp.
- [ ] Có bản ghi `PURGE` làm bằng chứng.
- [ ] Tài liệu xóa lúc T chưa được purge thì `purge_sweep(T + 23 giờ)` tạo tác vụ.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_purge_removes_chunks_and_file` | Tài liệu `READY` có 5 chunk, 1 gợi ý, tệp trong `FsStorage`; đặt `deleted_at`; chạy `purge_document` | 0 chunk, 0 gợi ý; `storage.size` ném `FileNotFoundError`; `status = DELETED` |
| `test_audit_purge_record` | Như trên | `audit_log` có 1 dòng `PURGE`, `actor="system"` |
| `test_scheduler_catches_missed_purge` | `deleted_at = T`, không có tác vụ `purge`; `purge_sweep(T + 23h)` | 1 tác vụ `purge` mới; gọi lại lần hai không tạo thêm |
| `test_not_deleted_skipped` | Tài liệu không có `deleted_at`; chạy `purge_document` | Không xóa gì; có cảnh báo nhật ký |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_purge.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Xóa trong bản sao lưu (ngoại lệ Q-A3, T-603).
- Hiển thị "Tài liệu đã bị xóa" (T-512, T-516).

## Lưu ý

Bản sao lưu là ngoại lệ đã ghi nhận (Q-A3), chờ Bảo mật thông tin duyệt.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
