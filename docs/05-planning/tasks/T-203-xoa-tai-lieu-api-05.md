# T-203 · Xóa tài liệu (API-05)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-016, US-062 |
| BR | BR-007, BR-018 |
| NFR, EC, cổng | EC-18 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md), [T-204](T-204-hang-doi-tac-vu-jobs.md) |
| Mở khóa | [T-213](T-213-tac-vu-xoa-du-lieu-trong-24-gio.md), [T-314](T-314-noi-telemetry-vao-dang-nhap-tai-len-xu-ly-va-xoa.md) |

## Mục tiêu

Xóa logic ngay, ghi nhật ký, chỉ người tải lên hoặc quản trị viên; xóa lặp không báo lỗi.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 API-05
- CONTRACTS mục 8 (`purge`)
- CONTRACTS mục 12, Q-C5

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md) Mô hình ORM và repository tài liệu: `add`, `get`, `list_documents`, `set_status`, `soft_delete`, `add_chunks` …
- [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md) Hợp đồng lỗi và bộ xử lý ngoại lệ: `ErrorCode`, `AppError`, `install_error_handlers`, `ERROR_DEFAULTS`
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-111](T-111-mo-dun-nhat-ky-kiem-toan-api-15.md) Mô-đun nhật ký kiểm toán (API-15): `record`, `expire`
- [T-204](T-204-hang-doi-tac-vu-jobs.md) Hàng đợi tác vụ (jobs): `enqueue`, `claim`, `complete`, `fail`, `release_stale`

## File cần tạo hoặc sửa

- `app/modules/documents/delete.py`
- `app/api/documents_delete.py`
- `tests/integration/test_delete_document.py`

## Chữ ký và giao diện

```python
async def delete_document(session: AsyncSession, doc_id: UUID, actor: CurrentUser, now: datetime) -> bool: ...  # trả already_deleted
```

## Các bước

1. `DELETE /api/v1/documents/{docId}`, `require_roles(TEAM_LEAD, ADMIN)`.
2. Tài liệu chưa từng tồn tại → 404 `DOC_NOT_FOUND`. TEAM_LEAD không phải người tải lên → 403 `AUTH_FORBIDDEN`.
3. Đã có `deleted_at` → 200 `{"docId", "alreadyDeleted": true}`, không ghi gì thêm (EC-18).
4. Còn lại, trong một giao dịch: `soft_delete`, `audit.record(actor, "DELETE", doc_id, name)`, `jobs.enqueue("purge", {"docId"}, run_after=now + 5 phút)`; trả 200 `{"docId", "alreadyDeleted": false}`.
5. Cho phép xóa ở mọi trạng thái (Q-C5); truy xuất đã lọc `deleted_at is null` nên tài liệu ngừng được dùng ngay.

## Tiêu chí hoàn thành

- [ ] Người tải lên xóa được tài liệu của mình; TEAM_LEAD khác và BD_USER không xóa được (AC-007).
- [ ] ADMIN xóa được mọi tài liệu.
- [ ] Sau khi xóa, `ready_doc_ids()` không còn tài liệu đó.
- [ ] Hai yêu cầu xóa liên tiếp: lần hai 200 `alreadyDeleted=true`, chỉ có 1 bản ghi `DELETE` và 1 tác vụ `purge`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_owner_can_delete` | minh@ (TN) tải X; minh@ gọi API-05 | 200 `alreadyDeleted=false`; `deleted_at` có giá trị; 1 tác vụ `purge` với `run_after` ≈ now + 5 phút |
| `test_other_team_lead_forbidden` | hoa@ (TN) xóa X của minh@ | 403 `AUTH_FORBIDDEN` |
| `test_bd_user_forbidden` | lan@ (BD) xóa X | 403 |
| `test_admin_can_delete_any` | quantri@ (QT) xóa X | 200 |
| `test_double_delete_idempotent` | Gọi API-05 hai lần | Lần hai 200 `alreadyDeleted=true`; `audit_log` có 1 `DELETE` |
| `test_unknown_doc_404` | Xóa UUID ngẫu nhiên | 404 `DOC_NOT_FOUND` |
| `test_deleted_not_ready` | Xóa X đang `READY`; gọi `ready_doc_ids()` | Không chứa X |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_delete_document.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Xóa chunk, gợi ý và tệp gốc (T-213).
- Sự kiện `document_deleted` (T-314).
- Hộp thoại xác nhận (T-510).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
