# T-314 · Nối telemetry vào đăng nhập, tải lên, xử lý và xóa

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-051 |
| BR | — |
| NFR, EC, cổng | NFR-001 |
| Quyết định kiến trúc | AD-10 |
| Phụ thuộc | [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) |
| Mở khóa | [T-610](T-610-kiem-tra-telemetry-tren-staging-g8.md) |

## Mục tiêu

Phát các sự kiện phía máy chủ còn lại của CONTRACTS mục 6 tại các luồng đăng nhập, phân quyền, tải lên, xử lý và xóa (sự kiện hỏi đáp do T-307, T-316 phát).

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 6 (cột "Task phát")
- Chữ ký `emit` ở T-113

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) Telemetry: lược đồ sự kiện và API-16: `anon_id`, `emit`, `EVENTS`, `CLIENT_EVENTS`
- [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md) Đăng nhập SSO, phiên và `GET /me` (API-01): `SessionData`, `issue_cookie`, `read_cookie`, `complete_login`
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-201](T-201-tai-len-tai-lieu-api-02.md) Tải lên tài liệu (API-02): `upload_documents`
- [T-203](T-203-xoa-tai-lieu-api-05.md) Xóa tài liệu (API-05): `delete_document`
- [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) Ingest: điều phối và chuyển trạng thái: `handle_ingest`

## File cần tạo hoặc sửa

- `backend/app/modules/telemetry/mapping.py`
- `backend/app/modules/auth/service.py`
- `backend/app/api/deps.py`
- `backend/app/modules/documents/upload.py`
- `backend/app/modules/documents/delete.py`
- `backend/app/worker/ingest.py`
- `backend/tests/integration/test_telemetry_wiring.py`

## Chữ ký và giao diện

```python
# app/modules/telemetry/mapping.py
def upload_reason(code: str, *, extension_ok: bool) -> Literal["not_pdf", "too_large", "too_many", "invalid_pdf"]: ...
def failure_reason(reason: FailureReason) -> Literal["ocr_unreadable", "corrupted", "encrypted", "other"]: ...
def emit_once(sid: str, reason: str) -> bool: ...  # True nếu cặp (sid, reason) chưa phát
```

## Các bước

1. Callback đăng nhập (T-108): trong allow-list → `auth_login_succeeded {is_first_login}`; ngoài allow-list → `auth_access_denied {reason: "not_in_allowlist"}`.
2. Phân quyền (T-109): cookie hợp lệ nhưng không còn trong allow-list → `auth_access_denied {reason: "revoked"}`; sai vai trò → `{reason: "wrong_role"}`. Mỗi cặp `(sid, reason)` chỉ phát một lần (tập trong bộ nhớ, tối đa 10.000 phần tử).
3. Tải lên (T-201): mỗi tệp bị từ chối → `document_upload_rejected {reason}` với `FILE_TOO_LARGE → too_large`, `FILE_TOO_MANY → too_many`, sai đuôi → `not_pdf`, sai nội dung `%PDF-` → `invalid_pdf`.
4. Xử lý (T-210): `READY` → `document_processing_completed {doc_id, page_count, processing_seconds = processed_at - uploaded_at}`; `FAILED` → `document_processing_failed {doc_id, reason, used_ocr}` với `OCR_UNREADABLE → ocr_unreadable`, `FILE_CORRUPTED → corrupted`, `FILE_ENCRYPTED → encrypted`, còn lại `other`. Sự kiện của worker dùng `anon_user_id` của người tải lên, `session_id = "worker"`.
5. Xóa (T-203): `document_deleted {doc_id, actor_role}` khi `alreadyDeleted=false`.
6. Mọi lời gọi `emit` không được làm hỏng luồng chính (T-113 đã nuốt lỗi).

## Tiêu chí hoàn thành

- [ ] Mọi sự kiện có cột "Task phát" = T-314 ở CONTRACTS mục 6 được ghi đúng tên và thuộc tính (G8).
- [ ] Không sự kiện nào chứa văn bản, tên tệp hay email.
- [ ] `emit` lỗi không làm đổi mã phản hồi của API.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_login_events` | Đăng nhập lan@ (trong danh sách) và x@ (ngoài) | 1 `auth_login_succeeded {is_first_login: true}`; 1 `auth_access_denied {reason: "not_in_allowlist"}` |
| `test_revoked_event_once` | Gỡ lan@ rồi gọi API 3 lần | Đúng 1 `auth_access_denied {reason: "revoked"}` |
| `test_upload_rejected_events` | Gửi `a.png` và `not_pdf.pdf` | 2 sự kiện, `reason` là `not_pdf` và `invalid_pdf` |
| `test_processing_events` | Chạy `handle_ingest` cho `text_1p.pdf` và `corrupted.pdf` | `document_processing_completed` có `page_count=1`; `document_processing_failed {reason: "corrupted", used_ocr: false}` |
| `test_document_deleted_event` | Xóa tài liệu hai lần | Đúng 1 `document_deleted {actor_role: "TEAM_LEAD"}` |
| `test_telemetry_failure_does_not_break_flow` | Monkeypatch `append_event` ném lỗi; tải lên tệp hợp lệ | Vẫn 202 |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/integration/test_telemetry_wiring.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Sự kiện hỏi đáp (T-307, T-316), đánh giá (T-313), lịch sử (T-401), tóm tắt (T-403).
- Sự kiện phía giao diện (T-521).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
