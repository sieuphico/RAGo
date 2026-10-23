# AGENTS.md

Dự án "Chat với tài liệu" (MVP): tải PDF lên kho chung, hỏi đáp tiếng Việt/Anh có trích dẫn tên tài liệu và số trang.
Nguồn sự thật: `docs/`. Docs chưa rõ hoặc mâu thuẫn → **dừng và hỏi**, không đoán.

## Stack
Python 3.12, FastAPI, SQLAlchemy 2 async + asyncpg, Alembic (psycopg), PostgreSQL 16 + pgvector, pydantic-settings.
Kiểm tra: pytest + pytest-asyncio, ruff, mypy `--strict`. Frontend (`frontend/`): Vue 3, TypeScript, Vite, Pinia, Vue Router, Vitest (`npm run lint | type-check | test | build`).
AI nội bộ: Ollama (`qwen3:1.7b` sinh, `qwen3-embedding:0.6b` nhúng) — `make ai-up ai-pull`; đặt `CWD_AI_PROVIDER=ollama`, `CWD_EMBEDDING_DIM=1024`.
AI, OCR, SSO, kho tệp đi qua `ports/`; chạy bằng bộ nối giả (`adapters/*_fake.py`) tới khi nhà cung cấp được chốt (AD-06).

## Lệnh
| Việc | Lệnh |
|---|---|
| Cài | `pip install -e ".[dev]"` (hoặc `make install`) |
| CSDL dev | `make db-up` (cổng **5433**; 5432 hay bị PostgreSQL cài sẵn chiếm), `make migrate`, `make db-down` |
| Chạy | `make run` (API), `python -m app.worker` (worker), `npm run dev` trong `frontend/` (proxy sang :8000) |
| Đóng gói | `docker compose -f deploy/compose.prod.yml --env-file deploy/.env up -d --build` (xem `deploy/evidence/runbook.md`) |
| E2E trình duyệt | `scripts/e2e/README.md` (Playwright cài riêng) |
| Lint / kiểu / test | `make lint`, `make type`, `make test` |
| **Cổng chất lượng** | `make gate` = lint + type + test |

Windows không có `make`: chạy trực tiếp `ruff check .`, `mypy app tests`, `pytest -q` (nên dùng `.venv\Scripts\python.exe -m ...`).
Sao chép `.env.example` thành `.env` và điền giá trị. Test tích hợp tự tạo CSDL `cwd_test` (đổi bằng `CWD_TEST_DATABASE_URL`).

## Cấu trúc
`app/` (domain, core, api, modules, ports, adapters, models, worker), `tests/` (unit, integration), `migrations/`, `deploy/`, `ci/`, `docs/`.
Phụ thuộc: router → mô-đun → ports → adapters. Mô-đun/api/worker **không** nhập `app.adapters` (chỉ `core/wiring.py`); chỉ `ai_gateway` gọi nhà cung cấp AI. Test `test_import_rules` bắt vi phạm.

## Quy ước code
- Tên kiểu, mã lỗi, đường dẫn API, sự kiện SSE, khóa cấu hình: đúng từng chữ với `docs/05-planning/CONTRACTS.md`. Không tự thêm mã lỗi hay trường JSON.
- JSON camelCase, Python snake_case; repository `async def`, nhận `AsyncSession` đầu tiên, chỉ `flush`; service/router quyết định `commit`.
- Hàm phụ thuộc thời gian nhận `now`/`clock`. `mypy --strict` phải sạch.
- Commit nhỏ, một task một commit, Conventional Commits kèm mã: `feat(documents): upload API (T-201, US-010, US-011, BR-001)`. Repo không có mã FR; dùng task + US + BR.
- Test trước hoặc cùng lúc với code; mỗi dòng trong bảng "Kiểm thử cần viết" của file task thành một test.

## Điều cấm
- Không ghi bí mật vào mã, log, ảnh container, dữ liệu thử. Không ghi nội dung câu hỏi, câu trả lời, tài liệu vào log hay telemetry.
- Không thêm thư viện ngoài danh sách đã duyệt (xem `pyproject.toml`) mà chưa hỏi.
- Không làm AC `[Đề xuất]` chưa được PM/PO duyệt; không làm test ngưỡng % tới khi có bộ mẫu DEP-003 (xem `docs/03-analysis/BACKBONE_STORIES.md`).
- Không tự đổi CONTRACTS.md để cho code chạy: dừng và hỏi.
- Không `git push`, `--force`, `reset --hard`, `--no-verify`, và không bỏ qua test hỏng.
- Không dùng dịch vụ cloud (Artifact/Docs/Drive): ghi file cục bộ.

## Quyền hạn
- **Được sửa:** `app/`, `tests/`, `migrations/`, `deploy/`, `ci/`, `.github/`, `Makefile`, `pyproject.toml`, `AGENTS.md`, `.claude/`, `docs/adr/`, `docs/traceability.md`.
- **Không sửa (docs đã baseline):** `docs/requirements/`, `docs/03-analysis/`, `docs/04-design/`, `docs/05-planning/`, `docs/design/`, `docs/archive/`. Cần đổi → ghi câu hỏi hoặc ADR, chờ người duyệt. (`.claude/settings.json` chặn ghi các thư mục này.)

## Lệnh nhanh (slash commands, `.claude/commands/`)
`/plan-story <US-xxx>` lập kế hoạch · `/gen-tests <T-xxx|đường dẫn>` sinh test · `/review-diff` rà thay đổi · `/fix-ci` sửa lỗi cổng.

## Vòng lặp làm việc
1. **Plan:** `/plan-story` → danh sách task, AC dùng được, câu hỏi mở. AC chưa rõ → dừng.
2. **Code:** một task, chỉ file ghi trong task, giữ nguyên chữ ký.
3. **Test:** `/gen-tests`, rồi `make gate`; đọc kết quả thật.
4. **Review:** `/review-diff` trên diff của task.
5. **Refine:** sửa theo review, chạy lại 3–4.
6. **Dừng** khi mọi cổng xanh (lint, type, test; CI khi có) và `docs/traceability.md` đã cập nhật. Bị chặn hoặc cần quyết định → dừng và hỏi, không vòng lặp vô hạn (tối đa 3 vòng refine cho một task).

## ADR và truy vết
- Quyết định kiến trúc mới (đổi cấu trúc, thư viện, hợp đồng, hành vi khác tài liệu thiết kế) → ghi `docs/adr/NNNN-tên.md` theo `docs/adr/0000-template.md` trong cùng commit với code.
- Mỗi task xong → cập nhật `docs/traceability.md` (US → BR → task → mã → test → trạng thái) trong cùng commit.
