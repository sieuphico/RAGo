# T-103 · Migration 003: quản trị, nhật ký, telemetry, hàng đợi

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
| Quyết định kiến trúc | AD-10, AD-12, AD-14 |
| Phụ thuộc | [T-102](T-102-migration-002-phien-hoi-thoai-va-tin-nhan.md) |
| Mở khóa | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-hang-doi.md) |

## Mục tiêu

Tạo bảng `allow_list_entry`, `audit_log`, `telemetry_event`, `job`.

## File cần tạo hoặc sửa

- `backend/migrations/versions/003_admin.py`
- `backend/tests/integration/test_migration_003.py`

## Các bước

1. `allow_list_entry`: `email pk`, `role` (BD_USER, TEAM_LEAD, ADMIN, SPONSOR), `added_by`, `added_at`.
2. `audit_log`: `id bigserial pk`, `actor`, `action`, `doc_id null`, `at`.
3. `telemetry_event`: `id bigserial pk`, `event`, `anon_user_id`, `session_id`, `ts`, `app_version`, `props jsonb`.
4. `job`: `job_id uuid pk`, `type`, `payload jsonb`, `status` (QUEUED, RUNNING, DONE, FAILED), `attempts int`, `run_after`, `locked_at null`, `locked_by null`, `last_error null`; chỉ mục `(status, run_after)`.

## Tiêu chí hoàn thành

- [ ] `upgrade` và `downgrade` sạch.
- [ ] Không có cột văn bản tự do trong `telemetry_event` ngoài `props` có kiểm tra ở lớp ứng dụng.
- [ ] `audit_log` không có thao tác cập nhật qua repository (chỉ thêm).

## Kiểm thử cần viết

- `test_upgrade_downgrade`
- `test_job_claim_index`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
