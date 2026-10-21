# T-608 · Thử tải (G4)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | — |
| BR | BR-013 |
| NFR, EC, cổng | NFR-001, NFR-003, NFR-002, G4 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-307](T-307-dich-vu-tra-loi-answerservice.md), [T-613](T-613-dung-moi-truong-staging.md) |
| Mở khóa | [T-612](T-612-ho-tro-uat-va-sua-loi.md) |

## Mục tiêu

Chứng minh NFR-001 và NFR-003 với kho ≥ 200 tài liệu và 20 người dùng đồng thời.

## File cần tạo hoặc sửa

- `backend/loadtest/locustfile.py`
- `docs/05-planning/evidence/load-test.md`

## Các bước

1. Mô phỏng 20 người dùng, mỗi người 1 câu hỏi/phút qua API-08 (đọc hết luồng SSE).
2. Đo thời gian tới trạng thái đầu và tới hoàn tất; tính p50, p90.
3. Chạy thêm một lần tải lên 10 tệp khi đang có truy vấn để kiểm tra worker không chặn hỏi đáp.
4. Ghi cấu hình máy, kết quả và điểm nghẽn.

## Tiêu chí hoàn thành

- [ ] p90 ≤ 15 giây và trạng thái đầu ≤ 1 giây ở 20 người dùng (NFR-001, NFR-003).
- [ ] Xử lý tài liệu không làm câu hỏi chậm hơn ngưỡng.
- [ ] Báo cáo có số đo thật, nêu rõ nếu dùng AI giả lập thay AI thật.

## Kiểm thử cần viết

- Báo cáo thử tải

## Lưu ý

Kết quả với AI giả lập không chứng minh độ trễ thật; cần chạy lại với nhà cung cấp đã chọn.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
