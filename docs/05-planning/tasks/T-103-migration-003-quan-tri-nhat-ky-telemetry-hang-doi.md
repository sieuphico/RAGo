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
| Mở khóa | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md), [T-204](T-204-hang-doi-tac-vu-jobs.md) |

## Mục tiêu

Tạo bảng `allow_list_entry`, `audit_log`, `telemetry_event`, `job`.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 1 (vai trò)
- CONTRACTS mục 6 (telemetry)
- CONTRACTS mục 8 (hàng đợi)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-102](T-102-migration-002-phien-hoi-thoai-va-tin-nhan.md) Migration 002: phiên hội thoại và tin nhắn: `backend/migrations/versions/002_chat.py`, `backend/tests/integration/test_migration_002.py`

## File cần tạo hoặc sửa

- `backend/migrations/versions/003_admin.py`
- `backend/tests/integration/test_migration_003.py`

## Các bước

1. `allow_list_entry`: `email text pk` (lưu chữ thường), `role text not null` CHECK theo `Role`, `added_by text not null`, `added_at timestamptz not null default now()`, `first_login_at timestamptz null`.
2. `audit_log`: `id bigserial pk`, `actor text not null`, `action text not null check (action in ('UPLOAD','DELETE','PURGE'))`, `doc_id uuid null`, `doc_name text null`, `at timestamptz not null default now()`; chỉ mục `(at desc)`.
3. `telemetry_event`: `id bigserial pk`, `event text not null`, `anon_user_id text not null`, `session_id text not null`, `ts timestamptz not null`, `app_version text not null`, `props jsonb not null default '{}'`; chỉ mục `(event, ts)`.
4. `job`: `job_id uuid pk`, `type text not null`, `payload jsonb not null`, `status text not null check (status in ('QUEUED','RUNNING','DONE','FAILED'))`, `attempts int not null default 0`, `run_after timestamptz not null default now()`, `locked_at timestamptz null`, `locked_by text null`, `last_error text null`, `created_at timestamptz not null default now()`; chỉ mục `ix_job_claim (status, run_after)`.
5. `ai_usage`: `month date pk` (ngày 1 của tháng), `cost_usd numeric(10,4) not null default 0`, `updated_at timestamptz not null default now()` (dùng ở T-301).

## Tiêu chí hoàn thành

- [ ] `upgrade` và `downgrade` sạch.
- [ ] `telemetry_event` không có cột văn bản tự do ngoài `props`.
- [ ] `audit_log.action='EDIT'` bị từ chối.
- [ ] Có chỉ mục `ix_job_claim`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_upgrade_downgrade` | CSDL ở revision 002; `upgrade 003` rồi `downgrade 002` | Không lỗi |
| `test_job_claim_index` | Truy vấn `pg_indexes` sau upgrade | Có `ix_job_claim` trên `(status, run_after)` |
| `test_audit_action_check` | Chèn `audit_log` với `action='EDIT'` | `IntegrityError` |
| `test_allowlist_role_check` | Chèn `allow_list_entry` với `role='GUEST'` | `IntegrityError` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_migration_003.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Repository (T-106, T-204).
- Xóa nhật ký quá 90 ngày (T-111).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
