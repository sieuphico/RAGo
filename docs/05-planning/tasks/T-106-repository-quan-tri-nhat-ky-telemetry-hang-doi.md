# T-106 · Repository quản trị, nhật ký, telemetry, hàng đợi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | US-061, US-063 |
| BR | BR-016, BR-018 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-14 |
| Phụ thuộc | [T-103](T-103-migration-003-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) |
| Mở khóa | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-110](T-110-api-quan-ly-allow-list-api-14.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-204](T-204-hang-doi-tac-vu-jobs.md), [T-312](T-312-so-lieu-hang-tuan-api-13.md), [T-402](T-402-goi-y-cau-hoi-mau-api-17.md) |

## Mục tiêu

Truy cập dữ liệu cho allow-list, nhật ký kiểm toán, telemetry và hàng đợi tác vụ.

## File cần tạo hoặc sửa

- `backend/app/models/admin.py`
- `backend/app/modules/users/repository.py`
- `backend/app/modules/audit/repository.py`
- `backend/app/modules/telemetry/repository.py`
- `backend/app/modules/jobs/repository.py`
- `backend/tests/integration/test_admin_repositories.py`

## Các bước

1. Mô hình tương ứng migration 003.
2. `users`: `get_by_email`, `list_all`, `add`, `remove`, `count`.
3. `audit`: chỉ `append(actor, action, doc_id)` và `list(since, limit)`; không có hàm sửa hoặc xóa lẻ.
4. `telemetry`: `append(event)`, `aggregate_weekly(week_start)` (dùng ở T-312).
5. `jobs`: `enqueue`, `claim(worker_id)` bằng `FOR UPDATE SKIP LOCKED`, `complete`, `fail`, `release_stale(timeout)`.

## Tiêu chí hoàn thành

- [ ] Hai worker gọi `claim` đồng thời không nhận cùng một tác vụ.
- [ ] Tác vụ treo quá thời hạn được `release_stale`.
- [ ] `audit` không có đường sửa dữ liệu.

## Kiểm thử cần viết

- `test_claim_is_exclusive`
- `test_release_stale`
- `test_audit_append_only`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
