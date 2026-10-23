"""PDF thử tối thiểu, tạo bằng mã thuần (chưa cần thư viện PDF; xem ADR-0003).

Đủ để qua kiểm tra `%PDF-` của API tải lên; chưa dùng cho test trích văn bản (T-206).
"""

MB = 1024 * 1024


def minimal_pdf(pad_to: int = 0) -> bytes:
    body = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    body += b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    body += b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\n"
    tail = b"trailer<</Root 1 0 R>>\n%%EOF\n"
    padding = max(0, pad_to - len(body) - len(tail))
    return body + b"%" + b"x" * max(0, padding - 2) + b"\n" + tail


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
