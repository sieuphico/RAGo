# T-307 · Dịch vụ trả lời (AnswerService)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 10 giờ `[Đề xuất]` |
| Tuần dự kiến | W6–W7 (xem PLAN mục 6) |
| Story | US-020, US-021, US-022, US-023, US-027 |
| BR | BR-008, BR-009, BR-010, BR-011, BR-013 |
| NFR, EC, cổng | NFR-001, EC-04, EC-06, EC-07 |
| Quyết định kiến trúc | AD-02, AD-04, AD-13 |
| Phụ thuộc | [T-105](T-105-repository-hoi-thoai.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-304](T-304-nguong-lien-quan-va-quyet-dinh-khong-tim-thay.md), [T-305](T-305-dung-prompt-voi-nhan-chunk.md), [T-306](T-306-kiem-tra-va-anh-xa-trich-dan.md) |
| Mở khóa | [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-310](T-310-cau-hoi-noi-tiep-trong-phien.md), [T-314](T-314-noi-telemetry-vao-cac-luong-chinh.md), [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-va-ocr-g3-g3b.md), [T-608](T-608-thu-tai-g4.md) |

## Mục tiêu

Điều phối truy xuất, quyết định đủ bằng chứng, gọi AI theo luồng, kiểm tra trích dẫn và phát các sự kiện `status`, `token`, `citation`, `done`, `error`.

## File cần tạo hoặc sửa

- `backend/app/modules/answer/service.py`
- `backend/tests/integration/test_answer_service.py`

## Chữ ký và giao diện

```python
async def ask(session, gateway: AiGateway, user_email: str, session_id: UUID, text: str, scope: set[UUID]) -> AsyncIterator[AnswerEvent]: ...
```

## Các bước

1. `ask(...) -> AsyncIterator[AnswerEvent]` thực hiện các bước SAD 3.2.
2. Phát `status{searching, docCount}` trong ≤ 1 giây; không đủ bằng chứng thì phát `done{isNotFound=true}` mà không gọi AI.
3. Gọi `gateway.generate`, chuyển token thành `token`, đổi nhãn bằng `resolve` và phát `citation`.
4. Hủy được giữa chừng (`stop`) và khi kết nối đóng: ngừng lời gọi AI, giữ phần đã sinh.
5. Lưu `Message` và `Citation`; mọi lỗi ánh xạ thành `error{code, retryable}`.

## Tiêu chí hoàn thành

- [ ] Câu hỏi có đáp án trong kho cho câu trả lời có ≥ 1 trích dẫn đúng.
- [ ] Câu hỏi ngoài phạm vi trả "không tìm thấy" và không có dữ kiện bịa.
- [ ] Dừng giữa chừng giữ phần đã có và dừng trong ≤ 1 giây.
- [ ] Lỗi AI cho `error{AI_UNAVAILABLE}` mà không làm hỏng dữ liệu.

## Kiểm thử cần viết

- `test_answer_has_citations`
- `test_not_found_skips_ai`
- `test_stop_keeps_partial`
- `test_ai_error_event`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
