# Bài học từ 5 phiên làm việc (19–26/10/2026)

Nguồn: transcript các phiên trong `C:\Users\dryuk\.claude\projects\d--SDLC-RAG\` (tóm tắt bởi tác tử, chưa đọc từng dòng) và `SDLC-Prompt-Checklist/AI_SDLC-SOP.md`.

## 1. Các phiên đã làm gì

| Phiên | Nội dung | Kết quả |
|---|---|---|
| 72265cf2 | "setup mcp figma" | Không đạt: OAuth cần phiên tương tác |
| d154db91 | BRD (IEEE 29148) → review bằng checklist xlsx → PRD (26 story) → use case .drawio → blueprint UI/UX; 2 đợt hỏi chọn để chốt DEC-012…018 | BRD v0.4, PRD v0.2, blueprint v0.2; push thất bại (chưa có remote), Figma bị chặn |
| 9ad43bfc | Figma/HTML prototype, SAD, USER_STORIES, 5 sơ đồ .drawio, PLAN + 98 task + CONTRACTS.md | Lần 1 chỉ 87 task sơ sài, phải làm lại tới chuẩn Definition of Ready |
| 4b688b01 | AGENTS.md + lệnh `/plan-story` `/gen-tests` `/review-diff` `/fix-ci`; MVP backend (330+ test) và frontend (241 test, subagent song song trong worktree); đóng gói Docker; test plan + spec.json + agent-browser | E2E 7/7 PASS; còn: AI CPU 17–24 s (mục tiêu ≤ 15 s), OCR ảnh thật, SSO thật, CI chưa chạy trên GitHub |
| e5621392 | (phiên này) | Tổng hợp + thiết kế workflow |

## 2. Bài học (xếp theo giá trị)

### Cách hỏi người dùng
1. **Hỏi bằng lựa chọn trực tiếp, kèm đề xuất mặc định**, không tạo file checklist trong repo (người dùng yêu cầu xóa file checklist đã commit). Gộp theo đợt, mỗi đợt ≤ 4 câu, đặt phương án khuyến nghị lên đầu.
2. **Không diễn giải câu trả lời mơ hồ.** "ok"/"có" cho câu hỏi gộp hai việc đã bị hiểu thành đồng ý cả hai. Mỗi câu hỏi chỉ một quyết định.
3. Ghi mọi quyết định vào nhật ký `DEC-xxx` (đã chạy tốt ở BRD) để truy vết và không hỏi lại.

### Chất lượng tài liệu
4. **Không bịa số.** Dùng nhãn `[TBD]`, `[Unverified]`, `[Đề xuất]` và gắn với câu hỏi mở; AC `[Đề xuất]` chưa được duyệt thì không làm.
5. **Kế hoạch lần đầu phải đạt Definition of Ready ngay**: chữ ký hàm/props, kiểu dữ liệu đã định nghĩa trong `CONTRACTS.md`, bảng "Kiểm thử cần viết", không có "theo Blueprint/PRD" thay cho nội dung. Làm sau tốn thêm cả vòng (87 → 98 task).
6. **Rủi ro lịch trình báo thẳng** (543 giờ so với 420 giờ có sẵn) và ghi thành RSK/OQ có chủ và hạn.
7. Tài liệu lệch code → hỏi, ghi ADR; AGENTS.md: không tự đổi CONTRACTS.md cho code chạy.

### Kiểm chứng
8. **Kiểm bằng công cụ thật**, không tin báo cáo của chính agent: trình duyệt headless cho prototype, `mermaid.parse`, `make gate`, ma trận AC–TC kiểm bằng máy, kỳ vọng ghi trước trong `spec.json`. Sơ đồ .drawio phải được mở/render thật, không chỉ kiểm XML.
9. Bộ kiểm tự viết cũng sai (27 lỗi báo nhầm) → kiểm lại mẫu trước khi tin.
10. Phát hiện lỗi đóng gói sớm bằng chạy Docker thật (httpx chỉ ở dev, nginx header, IPv6/IPv4, PyYAML).

### Môi trường và vận hành
11. **Preflight môi trường trước khi bắt đầu** (Docker, cổng 5432/5433, Ollama, Python/Node, `.env`, remote git, đăng nhập OAuth cần tương tác). Nhiều lần dừng giữa chừng vì thiếu bước này.
12. Windows/Git Bash: tránh heredoc nhiều tầng (dùng Write), `&` lồng làm báo "xong" sớm, `/tmp` của Git Bash ≠ Python, lệnh daemon phải ghi ra file thay vì `| tail`.
13. **Song song hóa từ đầu** (frontend/backend trong worktree riêng) nhưng mỗi worktree có chỉ mục git riêng; script commit phải nối `&&`, không nuốt lỗi.
14. Script sinh file không được xóa thư mục đang đứng trong đó; chỉ xóa file bên trong.

### Phạm vi và kiểm soát
15. Agent đọc docs quá lâu → người dùng ngắt. Đọc có mục tiêu (chỉ file liên quan story), tóm tắt trước khi hành động.
16. Commit chọn lọc, chỉ file do agent tạo; kiểm `git status` trước/sau; không đẩy bất ngờ nhiều commit tồn (lần push gộp 3 commit chưa push). **Không `git push` nếu người dùng chưa nói rõ.**
17. Chọn đúng công cụ theo CLAUDE.md (agent-browser, không Playwright); thay đổi thư viện phải có ADR.
18. Dừng và hỏi khi AC chưa rõ, mâu thuẫn, môi trường chết (đã ghi vào AGENTS.md/CLAUDE.md và chạy tốt).
