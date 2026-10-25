# Báo cáo kiểm thử E2E — 20261025-190801

Người chạy: phiên Claude đóng vai `qa-runner` (bộ điều khiển Python gọi `agent-browser`). Báo cáo này không được sửa sau khi ghi.

| Mục | Giá trị |
|---|---|
| Run ID | `20261025-190801` |
| Commit | `a241cf8` (cây làm việc không có thay đổi ngoài `reports/` và file chưa theo dõi của người dùng) |
| Hồ sơ AI | ollama: qwen3:1.7b (sinh), qwen3-embedding:0.6b (nhúng), `CWD_EMBEDDING_DIM=1024` |
| Đặc tả | `tests/e2e/spec.json` sha256 `6ccbda85c37d1a42…` (ma trận khớp: có, `check_test_matrix.py` thoát 0) |
| Môi trường | API `/healthz` ok (db ok, queue ok), frontend :5173 200, Ollama có hai mô hình; giờ chạy 2026-10-25T19:08:02+07:00 → 2026-10-25T19:09:57+07:00 |

## Tóm tắt

| Kết quả | Số TC |
|---|---|
| PASS | 7 |
| FAIL | 0 |
| INCONCLUSIVE | 0 |
| Không chạy | 0 |

AC đo được đã có TC `full` PASS (6/6): US-010/AC1, US-010/AC2, US-020/AC1, US-020/AC3, US-022/AC1, US-022/AC2.

AC không tính: NOT_MEASURABLE — US-020/AC2, US-022/AC3 (TC-CITE-03 chỉ là mẫu n=1, **không đóng** AC); OUT_OF_SCOPE (`[Đề xuất]`) — US-010/AC3, US-020/AC4–6, US-022/AC4. Lý do nguyên văn ở `tests/e2e/AC_TC_MATRIX.md`.

## Từng test case

### TC-UP-01 — Tệp PDF hợp lệ xuất hiện trong kho ≤ 2 giây sau khi tải lên → **PASS**
- AC: `US-010/AC1` (full) · 12.3 s · phiên agent-browser `qa-TC-UP-01-20261025-190801`

| Kỳ vọng | Mô tả (từ spec) | Giá trị thực | Kết quả |
|---|---|---|---|
| E1 | `elapsed_ms_lte` t0→doc-row <= `2000` | 0 | true |
| E2 | `text_matches` [data-testid=doc-row] [data-testid=doc-name] matches `^text_12p\.pdf$` | ['text_12p.pdf'] | true |
| E3 | `text_matches` [data-testid=doc-row] [data-testid=status-badge] matches `(Đang xử lý\|Đang nhận dạng ký tự\|Sẵn sàng)` | ['Đang xử lý'] | true |
- Bằng chứng: `reports/20261025-190801/TC-UP-01/` (snapshot trước/sau, screenshot, console)
- Ghi chú: Đo trong trang: XHR POST /documents kết thúc → hàng xuất hiện. Tham khảo: theo CLI (gồm ~0,5 s khởi chạy mỗi lệnh) = 1390 ms.

### TC-UP-02 — Người dùng khác hỏi về tệp đã Sẵn sàng và nhận trích dẫn đúng tên tệp → **PASS**
- AC: `US-010/AC2` (full) · 22.7 s · phiên agent-browser `qa-TC-UP-02-20261025-190801`

| Kỳ vọng | Mô tả (từ spec) | Giá trị thực | Kết quả |
|---|---|---|---|
| E1 | `count_gte` [data-testid=citation] >= `1` | 1 | true |
| E2 | `text_matches` [data-testid=citation] matches `text_12p\.pdf` | ['[text_12p.pdf – tr. 12]'] | true |
- Bằng chứng: `reports/20261025-190801/TC-UP-02/` (snapshot trước/sau, screenshot, console)

### TC-QA-01 — Câu hỏi tiếng Việt có đáp án trong tài liệu: trả lời đúng dữ kiện và có trích dẫn (3/3 phiên) → **PASS**
- AC: `US-020/AC1` (full) · 34.2 s · phiên agent-browser `qa-TC-QA-01-20261025-190801` (mỗi lượt một phiên `-r1..-r3`)

| Kỳ vọng | Mô tả (từ spec) | Giá trị thực | Kết quả |
|---|---|---|---|
| r1-E1 | `text_matches` [data-testid=answer-text] matches `24 tháng` | Hợp đồng số HD-2026-012 có thời hạn 24 tháng kể từ 01/03/2026.  ⏎ [text_12p.pdf – tr. 12] | true |
| r1-E2 | `count_gte` [data-testid=citation] >= `1` | 1 | true |
| r2-E1 | `text_matches` [data-testid=answer-text] matches `24 tháng` | Hợp đồng số HD-2026-012 có thời hạn 24 tháng kể từ 01/03/2026.  ⏎ [text_12p.pdf – tr. 12] | true |
| r2-E2 | `count_gte` [data-testid=citation] >= `1` | 1 | true |
| r3-E1 | `text_matches` [data-testid=answer-text] matches `24 tháng` | Hợp đồng số HD-2026-012 có thời hạn 24 tháng kể từ 01/03/2026.  ⏎ [text_12p.pdf – tr. 12] | true |
| r3-E2 | `count_gte` [data-testid=citation] >= `1` | 1 | true |
- Bằng chứng: `reports/20261025-190801/TC-QA-01/` (snapshot trước/sau, screenshot, console)

### TC-QA-02 — Ô nhập chỉ có khoảng trắng: không gửi được → **PASS**
- AC: `US-020/AC3` (full) · 11.3 s · phiên agent-browser `qa-TC-QA-02-20261025-190801`

| Kỳ vọng | Mô tả (từ spec) | Giá trị thực | Kết quả |
|---|---|---|---|
| E1 | `state` [data-testid=send] is `disabled` | disabled | true |
| E2 | `count_eq` [data-testid=user-message] == `0` | 0 | true |
| E3 | `request_count_eq` POST */chat/sessions/*/messages == `0` | 0 | true |
- Bằng chứng: `reports/20261025-190801/TC-QA-02/` (snapshot trước/sau, screenshot, console)

### TC-CITE-01 — Thẻ trích dẫn đúng định dạng, không lộ nhãn thô → **PASS**
- AC: `US-022/AC1` (full) · 11.2 s · phiên agent-browser `qa-TC-CITE-01-20261025-190801`

| Kỳ vọng | Mô tả (từ spec) | Giá trị thực | Kết quả |
|---|---|---|---|
| E1 | `count_gte` [data-testid=citation] >= `1` | 1 | true |
| E2 | `text_matches` [data-testid=citation] matches_each `^\[.+ – tr\. \d+\]$` | ['[text_12p.pdf – tr. 12]'] | true |
| E3 | `text_matches` [data-testid=answer-text] not_matches `\[c\d+\]\|\[\[\d+\]\]` | Hợp đồng số HD-2026-012 có thời hạn 24 tháng kể từ 01/03/2026.  ⏎ [text_12p.pdf – tr. 12] | true |
- Bằng chứng: `reports/20261025-190801/TC-CITE-01/` (snapshot trước/sau, screenshot, console)

### TC-CITE-02 — Bấm thẻ trích dẫn mở khung xem đúng tài liệu và trang của thẻ trong ≤ 3 giây → **PASS**
- AC: `US-022/AC2` (full) · 12.7 s · phiên agent-browser `qa-TC-CITE-02-20261025-190801`

| Kỳ vọng | Mô tả (từ spec) | Giá trị thực | Kết quả |
|---|---|---|---|
| E1 | `elapsed_ms_lte` t0→source-viewer <= `3000` | 12 | true |
| E2 | `text_matches` [data-testid=viewer-name] matches `^text_12p\.pdf$` | ['text_12p.pdf'] | true |
| E3 | `text_matches` [data-testid=viewer-page] equals_template `Trang {N} / 12` | ['Trang 12 / 12'] | true |
| E4 | `attr_matches` [data-testid=viewer-iframe]@src matches_template `^/api/v1/documents/[0-9a-f-]{36}/file#page={N}$` | /api/v1/documents/71c00576-6fba-4831-a836-7e36ace130fd/file#page=12 | true |
- Bằng chứng: `reports/20261025-190801/TC-CITE-02/` (snapshot trước/sau, screenshot, console)
- Ghi chú: N (từ thẻ) = 12. Thời gian đo trong trang (JS click → khung xem xuất hiện); không đọc được nội dung trong iframe.

### TC-CITE-03 — Mẫu n=1: trang được trích dẫn là trang chứa dữ kiện đã biết (không đóng AC) → **PASS**
- AC: `US-022/AC3` (partial) · 10.0 s · phiên agent-browser `qa-TC-CITE-03-20261025-190801`

| Kỳ vọng | Mô tả (từ spec) | Giá trị thực | Kết quả |
|---|---|---|---|
| E1 | `text_matches` [data-testid=citation] matches_any `^\[text_12p\.pdf – tr\. 12\]$` | ['[text_12p.pdf – tr. 12]'] | true |
- Bằng chứng: `reports/20261025-190801/TC-CITE-03/` (snapshot trước/sau, screenshot, console)
- Ghi chú: Mẫu n=1, không đóng US-022/AC3.

## Điều cần người biết (quan sát, không diễn giải)
1. **Phép đo thời gian làm khác spec ở mốc t0.** Spec ghi t0 = lúc lệnh `upload` trả về; mỗi lệnh CLI tốn ≈ 0,5 s khởi chạy nên không đo được ngưỡng 2 s/3 s. Bộ chạy đo **trong trang**: US-010/AC1 từ lúc XHR `POST /documents` kết thúc tới lúc hàng xuất hiện (thực đo ≈ 0 ms); US-022/AC2 từ lúc click tới lúc khung xem xuất hiện (12 ms). Theo CLI (tham khảo) hàng tệp xuất hiện sau 1390 ms — dưới 2000 ms nhưng gồm overhead. Đề nghị PM/PO/QA cập nhật mô tả mốc trong spec cho khớp.
2. **Hai lần thử trước chạy hỏng vì lỗi của bộ chạy**, không phải của sản phẩm, và đã loại khỏi báo cáo: (a) `shell=True` làm ký tự `&` cắt URL đăng nhập; (b) công cụ đo chỉ móc `fetch` trong khi giao diện tải lên bằng XHR nên E1 không có giá trị (đáng lẽ INCONCLUSIVE). Kỳ vọng không bị sửa. Lần chạy này chạy lại toàn bộ 7 TC từ trạng thái sạch.
3. **Kỳ vọng "Đang xử lý" thực sự quan sát được**: hàng tệp hiện `Đang xử lý` ngay khi xuất hiện (E3 của TC-UP-01), nên việc mở rộng tập trạng thái chấp nhận của AC viết lại không bị dùng đến.
4. **Chỗ agent-browser không đo được:** nội dung bên trong iframe PDF. Ảnh chụp của TC-CITE-02 cho thấy trình xem PDF hiển thị trang 12/12 và dòng chứa câu "24 tháng"; đây là bằng chứng để người xem, không phải kỳ vọng tự động.
5. **TC-QA-01 đạt 3/3 trên một mẫu nhỏ.** Qwen3 1.7B không tất định; kết quả chỉ nói về lần chạy này, không về tỉ lệ (đó là AC chưa đo được).
6. **Sườn chạy chưa nằm trong repo:** bộ điều khiển được chạy từ thư mục tạm; xem mục việc cần làm.

## Việc cần người quyết định
- Duyệt/bác các phát biểu AC tạm trong `spec.json` (6 AC) và mô tả mốc t0 ở mục 1.
- US-020/AC2 và US-022/AC3 vẫn chưa đo được (cần DEP-003).
- Không có TC INCONCLUSIVE hay FAIL.
