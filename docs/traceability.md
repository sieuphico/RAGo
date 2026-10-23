# Truy vết: story → yêu cầu → task → mã → test

Cập nhật trong cùng commit với mỗi task. Nguồn: `docs/05-planning/PLAN.md` mục 8, `docs/03-analysis/USER_STORIES.md`.
Trạng thái: ✅ xong và cổng xanh · 🔶 một phần · ⬜ chưa làm · ⛔ bị chặn (ghi lý do).
Chỉ AC `[PRD]`/`[BRD]` được tính; AC `[Đề xuất]` và ngưỡng % chưa làm (xem `03-analysis/BACKBONE_STORIES.md`).

## Story xương sống

| Story | BR | Task | Mã | Test | Trạng thái |
|---|---|---|---|---|---|
| US-010 Tải PDF lên | BR-001 | T-101, T-104, T-112, T-201, T-204–T-211 | `app/modules/documents/upload.py`, `app/api/documents_upload.py` | `tests/integration/test_upload_api.py` | 🔶 API tải lên xong (AC1); chờ worker T-205–T-211 để READY (AC2) |
| US-011 Báo tệp không hợp lệ | BR-003, BR-004 | T-201, T-508 | `app/modules/documents/upload.py` | `tests/integration/test_upload_api.py` | 🔶 phía máy chủ xong; chờ giao diện T-508 |
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
| T-107 | Mã lỗi và bộ xử lý ngoại lệ | `app/core/errors.py` | `tests/unit/test_errors.py` | ✅ |
| T-104 | ORM và repository tài liệu (US-010, US-015) | `app/models/document.py`, `app/modules/documents/repository.py` | `tests/integration/test_document_repository.py` | ✅ |
| T-106 | Repository allow-list, nhật ký, telemetry, chi phí AI (US-061, US-063) | `app/models/admin.py`, `app/modules/{users,audit,telemetry,usage}/repository.py` | `tests/integration/test_admin_repositories.py` | ✅ |
| T-108 | Đăng nhập, cookie phiên, `GET /me` — dùng IdpFake (US-001, US-002) | `app/modules/auth/`, `app/api/auth.py`, `app/api/me.py`, `app/api/deps.py` | `tests/integration/test_auth_flow.py` | 🔶 IdP thật chờ T-006 |
| T-109 | AuthZ theo vai trò và chống CSRF (US-002, US-061) | `app/api/deps.py`, `app/api/csrf.py` | `tests/integration/test_authz.py` | ✅ |
| T-111 | Nhật ký kiểm toán và API-15 (US-062, US-063) | `app/modules/audit/service.py`, `app/api/admin_audit.py`, `app/core/schemas.py` | `tests/integration/test_audit.py` | ✅ |
| T-112 | Bộ nối kho tệp FsStorage (US-010, US-022) | `app/adapters/storage_fs.py`, `app/core/wiring.py` | `tests/unit/test_storage_fs.py` | ✅ |
| T-204 | Hàng đợi tác vụ trong PostgreSQL | `app/models/job.py`, `app/modules/jobs/` | `tests/integration/test_jobs_service.py` | ✅ |
| T-201 | API-02 tải lên PDF (US-010, US-011, BR-001, BR-003, BR-004) | `app/modules/documents/upload.py`, `app/api/documents_upload.py` | `tests/integration/test_upload_api.py` | ✅ |
| T-207 | Ingest: chia chunk theo trang (US-022) | `app/worker/chunker.py` | `tests/unit/test_chunker.py` | ✅ |
| T-208 | Ingest: nhúng và lập chỉ mục (US-020) | `app/worker/indexer.py` | `tests/integration/test_indexer.py` | ✅ |
| T-205 | Worker: vòng lặp xử lý, scheduler, đăng ký | `app/worker/{registry,main,scheduler,__main__}.py` | `tests/integration/test_worker_loop.py` | ✅ |
| T-605 | Sinh PDF mẫu và fixture kiểm thử | `scripts/make_sample_data.py`, `tests/conftest.py` (`sample_pdfs`) | `tests/unit/test_sample_data.py` | ✅ |
| T-206 | Ingest: trích văn bản theo trang bằng pypdf (US-012, US-013) | `app/worker/extract.py` | `tests/unit/test_extract.py` | ✅ |
| T-211 | Sự kiện trạng thái tài liệu: NOTIFY/LISTEN và SSE API-04 (US-012) | `app/modules/documents/events.py`, `app/api/document_events.py`, `app/main.py` | `tests/integration/test_document_events.py` | ✅ |
| T-209 | Ingest: bước OCR cho PDF ảnh quét (lõi, bộ dựng ảnh và Tesseract chưa có) | `app/worker/ocr_step.py`, `app/core/wiring.py` | `tests/unit/test_ocr_step.py` | 🔶 ⛔ bộ nối Tesseract và dựng ảnh chờ T-004/T-010 |
| T-210 | Ingest: điều phối, chuyển trạng thái, phát sự kiện (US-010, US-012, US-013) | `app/worker/ingest.py`, `app/worker/main.py` | `tests/integration/test_ingest.py` | ✅ |
| T-202 | API-03 danh sách tài liệu (US-015, BR-006) | `app/api/documents.py` | `tests/integration/test_list_documents.py` | ✅ |
| T-203 | API-05 xóa tài liệu (US-016, US-062, BR-007) | `app/modules/documents/delete.py`, `app/api/documents_delete.py` | `tests/integration/test_delete_document.py` | ✅ |
| T-212 | API-06 tải PDF theo Range cho khung xem nguồn (US-022b) | `app/api/document_file.py` | `tests/integration/test_document_file.py` | ✅ |
| T-213 | Tác vụ xóa dữ liệu ≤ 24 giờ và purge_sweep (US-064, US-016, BR-029) | `app/worker/purge.py` | `tests/integration/test_purge.py` | ✅ |
| T-113 | Telemetry: 19 sự kiện, `emit`, API-16 (US-051, AD-10) | `app/modules/telemetry/{schema,service}.py`, `app/api/telemetry.py` | `tests/unit/test_telemetry_schema.py`, `tests/integration/test_telemetry_api.py` | ✅ |
| T-601 | CI (backend) | `ci/run_ci.sh`, `.github/workflows/ci.yml` | — | 🔶 chưa có frontend |

## Story còn lại

Chưa bắt đầu (⬜): US-001, 002, 013–017, 021, 023–027, 030, 031, 040–042, 050, 051, 060–064. Thêm dòng khi bắt đầu story.
US-013 ⛔ chờ chọn OCR (T-004, T-010). US-001 ⛔ chờ giao thức SSO (T-006). Bộ nối AI thật ⛔ chờ AD-06.

## ADR

| ADR | Quyết định |
|---|---|
| [0001](adr/0001-ma-nguon-o-goc-kho.md) | Mã ở gốc kho |
| [0002](adr/0002-engine-csdl-tao-luoi-va-cong-dev-5433.md) | Engine tạo lười, CSDL dev cổng 5433 |
| [0003](adr/0003-thu-vien-bo-sung-python-multipart-pypdf.md) | python-multipart, pypdf; reportlab chờ duyệt |
