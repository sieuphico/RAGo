"""19 sự kiện đo lường, chỉ siêu dữ liệu (CONTRACTS mục 6, AD-10).

Không thuộc tính nào chứa văn bản câu hỏi, câu trả lời, tên tệp hay email; `extra="forbid"`
chặn mọi trường lạ.
"""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain import Role

NonNeg = Annotated[int, Field(ge=0)]


class _Event(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuthLoginSucceeded(_Event):
    is_first_login: bool


class AuthAccessDenied(_Event):
    reason: Literal["not_in_allowlist", "revoked", "wrong_role"]


class OnboardingViewed(_Event):
    doc_count: NonNeg


class DocumentUploadStarted(_Event):
    file_count: Annotated[int, Field(ge=1, le=10)]
    total_size_mb: Annotated[float, Field(ge=0)]


class DocumentUploadRejected(_Event):
    reason: Literal["not_pdf", "too_large", "too_many", "invalid_pdf"]


class DocumentProcessingCompleted(_Event):
    doc_id: UUID
    page_count: NonNeg
    processing_seconds: Annotated[float, Field(ge=0)]


class DocumentProcessingFailed(_Event):
    doc_id: UUID
    reason: Literal["ocr_unreadable", "corrupted", "encrypted", "other"]
    used_ocr: bool


class SuggestionClicked(_Event):
    suggestion_index: Annotated[int, Field(ge=0, le=2)]


class DocumentDeleted(_Event):
    doc_id: UUID
    actor_role: Role


class QuestionSubmitted(_Event):
    question_id: UUID
    length_chars: NonNeg
    language: Literal["vi", "en", "other"]
    is_followup: bool
    scope_doc_count: NonNeg


class AnswerFirstToken(_Event):
    question_id: UUID
    latency_ms: NonNeg


class AnswerCompleted(_Event):
    question_id: UUID
    latency_ms: NonNeg
    citation_count: NonNeg
    distinct_doc_count: NonNeg
    is_not_found: bool


class QuestionFailed(_Event):
    question_id: UUID
    reason: Literal["timeout", "network", "provider_error", "budget"]


class AnswerStopped(_Event):
    question_id: UUID
    elapsed_ms: NonNeg


class CitationClicked(_Event):
    question_id: UUID
    doc_id: UUID
    page: Annotated[int, Field(ge=1)]


class AnswerCopied(_Event):
    question_id: UUID


class AnswerRated(_Event):
    question_id: UUID
    rating: Literal["up", "down"]
    reason_code: str | None = None


class SummaryRequested(_Event):
    doc_id: UUID
    latency_ms: NonNeg


class HistorySessionOpened(_Event):
    session_age_days: NonNeg


EVENTS: dict[str, type[_Event]] = {
    "auth_login_succeeded": AuthLoginSucceeded,
    "auth_access_denied": AuthAccessDenied,
    "onboarding_viewed": OnboardingViewed,
    "document_upload_started": DocumentUploadStarted,
    "document_upload_rejected": DocumentUploadRejected,
    "document_processing_completed": DocumentProcessingCompleted,
    "document_processing_failed": DocumentProcessingFailed,
    "suggestion_clicked": SuggestionClicked,
    "document_deleted": DocumentDeleted,
    "question_submitted": QuestionSubmitted,
    "answer_first_token": AnswerFirstToken,
    "answer_completed": AnswerCompleted,
    "question_failed": QuestionFailed,
    "answer_stopped": AnswerStopped,
    "citation_clicked": CitationClicked,
    "answer_copied": AnswerCopied,
    "answer_rated": AnswerRated,
    "summary_requested": SummaryRequested,
    "history_session_opened": HistorySessionOpened,
}

# Sự kiện có nguồn "giao diện"; sự kiện của máy chủ gửi từ client bị từ chối (chống giả mạo số liệu)
CLIENT_EVENTS: set[str] = {
    "onboarding_viewed",
    "document_upload_started",
    "document_upload_rejected",
    "suggestion_clicked",
    "citation_clicked",
    "answer_copied",
}
