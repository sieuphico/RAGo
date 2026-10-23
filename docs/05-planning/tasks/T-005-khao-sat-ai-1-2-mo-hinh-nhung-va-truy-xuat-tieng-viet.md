# T-005 · Khảo sát AI (1/2): mô hình nhúng và truy xuất tiếng Việt

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
| Phụ thuộc | — |
| Mở khóa | [T-011](T-011-khao-sat-ai-2-2-sinh-cau-tra-loi-do-tre-chi-phi-khuyen-nghi.md) |

## Mục tiêu

Đo chất lượng truy xuất tiếng Việt của ≥ 2 mô hình nhúng để làm đầu vào cho khuyến nghị AD-06 (T-011).

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CON-005 (a)(b)(c), NFR-001, NFR-009 trong BRD
- SAD mục 6 AD-06

## File cần tạo hoặc sửa

- `docs/05-planning/spikes/AI-provider.md`
- `backend/scripts/ai_trial.py`
- `docs/05-planning/spikes/ai-qa-pairs.json`

## Các bước

1. Chọn ≥ 2 ứng viên: 1 dịch vụ đám mây đáp ứng CON-005 và 1 mô hình mở tự host được.
2. Tạo `ai-qa-pairs.json`: 30 cặp `{question, passage_id}` từ 100 đoạn văn mẫu tiếng Việt không mật (10 câu hỏi diễn đạt khác hẳn đoạn văn).
3. Viết `ai_trial.py embed --model <tên>`: nhúng 100 đoạn và 30 câu hỏi, xếp hạng bằng cosine, tính recall@8 và MRR.
4. Ghi số chiều vector, giá mỗi 1 triệu token, điều khoản lưu giữ và huấn luyện, vị trí xử lý dữ liệu.
5. Ghi kết quả vào mục "Nhúng" của `AI-provider.md`.

## Tiêu chí hoàn thành

- [ ] Có recall@8 và MRR cho ≥ 2 mô hình trên cùng 30 câu hỏi.
- [ ] Mỗi ứng viên có số chiều vector, giá và điều khoản dữ liệu.
- [ ] Script chạy lại được bằng một lệnh.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Chạy lại script | Chạy `ai_trial.py embed` hai lần với cùng mô hình | Cùng recall@8 và MRR |
| Kiểm tra báo cáo | Mở `AI-provider.md` mục "Nhúng" | Bảng có đủ 2 ứng viên và 5 cột: recall@8, MRR, số chiều, giá, điều khoản |

## Lệnh kiểm tra

```bash
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đo mô hình sinh câu trả lời và khuyến nghị (T-011).
- Bộ nối AI trong ứng dụng (T-302, T-315).

## Lưu ý

Nếu chọn tự host trong hạ tầng tại chỗ, cần thêm kế hoạch phần cứng; báo ngay nhà tài trợ (RA-02).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
