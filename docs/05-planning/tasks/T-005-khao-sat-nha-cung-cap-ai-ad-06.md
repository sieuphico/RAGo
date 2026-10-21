# T-005 · Khảo sát nhà cung cấp AI (AD-06)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 10 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | US-060 |
| BR | — |
| NFR, EC, cổng | NFR-001, NFR-009 |
| Quyết định kiến trúc | AD-06 |
| Phụ thuộc | — |
| Mở khóa | [T-302](T-302-bo-noi-ai-that-ad-06.md) |

## Mục tiêu

Có đủ số liệu để chọn nhà cung cấp AI (nhúng và sinh câu trả lời) hoặc mô hình tự host.

## File cần tạo hoặc sửa

- `docs/05-planning/spikes/AI-provider.md`
- `backend/scripts/ai_trial.py`

## Các bước

1. Chọn ≥ 2 ứng viên (dịch vụ đám mây đáp ứng CON-005, mô hình mở tự host).
2. Đo trên mẫu tiếng Việt: chất lượng truy xuất bằng vector nhúng, độ trễ tới chữ đầu tiên (p90), chi phí cho 1.000 câu hỏi.
3. Ghi số chiều vector, điều khoản lưu giữ và huấn luyện dữ liệu, vị trí xử lý dữ liệu.
4. Viết báo cáo và đề xuất, chuyển cho Bảo mật thông tin để xét DEP-001.

## Tiêu chí hoàn thành

- [ ] Báo cáo có số đo cho ≥ 2 ứng viên.
- [ ] Nêu rõ ứng viên nào đáp ứng CON-005 (a)(b)(c).
- [ ] Ước tính chi phí hằng tháng so với 300 USD (NFR-009).

## Kiểm thử cần viết

- Không có test mã; báo cáo được Trưởng đội kỹ thuật và Bảo mật thông tin xem

## Lưu ý

Nếu chọn tự host trong hạ tầng tại chỗ, cần thêm kế hoạch phần cứng; báo ngay nhà tài trợ (RA-02).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
