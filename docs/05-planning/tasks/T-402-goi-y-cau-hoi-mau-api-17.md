# T-402 · Gợi ý câu hỏi mẫu (API-17)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 4 Tính năng P1 phía máy chủ |
| Ưu tiên | P1 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-031, US-030 |
| BR | BR-020, BR-035 |
| NFR, EC, cổng | NFR-009 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-614](T-614-co-tinh-nang-cho-phan-p1.md) |
| Mở khóa | — |

## Mục tiêu

Tạo 3 gợi ý một lần khi tài liệu `READY` và trả ngẫu nhiên 3 gợi ý.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-17, 4.2 `SuggestionOut`
- CONTRACTS mục 8 (`suggest`)
- DEC-018: tạo một lần, không cần duyệt

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) Ingest: điều phối và chuyển trạng thái: `handle_ingest`
- [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md) Cổng AI (AiGateway): thời hạn, hạn mức, ghi nhận: `AiGateway`
- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md) Worker: vòng lặp xử lý và scheduler: `run_worker`, `run_scheduler`
- [T-614](T-614-co-tinh-nang-cho-phan-p1.md) Cờ tính năng cho phần P1: `is_enabled`, `require_feature`, `ALL_P1`

## File cần tạo hoặc sửa

- `backend/app/worker/suggest.py`
- `backend/app/api/suggestions.py`
- `backend/tests/integration/test_suggestions.py`

## Chữ ký và giao diện

```python
async def generate_suggestions(job: Job) -> None: ...
@router.get("/api/v1/suggestions")
async def suggestions_api(user: CurrentUser = Depends(...)) -> SuggestionListOut: ...
```

## Các bước

1. Handler `generate_suggestions(job)` đăng ký `register("suggest", ...)`; cờ `suggestions` tắt → `complete` ngay, không gọi AI.
2. Lấy chunk của tài liệu theo trang; chọn tối đa 4 chunk ở vị trí `0, n//4, n//2, 3n//4` (bỏ trùng).
3. Gọi `gateway.generate` với `system`: "Đề xuất đúng 3 câu hỏi ngắn (mỗi câu ≤ 150 ký tự) mà người đọc có thể hỏi về tài liệu, chỉ dựa trên các đoạn trích. Trả về một mảng JSON gồm 3 chuỗi, không thêm gì khác." và `user` là các đoạn trích (không có tên tệp).
4. Gom toàn bộ văn bản, bỏ hàng rào mã ```, `json.loads`; phải là mảng đúng 3 chuỗi không rỗng ≤ 150 ký tự, sai → `ValueError` (T-204 thử lại).
5. Ghi `suggestion` (ghi đè nếu đã có). Tài liệu đã có gợi ý thì không gọi AI lại.
6. `GET /api/v1/suggestions`: gom câu hỏi của mọi tài liệu `READY` chưa xóa, trả ngẫu nhiên tối đa 3 (`random.sample`); không có → `{"items": []}`; `require_feature("suggestions")`.

## Tiêu chí hoàn thành

- [ ] Kho có ≥ 1 tài liệu sẵn sàng đã tạo gợi ý thì API-17 trả 3 gợi ý (AC-020).
- [ ] Kho trống hoặc chưa có tài liệu sẵn sàng trả `[]`.
- [ ] Mỗi tài liệu chỉ tốn một lần gọi AI cho gợi ý.
- [ ] Gợi ý của tài liệu đã xóa không được trả.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_three_suggestions` | 1 tài liệu `READY`; `AiFake` cấu hình trả `["Câu 1?","Câu 2?","Câu 3?"]`; chạy handler rồi gọi API-17 | 200, 3 mục, mỗi mục có `docId` và `text` |
| `test_empty_when_no_ready` | Không có tài liệu `READY` | `{"items": []}` |
| `test_generated_once` | Chạy handler hai lần | `generate` được gọi 1 lần |
| `test_invalid_json_retried` | `AiFake` trả "Đây là gợi ý" | Handler ném `ValueError` |
| `test_deleted_doc_excluded` | Tài liệu có gợi ý rồi bị `soft_delete` | API-17 trả `[]` |
| `test_flag_off` | Cờ `suggestions` tắt | Handler không gọi AI; API-17 404 |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_suggestions.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Khối gợi ý ở màn hình chào (T-515).
- Duyệt gợi ý thủ công (DEC-018: không làm).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
