# Truy vết: story → yêu cầu → task → mã → test

Cập nhật trong cùng commit với mỗi task. Nguồn: `docs/05-planning/PLAN.md` mục 8, `docs/03-analysis/USER_STORIES.md`.
Trạng thái: ✅ xong và cổng xanh · 🔶 một phần · ⬜ chưa làm · ⛔ bị chặn (ghi lý do).
Chỉ AC `[PRD]`/`[BRD]` được tính; AC `[Đề xuất]` và ngưỡng % chưa làm (xem `03-analysis/BACKBONE_STORIES.md`).

## Story xương sống

| Story | BR | Task | Mã | Test | Trạng thái |
|---|---|---|---|---|---|
| US-010 Tải PDF lên | BR-001 | T-101, T-104, T-112, T-201, T-204–T-211 | — | — | ⬜ |
| US-011 Báo tệp không hợp lệ | BR-003, BR-004 | T-201, T-508 | — | — | ⬜ |
| US-012 Trạng thái xử lý | BR-005 | T-206, T-210, T-211 | — | — | ⬜ |
| US-020 Hỏi và nhận trả lời | BR-008, BR-013 | T-303–T-308, T-315, T-316 | — | — | ⬜ |
| US-022a Thẻ trích dẫn trong câu trả lời | BR-010 | T-305, T-306, T-307, T-308 | — | — | ⬜ |
| US-022b Bấm mở đúng trang | BR-010 | T-212, T-512, T-513 | — | — | ⬜ |

## Task nền tảng (không gắn story)

| Task | Nội dung | Mã | Test | Trạng thái |
|---|---|---|---|---|
| T-001 | Khung backend, `/healthz` | `app/main.py`, `app/api/health.py` | `tests/unit/test_health.py` | ✅ |
| T-002 | Nạp cấu hình | `app/core/config.py` | `tests/unit/test_config.py` | ✅ |
| T-003 | CSDL dev, engine, Alembic | `app/core/db.py`, `migrations/`, `deploy/compose.dev.yml` | `tests/integration/test_db_connect.py` | ✅ |
| T-008 | Cổng và bộ nối giả | `app/ports/`, `app/adapters/*_fake.py`, `app/core/wiring.py` | `tests/unit/test_fakes.py`, `test_import_rules.py` | ✅ |
| T-009 | Kiểu miền, chuyển trạng thái | `app/domain/` | `tests/unit/test_domain.py` | ✅ |
| T-101 | Migration 001: tài liệu, chunk, gợi ý (US-010, US-015) | `migrations/versions/001_documents.py` | `tests/integration/test_migration_001.py` | ✅ |
| T-102 | Migration 002: phiên hội thoại, tin nhắn (US-020, US-041) | `migrations/versions/002_chat.py` | `tests/integration/test_migration_002.py` | ✅ |
| T-103 | Migration 003: quản trị, nhật ký, telemetry, hàng đợi (US-061, US-063) | `migrations/versions/003_admin.py` | `tests/integration/test_migration_003.py` | ✅ |
| T-601 | CI (backend) | `ci/run_ci.sh`, `.github/workflows/ci.yml` | — | 🔶 chưa có frontend |

## Story còn lại

Chưa bắt đầu (⬜): US-001, 002, 013–017, 021, 023–027, 030, 031, 040–042, 050, 051, 060–064. Thêm dòng khi bắt đầu story.
US-013 ⛔ chờ chọn OCR (T-004, T-010). US-001 ⛔ chờ giao thức SSO (T-006). Bộ nối AI thật ⛔ chờ AD-06.

## ADR

| ADR | Quyết định |
|---|---|
| [0001](adr/0001-ma-nguon-o-goc-kho.md) | Mã ở gốc kho |
| [0002](adr/0002-engine-csdl-tao-luoi-va-cong-dev-5433.md) | Engine tạo lười, CSDL dev cổng 5433 |
