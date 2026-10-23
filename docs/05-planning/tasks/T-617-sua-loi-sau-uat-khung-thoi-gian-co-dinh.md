# T-617 · Sửa lỗi sau UAT (khung thời gian cố định)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 10 giờ `[Đề xuất]` · khung thời gian cố định |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | G7, G9 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-612](T-612-ho-tro-uat.md) |
| Mở khóa | — |

## Mục tiêu

Sửa các lỗi Sev-1 và Sev-2 từ UAT và kiểm tra cổng, trong khung 10 giờ; lỗi vượt khung được báo PM để quyết định.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- `uat-log.md` (T-612)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-612](T-612-ho-tro-uat.md) Hỗ trợ UAT: `docs/05-planning/evidence/uat-log.md`

## File cần tạo hoặc sửa

- `docs/05-planning/evidence/uat-log.md`

## Các bước

1. Lấy danh sách lỗi Sev-1, Sev-2 đang mở từ `uat-log.md`, sắp theo mức độ rồi theo số người gặp.
2. Mỗi lỗi: viết test tái hiện trước (đỏ), sửa, test xanh, ghi mã commit vào dòng lỗi.
3. Chạy lại bộ kiểm tra bị ảnh hưởng (unit, E2E liên quan, T-609 nếu đụng phân quyền).
4. Còn 2 giờ trong khung mà lỗi Sev-1/2 chưa hết: báo PM danh sách còn lại và ước lượng, không tự kéo dài khung.

## Tiêu chí hoàn thành

- [ ] Không còn lỗi Sev-1 hoặc Sev-2 đang mở, hoặc PM đã quyết định bằng văn bản cho lỗi còn lại (G7).
- [ ] Mỗi lỗi đã sửa có test tái hiện.
- [ ] Mọi kiểm tra bị ảnh hưởng đã chạy lại và ghi kết quả.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Kiểm tra lỗi đã sửa | Với mỗi lỗi Sev-1/2 đóng | Có mã commit và tên test tái hiện |
| Chạy lại | `ci/run_ci.sh` và E2E bị ảnh hưởng | Đạt |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Lỗi Sev-3/4 (ghi chủ sở hữu ở T-612).
- Tính năng mới phát sinh từ UAT (đưa vào backlog sau thí điểm).

## Lưu ý

Task có khung thời gian cố định, là ngoại lệ duy nhất của quy tắc ≤ 8 giờ: khối lượng phụ thuộc số lỗi UAT nên không chia trước được. Mỗi lỗi lớn hơn 4 giờ được tách thành task riêng khi phát hiện.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
