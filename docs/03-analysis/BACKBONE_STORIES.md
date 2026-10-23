# Hai user story xương sống

Nguồn: [USER_STORIES.md](USER_STORIES.md), [PLAN.md](../05-planning/PLAN.md) mục 4, [CONTRACTS.md](../05-planning/CONTRACTS.md). Tài liệu này không thêm yêu cầu; chỉ chọn và liệt kê điểm còn mở.

## Lựa chọn

| # | Xương sống | Story | Task (PLAN 8.1) |
|---|---|---|---|
| 1 | Tải PDF lên | US-010 (BR-001), kèm US-011, US-012 vì cùng luồng | T-101, T-104, T-112, T-201, T-204 – T-211 |
| 2 | Hỏi đáp có trích nguồn | US-022 (BR-010) trên nền US-020 (BR-008, BR-013) | T-303 – T-308, T-315, T-316, T-512, T-513 |

Cả hai đều P0. US-010 chạy với bộ nối giả (T-008) nên không bị chặn bởi AD-06, DEP-005.

## Quyết định ngày 2026-10-23

| # | Vấn đề | Quyết định |
|---|---|---|
| 1 | Mã FR | Không có trong docs; commit gắn task + US + BR |
| 2 | Thư mục | `app/`, `tests/` ở gốc kho (PLAN 3.1 đã sửa) |
| 3 | US-022 | Tách 022a (thẻ trích dẫn trong câu trả lời, làm trước) và 022b (bấm mở đúng trang) |
| 4 | AC `[Đề xuất]` | Bỏ qua tới khi PM/PO duyệt; chỉ làm AC `[PRD]`, `[BRD]` |
| 5 | AC ngưỡng % | Chưa viết test; chờ bộ mẫu DEP-003 (2026-11-27) |
| 6 | Thư viện (RP-07) | Xác nhận danh sách đề xuất |
| 7 | CI | GitHub Actions |

## Còn mở

- Ngưỡng "đủ bằng chứng" mặc định 0,0 tới khi T-607 đo (CONTRACTS Q-C13).
- US-010, US-011, US-012 dùng AC `[PRD]`; mọi AC `[Đề xuất]` (EC-03 thử lại, EC-04/07/11, tài liệu đã xóa) chưa làm.
