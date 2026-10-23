# T-011 · Khảo sát AI (2/2): sinh câu trả lời, độ trễ, chi phí, khuyến nghị AD-06

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | US-060 |
| BR | — |
| NFR, EC, cổng | NFR-001, NFR-009 |
| Quyết định kiến trúc | AD-06 |
| Phụ thuộc | [T-005](T-005-khao-sat-ai-1-2-mo-hinh-nhung-va-truy-xuat-tieng-viet.md) |
| Mở khóa | [T-302](T-302-bo-noi-ai-that-1-2-nhung-theo-lo.md) |

## Mục tiêu

Đo mô hình sinh câu trả lời của các ứng viên ở T-005 và viết khuyến nghị AD-06 gửi Bảo mật thông tin.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- docs/05-planning/spikes/AI-provider.md mục "Nhúng" (kết quả T-005)
- CON-005 trong BRD

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-005](T-005-khao-sat-ai-1-2-mo-hinh-nhung-va-truy-xuat-tieng-viet.md) Khảo sát AI (1/2): mô hình nhúng và truy xuất tiếng Việt: `docs/05-planning/spikes/AI-provider.md`, `backend/scripts/ai_trial.py`, `docs/05-planning/spikes/ai-qa-pairs.json`

## File cần tạo hoặc sửa

- `docs/05-planning/spikes/AI-provider.md`
- `backend/scripts/ai_trial.py`

## Các bước

1. Với mỗi ứng viên: gửi 20 prompt, mỗi prompt gồm câu hỏi và 8 đoạn văn khoảng 3.000 token, chế độ luồng.
2. Ghi độ trễ tới token đầu (p50, p90), tổng thời gian, có hủy giữa chừng được không, có trả nhãn `[cN]` đúng chỉ dẫn không (đếm số câu trả lời có ≥ 1 nhãn hợp lệ).
3. Ước tính chi phí tháng với giả định 20 người × 10 câu/ngày × 22 ngày, cộng chi phí nhúng 500 tài liệu × 50 trang; so với 300 USD (NFR-009).
4. Viết mục "Khuyến nghị AD-06" trong `AI-provider.md`: ứng viên chọn, `embedding_dim`, giá mỗi 1.000 token vào và ra, rủi ro; gửi Bảo mật thông tin (DEP-001).

## Tiêu chí hoàn thành

- [ ] Báo cáo có p50, p90 độ trễ token đầu cho ≥ 2 ứng viên.
- [ ] Có ước tính chi phí tháng và kết luận đạt hay không đạt 300 USD.
- [ ] Có giá trị cụ thể cho `embedding_dim`, `ai_price_input_usd_per_1k`, `ai_price_output_usd_per_1k` của ứng viên chọn.
- [ ] Ghi ngày gửi Bảo mật thông tin.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Kiểm tra báo cáo | Mở `AI-provider.md` mục "Khuyến nghị AD-06" | Có ứng viên chọn, `embedding_dim`, hai giá token, ước tính chi phí tháng và ngày gửi Bảo mật thông tin |

## Lệnh kiểm tra

```bash
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Bộ nối AI trong ứng dụng (T-302, T-315).
- Phê duyệt DEP-001 (Bảo mật thông tin thực hiện).

## Lưu ý

Chỉ dùng văn bản mẫu không mật. Nếu chọn tự host trong hạ tầng tại chỗ, ghi yêu cầu phần cứng và báo nhà tài trợ (RA-02).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
