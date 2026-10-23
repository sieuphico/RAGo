# Checklist cần xác nhận

Đánh dấu `[x]` vào đúng một lựa chọn cho mỗi mục. Chưa chọn thì tôi không làm phần phụ thuộc.

## 1. Mã FR trong commit
Docs không có mã FR (chỉ US, BR, NFR, EC).
- [ ] A. Gắn task + US + BR, bỏ FR (đang dùng) *(khuyến nghị)*
- [ ] B. Tôi sẽ cung cấp bảng FR trước; tạm dừng việc gắn FR
- [ ] C. Coi BR là FR, ghi nhãn `FR=BR-xxx`

## 2. Vị trí thư mục mã
- [ ] A. `backend/app`, `backend/tests` theo PLAN 3.1 (đang dùng) *(khuyến nghị)*
- [ ] B. `app/`, `tests/` ở gốc repo; tôi di chuyển và sửa PLAN/AGENTS/CI

## 3. US-022 ghép hai kết quả
- [ ] A. Tách US-022a (thẻ trích dẫn trong câu trả lời) và US-022b (bấm mở đúng trang); làm 022a trước *(khuyến nghị)*
- [ ] B. Giữ nguyên một story, làm cả hai phần cùng lúc
- [ ] C. Chưa quyết; chỉ làm US-010 trước

## 4. AC `[Đề xuất]` (chưa PM/PO duyệt)
Gồm: US-010 thử lại khi mất mạng; US-020 EC-04/07/11; US-022 tài liệu đã xóa.
- [ ] A. Chỉ làm AC `[PRD]`/`[BRD]`, bỏ qua `[Đề xuất]` tới khi duyệt *(khuyến nghị)*
- [ ] B. Làm luôn các AC `[Đề xuất]`, ghi rõ trong commit
- [ ] C. Chọn từng AC (ghi bên dưới): ______

## 5. Ngưỡng AC phần trăm (cần bộ mẫu DEP-003, hạn 2026-11-27)
- [ ] A. Chưa viết test ngưỡng; thêm khi có bộ mẫu *(khuyến nghị)*
- [ ] B. Viết test ngưỡng với dữ liệu giả để giữ chỗ, đánh dấu skip

## 6. Thư viện đề xuất (RP-07)
SQLAlchemy 2 async, asyncpg, Alembic, psycopg, pytest, ruff, mypy, Python 3.12.
- [ ] A. Xác nhận cả danh sách *(khuyến nghị)*
- [ ] B. Thay đổi: ______

## 7. CI
- [ ] A. GitHub Actions (remote là GitHub; đang dùng) *(khuyến nghị)*
- [ ] B. GitLab CI theo mẫu T-601
- [ ] C. Chỉ chạy cục bộ `ci/run_ci.sh`

## 8. Bước tiếp theo
- [ ] A. T-002 → T-003 → T-009 → T-008 (cấu hình, CSDL, kiểu, ports/fake) *(khuyến nghị)*
- [ ] B. Dừng, chờ tôi duyệt phạm vi và lịch (PLAN mục 7, PQ-01)
