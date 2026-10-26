# Chat với tài liệu (MVP)

Tải PDF lên kho chung, hỏi đáp tiếng Việt/Anh, câu trả lời có trích dẫn **tên tài liệu + số trang**. Chạy hoàn toàn tại chỗ: FastAPI + PostgreSQL/pgvector + Vue 3 + Ollama.

Nguồn sự thật của dự án là `docs/` (yêu cầu, thiết kế, hợp đồng, kế hoạch). README này chỉ là điểm vào nhanh.

## Trạng thái (2026-10-26)

| Hạng mục | Trạng thái |
|---|---|
| Backend | `ruff` sạch, `mypy --strict` sạch, **415 test pass** (1 skip, 4 deselected) |
| Frontend | lint 0 error (2 warning), `vue-tsc` sạch, **241 test Vitest pass**, build OK |
| Xương sống | US-010, US-012, US-022a xong backend; US-011, US-020, US-022b một phần (NFR-001 chưa đạt trên CPU) |
| E2E trình duyệt | 7/7 PASS (lần chạy `20261025-190801`) |
| Còn chặn | OCR thật (T-004/T-010), SSO thật (T-006), nhà cung cấp AI (AD-06), diễn tập vận hành/backup |

Chi tiết từng story/task: [`docs/traceability.md`](docs/traceability.md).

## Kiến trúc

```
frontend/ (Vue 3 + TS + Vite)  ──proxy /api──▶  app/ (FastAPI)
                                                   │
                              ┌────────────────────┼────────────────────┐
                              ▼                    ▼                    ▼
                        PostgreSQL 16         worker (app/worker)   Ollama nội bộ
                        + pgvector            ingest/purge/suggest  qwen3:1.7b
                                                                     qwen3-embedding:0.6b
```

Phụ thuộc một chiều: `api → modules → ports → adapters`. Chỉ `app/core/wiring.py` được nhập `app/adapters/`; chỉ `ai_gateway` gọi nhà cung cấp AI (test `test_import_rules` bắt vi phạm).

| Thư mục | Nội dung |
|---|---|
| `app/domain`, `app/core` | Kiểu miền, cấu hình, CSDL, lỗi, cờ tính năng, metrics, wiring |
| `app/api` | Router HTTP + SSE (`/auth`, `/api/v1/*`, `/healthz`) |
| `app/modules` | Nghiệp vụ: documents, retrieval, answer, chat, summary, suggest, audit, telemetry, jobs… |
| `app/ports`, `app/adapters` | Cổng và bộ nối (Ollama, FS storage, IdP, OCR; kèm bản `*_fake`) |
| `app/worker` | Vòng lặp job: extract → chunk → embed → index, purge, suggest |
| `migrations/` | Alembic, 3 revision (001 tài liệu/chunk, 002 hội thoại, 003 quản trị/hàng đợi) |
| `frontend/` | Ứng dụng Vue 3, Pinia, Vue Router, Vitest |
| `deploy/`, `ci/`, `scripts/` | Docker/nginx/compose, CI, sinh dữ liệu mẫu, E2E |

## Yêu cầu môi trường

- Python **3.12+**, Node **20+**, Docker (compose v2)
- PostgreSQL 16 + pgvector chạy qua Docker (cổng **5433**; 5432 hay bị bản cài sẵn chiếm)
- Ollama có `qwen3:1.7b` và `qwen3-embedding:0.6b` (hoặc dùng bộ nối giả)

## Cài đặt

```bash
pip install -e ".[dev]"          # hoặc: make install
cp .env.example .env             # rồi điền giá trị
cd frontend && npm ci            # hoặc npm install
```

`.env` tối thiểu cần: `CWD_DATABASE_URL`, `CWD_SESSION_SECRET` (≥32 ký tự), `CWD_TELEMETRY_SECRET` (≥32), `CWD_STORAGE_ROOT`, `CWD_EMBEDDING_DIM`.

Bật AI nội bộ:

```bash
CWD_AI_PROVIDER=ollama
CWD_EMBEDDING_DIM=1024
make ai-up ai-pull               # docker compose --profile ai + ollama pull
```

## Chạy dev

```bash
make db-up        # PostgreSQL 16 + pgvector, cổng 5433
make migrate      # alembic upgrade head
make run          # API http://127.0.0.1:8000  (uvicorn --reload)
python -m app.worker             # worker xử lý job (terminal riêng)
cd frontend && npm run dev       # UI http://localhost:5173, proxy /api → :8000
```

Windows không có `make`: chạy trực tiếp

```powershell
docker compose -f deploy/compose.dev.yml up -d --wait
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --reload
.venv\Scripts\python.exe -m app.worker
```

Cấp quyền quản trị: `python -m app.cli add-admin quantri@congty.vn`.
Đăng nhập dev dùng IdP giả: bật `CWD_ALLOW_FAKE_IDP=true` rồi mở `http://localhost:5173/auth/login`.

Kiểm tra nhanh: `curl http://127.0.0.1:8000/healthz` → `{"status":"ok","db":"ok","queue":"ok"}`.

## Kiểm thử và cổng chất lượng

```bash
make gate    # = lint + type + test
make lint    # ruff check .
make type    # mypy app tests scripts  (--strict)
make test    # pytest -q  (tự tạo CSDL cwd_test; đổi bằng CWD_TEST_DATABASE_URL)
```

```bash
cd frontend
npm run lint && npm run type-check && npm test && npm run build
```

E2E trình duyệt: xem [`scripts/e2e/README.md`](scripts/e2e/README.md) (Playwright cài riêng). Test gọi Ollama thật bị loại mặc định: `pytest -m ollama`; đo hiệu năng: `pytest -m perf`.

> **Bẫy trên máy dev:** nếu đã `setx CWD_*` ở cấp hệ thống (ví dụ `CWD_EMBEDDING_DIM=1024`, `CWD_AI_PROVIDER=ollama`), biến đó **đè** giá trị test trong `tests/conftest.py` (dùng `setdefault`) và làm đỏ hàng loạt test (`expected 1024 dimensions, not 384`). Chỉ khai báo cấu hình trong `.env`, hoặc chạy test với môi trường đã xoá biến:
>
> ```powershell
> Get-ChildItem Env:CWD_* | Remove-Item Env:
> $env:PATH = 'C:\Program Files\Git\bin;' + $env:PATH   # test backup cần bash thật, không phải WSL
> .venv\Scripts\python.exe -m pytest -q
> ```

## API chính

Tiền tố `/api/v1` (trừ `/auth/*`, `/healthz`). Hợp đồng chi tiết: [`docs/05-planning/CONTRACTS.md`](docs/05-planning/CONTRACTS.md).

| Nhóm | Endpoint |
|---|---|
| Đăng nhập | `GET /auth/login`, `GET /auth/callback`, `POST /auth/logout`, `GET /api/v1/me` |
| Tài liệu | `POST/GET /api/v1/documents`, `DELETE /api/v1/documents/{docId}`, `GET …/{docId}/file` (Range), `GET …/events` (SSE) |
| Hỏi đáp | `POST /api/v1/chat/sessions`, `GET /api/v1/chat/sessions`, `GET /api/v1/chat/sessions/{sessionId}`, `POST /api/v1/chat/sessions/{sessionId}/messages` (SSE), `POST /api/v1/chat/messages/{messageId}/stop`, `POST /api/v1/chat/messages/{messageId}/rating` |
| Tổng hợp | `GET /api/v1/documents/{docId}/summary`, `GET /api/v1/suggestions` |
| Quản trị | `GET /api/v1/admin/users`, `GET /api/v1/admin/audit-log`, `GET /api/v1/metrics/weekly` |
| Hệ thống | `GET /healthz`, `GET /metrics`, `GET /api/v1/features`, `POST /api/v1/telemetry/events` |

Mọi phương thức ghi dưới `/api/v1` phải gửi header `X-Requested-With: cwd` (chống CSRF).

## Triển khai

```bash
docker compose -f deploy/compose.prod.yml --env-file deploy/.env up -d --build
```

Có Dockerfile backend, image web nginx (TLS + SSE), sao lưu/khôi phục, cảnh báo Prometheus. Sổ tay: [`deploy/evidence/runbook.md`](deploy/evidence/runbook.md).

## Tài liệu

| Tài liệu | Nội dung |
|---|---|
| [`docs/requirements/`](docs/requirements) | BRD, PRD, checklist ISO/IEEE |
| [`docs/03-analysis/`](docs/03-analysis) | USER_STORIES, BACKBONE_STORIES |
| [`docs/04-design/`](docs/04-design) | SAD, thiết kế UI/UX |
| [`docs/05-planning/`](docs/05-planning) | PLAN (98 task), CONTRACTS, từng task trong `tasks/` |
| [`docs/adr/`](docs/adr) | Quyết định kiến trúc (0001–0005, 0101–0102) |
| [`docs/traceability.md`](docs/traceability.md) | Story → BR → task → mã → test → trạng thái |
| [`AGENTS.md`](AGENTS.md) | Quy ước code, quyền hạn, vòng lặp làm việc |

## Giới hạn đã biết

- **NFR-001 chưa đạt**: sinh câu trả lời trên CPU chậm hơn mục tiêu (xem ADR-0004).
- Câu hỏi chung đôi khi trả về `citationCount=0` (mô hình không phát nhãn `[cN]`); câu hỏi không dấu bị đánh dấu `LANG_UNSUPPORTED`.
- OCR, SSO, nhà cung cấp AI thật vẫn chạy sau cổng với bộ nối giả.
- CI đã xanh cục bộ nhưng **chưa chạy trên GitHub Actions thật**; sổ tay vận hành chưa được người vận hành diễn tập.
