# T-212 · Tải tệp PDF cho khung xem nguồn (API-06)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-022 |
| BR | BR-010 |
| NFR, EC, cổng | EC-14 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-112](T-112-bo-noi-kho-tep-storageport.md) |
| Mở khóa | [T-615](T-615-kiem-thu-dau-cuoi-2-2-hoi-dap-xem-nguon-cac-trang-thai.md) |

## Mục tiêu

Trả PDF (hỗ trợ khoảng byte) sau khi kiểm tra quyền.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-06
- Chữ ký `StoragePort.read` ở T-008 (end không bao gồm)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-112](T-112-bo-noi-kho-tep-storageport.md) Bộ nối kho tệp (StoragePort): `FsStorage`, `new_file_key`

## File cần tạo hoặc sửa

- `backend/app/api/document_file.py`
- `backend/tests/integration/test_document_file.py`

## Chữ ký và giao diện

```python
@router.get("/api/v1/documents/{doc_id}/file")
async def get_file(doc_id: UUID, request: Request, user: CurrentUser = Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN)),
                   session: AsyncSession = Depends(get_session)) -> Response: ...
```

## Các bước

1. `GET /api/v1/documents/{docId}/file`, `require_roles(BD_USER, TEAM_LEAD, ADMIN)`.
2. Tài liệu không có hoặc có `deleted_at` → 404 `DOC_NOT_FOUND` (EC-14).
3. Không có `Range` → 200, toàn bộ tệp, `Content-Length`, `Accept-Ranges: bytes`.
4. `Range: bytes=a-b` (b bao gồm theo chuẩn HTTP) → đọc `storage.read(key, a, b + 1)`, trả 206 với `Content-Range: bytes a-b/size`. `bytes=a-` đọc tới cuối. Khoảng ngoài kích thước hoặc nhiều khoảng → 416 với `Content-Range: bytes */size`.
5. Tiêu đề: `Content-Type: application/pdf`, `Content-Disposition: inline; filename*=UTF-8''<tên mã hóa>`, `Cache-Control: private, max-age=0`, `X-Content-Type-Options: nosniff`.

## Tiêu chí hoàn thành

- [ ] Người không có quyền không tải được tệp (AC-016).
- [ ] `Range: bytes=0-99` trả 206 đúng 100 byte đầu.
- [ ] Tài liệu đã xóa trả 404 `DOC_NOT_FOUND` (EC-14).
- [ ] Khoảng sai trả 416.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_file_requires_auth` | Không cookie; SPONSOR | 401; 403 |
| `test_full_file_200` | Tài liệu 1.000 byte | 200, `Content-Length: 1000`, `Accept-Ranges: bytes` |
| `test_range_request_206` | `Range: bytes=0-99` | 206; 100 byte; `Content-Range: bytes 0-99/1000` |
| `test_open_ended_range` | `Range: bytes=900-` | 206; 100 byte cuối |
| `test_bad_range_416` | `Range: bytes=2000-3000` | 416; `Content-Range: bytes */1000` |
| `test_deleted_file_404` | Tài liệu đã `soft_delete` | 404 `DOC_NOT_FOUND` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_document_file.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Hiển thị PDF và chuyển trang (T-513).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
