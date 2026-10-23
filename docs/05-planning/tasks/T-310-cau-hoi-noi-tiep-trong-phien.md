# T-310 · Câu hỏi nối tiếp trong phiên

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P1 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-025 |
| BR | BR-014 |
| NFR, EC, cổng | NFR-009 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md), [T-105](T-105-repository-hoi-thoai.md), [T-614](T-614-co-tinh-nang-cho-phan-p1.md) |
| Mở khóa | — |

## Mục tiêu

Đưa các lượt gần nhất của phiên vào truy xuất và prompt để hiểu đại từ.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`Turn`)
- CONTRACTS mục 6 (`question_submitted.is_followup`)
- US-025 trong USER_STORIES.md

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) Dịch vụ trả lời (1/2): luồng chính có trích dẫn: `AnswerService`, `detect_lang`
- [T-105](T-105-repository-hoi-thoai.md) Repository hội thoại: `create_session`, `set_title_if_empty`, `get_session`, `list_sessions`, `add_message`, `update_message` …
- [T-614](T-614-co-tinh-nang-cho-phan-p1.md) Cờ tính năng cho phần P1: `is_enabled`, `require_feature`, `ALL_P1`

## File cần tạo hoặc sửa

- `backend/app/modules/answer/history.py`
- `backend/app/modules/answer/service.py`
- `backend/tests/integration/test_followup.py`

## Chữ ký và giao diện

```python
async def recent_turns(session: AsyncSession, session_id: UUID, n: int = 3) -> list[Turn]: ...
```

## Các bước

1. `recent_turns(session, session_id, n=3)`: lấy tối đa 3 cặp hỏi–đáp gần nhất đã `COMPLETED` của phiên, cũ trước mới sau.
2. Trong `ask`, khi `is_enabled("followup")` và có ≥ 1 lượt trước: `is_followup=True`; truy vấn truy xuất = câu hỏi trước gần nhất + `" "` + câu hỏi hiện tại `[Đề xuất: không tốn thêm lời gọi AI]`; truyền `history=turns` cho `build_prompt`.
3. Chỉ dùng lượt của chính phiên đó; tính năng tắt thì hành vi như T-307.

## Tiêu chí hoàn thành

- [ ] Phiên có lượt "Hợp đồng X có thời hạn bao lâu?": câu "Còn giá trị của nó?" được truy xuất bằng chuỗi có "Hợp đồng X" và prompt có khối `<history>`.
- [ ] Không dùng lịch sử của phiên khác.
- [ ] Tắt cờ `followup` thì không có `<history>` và `is_followup=False`.
- [ ] AC-014 (≥ 8/10 cặp) đo ở T-607.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_followup_uses_previous_turn` | Phiên có 1 lượt về "Hợp đồng X"; hỏi "Còn giá trị của nó?" với `retrieve` giả ghi lại truy vấn | Truy vấn chứa "Hợp đồng X"; `user` của prompt có `<history>`; `question_submitted.is_followup=True` |
| `test_no_cross_session_history` | Phiên A có lượt về X; hỏi trong phiên B mới | Không có `<history>`; `is_followup=False` |
| `test_flag_off` | `features` không có `followup` | Như phiên mới |
| `test_recent_turns_limit` | Phiên có 5 lượt | `recent_turns` trả 3 lượt mới nhất theo thứ tự thời gian |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_followup.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Viết lại câu hỏi bằng AI (chỉ làm nếu T-607 cho thấy cách ghép không đạt AC-014).
- Hiển thị phiên ở giao diện (T-516).

## Lưu ý

Thêm một lời gọi AI mỗi lượt nối tiếp: kiểm tra ảnh hưởng chi phí (NFR-009).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
