# Hai user story xương sống

Nguồn: [USER_STORIES.md](USER_STORIES.md), [PLAN.md](../05-planning/PLAN.md) mục 4, [CONTRACTS.md](../05-planning/CONTRACTS.md). Tài liệu này không thêm yêu cầu; chỉ chọn và liệt kê điểm còn mở.

## Lựa chọn

| # | Xương sống | Story | Task (PLAN 8.1) |
|---|---|---|---|
| 1 | Tải PDF lên | US-010 (BR-001), kèm US-011, US-012 vì cùng luồng | T-101, T-104, T-112, T-201, T-204 – T-211 |
| 2 | Hỏi đáp có trích nguồn | US-022 (BR-010) trên nền US-020 (BR-008, BR-013) | T-303 – T-308, T-315, T-316, T-512, T-513 |

Cả hai đều P0. US-010 chạy với bộ nối giả (T-008) nên không bị chặn bởi AD-06, DEP-005.

## Điểm chưa rõ — dừng, chờ PM/PO hoặc Trưởng đội kỹ thuật

1. **Không có mã FR trong docs.** PRD/USER_STORIES chỉ dùng US, BR, NFR, EC. Commit gắn US và BR; nếu cần FR thì phải có bảng FR trước.
2. **Vị trí thư mục.** Yêu cầu nói `app/`, `tests/` ở gốc; PLAN 3.1 đặt `backend/app`, `backend/tests`. Đang theo PLAN (docs là nguồn sự thật).
3. **US-022 ghép hai kết quả** (có thẻ trích dẫn; bấm mở đúng trang) — USER_STORIES mục 10.2 đề nghị tách 022a/022b, chưa quyết. Chỉ làm phần trích dẫn trong câu trả lời (API-08) trước.
4. **AC ngưỡng chưa kiểm chứng được:** US-022 "≥ 90% trích dẫn đúng trang" và US-020 "≥ 90% trong 15 giây" cần bộ mẫu DEP-003 (hạn 2026-11-27). Chưa viết test ngưỡng.
5. **AC `[Đề xuất]` chưa được duyệt** (US-010 EC-03 thử lại; US-020 EC-04/07/11; US-022 tài liệu đã xóa). Chưa triển khai các AC này.
6. **Ngưỡng "đủ bằng chứng"** mặc định 0,0 tới khi T-607 đo (CONTRACTS Q-C13).
