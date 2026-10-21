# T-604 · Giám sát: sức khỏe, chỉ số và cảnh báo

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | NFR-005, NFR-009 |
| Quyết định kiến trúc | AD-04 |
| Phụ thuộc | [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) |
| Mở khóa | [T-611](T-611-so-tay-van-hanh-va-ghi-chu-phat-hanh.md) |

## Mục tiêu

Điểm cuối sức khỏe, chỉ số Prometheus và cảnh báo theo SAD mục 4.3.

## File cần tạo hoặc sửa

- `backend/app/api/health.py`
- `backend/app/core/metrics.py`
- `deploy/alerts.yml`
- `backend/tests/integration/test_health_metrics.py`

## Các bước

1. `/healthz` kiểm tra API, kết nối PostgreSQL và hàng đợi; worker có kiểm tra riêng.
2. `/metrics` (định dạng Prometheus `[Đề xuất]`): độ trễ API và chữ đầu tiên, số câu hỏi, lỗi theo mã, độ sâu hàng đợi, thời gian xử lý tài liệu, chi phí AI ước tính, dung lượng đĩa. Không có nhãn chứa nội dung.
3. Cảnh báo: chi phí AI đạt 80% hạn mức, tác vụ lỗi liên tiếp, đĩa gần đầy, sao lưu thất bại, p90 vượt 15 giây.

## Tiêu chí hoàn thành

- [ ] Có cảnh báo khi chi phí AI đạt 80% hạn mức (G10).
- [ ] Chỉ số không chứa nội dung hay mã người dùng.
- [ ] `/healthz` phản ánh đúng khi CSDL mất kết nối.

## Kiểm thử cần viết

- `test_healthz_db_down`
- `test_metrics_no_content_labels`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
