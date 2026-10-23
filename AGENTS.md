# AGENTS.md

Dự án "Chat với tài liệu" (MVP). Nguồn sự thật duy nhất: `docs/`. Docs chưa rõ hoặc mâu thuẫn → dừng và ghi câu hỏi, không đoán.

## Đọc trước
- `docs/05-planning/PLAN.md` (cấu trúc, quy ước, định nghĩa hoàn thành), `docs/05-planning/CONTRACTS.md` (tên, mã lỗi, API, SSE).
- Một task = một file trong `docs/05-planning/tasks/`; chỉ làm đúng file task, giữ nguyên chữ ký.
- Story xương sống: `docs/03-analysis/BACKBONE_STORIES.md`.

## Cấu trúc
`app` (domain, core, api, modules, ports, adapters, models, worker), `tests`, `docs/`, `ci/`.
Quy tắc phụ thuộc: router → mô-đun → ports → adapters; mô-đun không nhập `app.adapters`; chỉ `ai_gateway` gọi nhà cung cấp AI.

## Lệnh
`make install lint type test` (Python). Trên Windows không có make: chạy ở gốc kho `ruff check .`, `mypy app`, `pytest`.

## Quy ước
- Commit: Conventional Commits, kèm mã task/US/BR, ví dụ `feat(documents): upload API (T-201, US-010, US-011)`. Commit nhỏ, một task một commit.
- Không bí mật trong mã/log; không ghi nội dung câu hỏi, câu trả lời, tài liệu vào log hay telemetry.
- Thư viện ngoài danh sách đã duyệt: hỏi trước.
- Không tự chạy lại "test xanh" của trợ lý làm bằng chứng; chạy và đọc kết quả thật.

## CSDL phát triển
`make db-up` (PostgreSQL + pgvector, cổng **5433** vì 5432 hay bị PostgreSQL cài sẵn chiếm), rồi `make migrate`. Sao chép `.env.example` thành `.env` và điền giá trị (`CWD_DATABASE_URL=postgresql+asyncpg://cwd:cwd@localhost:5433/cwd`). Test tích hợp tự tạo CSDL `cwd_test` (đổi bằng `CWD_TEST_DATABASE_URL`).
