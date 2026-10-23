# T-607 · Bộ đánh giá chất lượng trả lời (G3)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | BR-009, BR-010, BR-011, BR-012, BR-027, BR-030 |
| NFR, EC, cổng | G3, G3b |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md), [T-316](T-316-dich-vu-tra-loi-2-2-dung-dut-ket-noi-loi-va-het-gio.md), [T-315](T-315-bo-noi-ai-that-2-2-sinh-cau-tra-loi-dang-luong.md), [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) |
| Mở khóa | [T-616](T-616-danh-gia-chat-luong-ocr-g3b.md) |

## Mục tiêu

Chạy bộ câu hỏi chuẩn qua `AnswerService`, tính các chỉ số tự động và xuất tệp cho 2 người chấm đội BD.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- Định dạng bộ câu hỏi ở bước 1
- AC-009 – AC-014, AC-026 trong BRD
- PRD mục 5.1 dòng G3

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) Dịch vụ trả lời (1/2): luồng chính có trích dẫn: `AnswerService`, `detect_lang`
- [T-316](T-316-dich-vu-tra-loi-2-2-dung-dut-ket-noi-loi-va-het-gio.md) Dịch vụ trả lời (2/2): dừng, đứt kết nối, lỗi và hết giờ: `RunningAnswers`
- [T-315](T-315-bo-noi-ai-that-2-2-sinh-cau-tra-loi-dang-luong.md) Bộ nối AI thật (2/2): sinh câu trả lời dạng luồng: `ProviderAi`
- [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) Dữ liệu mẫu và fixture kiểm thử: `backend/scripts/make_sample_data.py`, `backend/tests/fixtures/README.md`

## File cần tạo hoặc sửa

- `backend/scripts/eval_answers.py`
- `backend/eval/README.md`
- `docs/05-planning/evidence/eval-method.md`
- `docs/05-planning/evidence/eval-answers.md`

## Các bước

1. Đọc `eval/questions.jsonl` (DEP-003, ≥ 50 câu); mỗi dòng `{id, question, type: "single"|"multi"|"out_of_scope"|"language"|"followup", expected_answer, expected_docs: [tên], expected_pages: [số], followup_of?: id}`.
2. Nạp tài liệu của bộ mẫu vào CSDL đánh giá riêng (`CWD_DATABASE_URL` khác), chờ tất cả `READY`.
3. Chạy từng câu qua `AnswerService.ask` (câu `followup` chạy trong cùng phiên với `followup_of`); ghi văn bản, trích dẫn, `is_not_found`, độ trễ.
4. Tự tính: trích dẫn đúng trang (`(doc, page)` ∈ kỳ vọng, AC-010); từ chối đúng câu `out_of_scope` (AC-011); ngôn ngữ trả lời đúng (AC-026, dùng `detect_lang`); đa tài liệu có trích dẫn từ ≥ 2 tài liệu kỳ vọng (AC-009).
5. Xuất `eval-answers.csv` có cột trống `grader_1_correct`, `grader_2_correct` cho người chấm (AC-012, AC-014); `eval-answers.md` ghi số liệu tự động, `relevance_threshold`, `retrieval_k`, mô hình đã dùng.
6. Thử 3 giá trị `relevance_threshold` (0,0; 0,3; 0,5) và đề xuất giá trị cân bằng giữa AC-011 và AC-012 cho T-304.

## Tiêu chí hoàn thành

- [ ] Có số liệu tự động cho AC-009, AC-010, AC-011, AC-026 và tệp chấm cho AC-012, AC-014.
- [ ] Chạy lại cho cùng số liệu với cùng dữ liệu và cấu hình (nhiệt độ thấp, ghi rõ nếu nhà cung cấp không tất định).
- [ ] Có giá trị `relevance_threshold` đề xuất kèm số liệu.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Chạy thử bộ nhỏ | 5 câu mẫu tự tạo trên `text_12p.pdf` với `AiFake` | CSV có 5 dòng đủ cột; số liệu tự động in ra |
| Tái lập | Chạy hai lần cùng cấu hình | Cột tự động giống nhau |
| Câu nối tiếp | Câu `followup` trỏ `followup_of` | Chạy trong cùng phiên (kiểm bằng `session_id` ghi trong CSV) |

## Lệnh kiểm tra

```bash
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đánh giá OCR (T-616).
- Chấm điểm cuối (2 người đội BD).
- Chỉnh prompt (Trưởng đội kỹ thuật, nếu số liệu không đạt).

## Lưu ý

Bị chặn bởi DEP-003 (hạn 2026-11-27). Kết quả có ý nghĩa chỉ khi dùng nhà cung cấp AI thật (T-315). Câu loại `language` (AC-026) và `followup` (AC-014) đo tính năng P1 T-309, T-310: chạy khi hai task đó đã xong, nếu chưa thì ghi "chưa đo" thay vì chờ.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
