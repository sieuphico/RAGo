# T-309 · Trả lời theo ngôn ngữ của câu hỏi

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P1 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 3 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-024 |
| BR | BR-026 |
| NFR, EC, cổng | EC-12 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-305](T-305-dung-prompt-voi-nhan-chunk.md), [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) |
| Mở khóa | — |

## Mục tiêu

Prompt yêu cầu trả lời cùng ngôn ngữ với câu hỏi; ghi chú khi ngôn ngữ ngoài Việt và Anh.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 5.2 (`notice: LANG_UNSUPPORTED`)
- EC-12 (PRD mục 4.2): "Vẫn xử lý; nếu chất lượng không đảm bảo, trả lời bằng tiếng Việt kèm ghi chú"

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-305](T-305-dung-prompt-voi-nhan-chunk.md) Dựng prompt với nhãn chunk: `BuiltPrompt`, `format_context`, `build_prompt`, `SYSTEM_PROMPT`
- [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) Dịch vụ trả lời (1/2): luồng chính có trích dẫn: `AnswerService`, `detect_lang`

## File cần tạo hoặc sửa

- `app/modules/answer/prompt.py`
- `app/modules/answer/service.py`
- `tests/unit/test_lang_prompt.py`

## Chữ ký và giao diện

```python
def build_prompt(question: str, chunks: list[ScoredChunk], history: list[Turn] | None = None, lang: Literal["vi", "en", "other"] = "vi") -> BuiltPrompt: ...
```

## Các bước

1. Thêm tham số `lang: Literal["vi","en","other"] = "vi"` vào `build_prompt` (giữ mặc định để T-307 không đổi hành vi).
2. `lang == "en"`: thêm dòng `Answer in English.` vào cuối `system`. `lang == "other"`: thêm `Trả lời bằng tiếng Việt.`
3. Trong `AnswerService.ask`: truyền `lang = detect_lang(text)` (đã có từ T-307); `lang == "other"` thì `DoneEvent.notice = "LANG_UNSUPPORTED"`.

## Tiêu chí hoàn thành

- [ ] Câu hỏi tiếng Anh tạo prompt có `Answer in English.`.
- [ ] Câu hỏi tiếng Đức tạo prompt có `Trả lời bằng tiếng Việt.` và `done.notice = "LANG_UNSUPPORTED"`.
- [ ] Câu hỏi tiếng Việt không đổi prompt so với T-307.
- [ ] Sẵn sàng đo AC-026 (≥ 19/20) ở T-607.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_english_instruction` | `build_prompt("What is the term?", chunks, lang="en")` | `system` kết thúc bằng `Answer in English.` |
| `test_other_language_note` | `ask` với "Was ist die Laufzeit?" | `done.notice == "LANG_UNSUPPORTED"`; `system` có `Trả lời bằng tiếng Việt.` |
| `test_vietnamese_unchanged` | `build_prompt(q, chunks)` và `build_prompt(q, chunks, lang="vi")` | Hai kết quả bằng nhau |
| `test_lang_eval_fixture` | Chạy `ask` với 20 câu trong `tests/fixtures/lang_questions.json` (10 vi, 10 en) bằng `AiFake` | Prompt của 10 câu tiếng Anh có `Answer in English.`, 10 câu tiếng Việt không có; tệp sẵn để T-607 đo AC-026 |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_lang_prompt.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Phát hiện ngôn ngữ (đã có ở T-307).
- Hiển thị ghi chú ở giao diện (T-525).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
