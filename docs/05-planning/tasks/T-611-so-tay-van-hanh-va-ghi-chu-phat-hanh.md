# T-611 · Sổ tay vận hành và ghi chú phát hành

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | NFR-005, NFR-006 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-603](T-603-sao-luu-khoi-phuc-va-buoi-thu-khoi-phuc.md), [T-604](T-604-giam-sat-suc-khoe-chi-so-va-canh-bao.md) |
| Mở khóa | — |

## Mục tiêu

Tài liệu để chuyển giao cho người vận hành.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- deploy-notes.md (T-602), restore-drill.md (T-603), alerts.yml (T-604)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-603](T-603-sao-luu-khoi-phuc-va-buoi-thu-khoi-phuc.md) Sao lưu, khôi phục và buổi thử khôi phục: `deploy/backup/backup.sh`, `deploy/backup/restore.sh`, `docs/05-planning/evidence/restore-drill.md`
- [T-604](T-604-giam-sat-suc-khoe-chi-so-va-canh-bao.md) Giám sát: sức khỏe, chỉ số và cảnh báo: `install_metrics`, `AI_COST`, `FIRST_TOKEN`, `ERRORS`

## File cần tạo hoặc sửa

- `docs/05-planning/evidence/runbook.md`
- `docs/05-planning/evidence/release-notes.md`

## Các bước

1. Sổ tay `runbook.md` mỗi mục gồm: dấu hiệu, kiểm tra, lệnh xử lý, cách xác nhận đã ổn. Mục: khởi động, dừng, cập nhật phiên bản, sao lưu, khôi phục, AI lỗi hoặc hết hạn mức, SSO lỗi, hàng đợi kẹt (`release_stale`), đĩa gần đầy, thu hồi và thay khóa API, thêm quản trị viên đầu tiên (`make add-admin`).
2. Danh sách chỉ số, cảnh báo và người liên hệ (vai trò, không ghi số điện thoại cá nhân vào kho mã).
3. `release-notes.md`: tính năng đã có, tính năng P1 đang tắt bằng cờ, giới hạn đã biết (OCR, ngôn ngữ, không phân trang), điểm cần kiểm khi thí điểm.

## Tiêu chí hoàn thành

- [ ] Một người không tham gia phát triển làm theo mục khôi phục và mục hàng đợi kẹt trên staging thành công.
- [ ] Ghi rõ tính năng P1 nào chưa đạt hoặc đang tắt.
- [ ] Không chứa bí mật.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Diễn tập | Người vận hành đọc `runbook.md`, khôi phục staging từ bản sao lưu | Thành công, ghi thời gian và điểm khó hiểu vào sổ tay |
| Kiểm tra bí mật | Tìm `CWD_.*SECRET=.+`, `sk-` trong hai tệp | Không có |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đào tạo người dùng (đội BD tự làm trong UAT).
- Quy trình trực sự cố 24/7 (ngoài MVP).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
