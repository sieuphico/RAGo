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
| Phụ thuộc | [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-208](T-208-ingest-nhung-va-lap-chi-muc.md), [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) |

## Mục tiêu

Chia văn bản từng trang thành chunk, giữ số trang để trích dẫn đúng.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`PageText`, `ChunkDraft`)
- CONTRACTS mục 7 (`chunk_target_chars`, `chunk_overlap_chars`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `PageText`, `ChunkDraft`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `backend/app/worker/chunker.py`
- `backend/tests/unit/test_chunker.py`

## Chữ ký và giao diện

```python
def split(pages: list[PageText], target_chars: int = 1200, overlap: int = 150) -> list[ChunkDraft]: ...
```

## Các bước

1. `split(pages, target_chars, overlap)` xử lý từng trang riêng; không chunk nào chứa văn bản của hai trang.
2. Trong một trang: tách theo đoạn (`\n\n`), rồi theo câu (`. `, `? `, `! `, `; `) nếu đoạn dài hơn `target_chars`; ghép các phần liền nhau tới khi vượt `target_chars`.
3. Phần đơn lẻ vẫn dài hơn `target_chars + 200` thì cắt cứng tại khoảng trắng gần nhất trước giới hạn.
4. Chunk kế tiếp trong cùng trang bắt đầu bằng 100–150 ký tự cuối của chunk trước (cắt tại khoảng trắng).
5. Bỏ trang và chunk rỗng hoặc chỉ khoảng trắng. `lang` để `None` (T-208 không cần).

## Tiêu chí hoàn thành

- [ ] Mọi chunk có `page` bằng trang nguồn.
- [ ] Không chunk nào dài hơn `target_chars + 200` ký tự.
- [ ] Trang rỗng không sinh chunk.
- [ ] Hai chunk liền nhau cùng trang chung 100–150 ký tự.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_chunk_keeps_page` | Trang 1 và trang 2, mỗi trang 100 ký tự | Đúng 2 chunk, `page` lần lượt 1 và 2 |
| `test_chunk_size_bounds` | Trang 1 dài 5.000 ký tự gồm câu 80 ký tự | ≥ 4 chunk; mỗi chunk ≤ 1.400 ký tự; tất cả `page == 1` |
| `test_long_sentence_hard_cut` | Một câu 3.000 ký tự không có dấu câu | Mỗi chunk ≤ 1.400 ký tự, cắt tại khoảng trắng |
| `test_overlap` | Trang 3.000 ký tự | Phần đầu chunk 2 trùng 100–150 ký tự cuối chunk 1 |
| `test_empty_page_skipped` | `[PageText(1, "   ", False), PageText(2, "abc ...", True)]` | Chỉ có chunk của trang 2 |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/unit/test_chunker.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Nhúng và ghi chunk (T-208).
- Chỉnh `target_chars`, `overlap` theo kết quả đánh giá (T-607).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
