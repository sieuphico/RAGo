# T-307 · Dịch vụ trả lời (1/2): luồng chính có trích dẫn

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W6–W7 (xem PLAN mục 6) |
| Story | US-020, US-021, US-022, US-023, US-027 |
| BR | BR-008, BR-009, BR-010, BR-011, BR-013 |
| NFR, EC, cổng | NFR-001, EC-04, EC-06, EC-07 |
| Quyết định kiến trúc | AD-02, AD-04, AD-13 |
| Phụ thuộc | [T-105](T-105-repository-hoi-thoai.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md), [T-304](T-304-nguong-lien-quan-va-quyet-dinh-khong-tim-thay.md), [T-305](T-305-dung-prompt-voi-nhan-chunk.md), [T-306](T-306-kiem-tra-va-anh-xa-trich-dan.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-309](T-309-tra-loi-theo-ngon-ngu-cua-cau-hoi.md), [T-310](T-310-cau-hoi-noi-tiep-trong-phien.md), [T-316](T-316-dich-vu-tra-loi-2-2-dung-dut-ket-noi-loi-va-het-gio.md), [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-g3.md) |

## Mục tiêu

Điều phối một câu hỏi từ lúc nhận tới lúc xong: tạo tin nhắn, gửi trạng thái, truy xuất, quyết định đủ bằng chứng, gọi AI theo luồng, đổi nhãn thành trích dẫn, lưu và ghi telemetry.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (sự kiện `AnswerEvent`)
- CONTRACTS mục 5.2 (thứ tự sự kiện)
- CONTRACTS mục 6 (`question_submitted`, `answer_first_token`, `answer_completed`)
- SAD mục 3.2 (đã chép thành các bước dưới)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-105](T-105-repository-hoi-thoai.md) Repository hội thoại: `create_session`, `set_title_if_empty`, `get_session`, `list_sessions`, `add_message`, `update_message` …
- [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md) Cổng AI (AiGateway): thời hạn, hạn mức, ghi nhận: `AiGateway`
- [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md) Truy xuất lai (vector + từ khóa) theo phạm vi: `retrieve`
- [T-304](T-304-nguong-lien-quan-va-quyet-dinh-khong-tim-thay.md) Ngưỡng liên quan và quyết định "không tìm thấy": `decide`, `filter_evidence`, `Decision`
- [T-305](T-305-dung-prompt-voi-nhan-chunk.md) Dựng prompt với nhãn chunk: `BuiltPrompt`, `format_context`, `build_prompt`, `SYSTEM_PROMPT`
- [T-306](T-306-kiem-tra-va-anh-xa-trich-dan.md) Kiểm tra và ánh xạ trích dẫn: `CitationResolver`, `resolve`
- [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) Telemetry: lược đồ sự kiện và API-16: `anon_id`, `emit`, `EVENTS`, `CLIENT_EVENTS`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `CurrentUser`, `AnswerEvent`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `backend/app/modules/answer/service.py`
- `backend/app/modules/answer/lang.py`
- `backend/tests/integration/test_answer_service.py`

## Chữ ký và giao diện

```python
class AnswerService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], gateway: AiGateway, settings: Settings) -> None: ...
    def ask(self, user: CurrentUser, sid: str, session_id: UUID, text: str, scope: set[UUID]) -> AsyncIterator[AnswerEvent]: ...

def detect_lang(text: str) -> Literal["vi", "en", "other"]: ...
```

## Các bước

1. Một giao dịch: `add_message(user, text, COMPLETED)`, `add_message(assistant, "", SEARCHING)`, `set_title_if_empty`; `commit`. Ghi `t0 = monotonic()`.
2. `ready = ready_doc_ids(scope or None)`; `yield StatusEvent(message_id, doc_count=len(ready))` **trước** mọi lời gọi AI; phát `question_submitted` với `language = detect_lang(text)`, `is_followup=False`, `scope_doc_count=len(scope)`.
3. `detect_lang(text)` ở `lang.py`: có ký tự có dấu tiếng Việt (ă â đ ê ô ơ ư hoặc dấu thanh) → `"vi"`; ≥ 80% chữ cái là a–z và có ≥ 1 từ trong {the, what, is, are, of, how, which, when, who} → `"en"`; còn lại `"other"`.
4. `len(ready) == 0` → lưu `NOT_FOUND`, `yield DoneEvent(..., is_not_found=True, not_found_reason="NO_READY_DOCS")`, phát `answer_completed`; kết thúc, **không** gọi AI.
5. `chunks = retrieve(...)`; `decide(chunks, len(ready), threshold)` là `NO_EVIDENCE` → như bước 4 với `"NO_EVIDENCE"`, không gọi `generate`.
6. `prompt = build_prompt(text, filter_evidence(chunks, threshold))`; `resolver = CitationResolver(prompt.label_map)`; với mỗi `delta` của `gateway.generate(prompt.system, prompt.user)`: `t, cits = resolver.feed(delta)`; `yield CitationEvent` cho từng trích dẫn mới rồi `yield TokenEvent(t)` nếu `t` khác rỗng. Token đầu tiên: đổi trạng thái `STREAMING`, phát `answer_first_token`.
7. Hết luồng: `resolver.finish()`; văn bản đầy đủ bắt đầu bằng "Không tìm thấy thông tin này" và 0 trích dẫn → `is_not_found=True`, trạng thái `NOT_FOUND`; ngược lại `COMPLETED`. Lưu văn bản, trích dẫn, `latency_ms`; `yield DoneEvent`; phát `answer_completed` với `distinct_doc_count`.
8. Không bắt `AppError` hay hủy ở task này; T-316 bổ sung các nhánh đó.

## Tiêu chí hoàn thành

- [ ] Câu hỏi có đáp án trong kho cho ≥ 1 trích dẫn đúng chunk và văn bản chứa `[[1]]`.
- [ ] Kho không có tài liệu `READY`: `done` với `NO_READY_DOCS`, `generate` và `embed` không được gọi.
- [ ] Không đủ bằng chứng: `done` với `NO_EVIDENCE`, `generate` không được gọi.
- [ ] Thứ tự sự kiện: `status` đầu tiên; mỗi `citation n` đến trước `token` chứa `[[n]]`; `done` cuối cùng.
- [ ] `status` được `yield` trong ≤ 1 giây kể cả khi `embed` chậm 3 giây.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_answer_has_citations` | Tài liệu `READY` có chunk "thời hạn 24 tháng" (vector dựng tay khớp truy vấn); `AiFake` trả "Theo tài liệu [c1]." | Sự kiện: `status`, `citation(index=1)`, `token` chứa `[[1]]`, `done(citation_count=1, is_not_found=False)`; tin nhắn `COMPLETED` có 1 trích dẫn |
| `test_no_ready_docs_skips_ai` | Không có tài liệu `READY`; gateway giả đếm lời gọi | `done(is_not_found=True, not_found_reason="NO_READY_DOCS")`; 0 lời gọi `embed` và `generate` |
| `test_not_found_skips_ai` | `relevance_threshold=0.99`, không chunk nào đạt | `done(..., not_found_reason="NO_EVIDENCE")`; 0 lời gọi `generate` |
| `test_status_first_and_fast` | `embed` giả chờ 3 giây | Sự kiện đầu tiên là `status` và đến trong ≤ 1 giây |
| `test_model_says_not_found` | `AiFake` được cấu hình trả "Không tìm thấy thông tin này trong các tài liệu hiện có." | `done(is_not_found=True)`; trạng thái `NOT_FOUND` |
| `test_detect_lang` | "Thời hạn hợp đồng?", "What is the term?", "Was ist das?" | `vi`, `en`, `other` |
| `test_telemetry_events` | Chạy câu hỏi ở test đầu với `emit` giả | Ghi đúng `question_submitted`, `answer_first_token`, `answer_completed` với cùng `question_id`; không thuộc tính nào chứa văn bản câu hỏi |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_answer_service.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Dừng, đứt kết nối, lỗi AI, quá thời gian (T-316).
- Kiểm tra câu hỏi rỗng, quá dài, phiên của ai, câu hỏi đang chạy (T-308).
- Câu hỏi nối tiếp (T-310), phạm vi (T-311), ghi chú ngôn ngữ (T-309).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
