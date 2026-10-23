# T-605 · Dữ liệu mẫu và fixture kiểm thử

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | — |
| BR | BR-001, BR-027 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) |
| Mở khóa | [T-206](T-206-ingest-trich-van-ban-theo-trang.md), [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md), [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md), [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-g3.md) |

## Mục tiêu

Sinh PDF mẫu (có lớp văn bản, nhiều trang, tiếng Việt có dấu, bản ảnh quét giả) để test tích hợp và thử tải.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- tests/fixtures/README.md (task này tạo)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) Khung mã nguồn backend và công cụ: `create_app`

## File cần tạo hoặc sửa

- `scripts/make_sample_data.py`
- `tests/fixtures/README.md`

## Các bước

1. Viết `make_sample_data.py --out <thư mục> [--count N]` (`--count` sinh thêm N tài liệu văn bản 5–50 trang có nội dung ngẫu nhiên tất định theo seed, dùng cho staging và thử tải ở T-613, T-608) tạo bằng thư viện của T-007 hoặc `reportlab` `[Đề xuất]`: `text_1p.pdf` (1 trang), `text_12p.pdf`, `text_100p.pdf`, `scan_1p.pdf` (ảnh chữ, không có lớp văn bản), `corrupted.pdf` (cắt 50% cuối), `encrypted.pdf` (mật khẩu `x`), `not_pdf.pdf` (nội dung PNG đổi đuôi), `big_51mb.pdf`.
2. Mỗi tệp văn bản chứa câu biết trước ở trang biết trước, ví dụ trang 12 của `text_12p.pdf`: "Hợp đồng số HD-2026-012 có thời hạn 24 tháng kể từ 01/03/2026."
3. Ghi `manifest.json`: tên tệp, số trang, các câu biết trước kèm số trang.
4. Thêm đích `make sample-data` (ghi vào `tests/fixtures/generated/`, đã có trong `.gitignore`).

## Tiêu chí hoàn thành

- [ ] Chạy script tạo đủ 8 tệp và `manifest.json`.
- [ ] `text_12p.pdf` trang 12 chứa đúng câu ở bước 2.
- [ ] Không dùng tài liệu thật của công ty.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_sample_files_generated` | Chạy `make_sample_data.py --out tmp_path` | Có đủ 8 tệp; `manifest.json` liệt kê đủ |
| `test_known_sentence_page` | Đọc `text_12p.pdf` bằng thư viện của T-007 | Trang 12 chứa "HD-2026-012" |
| `test_big_file_size` | Kích thước `big_51mb.pdf` | > 52.428.800 byte |
| `test_count_option` | `--count 3 --seed 1` chạy hai lần | Thêm 3 tệp `gen_001.pdf`…`gen_003.pdf`; hai lần cho tệp giống hệt |

## Lệnh kiểm tra

```bash
pytest tests/fixtures/README.md -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Bộ tài liệu mẫu chính thức ≥ 200 tài liệu (DEP-003, T-613).
- Bộ câu hỏi chuẩn (DEP-003, T-607).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
