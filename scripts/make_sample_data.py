"""Sinh PDF mẫu tất định cho test tích hợp và thử tải (T-605).

    python scripts/make_sample_data.py --out tests/fixtures/generated [--count N] [--seed S]

Cần font TTF có tiếng Việt (Arial, hoặc DejaVu Sans trên Linux). Đặt `CWD_SAMPLE_FONT` để chỉ định.
"""

import argparse
import io
import json
import os
import random
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import pdfencrypt
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_NAME = "CwdSans"
FONT_CANDIDATES = [
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
]
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
BIG_BYTES = 51 * 1024 * 1024 + 1024  # > 52.428.800
WORDS = ["hợp", "đồng", "điều", "khoản", "thanh", "toán", "bên", "A", "bên", "B", "thời", "hạn", "giao", "hàng", "bảo", "hành", "chất", "lượng", "phụ", "lục", "báo", "cáo", "tài", "chính", "quý", "doanh", "thu", "chi", "phí", "kế", "hoạch", "dự", "án", "khách", "hàng", "đối", "tác", "cam", "kết", "trách", "nhiệm", "quyền", "lợi", "phạt", "vi", "phạm"]

KNOWN = {
    "text_1p.pdf": [(1, "Biên bản họp số BB-2026-001 được lập ngày 02/11/2026.")],
    "text_12p.pdf": [(12, "Hợp đồng số HD-2026-012 có thời hạn 24 tháng kể từ 01/03/2026.")],
    "text_100p.pdf": [(50, "Phụ lục A-2026-050 quy định mức phạt chậm thanh toán là 0,05% mỗi ngày.")],
}
PAGES = {"text_1p.pdf": 1, "text_12p.pdf": 12, "text_100p.pdf": 100}


def _register_font() -> None:
    candidates = [os.environ.get("CWD_SAMPLE_FONT", ""), *FONT_CANDIDATES]
    for path in candidates:
        if path and Path(path).is_file():
            registerFont(TTFont(FONT_NAME, path))
            return
    raise SystemExit("Không tìm thấy font TTF; đặt CWD_SAMPLE_FONT tới một tệp .ttf có tiếng Việt")


def _filler(rng: random.Random, lines: int = 12) -> list[str]:
    return [" ".join(rng.choice(WORDS) for _ in range(14)).capitalize() + "." for _ in range(lines)]


def _text_pdf(
    pages: int, known: list[tuple[int, str]], rng: random.Random, encrypt: str | None = None
) -> bytes:
    buffer = io.BytesIO()
    enc = pdfencrypt.StandardEncryption(encrypt, canPrint=1) if encrypt else None
    pdf = canvas.Canvas(buffer, pagesize=A4, invariant=1, encrypt=enc)
    by_page = dict(known)
    for number in range(1, pages + 1):
        pdf.setFont(FONT_NAME, 11)
        y = 800
        pdf.drawString(50, y, f"Trang {number}")
        lines = _filler(rng)
        if number in by_page:
            lines.insert(3, by_page[number])
        for line in lines:
            y -= 24
            pdf.drawString(50, y, line[:110])
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def _scan_pdf() -> bytes:
    """PDF chỉ có ảnh chữ, không có lớp văn bản."""
    image = Image.new("L", (800, 400), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=28)
    for i, line in enumerate(["BAN QUET GIA", "Hop dong so SCAN-2026-001", "Khong co lop van ban"]):
        draw.text((40, 60 + i * 70), line, fill=0, font=font)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4, invariant=1)
    pdf.drawImage(ImageReader(image), 50, 450, width=500, height=250)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def generate(out: Path, count: int = 0, seed: int = 0) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    _register_font()
    manifest: dict[str, Any] = {"files": {}}

    def write(name: str, data: bytes, pages: int | None, known: list[tuple[int, str]] | None = None
              ) -> None:  # fmt: skip
        (out / name).write_bytes(data)
        manifest["files"][name] = {
            "pages": pages,
            "bytes": len(data),
            "sentences": [{"page": p, "text": t} for p, t in (known or [])],
        }

    for name, pages in PAGES.items():
        rng = random.Random(f"{seed}:{name}")
        write(name, _text_pdf(pages, KNOWN[name], rng), pages, KNOWN[name])
    write("scan_1p.pdf", _scan_pdf(), 1)
    twelve = (out / "text_12p.pdf").read_bytes()
    write("corrupted.pdf", twelve[: len(twelve) // 2], None)
    write("encrypted.pdf", _text_pdf(1, [], random.Random(seed), encrypt="x"), 1)
    write("not_pdf.pdf", PNG_MAGIC + b"\x00" * 64, None)
    one = (out / "text_1p.pdf").read_bytes()
    write("big_51mb.pdf", one + b"\n%" + b"0" * (BIG_BYTES - len(one) - 2), 1)
    for i in range(1, count + 1):
        rng = random.Random(f"{seed}:gen:{i}")
        write(f"gen_{i:03d}.pdf", _text_pdf(rng.randint(5, 50), [], rng), None)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), "utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--count", type=int, default=0)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    manifest = generate(args.out, args.count, args.seed)
    print(f"Đã sinh {len(manifest['files'])} tệp vào {args.out}")


if __name__ == "__main__":
    main()
