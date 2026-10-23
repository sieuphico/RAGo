# T-311 · Phạm vi tài liệu trong API-08 và EC-15

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P1 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W9 (xem PLAN mục 6) |
| Story | US-026 |
| BR | BR-015 |
| NFR, EC, cổng | EC-15 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-614](T-614-co-tinh-nang-cho-phan-p1.md) |
| Mở khóa | — |

## Mục tiêu

Giới hạn truy xuất theo `scopeDocIds`; tự loại tài liệu đã xóa và báo người dùng.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 5.2 (`scopeRemoved`)
- EC-15 (PRD mục 4.2)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md) API hội thoại: phiên, gửi câu hỏi SSE, dừng (API-07/08/09): `create_session_api`, `ask_api`, `stop_api`, `to_sse_frame`
- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-614](T-614-co-tinh-nang-cho-phan-p1.md) Cờ tính năng cho phần P1: `is_enabled`, `require_feature`, `ALL_P1`

## File cần tạo hoặc sửa

- `backend/app/modules/answer/scope.py`
- `backend/app/modules/answer/service.py`
- `backend/tests/integration/test_scope.py`

## Chữ ký và giao diện

```python
@dataclass(frozen=True)
class ScopeResult:
    effective: set[UUID]
    removed: set[UUID]

async def normalize_scope(session: AsyncSession, requested: set[UUID]) -> ScopeResult: ...
```

## Các bước

1. `normalize_scope(session, requested)`: `effective = requested ∩ ready_doc_ids()`; `removed = requested - effective`.
2. `requested` rỗng → `ScopeResult(set(), set())` (tất cả tài liệu). `effective` rỗng nhưng `requested` không rỗng → `effective = set()` (quay về tất cả) và `removed = requested`.
3. Trong `ask`: dùng `effective` cho truy xuất; `StatusEvent.scope_removed = sorted(removed)`; lưu `chat_session.scope_doc_ids = effective`.
4. Cờ `scope` tắt → bỏ qua `scopeDocIds`.

## Tiêu chí hoàn thành

- [ ] Giới hạn vào A thì mọi trích dẫn thuộc A (AC-015).
- [ ] Tài liệu đã xóa trong phạm vi được trả trong `scopeRemoved` (EC-15).
- [ ] Phạm vi chỉ gồm tài liệu đã xóa quay về tất cả tài liệu.
- [ ] Cờ tắt thì phạm vi bị bỏ qua.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_scope_only_cites_selected` | Tài liệu A, B đều có chunk khớp; `scopeDocIds=[A]` | Mọi `citation.docId == A` |
| `test_deleted_doc_removed_from_scope` | `scopeDocIds=[A, D]`, D đã xóa | `status.scopeRemoved == [D]`; truy xuất trong {A} |
| `test_all_removed_falls_back` | `scopeDocIds=[D]`, D đã xóa | `scopeRemoved == [D]`; truy xuất trên mọi tài liệu `READY` |
| `test_flag_off_ignores_scope` | Cờ `scope` tắt; `scopeDocIds=[A]` | Truy xuất trên mọi tài liệu; `scopeRemoved == []` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_scope.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Chọn phạm vi ở giao diện (T-514).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
