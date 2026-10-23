# T-202 · Danh sách tài liệu (API-03)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-015 |
| BR | BR-006 |
| NFR, EC, cổng | NFR-004 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) |
| Mở khóa | [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) |

## Mục tiêu

Trả danh sách tài liệu có tìm theo tên và sắp xếp.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-03, 4.2 `DocumentOut`
- CONTRACTS mục 11 (`documents.py` do task này tạo)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`

## File cần tạo hoặc sửa

- `app/api/documents.py`
- `tests/integration/test_list_documents.py`

## Chữ ký và giao diện

```python
@router.get("/api/v1/documents", response_model=DocumentListOut)
async def list_documents_api(search: str | None = None, sort: DocumentSort = "uploadedAt_desc",
                             user: CurrentUser = Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN)),
                             session: AsyncSession = Depends(get_session)) -> DocumentListOut: ...
```

## Các bước

1. Tạo router `api/documents.py` và `GET /api/v1/documents?search=&sort=`, `require_roles(BD_USER, TEAM_LEAD, ADMIN)`.
2. Gọi `documents.list_documents(search, sort)`; `sort` sai → 422.
3. Mỗi mục theo `DocumentOut`; `canDelete = (role == ADMIN) or (role == TEAM_LEAD and uploadedBy == email)`.
4. Trả `{"items": [...], "total": len(items)}`; không phân trang (tối đa 500 tài liệu, NFR-004).

## Tiêu chí hoàn thành

- [ ] Kho có 3 tài liệu trả 3 mục đủ 11 trường của `DocumentOut` (AC-006).
- [ ] `search=hop dong` lọc đúng.
- [ ] SPONSOR và người chưa xác thực bị từ chối.
- [ ] `canDelete` đúng cho 3 vai trò.
- [ ] 500 tài liệu trả trong ≤ 500 ms trên máy phát triển.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_list_three_documents` | 3 tài liệu; BD_USER gọi API-03 | 200; `total == 3`; mỗi mục có đủ khóa của `DocumentOut` |
| `test_search_filters` | "Hợp đồng A.pdf", "Báo cáo.pdf"; `search=hop dong` | 1 mục |
| `test_bad_sort_422` | `sort=size` | 422 `VALIDATION_ERROR` |
| `test_can_delete_flags` | Tài liệu do minh@ tải; gọi bằng minh@ (TN), hoa@ (TN), lan@ (BD), quantri@ (QT) | `canDelete`: true, false, false, true |
| `test_list_requires_auth` | SPONSOR gọi; không cookie gọi | 403; 401 |
| `test_list_500_perf` | Chèn 500 tài liệu; đo thời gian gọi | ≤ 500 ms |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_list_documents.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Giao diện bảng, tìm kiếm và sắp xếp (T-507).
- Phân trang (ngoài MVP).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
