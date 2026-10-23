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
| FQ-07 | T-522 | `@playwright/test` và `@axe-core/playwright` (T-522 ghi [Đề xuất]) chưa được duyệt; môi trường E2E của T-606 (backend) chưa có | Không thêm thư viện; viết khung `e2e/a11y.spec.ts` (loại khỏi tsc và eslint) + kiểm tra tĩnh bằng Vitest (`a11y_static.spec.ts`); phần còn lại ghi ở `A11Y_REPORT.md` |
| FQ-08 | T-522 | Task yêu cầu ghi `docs/05-planning/evidence/a11y-report.md`, nhưng `docs/05-planning` nằm ngoài quyền sửa của nhánh frontend | Ghi `frontend/A11Y_REPORT.md`; người gộp nhánh chuyển sang `docs/05-planning/evidence/` nếu muốn |
| FQ-09 | T-523, T-524, T-525, T-512 | Các AC đánh dấu `[Đề xuất]` trong USER_STORIES (EC-03 thử lại từng tệp, EC-04 mất kết nối giữa chừng, EC-05 mất mạng, EC-06 thông báo chậm, EC-07 dừng, EC-11 giới hạn 2.000 ký tự, tài liệu đã xóa trong trích dẫn EC-14) chưa được PM/PO duyệt nhưng nằm trong tiêu chí hoàn thành của file task | Đã làm đúng theo tiêu chí của task; cần PM/PO duyệt hoặc loại bỏ |
| FQ-10 | T-524 | Task không nói URL có đổi thành `/chat/:sessionId` khi tạo phiên mới lúc gửi câu hỏi đầu | Không đổi URL (tránh mở lại phiên giữa lúc đang trả lời); lịch sử (T-516) mở phiên bằng liên kết |
| FQ-11 | T-525 | "Sau 65 giây đặt FAILED/TIMEOUT" ghi cho thành phần, nhưng thành phần chỉ nhận `message` | Làm cả ở `stores/chat.ts` (hủy luồng, `FAILED`/`TIMEOUT`) và ở `AnswerState.vue` (hiển thị dự phòng) |
| FQ-12 | T-502, T-507, T-511 | CONTRACTS mục 11 chỉ cho T-505, T-519, T-520 sửa `router/index.ts`; các task màn hình khác cũng phải thay component tạm | Đã thay component tạm trong `router/index.ts` ở các task tương ứng (không đổi route hay `meta.roles`) |
| FQ-13 | T-506 | `useDocumentsStore.uploads: Map` (CONTRACTS 10.5) trùng vai trò với `useUpload().items` (T-523) | Không tạo `uploads` trong store; hàng đợi nằm ở `composables/useUpload.ts` |
