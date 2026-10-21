# T-207 · Ingest: chia chunk theo trang

| Thuộc tính | Giá trị |
|---|---|
| Pha | 2 Tài liệu và xử lý |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W4 (xem PLAN mục 6) |
| Story | US-022 |
| BR | BR-010 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-03 |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) |
| Mở khóa | [T-208](T-208-ingest-nhung-va-lap-chi-muc.md) |

## Mục tiêu

Chia văn bản từng trang thành chunk, giữ số trang để trích dẫn đúng.

## File cần tạo hoặc sửa

- `backend/app/worker/chunker.py`
- `backend/tests/unit/test_chunker.py`

## Các bước

1. `split(pages: list[PageText], target_chars: int = 1200, overlap: int = 150) -> list[ChunkDraft]` (giá trị `[Đề xuất]`, chỉnh sau thử nghiệm).
2. Không chunk nào trộn nội dung của hai trang.
3. Bỏ chunk rỗng hoặc chỉ khoảng trắng.

## Tiêu chí hoàn thành

- [ ] Mọi chunk có `page` đúng với trang nguồn.
- [ ] Không có chunk vượt `target_chars` quá một ngưỡng nhỏ.
- [ ] Trang rỗng không sinh chunk.

## Kiểm thử cần viết

- `test_chunk_keeps_page`
- `test_chunk_size_bounds`
- `test_empty_page_skipped`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
