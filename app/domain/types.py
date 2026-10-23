"""Kiểu dữ liệu miền; chép từ CONTRACTS mục 2. Đổi kiểu = đổi hợp đồng."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal
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
    payload: dict[str, Any]
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
