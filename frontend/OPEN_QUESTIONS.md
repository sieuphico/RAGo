# Câu hỏi mở của frontend

Mỗi dòng: mã task, vấn đề, lựa chọn tạm đã dùng. Không sửa CONTRACTS.md; chờ người duyệt.

| # | Task | Vấn đề | Lựa chọn tạm |
|---|---|---|---|
| FQ-01 | Chung | Worktree này thiếu `AGENTS.md`, `docs/adr/0000-template.md`, `docs/03-analysis/BACKBONE_STORIES.md` (có ở kho chính, chưa commit) | Đọc bản ở kho chính, làm theo; ADR tự tạo `docs/adr/` theo mẫu |
| FQ-02 | Chung | Dev chưa có chế độ "mock trong trình duyệt": API chưa có ở backend sẽ 404 khi chạy `npm run dev` | Chỉ test bằng mock (ADR 0101); chạy dev cần backend thật |
| FQ-03 | T-503, T-507 | CONTRACTS 10.1 chỉ có một tên `StatusData`, nhưng khung `status` của API-08 (`stage, docCount, messageId, scopeRemoved`) và của API-04 (`docId, status, failureReason, pageCount`) khác nhau; T-504 và T-507 đều dùng `StatusData` | `StatusData` = API-08 (theo T-504); API-04 là `DocumentStatusData`, `useDocumentsStore.applyEvent` nhận kiểu này |
| FQ-04 | T-503 | `AUTH_FORBIDDEN` có hai thông báo (chưa cấp quyền / bị thu hồi); bảng `ERROR_MESSAGES` chỉ có một giá trị cho mỗi mã | `ERROR_MESSAGES.AUTH_FORBIDDEN` = "chưa cấp quyền"; trường hợp thu hồi dùng khóa `denied.revoked` (T-505) |
| FQ-05 | T-505 | T-505 yêu cầu bắt `AUTH_FORBIDDEN` trong `request` nhưng chữ ký T-503 chỉ có `setAuthExpiredHandler` | Thêm export `setForbiddenHandler` ở `api/client.ts` (chỉ thêm, không đổi chữ ký có sẵn) |
| FQ-06 | T-506 | Task nói "8 giá trị trạng thái" nhưng CONTRACTS 10.3 chỉ có 6 nhãn (không có `DELETED`) | Thêm nhãn trung tính "Đã xóa" cho `DELETED` và biến thể "Xử lý lâu bất thường" (prop `slow`) làm đủ 8 trường hợp |
