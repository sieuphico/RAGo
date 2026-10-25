# Ma trận AC ↔ test case (sinh tự động, không sửa tay)

Nguồn: `tests/e2e/spec.json`. Sinh bằng `python scripts/check_test_matrix.py --write`.

| AC | Story | Trạng thái | Phát biểu đo được (tạm, chờ PM/PO duyệt) | TC (full) | TC (một phần) |
|---|---|---|---|---|---|
| US-010/AC1 | US-010 | MEASURABLE | Mốc t0 = lúc lệnh `upload` trả về. Trong ≤ 2000 ms sau t0, danh sách có một hàng tên tệp đã chọn và trạng thái là "Đang xử lý", "Đang nhận dạng ký tự (OCR)" hoặc "Sẵn sàng". | TC-UP-01 | — |
| US-010/AC2 | US-010 | MEASURABLE | Given tệp do minh tải lên đã "Sẵn sàng", When lan (BD_USER) hỏi câu có đáp án nằm trong tệp, Then câu trả lời có ≥ 1 thẻ trích dẫn mang tên tệp đó. | TC-UP-02 | — |
| US-010/AC3 | US-010 | OUT_OF_SCOPE | **OUT_OF_SCOPE**: AC [Đề xuất] chưa được PM/PO duyệt (AGENTS.md, BACKBONE_STORIES mục 4). | — | — |
| US-020/AC1 | US-020 | MEASURABLE | Với câu hỏi chuẩn và tệp mẫu, câu trả lời hiển thị chứa chuỗi "24 tháng" và có ≥ 1 thẻ trích dẫn. Chạy 3 phiên độc lập; đạt khi cả 3 phiên đạt. | TC-QA-01 | — |
| US-020/AC2 | US-020 | NOT_MEASURABLE | **NOT_MEASURABLE**: Cần 200 tài liệu và bộ câu hỏi chuẩn (DEP-003, hạn 2026-11-27); "hiển thị đầy đủ" chưa định nghĩa. Đo thủ công trên CPU cho 17–24 s nên dự kiến FAIL. Cần PM/PO sửa AC (tách NFR-001/NFR-003) trước khi có TC. | — | — |
| US-020/AC3 | US-020 | MEASURABLE | Với ô nhập chỉ có khoảng trắng: nút Gửi ở trạng thái disabled; sau khi nhấn Enter, số tin nhắn người dùng bằng 0 và số yêu cầu POST tới `/messages` bằng 0. | TC-QA-02 | — |
| US-020/AC4 | US-020 | OUT_OF_SCOPE | **OUT_OF_SCOPE**: AC [Đề xuất] chưa duyệt. | — | — |
| US-020/AC5 | US-020 | OUT_OF_SCOPE | **OUT_OF_SCOPE**: AC [Đề xuất] chưa duyệt. | — | — |
| US-020/AC6 | US-020 | OUT_OF_SCOPE | **OUT_OF_SCOPE**: AC [Đề xuất] chưa duyệt. | — | — |
| US-022/AC1 | US-022 | MEASURABLE | Câu trả lời không phải "không tìm thấy" có ≥ 1 thẻ; mọi thẻ khớp `^\[.+ – tr\. \d+\]$`; văn bản hiển thị không còn nhãn thô `[cN]` hay `[[n]]`. | TC-CITE-01 | — |
| US-022/AC2 | US-022 | MEASURABLE | Sau khi bấm thẻ có trang N, trong ≤ 3000 ms: khung xem hiển thị, tên tài liệu khớp thẻ, nhãn trang là "Trang N / <tổng số trang>" và iframe có src kết thúc bằng `/file#page=N`. Việc trình duyệt cuộn đúng trang bên trong iframe ngoài phạm vi tự động. | TC-CITE-02 | — |
| US-022/AC3 | US-022 | NOT_MEASURABLE | **NOT_MEASURABLE**: Ngưỡng 90% cần bộ câu hỏi chuẩn + người chấm (DEP-003). Chỉ có thể lấy mẫu n=1 với dữ kiện đã biết (TC-CITE-03, không đóng AC này). | — | TC-CITE-03 |
| US-022/AC4 | US-022 | OUT_OF_SCOPE | **OUT_OF_SCOPE**: AC [Đề xuất] chưa duyệt. | — | — |

## Test case và kỳ vọng ghi trước

| TC | AC | Hồ sơ | Lặp | Kỳ vọng (PASS khi mọi kỳ vọng đúng) |
|---|---|---|---|---|
| TC-UP-01 | US-010/AC1 (full) | any | 1 | E1: `elapsed_ms_lte` t0→doc-row <= `2000`<br>E2: `text_matches` [data-testid=doc-row] [data-testid=doc-name] matches `^text_12p\.pdf$`<br>E3: `text_matches` [data-testid=doc-row] [data-testid=status-badge] matches `(Đang xử lý|Đang nhận dạng ký tự|Sẵn sàng)` |
| TC-UP-02 | US-010/AC2 (full) | ollama | 1 | E1: `count_gte` [data-testid=citation] >= `1`<br>E2: `text_matches` [data-testid=citation] matches `text_12p\.pdf` |
| TC-QA-01 | US-020/AC1 (full) | ollama | 3 phiên, all | E1: `text_matches` [data-testid=answer-text] matches `24 tháng`<br>E2: `count_gte` [data-testid=citation] >= `1` |
| TC-QA-02 | US-020/AC3 (full) | any | 1 | E1: `state` [data-testid=send] is `disabled`<br>E2: `count_eq` [data-testid=user-message] == `0`<br>E3: `request_count_eq` POST */chat/sessions/*/messages == `0` |
| TC-CITE-01 | US-022/AC1 (full) | ollama | 1 | E1: `count_gte` [data-testid=citation] >= `1`<br>E2: `text_matches` [data-testid=citation] matches_each `^\[.+ – tr\. \d+\]$`<br>E3: `text_matches` [data-testid=answer-text] not_matches `\[c\d+\]|\[\[\d+\]\]` |
| TC-CITE-02 | US-022/AC2 (full) | ollama | 1 | E1: `elapsed_ms_lte` t0→source-viewer <= `3000`<br>E2: `text_matches` [data-testid=viewer-name] matches `^text_12p\.pdf$`<br>E3: `text_matches` [data-testid=viewer-page] equals_template `Trang {N} / 12`<br>E4: `attr_matches` [data-testid=viewer-iframe]@src matches_template `^/api/v1/documents/[0-9a-f-]{36}/file#page={N}$` |
| TC-CITE-03 | US-022/AC3 (partial) | ollama | 1 | E1: `text_matches` [data-testid=citation] matches_any `^\[text_12p\.pdf – tr\. 12\]$` |
