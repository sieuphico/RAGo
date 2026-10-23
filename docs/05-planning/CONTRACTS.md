# HỢP ĐỒNG GIAO TIẾP DÙNG CHUNG (CONTRACTS)
# Công cụ "Chat với tài liệu" – MVP

| Thuộc tính | Giá trị |
|---|---|
| Mã tài liệu | CTR-CWD-001 |
| Phiên bản | 0.1 (2026-10-21) |
| Nguồn | [SAD.md](../04-design/SAD.md) mục 2.4, 3, 4; [Blueprint](../design/Blueprint_UIUX_Design.md) mục 3.2, 3.3, 3.5, 3.8, 5.2; [PRD](../requirements/PRD.md) mục 4.2, 5.2 |
| Dùng cho | Mọi task trong [tasks/](tasks/). Mỗi task ghi rõ cần đọc mục nào ở dòng "Đọc trước" |

## 0. Cách dùng

- Đây là **nguồn duy nhất** cho tên kiểu, giá trị enum, mã lỗi, đường dẫn API, dạng JSON, sự kiện SSE, sự kiện telemetry và khóa cấu hình. Task chỉ nêu phần riêng của nó và trỏ về đây.
- Đổi bất kỳ mục nào ở đây là **đổi hợp đồng**: cập nhật file này, ghi vào mục 12, báo người làm các task dùng mục đó.
- Ký hiệu: `[Đề xuất]` là lựa chọn của kế hoạch để task làm được ngay, chưa có trong SAD hay Blueprint, cần Trưởng đội kỹ thuật xác nhận (mục 12). Mục không có ký hiệu là chép từ tài liệu nguồn.
- Trên đường truyền (JSON) dùng `camelCase`; trong Python dùng `snake_case`. Mã định danh là chuỗi UUID. Thời điểm là ISO 8601 UTC có hậu tố `Z`, ví dụ `"2026-11-02T08:15:00Z"`. Giao diện hiển thị theo giờ máy người dùng, dạng `dd/MM/yyyy HH:mm`.

## 1. Vai trò

| Giá trị | Tên hiển thị | Ghi chú |
|---|---|---|
| `BD_USER` | Người dùng BD | Hỏi đáp, xem kho |
| `TEAM_LEAD` | Trưởng nhóm BD | Như BD_USER, cộng tải lên và xóa tài liệu của mình (DEC-001) |
| `ADMIN` | Quản trị viên | Hỏi đáp, xem kho, xóa mọi tài liệu, quản trị người dùng và nhật ký, số liệu |
| `SPONSOR` | Nhà tài trợ | Chỉ xem số liệu |

Quyền theo API ở mục 4; quyền theo màn hình ở mục 10.2.

## 2. Kiểu dữ liệu miền (backend)

Tạo một lần ở `app/domain/types.py` (task [T-009](tasks/T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md)); mọi mô-đun khác nhập từ đây, không định nghĩa lại.

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID


class Role(str, Enum):
    BD_USER = "BD_USER"
    TEAM_LEAD = "TEAM_LEAD"
    ADMIN = "ADMIN"
    SPONSOR = "SPONSOR"


class DocumentStatus(str, Enum):          # chỉ trạng thái phía máy chủ
    PROCESSING = "PROCESSING"
    OCR_PROCESSING = "OCR_PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    DELETED = "DELETED"                   # đặt khi tác vụ purge xong (T-213)


class FailureReason(str, Enum):
    FILE_CORRUPTED = "FILE_CORRUPTED"
    FILE_ENCRYPTED = "FILE_ENCRYPTED"
    OCR_UNREADABLE = "OCR_UNREADABLE"
    PROCESSING_ERROR = "PROCESSING_ERROR"  # lỗi khác sau khi hết số lần thử [Đề xuất]


class MessageStatus(str, Enum):
    SEARCHING = "SEARCHING"
    STREAMING = "STREAMING"
    COMPLETED = "COMPLETED"
    NOT_FOUND = "NOT_FOUND"
    STOPPED = "STOPPED"
    INTERRUPTED = "INTERRUPTED"           # kết nối đóng trước khi xong
    FAILED = "FAILED"


@dataclass(frozen=True)
class CurrentUser:
    email: str
    role: Role


@dataclass(frozen=True)
class PageText:                           # T-206 tạo, T-207/T-209 dùng
    page: int                             # bắt đầu từ 1
    text: str
    has_text_layer: bool


@dataclass(frozen=True)
class ChunkDraft:                         # T-207 tạo, T-208 dùng
    page: int
    text: str
    lang: Literal["vi", "en"] | None = None


@dataclass(frozen=True)
class ScoredChunk:                        # T-303 trả, T-304/T-305 dùng
    chunk_id: UUID
    doc_id: UUID
    doc_name: str
    page: int
    text: str
    score: float                          # điểm RRF, chỉ dùng để xếp hạng
    similarity: float | None = None       # 1 - khoảng cách cosine; None nếu chỉ khớp từ khóa
    keyword_hit: bool = False             # True nếu khớp truy vấn từ khóa


@dataclass(frozen=True)
class ChunkRef:                           # giá trị của label_map (T-305 → T-306)
    chunk_id: UUID
    doc_id: UUID
    doc_name: str
    page: int
    snippet: str                          # ≤ 200 ký tự


@dataclass(frozen=True)
class CitationOut:                        # một trích dẫn gửi cho giao diện
    index: int                            # 1, 2, 3… theo thứ tự xuất hiện lần đầu
    doc_id: UUID
    doc_name: str
    page: int
    snippet: str                          # ≤ 200 ký tự
    deleted: bool = False                 # True khi tài liệu đã bị xóa (EC-14)


@dataclass(frozen=True)
class Turn:                               # một lượt hỏi đáp trước đó (T-310)
    question: str
    answer: str


@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float                     # 0.0 – 1.0


@dataclass(frozen=True)
class IdpIdentity:
    email: str


@dataclass
class Job:
    job_id: UUID
    type: str                             # mục 8
    payload: dict
    attempts: int


@dataclass(frozen=True)
class UploadResult:                       # một dòng trong phản hồi API-02
    name: str
    doc_id: UUID | None
    status: DocumentStatus | None         # PROCESSING khi nhận
    error: str | None                     # mã lỗi mục 3 khi từ chối tệp này


# ---- Sự kiện của AnswerService (T-307) → SSE API-08 (T-308), xem mục 5.2
@dataclass(frozen=True)
class StatusEvent:
    message_id: UUID
    doc_count: int
    stage: Literal["searching"] = "searching"
    scope_removed: list[UUID] = field(default_factory=list)


@dataclass(frozen=True)
class TokenEvent:
    text: str


@dataclass(frozen=True)
class CitationEvent:
    citation: CitationOut


@dataclass(frozen=True)
class DoneEvent:
    message_id: UUID
    citation_count: int
    is_not_found: bool
    not_found_reason: Literal["NO_READY_DOCS", "NO_EVIDENCE"] | None = None
    notice: Literal["LANG_UNSUPPORTED"] | None = None
    stopped: bool = False                 # True khi người dùng bấm Dừng (API-09)


@dataclass(frozen=True)
class ErrorEvent:
    code: str                             # mã lỗi mục 3
    retryable: bool


AnswerEvent = StatusEvent | TokenEvent | CitationEvent | DoneEvent | ErrorEvent
```

### 2.1 Chuyển trạng thái tài liệu

Đặt ở `app/domain/status.py` (T-009). `set_status` (T-104) gọi `assert_transition` trước khi ghi.

| Từ | Được sang |
|---|---|
| (tạo mới) | `PROCESSING` |
| `PROCESSING` | `OCR_PROCESSING`, `READY`, `FAILED`, `DELETED` |
| `OCR_PROCESSING` | `READY`, `FAILED`, `DELETED` |
| `READY` | `DELETED` |
| `FAILED` | `DELETED` |
| `DELETED` | — |

```python
ALLOWED: dict[DocumentStatus, set[DocumentStatus]] = {...}   # đúng bảng trên
class InvalidTransition(Exception): ...
def assert_transition(old: DocumentStatus, new: DocumentStatus) -> None: ...
```

- `Uploading` và `Interrupted` trong Blueprint 3.5.1 **chỉ có ở trình duyệt** (tệp đang gửi hoặc gửi lỗi), không lưu ở CSDL. `[Đề xuất]`: bỏ hai giá trị này khỏi enum CSDL.
- Xóa tài liệu đang xử lý được phép `[Đề xuất]`: API-05 đặt `deleted_at`; worker kiểm tra `deleted_at` trước khi ghi chunk và dừng nếu đã xóa (T-210).
- Tài liệu có `deleted_at` khác rỗng coi như đã xóa với mọi API, dù `status` chưa thành `DELETED`.

### 2.2 Quy ước mã backend `[Đề xuất]`

- SQLAlchemy 2.0 **bất đồng bộ** với `asyncpg` cho ứng dụng và worker; Alembic dùng driver đồng bộ `psycopg`. Mô hình ORM viết kiểu `Mapped[...]` trong `app/models/`.
- Hàm repository là `async def`, nhận `session: AsyncSession` làm tham số đầu, chỉ `flush`; lớp dịch vụ (`modules/*/service.py`) hoặc router quyết định `commit`.
- Mô hình Pydantic vào/ra của API đặt cùng file router, tên theo mục 4.2 (`DocumentOut`…), dùng `alias_generator=to_camel` và `populate_by_name=True` để JSON là camelCase.
- Hàm cần thời gian nhận tham số `now` hoặc `clock` để test không phụ thuộc đồng hồ thật.
- Test: `pytest` + `pytest-asyncio` (`asyncio_mode = "auto"`); test tích hợp dùng CSDL `cwd_test` và rollback sau mỗi test (T-003).
- Chọn bộ nối (giả hay thật) chỉ ở `app/core/wiring.py`; mô-đun nghiệp vụ không nhập `app.adapters` (T-008 có test kiểm tra).

## 3. Mã lỗi

Thân phản hồi lỗi luôn là `{"code": "<MÃ>", "retryable": true|false}`; không có trường nào khác, không có chuỗi kỹ thuật (DD-06). Giao diện lấy thông báo từ cột cuối, không bao giờ hiển thị nội dung máy chủ gửi. Mã có ký hiệu `[Bổ sung]` chưa có trong Blueprint 3.3.3.

| Mã | HTTP | `retryable` | Khi nào | Thông báo tiếng Việt (giao diện) |
|---|---|---|---|---|
| `AUTH_EXPIRED` | 401 | false | Không có cookie phiên hoặc hết hạn | "Phiên đã hết hạn. Đang chuyển tới trang đăng nhập…" |
| `AUTH_FORBIDDEN` | 403 | false | Không trong allow-list, bị thu hồi, hoặc sai vai trò | Bị thu hồi: "Quyền truy cập của bạn đã bị thu hồi." · Chưa cấp quyền: "Bạn chưa được cấp quyền. Liên hệ quản trị viên." |
| `CSRF_REJECTED` `[Bổ sung]` | 403 | false | Phương thức ghi thiếu tiêu đề `X-Requested-With` | "Không thực hiện được thao tác. Hãy tải lại trang rồi thử lại." |
| `VALIDATION_ERROR` `[Bổ sung]` | 422 | false | Thân yêu cầu sai lược đồ (kể cả telemetry) | "Dữ liệu gửi lên không hợp lệ." |
| `NOT_FOUND` `[Bổ sung]` | 404 | false | Đường dẫn không có, tính năng đang tắt, tin nhắn không thuộc người gọi | "Không tìm thấy nội dung yêu cầu." |
| `FILE_NOT_PDF` | (trong kết quả từng tệp) | false | Đuôi không phải `.pdf` hoặc nội dung không bắt đầu bằng `%PDF-` | "Chỉ hỗ trợ tệp PDF." |
| `FILE_TOO_LARGE` | (trong kết quả từng tệp) | false | Tệp > 50 MB (52.428.800 byte) | "Tệp vượt quá 50 MB." |
| `FILE_TOO_MANY` | 400 | false | 0 tệp hoặc > 10 tệp trong một yêu cầu | "Chỉ tải tối đa 10 tệp mỗi lần." |
| `FILE_CORRUPTED` | (lý do `failureReason`) | false | PDF hỏng | "Tệp bị hỏng." |
| `FILE_ENCRYPTED` | (lý do `failureReason`) | false | PDF có mật khẩu | "Tệp có mật khẩu." |
| `OCR_UNREADABLE` | (lý do `failureReason`) | false | Bản quét không đạt ngưỡng OCR | "Không đọc được nội dung." · chú thích "Thử tải bản quét rõ nét hơn." |
| `PROCESSING_ERROR` `[Bổ sung]` | (lý do `failureReason`) | false | Lỗi xử lý khác sau khi hết số lần thử | "Không xử lý được tài liệu." |
| `DOC_NOT_FOUND` | 404 | false | Tài liệu không tồn tại hoặc đã xóa | "Tài liệu đã bị xóa." |
| `DOC_NOT_READY` `[Bổ sung]` | 409 | false | Tóm tắt tài liệu chưa `READY` | "Tài liệu chưa sẵn sàng." |
| `SESSION_NOT_FOUND` `[Bổ sung]` | 404 | false | Phiên không tồn tại hoặc thuộc người khác (không tiết lộ là của ai) | "Không tìm thấy phiên hội thoại." |
| `QUESTION_EMPTY` | 400 | false | Câu hỏi trống hoặc chỉ khoảng trắng | "Hãy nhập câu hỏi." |
| `QUESTION_TOO_LONG` | 400 | false | > 2.000 ký tự (đếm sau khi bỏ khoảng trắng đầu cuối) | "Câu hỏi vượt quá 2.000 ký tự." |
| `QUESTION_IN_PROGRESS` `[Bổ sung]` | 409 | true | Người dùng đang có một câu trả lời chưa xong (SAD 5.2: mỗi người một câu hỏi tại một thời điểm) | "Đang trả lời câu hỏi trước. Hãy chờ hoặc bấm Dừng." |
| `MESSAGE_NOT_RATEABLE` `[Bổ sung]` | 409 | false | Đánh giá tin nhắn chưa xong hoặc không phải câu trả lời | "Chỉ đánh giá được câu trả lời đã hoàn tất." |
| `EMAIL_INVALID` `[Bổ sung]` | 400 | false | Email sai định dạng | "Email không hợp lệ." |
| `USER_EXISTS` `[Bổ sung]` | 409 | false | Email đã có trong allow-list | "Người dùng này đã có trong danh sách." |
| `USER_LIMIT_REACHED` `[Bổ sung]` | 409 | false | Đã đủ 20 người (ASM-002) | "Đã đạt giới hạn 20 người dùng." |
| `LAST_ADMIN` `[Bổ sung]` | 409 | false | Gỡ quản trị viên cuối cùng | "Không thể gỡ quản trị viên cuối cùng." |
| `AI_UNAVAILABLE` | 503 | true | Nhà cung cấp AI lỗi hoặc ngắt mạch đang mở | "Dịch vụ hỏi đáp tạm thời gián đoạn. Vui lòng thử lại sau ít phút." |
| `BUDGET_EXCEEDED` | 503 | false | Vượt hạn mức chi phí tháng | "Dịch vụ hỏi đáp tạm thời gián đoạn. Vui lòng thử lại sau ít phút." |
| `TIMEOUT` | 504 | true | Quá `ai_timeout_s` (60 giây) | "Không thể trả lời lúc này." |
| `INTERNAL` `[Bổ sung]` | 500 | false | Lỗi không lường trước | "Đã có lỗi xảy ra. Vui lòng thử lại." |

Mã không có trong bảng → giao diện dùng thông báo của `INTERNAL`.

## 4. API

Chung cho mọi API dưới `/api/v1`:

- Xác thực bằng cookie phiên `cwd_session` (T-108). Không có hoặc hết hạn → 401 `AUTH_EXPIRED`. Không trong allow-list → 403 `AUTH_FORBIDDEN`. Kiểm tra allow-list ở **mọi** yêu cầu (T-109).
- Phương thức `POST`, `PUT`, `DELETE` phải có tiêu đề `X-Requested-With: cwd` `[Đề xuất]`; thiếu → 403 `CSRF_REJECTED`. Áp dụng cả API-08 và API-16.
- Thân yêu cầu sai lược đồ → 422 `VALIDATION_ERROR`.
- API của tính năng P1 đang tắt (mục 7, `features`) → 404 `NOT_FOUND`.
- Cột "Vai trò": BD = `BD_USER`, TN = `TEAM_LEAD`, QT = `ADMIN`, NTT = `SPONSOR`.

### 4.0 Đăng nhập (không đánh số API trong SAD)

| Phương thức, đường dẫn | Kết quả |
|---|---|
| `GET /auth/login?next=/duong-dan&login_hint=email` | 302 tới IdP. `next` chỉ nhận đường dẫn tương đối bắt đầu bằng `/` và không bắt đầu bằng `//` (chống chuyển hướng mở); sai thì dùng `/`. `login_hint` tùy chọn, chuyển tiếp cho IdP; với `IdpFake` nó là email đăng nhập (dùng cho E2E) |
| `GET /auth/callback?...` | Hoàn tất với IdP, đặt cookie `cwd_session` (`HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`, `Max-Age` = `session_ttl_s`), 302 tới `next` |
| `POST /auth/logout` | Xóa cookie, 204 |

### 4.1 Bảng API

| ID | Phương thức, đường dẫn | Vai trò | Yêu cầu | Phản hồi thành công | Lỗi riêng |
|---|---|---|---|---|---|
| API-01 | `GET /api/v1/me` | đã xác thực (kể cả ngoài allow-list) | — | 200 `MeOut` | 401 |
| API-02 | `POST /api/v1/documents` | TN | `multipart/form-data`, trường `files` lặp 1–10 lần. Giao diện gửi **mỗi tệp một yêu cầu** để có tiến độ và thử lại từng tệp `[Đề xuất]` | 202 `{"results": UploadResultOut[]}` | 400 `FILE_TOO_MANY`; 403 nếu không phải TN |
| API-03 | `GET /api/v1/documents?search=&sort=` | BD, TN, QT | `search` (chuỗi, tùy chọn); `sort` ∈ `uploadedAt_desc` (mặc định), `uploadedAt_asc`, `name_asc`, `name_desc` | 200 `{"items": DocumentOut[], "total": int}` | 422 nếu `sort` sai |
| API-04 | `GET /api/v1/documents/events` | BD, TN, QT | — | 200 `text/event-stream`, mục 5.1 | 401, 403 trước khi mở luồng |
| API-05 | `DELETE /api/v1/documents/{docId}` | người tải lên (TN) hoặc QT | — | 200 `{"docId": "...", "alreadyDeleted": bool}` | 403 nếu không phải chủ hoặc QT; 404 `DOC_NOT_FOUND` nếu chưa từng tồn tại |
| API-06 | `GET /api/v1/documents/{docId}/file` | BD, TN, QT | tiêu đề `Range: bytes=a-b` tùy chọn | 200 hoặc 206 `application/pdf` | 404 `DOC_NOT_FOUND`; 416 khi khoảng sai |
| API-07 | `POST /api/v1/chat/sessions` | BD, TN, QT | `{}` | 201 `{"sessionId": "...", "title": null, "createdAt": "..."}` | — |
| API-08 | `POST /api/v1/chat/sessions/{sessionId}/messages` | chủ phiên | `{"text": str, "scopeDocIds": [uuid]}` (`[]` = tất cả) | 200 `text/event-stream`, mục 5.2 | Trước khi mở luồng (JSON): 400 `QUESTION_EMPTY`, `QUESTION_TOO_LONG`; 404 `SESSION_NOT_FOUND`; 409 `QUESTION_IN_PROGRESS` |
| API-09 | `POST /api/v1/chat/messages/{messageId}/stop` | chủ phiên | `{}` | 200 `{"messageId": "...", "status": MessageStatus}` (đã xong thì trả trạng thái hiện tại, không lỗi) | 404 `NOT_FOUND` |
| API-10a | `GET /api/v1/chat/sessions` | BD, TN, QT | — | 200 `{"items": SessionSummaryOut[]}`, mới nhất trước, chỉ trong `history_days` | — |
| API-10b | `GET /api/v1/chat/sessions/{sessionId}` | chủ phiên | — | 200 `SessionDetailOut` | 404 `SESSION_NOT_FOUND` |
| API-11 | `POST /api/v1/chat/messages/{messageId}/rating` | chủ phiên | `{"value": "UP"\|"DOWN", "reasonCode": null\|"WRONG_INFO"\|"WRONG_CITATION"\|"MISSING_INFO"\|"OTHER"}` | 204; gửi lại thì ghi đè | 404 `NOT_FOUND`; 409 `MESSAGE_NOT_RATEABLE`; 422 khi `reasonCode` lạ hoặc có `reasonCode` với `UP` |
| API-12 | `POST /api/v1/documents/{docId}/summary` | BD, TN, QT | `{}` | 200 `{"docId", "docName", "text", "citations": CitationOut[]}` | 404 `DOC_NOT_FOUND`; 409 `DOC_NOT_READY`; 503 `AI_UNAVAILABLE`, `BUDGET_EXCEEDED`; 504 `TIMEOUT` |
| API-13 | `GET /api/v1/metrics/weekly?week=YYYY-MM-DD` | QT, NTT | `week` là thứ Hai đầu tuần; bỏ trống = tuần gần nhất có dữ liệu | 200 `WeeklyMetricsOut` | 422 nếu `week` không phải thứ Hai |
| API-14a | `GET /api/v1/admin/users` | QT | — | 200 `{"items": UserOut[], "count": int, "limit": 20}` | — |
| API-14b | `POST /api/v1/admin/users` | QT | `{"email": str, "role": Role}` | 201 `UserOut` | 400 `EMAIL_INVALID`; 409 `USER_EXISTS`, `USER_LIMIT_REACHED` |
| API-14c | `DELETE /api/v1/admin/users/{email}` | QT | — | 204 | 404 `NOT_FOUND`; 409 `LAST_ADMIN` |
| API-15 | `GET /api/v1/admin/audit-log?since=&limit=` | QT | `since` ISO (mặc định 90 ngày trước); `limit` 1–500 (mặc định 100) | 200 `{"items": AuditOut[]}`, mới nhất trước | — |
| API-16 | `POST /api/v1/telemetry/events` | đã xác thực | `TelemetryIn` (mục 6) | 204 | 422 `VALIDATION_ERROR` (trường lạ, sự kiện không thuộc nhóm "giao diện") |
| API-17 | `GET /api/v1/suggestions` | BD, TN, QT | — | 200 `{"items": SuggestionOut[]}`, tối đa 3 phần tử chọn ngẫu nhiên; rỗng khi chưa có tài liệu `READY` | — |
| — | `GET /api/v1/features` | đã xác thực | — | 200 `{"suggestions": bool, "summary": bool, "history": bool, "rating": bool, "copy": bool, "scope": bool, "followup": bool, "duplicateCheck": bool}` | — |
| — | `GET /healthz`, `GET /metrics` | không qua `/api/v1`; chỉ mạng nội bộ | — | mục 9 | — |

### 4.2 Dạng dữ liệu trả về

```jsonc
// MeOut
{ "email": "lan@congty.vn", "role": "BD_USER", "allowed": true }   // ngoài allow-list: role null, allowed false

// UploadResultOut
{ "name": "HD_ABC.pdf", "docId": "uuid", "status": "PROCESSING", "error": null }
{ "name": "anh.png",    "docId": null,   "status": null,         "error": "FILE_NOT_PDF" }

// DocumentOut
{ "docId": "uuid", "name": "HD_ABC_2026.pdf", "pageCount": 48, "uploadedBy": "minh@congty.vn",
  "uploadedAt": "2026-10-19T02:12:00Z", "sizeBytes": 4404019, "status": "READY",
  "failureReason": null, "usedOcr": false, "canDelete": true }        // canDelete tính theo người gọi [Đề xuất]

// SessionSummaryOut
{ "sessionId": "uuid", "title": "Thời hạn hợp đồng với công ty X là bao lâu?", "createdAt": "...", "lastMessageAt": "..." }

// SessionDetailOut
{ "sessionId": "uuid", "title": "...", "createdAt": "...", "scopeDocIds": [],
  "messages": [
    { "messageId": "uuid", "role": "user", "text": "...", "status": "COMPLETED", "createdAt": "...",
      "isNotFound": false, "citations": [], "rating": null },
    { "messageId": "uuid", "role": "assistant", "text": "Thời hạn 24 tháng [[1]].", "status": "COMPLETED",
      "createdAt": "...", "isNotFound": false,
      "citations": [ { "index": 1, "docId": "uuid", "docName": "HD_ABC_2026.pdf", "page": 12,
                       "snippet": "…thời hạn 24 tháng kể từ…", "deleted": false } ],
      "rating": "UP" } ] }

// WeeklyMetricsOut
{ "week": "2026-12-21", "weeks": ["2026-12-21", "2026-12-14"], "updatedAt": "2026-12-28T06:00:00Z",
  "metrics": { "wauPercent": 72.2, "wauCount": 13, "allowedCount": 18, "questions": 241,
               "latencyP50Ms": 6200, "latencyP90Ms": 13800,
               "thumbsUpPercent": 76.0, "notFoundPercent": 18.0 },      // không có dữ liệu → null
  "series": [ { "week": "2026-12-14", "questions": 198, "wauPercent": 66.7 } ] }

// UserOut
{ "email": "lan@congty.vn", "role": "BD_USER", "addedBy": "quantri@congty.vn", "addedAt": "..." }

// AuditOut   action ∈ UPLOAD | DELETE | PURGE (PURGE: actor = "system")
{ "actor": "minh@congty.vn", "action": "UPLOAD", "docId": "uuid", "docName": "HD_XYZ.pdf", "at": "..." }

// SuggestionOut
{ "docId": "uuid", "text": "Điều khoản thanh toán trong hợp đồng X là gì?" }
```

### 4.3 Dấu trích dẫn trong văn bản câu trả lời `[Đề xuất]`

- Máy chủ thay mỗi nhãn chunk `[cK]` trong đầu ra của AI bằng dấu `[[n]]`, với `n` là `index` của trích dẫn. Nhãn lạ bị xóa khỏi văn bản.
- Sự kiện `citation` của `n` luôn được gửi **trước** sự kiện `token` chứa `[[n]]` đầu tiên.
- Giao diện thay `[[n]]` bằng thẻ trích dẫn `[Tên tài liệu – tr. N]`. Khi sao chép, `[[n]]` thành `[n]` và thêm dòng "Nguồn: [n] Tên tài liệu, tr. N".
- Cùng một chunk được trích nhiều lần dùng cùng `n`.

## 5. Luồng SSE

Định dạng theo chuẩn SSE: mỗi khung là `event: <tên>\ndata: <JSON một dòng>\n\n`, mã hóa UTF-8. Dòng bắt đầu bằng `:` là chú thích giữ kết nối, client bỏ qua. Máy chủ web không được đệm luồng (T-602).

### 5.1 API-04 trạng thái tài liệu

```
event: status
data: {"docId":"uuid","status":"READY","failureReason":null,"pageCount":48}

: ping
```

- Gửi `: ping` mỗi 15 giây `[Đề xuất]`.
- Mỗi lần worker đổi trạng thái tài liệu thì mọi client đang mở nhận một khung `status` trong ≤ 2 giây `[Đề xuất]` (qua PostgreSQL `NOTIFY` kênh `doc_status`).
- Tài liệu bị xóa logic: gửi `status` với `"status":"DELETED"`.

### 5.2 API-08 câu trả lời

| Sự kiện | `data` | Số lần |
|---|---|---|
| `status` | `{"stage":"searching","docCount":125,"messageId":"uuid","scopeRemoved":["uuid"]}` | đúng 1, là khung đầu tiên, gửi trong ≤ 1 giây |
| `citation` | `{"index":1,"docId":"uuid","docName":"HD_ABC_2026.pdf","page":12,"snippet":"…"}` | 0 – n |
| `token` | `{"text":"Hợp đồng có thời hạn 24 tháng [[1]]"}` | 0 – n |
| `done` | `{"messageId":"uuid","citationCount":2,"isNotFound":false,"notFoundReason":null,"notice":null,"stopped":false}` | đúng 1 khung kết thúc, hoặc |
| `error` | `{"code":"AI_UNAVAILABLE","retryable":true}` | đúng 1 khung kết thúc |

- `messageId` là mã tin nhắn của câu trả lời (vai trò `assistant`), tạo ngay khi nhận câu hỏi. Giao diện dùng nó để gọi API-09 và làm `question_id` trong telemetry `[Đề xuất]` (Blueprint 3.3.2 chưa có trường này).
- `docCount` là số tài liệu `READY` trong phạm vi hiệu lực.
- `notFoundReason`: `NO_READY_DOCS` khi phạm vi không có tài liệu `READY` (giao diện hiện "Kho chưa có tài liệu sẵn sàng. Hãy tải PDF lên để bắt đầu."); `NO_EVIDENCE` khi không chunk nào vượt ngưỡng (hiện "Không tìm thấy thông tin này…").
- `notice: "LANG_UNSUPPORTED"` khi câu hỏi không phải tiếng Việt hay tiếng Anh; giao diện hiện "Hiện chỉ hỗ trợ tốt tiếng Việt và tiếng Anh." (EC-12).
- Trong khi chờ AI, máy chủ gửi `: ping` mỗi 10 giây `[Đề xuất]`.
- Luồng đóng mà chưa có `done` hay `error` → giao diện coi là `INTERRUPTED` (EC-04).
- Sau `done` hoặc `error`, máy chủ đóng luồng.

## 6. Telemetry

PRD 5.2 liệt kê **19** sự kiện (Blueprint 3.3.4 và SAD ghi 18; xem câu hỏi Q-C1). Lược đồ ở `app/modules/telemetry/schema.py` (T-113); mỗi sự kiện là một mô hình Pydantic `extra="forbid"`.

**Thuộc tính chung** (máy chủ tự thêm, client không gửi): `anon_user_id = HMAC-SHA256(telemetry_secret, email)` dạng hex, `session_id` (mã ngẫu nhiên của phiên đăng nhập, không phải `sessionId` hội thoại), `ts` (giờ máy chủ), `app_version`.

**Yêu cầu API-16** (`TelemetryIn`): `{"event": "<tên>", "props": {...}}`. Chỉ nhận sự kiện có nguồn "giao diện" ở bảng dưới; sự kiện nguồn "máy chủ" gửi từ client → 422 (chống giả mạo số liệu) `[Đề xuất]`.

| Sự kiện | Nguồn | Task phát | Thuộc tính riêng (kiểu, giá trị cho phép) | Ưu tiên |
|---|---|---|---|---|
| `auth_login_succeeded` | máy chủ | T-314 | `is_first_login: bool` | P0 |
| `auth_access_denied` | máy chủ | T-314 | `reason: "not_in_allowlist" \| "revoked" \| "wrong_role"` | P0 |
| `onboarding_viewed` | giao diện | T-515 | `doc_count: int ≥ 0` | P1 |
| `document_upload_started` | giao diện | T-523 | `file_count: int 1–10`, `total_size_mb: float ≥ 0` | P0 |
| `document_upload_rejected` | giao diện (kiểm tra trình duyệt) và máy chủ (API-02) | T-508 (giao diện), T-314 (máy chủ) | `reason: "not_pdf" \| "too_large" \| "too_many" \| "invalid_pdf"` | P0 |
| `document_processing_completed` | máy chủ | T-314 | `doc_id: uuid`, `page_count: int`, `processing_seconds: float` | P0 |
| `document_processing_failed` | máy chủ | T-314 | `doc_id: uuid`, `reason: "ocr_unreadable" \| "corrupted" \| "encrypted" \| "other"`, `used_ocr: bool` | P0 |
| `suggestion_clicked` | giao diện | T-515 | `suggestion_index: int 0–2` | P1 |
| `document_deleted` | máy chủ | T-314 | `doc_id: uuid`, `actor_role: Role` | P1 |
| `question_submitted` | máy chủ | T-307 | `question_id: uuid`, `length_chars: int`, `language: "vi" \| "en" \| "other"`, `is_followup: bool`, `scope_doc_count: int` (0 = tất cả) | P0 |
| `answer_first_token` | máy chủ | T-307 | `question_id`, `latency_ms: int` (từ lúc nhận yêu cầu tới token đầu) | P0 |
| `answer_completed` | máy chủ | T-307 | `question_id`, `latency_ms`, `citation_count: int`, `distinct_doc_count: int`, `is_not_found: bool` | P0 |
| `question_failed` | máy chủ | T-316 | `question_id`, `reason: "timeout" \| "network" \| "provider_error" \| "budget"` (`network` = client đóng kết nối trước khi xong) | P0 |
| `answer_stopped` | máy chủ | T-316 | `question_id`, `elapsed_ms: int` | P1 |
| `citation_clicked` | giao diện | T-513 | `question_id`, `doc_id`, `page: int` | P0 |
| `answer_copied` | giao diện | T-517 | `question_id` | P1 |
| `answer_rated` | máy chủ | T-313 | `question_id`, `rating: "up" \| "down"`, `reason_code: str \| null` | P1 |
| `summary_requested` | máy chủ | T-403 | `doc_id`, `latency_ms` | P1 |
| `history_session_opened` | máy chủ | T-401 | `session_age_days: int` | P1 |

Không thuộc tính nào chứa văn bản câu hỏi, câu trả lời, tên tệp, nội dung gợi ý hay email.

## 7. Cấu hình (`Settings`, T-002)

Tên biến môi trường = tên khóa viết hoa, tiền tố `CWD_`, ví dụ `CWD_DATABASE_URL`.

| Khóa | Kiểu | Mặc định | Nguồn |
|---|---|---|---|
| `database_url` | str | **bắt buộc** | — |
| `session_secret` | str (≥ 32 ký tự) | **bắt buộc** | NFR-008 |
| `telemetry_secret` | str (≥ 32 ký tự) | **bắt buộc** | AD-10 |
| `storage_root` | đường dẫn | **bắt buộc** | AD-11 |
| `embedding_dim` | int | **bắt buộc** (theo AD-06; dùng 384 cho `ai_fake`) | AD-06 |
| `ai_provider` | `"fake"` \| tên bộ nối thật | `"fake"` | AD-06 |
| `ai_api_key` | str \| None | None | CON-005 |
| `ocr_engine` | `"fake"` \| tên bộ nối thật | `"fake"` | T-004 |
| `idp` | `"fake"` \| `"oidc"` \| `"saml"` | `"fake"` | PD-001 |
| `session_ttl_s` | int | 28800 (8 giờ) `[Đề xuất, chốt ở T-006]` | — |
| `max_upload_mb` | int | 50 | NFR-004 |
| `max_files` | int | 10 | BR-003 |
| `max_pages` | int | 300 | NFR-004 |
| `max_question_chars` | int | 2000 | EC-11 |
| `ai_timeout_s` | int | 60 | EC-06 |
| `ai_slow_notice_s` | int | 15 | EC-06 |
| `ai_monthly_budget_usd` | float | 300 | NFR-009 |
| `ai_budget_alert_ratio` | float | 0.8 | G10 |
| `ai_price_input_usd_per_1k` | float | 0 (giá thật từ T-011) | NFR-009 |
| `ai_price_output_usd_per_1k` | float | 0 (giá thật từ T-011) | NFR-009 |
| `timezone` | str | `"Asia/Ho_Chi_Minh"` | Tuần của số liệu (T-312) |
| `ai_circuit_failures` | int | 5 `[Đề xuất]` | SAD 4.2 |
| `ai_circuit_open_s` | int | 30 `[Đề xuất]` | SAD 4.2 |
| `embed_batch_size` | int | 32 `[Đề xuất]` | — |
| `retrieval_k` | int | 8 `[Đề xuất]` | — |
| `relevance_threshold` | float | 0.0 (mọi chunk đều đạt) `[TBD: chỉnh ở T-607]` | RA-06 |
| `chunk_target_chars` | int | 1200 `[Đề xuất]` | — |
| `chunk_overlap_chars` | int | 150 `[Đề xuất]` | — |
| `ocr_min_confidence` | float | 0.80 `[TBD: chốt ở T-004]` | NFR-011 |
| `history_days` | int | 90 | OQ-013 |
| `audit_days` | int | 90 | BR-018 |
| `purge_hours` | int | 24 | BR-029 |
| `job_max_attempts` | int | 3 `[Đề xuất]` | — |
| `job_stale_after_s` | int | 1800 `[Đề xuất]` | — |
| `features` | tập chuỗi | tất cả P1 bật | DD-08 |
| `app_version` | str | `"0.0.0-dev"` | — |

## 8. Hàng đợi và tác vụ định kỳ

| Loại tác vụ (`job.type`) | `payload` | Đưa vào bởi | Xử lý bởi |
|---|---|---|---|
| `ingest` | `{"docId": "uuid"}` | T-201 (API-02) | T-210 |
| `suggest` | `{"docId": "uuid"}` | T-210 khi `READY` và `features.suggestions` bật | T-402 |
| `purge` | `{"docId": "uuid"}` | T-203 (API-05), `run_after = now + 5 phút` `[Đề xuất]` | T-213 |

- Thử lại: tối đa `job_max_attempts` lần, chờ 30 giây rồi 120 giây `[Đề xuất]`; sau đó `FAILED` kèm `last_error` (chỉ tên lớp lỗi, không có nội dung tài liệu).
- Tác vụ `RUNNING` quá `job_stale_after_s` được trả về `QUEUED`.

| Tác vụ định kỳ | Chu kỳ | Task |
|---|---|---|
| `release_stale_jobs` | mỗi 60 giây | T-205 |
| `purge_sweep` (tài liệu `deleted_at` quá `purge_hours` mà chưa `DELETED`) | mỗi giờ | T-213 |
| `audit_expire` | hằng ngày 02:00 | T-111 |
| `history_expire` | hằng ngày 02:30 | T-401 |

API đăng ký (T-205):

```python
def register(job_type: str, handler: Callable[[Job], Awaitable[None]]) -> None: ...
def every(name: str, seconds: int, fn: Callable[[], Awaitable[None]]) -> None: ...
def daily(name: str, at: str, fn: Callable[[], Awaitable[None]]) -> None: ...   # at = "HH:MM" giờ máy chủ
```

## 9. Sức khỏe và chỉ số vận hành (T-604)

- `GET /healthz` → 200 `{"status":"ok","db":"ok","queue":"ok"}`; CSDL lỗi → 503 `{"status":"degraded","db":"down",...}`.
- `GET /metrics` (Prometheus). Tên chỉ số `[Đề xuất]`: `cwd_http_request_seconds{route,method,status}`, `cwd_answer_first_token_seconds`, `cwd_questions_total`, `cwd_errors_total{code}`, `cwd_jobs_queued`, `cwd_document_processing_seconds{ocr}`, `cwd_ai_cost_usd_month`, `cwd_disk_free_bytes`. Nhãn không chứa email, mã tài liệu hay nội dung.

## 10. Giao diện (frontend)

### 10.1 Kiểu TypeScript

`frontend/src/api/types.ts` (T-503) chép đúng mục 2, 4.2, 5 sang TypeScript: `Role`, `DocumentStatus`, `FailureReason`, `MessageStatus`, `MeOut`, `UploadResultOut`, `DocumentOut`, `CitationOut`, `SessionSummaryOut`, `SessionDetailOut`, `WeeklyMetricsOut`, `UserOut`, `AuditOut`, `SuggestionOut`, `Features`, và các sự kiện SSE `StatusData`, `TokenData`, `CitationData`, `DoneData`, `ErrorData`.

Trạng thái chỉ có ở trình duyệt: `type ClientUploadState = "UPLOADING" | "INTERRUPTED"`.

### 10.2 Đường dẫn và điều hướng theo vai trò

| Màn hình | Đường dẫn | Vai trò vào được | Mục điều hướng |
|---|---|---|---|
| S-01 Đăng nhập | `/login` | mọi người | — |
| S-02 Không có quyền | `/denied` | đã xác thực | — |
| S-03 Hỏi đáp | `/`, `/chat/:sessionId` | BD, TN, QT | "Hỏi đáp" |
| S-04 Kho tài liệu | `/library` | BD, TN, QT | "Kho tài liệu" |
| S-05 Khung xem nguồn | ngăn trong S-03, tham số `?doc=<docId>&page=<n>` | BD, TN, QT | — |
| S-06 Lịch sử | thanh bên của S-03 | BD, TN, QT | — |
| S-07 Người dùng | `/admin/users` | QT | "Quản trị" |
| S-08 Nhật ký | `/admin/audit` | QT | (tab trong "Quản trị") |
| S-09 Số liệu | `/metrics` | QT, NTT | "Số liệu" |

Nhà tài trợ đăng nhập thì vào thẳng `/metrics`. Vai trò không được vào một đường dẫn → `/denied`.

| Thao tác | BD | TN | QT | NTT |
|---|---|---|---|---|
| Thấy vùng tải lên | ✘ (thấy dòng "Chỉ Trưởng nhóm BD tải được tài liệu lên.") | ✔ | ✘ (thấy dòng trên) | — |
| Nút Xóa trên một dòng | ✘ | khi `canDelete` | ✔ | — |

### 10.3 Nhãn trạng thái tài liệu

| Giá trị | Nhãn | Biểu tượng | Tông | Hỏi đáp được |
|---|---|---|---|---|
| `UPLOADING` (trình duyệt) | "Đang tải lên ({p}%)" | mũi tên lên | thông tin | không |
| `INTERRUPTED` (trình duyệt) | "Tải lên bị gián đoạn" + [Thử lại] | cảnh báo | cảnh báo | không |
| `PROCESSING` | "Đang xử lý" | vòng quay | thông tin | không |
| `OCR_PROCESSING` | "Đang nhận dạng ký tự" · chú thích "Tài liệu dạng ảnh quét cần thêm thời gian xử lý."; quá 15 phút thêm "Xử lý lâu bất thường" | vòng quay + văn bản | thông tin | không |
| `READY` | "Sẵn sàng" | dấu tích | thành công | **có** |
| `FAILED` | "Thất bại – {thông báo của `failureReason` ở mục 3}" | dấu X | lỗi | không |

### 10.4 Vi nội dung dùng chung

Đặt ở `frontend/src/content/messages.ts` (T-503); thành phần không viết chuỗi cứng.

| Khóa | Nội dung |
|---|---|
| `composer.placeholder` | "Hỏi về nội dung tài liệu…" |
| `composer.disclaimer` | "Câu trả lời do AI tạo – hãy kiểm tra trích dẫn với thông tin quan trọng." |
| `composer.counter` | "{n}/2.000" |
| `answer.searching` | "Đang tìm trong {N} tài liệu…" |
| `answer.slow` | "Câu hỏi đang mất nhiều thời gian hơn bình thường…" |
| `answer.notFound` | "Không tìm thấy thông tin này trong các tài liệu hiện có." |
| `answer.notFoundHint` | "Thử diễn đạt khác, hoặc kiểm tra tài liệu đã được tải lên chưa." |
| `answer.noReadyDocs` | "Kho chưa có tài liệu sẵn sàng. Hãy tải PDF lên để bắt đầu." |
| `answer.stopped` | "Đã dừng" |
| `answer.interrupted` | "Mất kết nối – câu trả lời chưa đầy đủ." |
| `answer.langNotice` | "Hiện chỉ hỗ trợ tốt tiếng Việt và tiếng Anh." |
| `net.offline` | "Mất kết nối. Đang thử kết nối lại…" |
| `library.empty` | "Chưa có tài liệu. Kéo thả PDF vào đây." |
| `library.emptyNoUpload` | "Chưa có tài liệu." |
| `library.loadError` | "Không tải được danh sách." |
| `library.uploadNotAllowed` | "Chỉ Trưởng nhóm BD tải được tài liệu lên." |
| `library.processingCount` | "{N} tài liệu đang được xử lý, chưa dùng để trả lời." |
| `chat.emptyLibrary` | "Kho chưa có tài liệu." |
| `scope.all` | "Phạm vi: Tất cả tài liệu" |
| `scope.some` | "Đang hỏi trong {N} tài liệu" |
| `scope.removed` | "Một tài liệu trong phạm vi đã bị xóa và được bỏ khỏi phạm vi." |
| `citation.deleted` | "Tài liệu đã bị xóa" |
| `citation.aria` | "Trích dẫn: {tên tài liệu}, trang {N}, mở trang nguồn" |
| `viewer.error` | "Không mở được trang." |
| `copy.done` | "Đã sao chép" |
| `delete.title` | "Xóa tài liệu?" |
| `delete.body` | "Bạn sắp xóa \"{tên}\". Cả đội sẽ không thể hỏi về tài liệu này nữa. Dữ liệu được xóa trong 24 giờ." |
| `delete.already` | "Tài liệu đã được xóa trước đó." |
| `duplicate.title` | "Tài liệu này có thể đã có trong kho" |
| `summary.title` | "Tóm tắt do AI tạo cho {tên tài liệu}" |
| `suggest.title` | "Gợi ý câu hỏi" |
| `history.empty` | "Chưa có phiên nào" |
| `history.error` | "Không tải được lịch sử." |
| `denied.title` | "Bạn chưa được cấp quyền. Liên hệ quản trị viên." |
| `denied.revoked` | "Quyền truy cập của bạn đã bị thu hồi." |
| `login.button` | "Đăng nhập bằng tài khoản công ty" |
| `login.expired` | "Phiên đã hết hạn. Đăng nhập lại để tiếp tục." |
| `metrics.empty` | "Chưa có dữ liệu. Số liệu xuất hiện sau tuần sử dụng đầu tiên." |
| `users.empty` | "Chưa có người dùng nào được cấp quyền" |
| `audit.empty` | "Chưa có hoạt động nào" |
| `action.retry` | "Thử lại" |
| `action.askAgain` | "Hỏi lại" |

### 10.5 Kho trạng thái (Pinia)

| Store | Trạng thái | Hành động | Task |
|---|---|---|---|
| `useAuthStore` | `status: "loading" \| "unauthenticated" \| "denied" \| "revoked" \| "allowed"`, `me: MeOut \| null` | `load()`, `login(next)`, `logout()` | T-505 |
| `useFeaturesStore` | `flags: Features` | `load()` | T-505 |
| `useDocumentsStore` | `items: DocumentOut[]`, `uploads: Map<string, {name, state: ClientUploadState, progress}>`, `loading`, `error` | `fetch(search, sort)`, `applyEvent(StatusData)`, `remove(docId)` | T-507 |
| `useChatStore` | `sessionId`, `messages: UiMessage[]`, `draft`, `busy`, `scope: string[]` | `newSession()`, `send(text)`, `stop()`, `open(sessionId)` | T-524, T-512 |

`UiMessage = { id, role, text, state: "SUBMITTING" | "SEARCHING" | "STREAMING" | "COMPLETED" | "NOT_FOUND" | "STOPPED" | "INTERRUPTED" | "FAILED", citations: CitationOut[], messageId?, docCount?, errorCode?, notFoundReason?, notice?, sentAt }` (Blueprint 3.5.2).

### 10.6 Quy ước mã giao diện `[Đề xuất]`

- Vue 3 `<script setup lang="ts">`; store Pinia kiểu setup (`defineStore("x", () => {...})`); router Vue Router 4 với `meta.roles`.
- Mọi chuỗi hiển thị lấy từ `content/messages.ts` (mục 10.4) hoặc `api/errors.ts` (mục 3); component không viết chuỗi cứng, không hiển thị chuỗi do máy chủ gửi.
- Mọi màu, cỡ chữ, khoảng cách dùng biến CSS của `styles/tokens.css` (chép từ prototype).
- Nội dung do AI tạo và tên tệp luôn hiển thị bằng nút văn bản; **không** dùng `v-html`.
- Gọi API chỉ qua `api/client.ts` (`request`, `streamPost`); dữ liệu theo kiểu ở `api/types.ts`.
- Test: Vitest + `@vue/test-utils` + `jsdom`; giả lập API bằng `vi.mock("@/api/client")`; đồng hồ bằng `vi.useFakeTimers()`; phần tử cần tìm có `data-testid`.
- `sessionStorage` và `localStorage` luôn bọc `try/catch`; trang phải chạy đúng khi bộ nhớ trình duyệt không dùng được.
- Task giao diện không chờ task back-end: test bằng API giả theo hợp đồng này; tích hợp thật kiểm ở T-606, T-615.

## 11. File dùng chung giữa các task

| File | Task tạo | Task được sửa | Quy tắc |
|---|---|---|---|
| `app/main.py` | T-001 | mọi task thêm router | Chỉ thêm đúng một dòng `app.include_router(...)` trong `create_app()`; không sửa dòng khác |
| `app/domain/types.py` | T-009 | không ai | Đổi kiểu = đổi hợp đồng (mục 0) |
| `app/core/config.py` | T-002 | T-301, T-312 | Chỉ thêm khóa đã có ở mục 7 |
| `app/core/wiring.py` | T-008 | T-112, T-209, T-301, T-302 | Mỗi task thêm nhánh chọn bộ nối của mình |
| `app/worker/registry.py` | T-205 | T-210, T-213, T-401, T-402 | Mỗi task thêm đúng các dòng `register`/`every`/`daily` của mình |
| `app/api/health.py` | T-001 | T-604 | T-604 mở rộng, giữ đường dẫn `/healthz` |
| `app/core/errors.py` | T-107 | không ai | Mã lỗi mới phải thêm vào mục 3 trước |
| `app/api/documents.py` | T-202 | không ai | API-02 ở `documents_upload.py` (T-201), API-05 ở `documents_delete.py` (T-203) để tránh xung đột |
| `app/modules/answer/prompt.py` | T-305 | T-309, T-310 | T-309 và T-310 chỉ thêm tham số có giá trị mặc định, không đổi hành vi mặc định |
| `app/modules/answer/service.py` | T-307 | T-316, T-309, T-310, T-311 | Mỗi task chỉ thêm bước của mình; giữ nguyên chữ ký `ask` |
| `app/modules/auth/service.py`, `api/deps.py`, `modules/documents/upload.py`, `delete.py`, `worker/ingest.py` | T-108, T-109, T-201, T-203, T-210 | T-314 | T-314 chỉ thêm lời gọi `emit` |
| `frontend/src/router/index.ts` | T-502 | T-505, T-519, T-520 | Chỉ thêm route và `meta.roles` |
| `frontend/src/views/LibraryView.vue` | T-507 | T-508, T-510, T-523 | Mỗi task gắn thành phần của mình vào đúng vị trí đã chừa |
| `frontend/src/components/RowMenu.vue` | T-510 | T-518 | T-518 chỉ thêm mục "Tóm tắt" qua slot |
| `frontend/src/views/ChatView.vue` | T-511 | T-512, T-513, T-514, T-515, T-516, T-524 | Mỗi task gắn thành phần của mình vào slot đã chừa |
| `frontend/src/content/messages.ts` | T-503 | mọi task giao diện | Chỉ thêm khóa; không đổi nội dung khóa đã có mà không cập nhật mục 10.4 |
| `Makefile` | T-001 | T-003, T-601, T-605 | Chỉ thêm đích mới |

## 12. Câu hỏi mở và lựa chọn tạm của kế hoạch

Các lựa chọn dưới đây đã được dùng trong task để không bị chặn. Trưởng đội kỹ thuật xác nhận ở tuần 1; nếu đổi, sửa file này trước rồi mới sửa task.

| # | Vấn đề | Lựa chọn tạm | Ảnh hưởng nếu đổi |
|---|---|---|---|
| Q-C1 | PRD 5.2 liệt kê 19 sự kiện, Blueprint 3.3.4 và SAD ghi 18 | Làm đủ 19 | T-113, T-610 |
| Q-C2 | Sự kiện `status` (Blueprint 3.3.2) không có `messageId`, nên giao diện không gọi được API-09 trước `done` | Thêm `messageId` và `scopeRemoved` vào `status` | T-307, T-504, T-512 |
| Q-C3 | Blueprint 3.3.3 thiếu mã lỗi cho CSRF, sai lược đồ, câu hỏi đang chạy, allow-list, tóm tắt chưa sẵn sàng | Thêm các mã `[Bổ sung]` ở mục 3 | T-107, T-503 |
| Q-C4 | Cách đặt thẻ trích dẫn vào văn bản | Dấu `[[n]]` (mục 4.3) | T-306, T-512, T-517 |
| Q-C5 | Xóa tài liệu đang xử lý | Cho phép; worker dừng nếu đã xóa | T-203, T-210 |
| Q-C6 | `Uploading`, `Interrupted` có lưu ở CSDL không | Không; chỉ ở trình duyệt | T-101, T-506 |
| Q-C7 | Tiêu đề phiên khi API-07 tạo phiên trước câu hỏi | `title = null` khi tạo; đặt 60 ký tự đầu ở câu hỏi đầu tiên | T-105, T-308 |
| Q-C8 | EC-13 (chào hỏi, kiến thức chung) | Đi theo nhánh `NO_EVIDENCE`, giao diện hiện khối "không tìm thấy" | T-304, T-525 |
| Q-C9 | Ai phát `answer_rated`, `answer_stopped`, `question_failed` | Máy chủ (tránh đếm trùng) | T-313, T-316, T-521 |
| Q-C10 | Tiêu đề CSRF | `X-Requested-With: cwd` | T-109, T-503 |
| Q-C11 | Tải lên nhiều tệp: một yêu cầu cho cả lô hay mỗi tệp một yêu cầu | Mỗi tệp một yêu cầu (tiến độ và thử lại từng tệp, EC-03); API vẫn nhận tối đa 10 | T-523 |
| Q-C12 | Tìm và sắp xếp kho tài liệu ở máy chủ hay trình duyệt | Trình duyệt (≤ 500 dòng); API-03 vẫn hỗ trợ `search`, `sort` | T-507 |
| Q-C13 | Ngưỡng "đủ bằng chứng" đặt trên điểm nào | Trên `similarity` của nhánh vector; chunk khớp từ khóa luôn đạt; mặc định 0,0 tới khi T-607 đo | T-303, T-304 |
| Q-C14 | Câu hỏi nối tiếp có cần lời gọi AI để viết lại câu hỏi | Không; ghép câu hỏi trước vào truy vấn, chỉ thêm lời gọi AI nếu T-607 cho thấy không đạt AC-014 | T-310 |
