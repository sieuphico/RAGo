# Test plan E2E — hai story xương sống (một trang)

Phiên bản 0.1 · 2026-10-25 · Đặc tả máy đọc: [spec.json](spec.json) · Ma trận: [AC_TC_MATRIX.md](AC_TC_MATRIX.md) · Báo cáo: [report-template.md](report-template.md)

## 1. Mục tiêu
Chứng minh bằng trình duyệt thật rằng hai luồng xương sống chạy đúng theo AC: **(A) tải PDF lên kho** (US-010) và **(B) hỏi đáp có trích nguồn** (US-020, US-022). Kết quả phải tái lập được và chấm bằng quy tắc ghi trước, không bằng cảm nhận.

## 2. Phạm vi
13 AC của US-010 (3), US-020 (6), US-022 (4); 7 test case, mỗi TC trỏ về đúng một AC. 8 AC đo được ở mức tự động hóa được; 2 AC chưa đo được (US-020/AC2, US-022/AC3) và 4 AC `[Đề xuất]` không có TC full (xem ma trận).

## 3. Non-goals
- AC `[Đề xuất]` chưa được PM/PO duyệt (US-010/AC3, US-020/AC4–6, US-022/AC4).
- Ngưỡng phần trăm và hiệu năng (US-020/AC2, US-022/AC3): cần DEP-003, 200 tài liệu, người chấm; thuộc T-607/T-608.
- Nội dung trang PDF hiển thị trong iframe (agent-browser không đọc được); OCR (US-013); SSO thật; tải đồng thời; truy cập từ điện thoại; chất lượng ngôn ngữ ngoài tiếng Việt/Anh.
- US-011, US-012, US-023 chỉ được kiểm gián tiếp ở các lớp dưới, không có TC E2E trong vòng này.

## 4. Chiến lược phân lớp (rẻ → đắt)
| Lớp | Công cụ | Đã có | Vai trò |
|---|---|---|---|
| L1 Đơn vị | pytest, Vitest | 407 + 241 test | logic: trích dẫn, prompt, chunk, validate tệp, trạng thái (`test_citations`, `test_prompt`, `test_upload_api`, `test_ingest`) |
| L2 Tích hợp API | pytest + PostgreSQL thật | gồm `test_chat_api`, `test_document_file`, `test_document_events` | hợp đồng API, SSE, phân quyền, dữ liệu |
| L3 E2E trình duyệt | `agent-browser`, 7 TC | tài liệu này | chỉ những gì L1–L2 không thấy: nối giao diện ↔ API ↔ worker ↔ AI thật, SSE sống, khung xem nguồn |
| L4 Đánh giá chất lượng | bộ câu hỏi chuẩn | chưa có | tỉ lệ đúng/hiệu năng; bị chặn bởi DEP-003 |
Nguyên tắc: một hành vi chỉ kiểm ở lớp thấp nhất thấy được nó; L3 không lặp lại L1–L2.

## 5. Môi trường và dữ liệu
URL app `http://localhost:5173` (proxy sang API `:8000`); tài khoản `minh@` (TEAM_LEAD), `lan@` (BD_USER), `quantri@` (ADMIN) qua IdP giả (`CWD_ALLOW_FAKE_IDP=true`, chỉ dev). Dữ liệu: `var/sample/text_12p.pdf` (12 trang; trang 12 có câu "Hợp đồng số HD-2026-012 có thời hạn 24 tháng kể từ 01/03/2026.") sinh tất định bởi `scripts/make_sample_data.py`. Hồ sơ **ollama** (Qwen3 1.7B + qwen3-embedding:0.6b) cho TC kiểm nội dung; hồ sơ **fake** chỉ kiểm đường ống. Chuẩn bị bằng `python scripts/e2e/setup_env.py` (SETUP-1, thêm `--reset` để xóa dữ liệu dev).

## 6. Định nghĩa PASS/FAIL
Mỗi TC có danh sách kỳ vọng ghi trước trong `spec.json` (`kind`, `target`, `op`, `value`). **PASS** = mọi kỳ vọng đúng (TC lặp: đúng ở mọi lượt). **FAIL** = ≥ 1 kỳ vọng sai trong môi trường khỏe. **INCONCLUSIVE** = môi trường chết, phần tử không quan sát được hoặc kết quả không so được: dừng và hỏi người. Kỳ vọng không được sửa trong lúc chạy; sửa kỳ vọng = đổi AC, qua PM/PO.

## 7. Tiêu chí thoát
1. 7/7 TC chạy trong một lần chạy sạch trên cùng một commit; mọi TC `full` PASS; báo cáo và `results.json` ở `reports/<run>/`.
2. Mỗi AC đo được có ≥ 1 TC `full` PASS; ma trận khớp spec (`python scripts/check_test_matrix.py` thoát 0, nằm trong `pytest`).
3. Cổng chất lượng xanh trên commit đó (ruff, mypy, pytest, frontend lint/type/test/build).
4. 0 FAIL/INCONCLUSIVE chưa có người xử lý; AC chưa đo được và AC ngoài phạm vi được liệt kê kèm chủ sở hữu.

## 8. Rủi ro đã biết
- Mô hình sinh không tất định: TC-QA-01 lặp 3 phiên, đạt khi 3/3. Có thể FAIL do chất lượng Qwen3 1.7B, không do lỗi hệ thống; kết quả phải ghi rõ là hành vi quan sát được.
- Các AC viết lại ở `spec.json` là phát biểu **tạm**, chưa được PM/PO duyệt; AC gốc trong `docs/03-analysis` chưa bị sửa (docs đã baseline).
- `setup_env.py` và các lệnh agent-browser trong TC chưa chạy thử được khi soạn (Docker tắt); lần chạy đầu tiên có thể phải chỉnh lệnh (không chỉnh kỳ vọng).
