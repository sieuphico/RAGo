import json
from pathlib import Path

from pypdf import PdfReader

from scripts.make_sample_data import generate

EXPECTED = {
    "text_1p.pdf", "text_12p.pdf", "text_100p.pdf", "scan_1p.pdf",
    "corrupted.pdf", "encrypted.pdf", "not_pdf.pdf", "big_51mb.pdf",
}  # fmt: skip


def test_sample_files_generated(sample_pdfs: Path) -> None:
    manifest = json.loads((sample_pdfs / "manifest.json").read_text("utf-8"))
    assert EXPECTED <= set(manifest["files"])
    assert all((sample_pdfs / name).is_file() for name in EXPECTED)


def test_known_sentence_page(sample_pdfs: Path) -> None:
    reader = PdfReader(sample_pdfs / "text_12p.pdf")
    assert len(reader.pages) == 12
    assert "HD-2026-012" in (reader.pages[11].extract_text() or "")
    manifest = json.loads((sample_pdfs / "manifest.json").read_text("utf-8"))
    assert manifest["files"]["text_12p.pdf"]["sentences"][0]["page"] == 12


def test_big_file_size(sample_pdfs: Path) -> None:
    assert (sample_pdfs / "big_51mb.pdf").stat().st_size > 52_428_800


def test_count_option_is_deterministic(tmp_path: Path) -> None:
    first, second = tmp_path / "a", tmp_path / "b"
    generate(first, count=3, seed=1)
    generate(second, count=3, seed=1)
    names = sorted(p.name for p in first.glob("gen_*.pdf"))
    assert names == ["gen_001.pdf", "gen_002.pdf", "gen_003.pdf"]
    for name in names:
        assert (first / name).read_bytes() == (second / name).read_bytes()
