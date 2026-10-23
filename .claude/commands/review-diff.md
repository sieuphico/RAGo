---
description: Rà soát diff hiện tại theo AGENTS.md, CONTRACTS.md và file task
argument-hint: [T-xxx]
---

Rà soát thay đổi chưa commit và các commit chưa push (`git diff HEAD`, `git log origin/main..HEAD` nếu có). Task: **$ARGUMENTS**. Chỉ đọc; không sửa.

Kiểm theo thứ tự:
1. **Phạm vi:** chỉ có file ghi trong file task; không tệp tạm, mã gỡ lỗi, thay đổi ngoài phạm vi; không sửa `docs/` đã baseline.
2. **Hợp đồng:** tên, kiểu, mã lỗi, đường dẫn, khóa cấu hình khớp từng chữ với CONTRACTS.md; chữ ký không đổi.
3. **Kiến trúc:** mô-đun/api/worker không nhập `app.adapters`; repository chỉ `flush`; không gọi nhà cung cấp AI ngoài `ai_gateway`.
4. **An toàn:** không bí mật; không ghi nội dung câu hỏi/câu trả lời/tài liệu vào log hay telemetry; kiểm quyền ở máy chủ.
5. **Test:** mỗi dòng bảng "Kiểm thử cần viết" có test; không test skip ẩn; không AC `[Đề xuất]` làm lén.
6. **Truy vết:** `docs/traceability.md` đã cập nhật; quyết định kiến trúc mới có ADR; commit đúng Conventional Commits kèm T/US/BR.

Xuất danh sách phát hiện theo mức (Chặn / Nên sửa / Ghi chú), mỗi mục có `file:dòng` và cách sửa. Không có phát hiện chặn thì nói rõ "đạt".
