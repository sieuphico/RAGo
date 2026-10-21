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

## File cần tạo hoặc sửa

- `docs/05-planning/evidence/runbook.md`
- `docs/05-planning/evidence/release-notes.md`

## Các bước

1. Sổ tay: khởi động, dừng, sao lưu, khôi phục, xử lý khi AI lỗi, khi SSO lỗi, khi hàng đợi kẹt, khi đĩa đầy, thu hồi khóa API.
2. Danh sách bảng điều khiển và cảnh báo; liên hệ hỗ trợ.
3. Ghi chú phát hành: tính năng đã có và đã hoãn (cờ tắt), giới hạn đã biết, hành vi cần kiểm đặc biệt.

## Tiêu chí hoàn thành

- [ ] Người không tham gia phát triển làm theo sổ tay khôi phục được dịch vụ.
- [ ] Ghi rõ tính năng P1 chưa đạt hoặc đã hoãn.
- [ ] Không chứa bí mật.

## Kiểm thử cần viết

- Một người khác diễn tập theo sổ tay

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
