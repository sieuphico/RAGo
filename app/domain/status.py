from app.domain.types import DocumentStatus

S = DocumentStatus

# CONTRACTS mục 2.1; DELETED là trạng thái cuối
ALLOWED: dict[DocumentStatus, set[DocumentStatus]] = {
    S.PROCESSING: {S.OCR_PROCESSING, S.READY, S.FAILED, S.DELETED},
    S.OCR_PROCESSING: {S.READY, S.FAILED, S.DELETED},
    S.READY: {S.DELETED},
    S.FAILED: {S.DELETED},
    S.DELETED: set(),
}


class InvalidTransition(Exception):
    pass


def assert_transition(old: DocumentStatus | None, new: DocumentStatus) -> None:
    """`old=None` là tạo mới, chỉ được vào PROCESSING."""
    allowed = {S.PROCESSING} if old is None else ALLOWED[old]
    if new not in allowed:
        raise InvalidTransition(f"{old.value if old else None} -> {new.value}")
