from io import BytesIO
from pathlib import Path

import pytest
from pypdf import PdfWriter

from app.domain import FailureReason
from app.worker.extract import ExtractError, extract_pages


def _read(sample_pdfs: Path, name: str) -> bytes:
    return (sample_pdfs / name).read_bytes()


def test_extract_vietnamese_text(sample_pdfs: Path) -> None:
    pages = extract_pages(_read(sample_pdfs, "text_12p.pdf"), max_pages=300)
    assert len(pages) == 12
    assert pages[11].page == 12
    assert "Hợp đồng số HD-2026-012" in pages[11].text
    assert all(p.has_text_layer for p in pages)


def test_detect_scanned_page(sample_pdfs: Path) -> None:
    pages = extract_pages(_read(sample_pdfs, "scan_1p.pdf"), max_pages=300)
    assert len(pages) == 1
    assert pages[0].has_text_layer is False


def test_encrypted_pdf(sample_pdfs: Path) -> None:
    with pytest.raises(ExtractError) as info:
        extract_pages(_read(sample_pdfs, "encrypted.pdf"), max_pages=300)
    assert info.value.reason == FailureReason.FILE_ENCRYPTED


def test_corrupted_pdf(sample_pdfs: Path) -> None:
    with pytest.raises(ExtractError) as info:
        extract_pages(_read(sample_pdfs, "corrupted.pdf"), max_pages=300)
    assert info.value.reason == FailureReason.FILE_CORRUPTED


def test_not_a_pdf_is_corrupted(sample_pdfs: Path) -> None:
    with pytest.raises(ExtractError) as info:
        extract_pages(_read(sample_pdfs, "not_pdf.pdf"), max_pages=300)
    assert info.value.reason == FailureReason.FILE_CORRUPTED


def test_too_many_pages() -> None:
    writer = PdfWriter()
    for _ in range(301):
        writer.add_blank_page(width=100, height=100)
    buffer = BytesIO()
    writer.write(buffer)
    with pytest.raises(ExtractError) as info:
        extract_pages(buffer.getvalue(), max_pages=300)
    assert info.value.reason == FailureReason.PROCESSING_ERROR


def test_timeout_kills_child(sample_pdfs: Path) -> None:
    with pytest.raises(ExtractError) as info:
        extract_pages(_read(sample_pdfs, "text_100p.pdf"), max_pages=300, timeout_s=0.001)
    assert info.value.reason == FailureReason.PROCESSING_ERROR
