# T-007 · Khảo sát thư viện trích văn bản PDF

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | US-012, US-013 |
| BR | BR-005, BR-027 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-05 |
| Phụ thuộc | — |
| Mở khóa | [T-206](T-206-ingest-trich-van-ban-theo-trang.md) |

## Mục tiêu

Chọn thư viện trích văn bản theo trang, có phát hiện lớp văn bản, hỗ trợ tiếng Việt và giấy phép phù hợp.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- SAD mục 8 câu hỏi Q-A9
- SAD mục 4.1 dòng "PDF là đầu vào không tin cậy"
- NFR-004 (300 trang) trong BRD

## File cần tạo hoặc sửa

- `docs/05-planning/spikes/PDF-lib.md`

## Các bước

1. Tạo 4 tệp thử: PDF có văn bản tiếng Việt có dấu (3 trang), PDF chỉ có ảnh, PDF có mật khẩu, PDF bị cắt cụt (xóa nửa sau tệp).
2. So sánh 2–3 thư viện Python (ví dụ pypdf, pdfplumber, pypdfium2, PyMuPDF): chữ có dấu có đúng không, phát hiện trang không có lớp văn bản, tốc độ trên PDF 300 trang, phản ứng với tệp có mật khẩu và tệp hỏng, khả năng dựng trang thành ảnh 300 dpi cho OCR.
3. Ghi giấy phép từng thư viện (PyMuPDF dùng AGPL hoặc giấy phép thương mại).
4. Đề xuất một thư viện (hoặc một cặp: trích văn bản + dựng ảnh) và lý do.

## Tiêu chí hoàn thành

- [ ] `PDF-lib.md` có bảng so sánh 5 tiêu chí ở bước 2 cho từng thư viện.
- [ ] Có tên thư viện đề xuất và giấy phép được Trưởng đội kỹ thuật chấp nhận.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Kiểm tra báo cáo | Mở `PDF-lib.md` | Mỗi thư viện có kết quả trên đủ 4 tệp thử và cột giấy phép |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Viết mã trích văn bản (T-206).
- Dựng trang thành ảnh cho OCR (T-209).

## Lưu ý

Giải quyết câu hỏi mở Q-A9 của SAD.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
