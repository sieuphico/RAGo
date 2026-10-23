# T-610 · Kiểm tra telemetry trên staging (G8)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | US-051 |
| BR | — |
| NFR, EC, cổng | G8 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-314](T-314-noi-telemetry-vao-dang-nhap-tai-len-xu-ly-va-xoa.md), [T-521](T-521-telemetry-phia-giao-dien.md), [T-613](T-613-dung-moi-truong-staging.md) |
| Mở khóa | [T-612](T-612-ho-tro-uat.md) |

## Mục tiêu

Danh sách kiểm tra mọi sự kiện P0 bắn đúng tên và thuộc tính, không có nội dung.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 6 (19 sự kiện; 11 sự kiện P0)
- PRD mục 5.1 dòng G8

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-314](T-314-noi-telemetry-vao-dang-nhap-tai-len-xu-ly-va-xoa.md) Nối telemetry vào đăng nhập, tải lên, xử lý và xóa: `upload_reason`, `failure_reason`, `emit_once`
- [T-521](T-521-telemetry-phia-giao-dien.md) Telemetry phía giao diện: `track`
- [T-613](T-613-dung-moi-truong-staging.md) Dựng môi trường staging: `docs/05-planning/evidence/staging-setup.md`

## File cần tạo hoặc sửa

- `docs/05-planning/evidence/telemetry-checklist.md`

## Các bước

1. Lập bảng 19 sự kiện ở CONTRACTS mục 6 với cột: thao tác để kích hoạt, nguồn, kết quả mong đợi, đạt/không.
2. Với mỗi sự kiện, thực hiện thao tác trên staging bằng tài khoản thử; truy vấn `telemetry_event` theo `event` và `ts`; đối chiếu tên và thuộc tính.
3. Gửi câu hỏi có chuỗi đánh dấu `CWD-CANARY-7731`; tìm chuỗi trong `telemetry_event.props`: không được có.
4. Mở S-09 và kiểm tra các chỉ số phản ánh dữ liệu vừa tạo.

## Tiêu chí hoàn thành

- [ ] 100% sự kiện P0 (11 sự kiện) bắn đúng tên và thuộc tính (G8).
- [ ] Sự kiện P1 của tính năng đang bật cũng được kiểm.
- [ ] Không trường nào chứa chuỗi đánh dấu.
- [ ] PM ký nhận danh sách.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Danh sách kiểm tra | Thực hiện 19 thao tác | Mỗi dòng có kết quả; 11 dòng P0 đạt |
| Chuỗi đánh dấu | `SELECT count(*) FROM telemetry_event WHERE props::text LIKE '%CWD-CANARY%'` | 0 |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Sửa sự kiện sai (mở lỗi cho task gốc).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
