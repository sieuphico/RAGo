---
description: Lập kế hoạch triển khai một user story từ docs (dừng nếu AC chưa rõ)
argument-hint: <US-xxx>
---

Lập kế hoạch cho story **$ARGUMENTS**. Chỉ đọc, không sửa file.

1. Đọc `docs/03-analysis/USER_STORIES.md` (story và AC), `docs/05-planning/PLAN.md` mục 8.1 (task của story), `docs/03-analysis/BACKBONE_STORIES.md` (quyết định đã chốt) và `docs/traceability.md` (đã làm tới đâu).
2. Với mỗi task của story: đọc file task và các mục CONTRACTS ghi ở "Đọc trước".
3. Phân loại từng AC: `[PRD]`/`[BRD]` = làm; `[Đề xuất]` = bỏ qua (chưa duyệt); ngưỡng % = chưa làm test (chờ DEP-003).
4. Xuất kế hoạch gồm: thứ tự task theo phụ thuộc và task đã xong; với mỗi task: file sẽ tạo/sửa, test sẽ viết (từ bảng "Kiểm thử cần viết"), AC nó đáp ứng; rủi ro; ADR có thể cần.
5. **Câu hỏi mở:** liệt kê AC chưa rõ, mâu thuẫn giữa docs, hoặc chỗ cần đổi CONTRACTS. Nếu có, kết thúc bằng "DỪNG: cần xác nhận" và không bắt đầu code.
