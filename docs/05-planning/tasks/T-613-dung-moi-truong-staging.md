# T-613 · Dựng môi trường staging

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | G4, G8 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) |
| Mở khóa | [T-608](T-608-thu-tai-g4.md), [T-609](T-609-kiem-tra-bao-mat-g6.md), [T-610](T-610-kiem-tra-telemetry-tren-staging-g8.md) |

## Mục tiêu

Môi trường staging tại chỗ cùng cấu trúc với production, dữ liệu mẫu.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- deploy-notes.md (T-602)
- Script `make_sample_data.py` (T-605)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) Đóng gói và cấu hình triển khai tại chỗ: `deploy/Dockerfile.backend`, `deploy/compose.prod.yml`, `deploy/web/`

## File cần tạo hoặc sửa

- `docs/05-planning/evidence/staging-setup.md`

## Các bước

1. Triển khai gói T-602 lên máy staging; ghi địa chỉ, phiên bản ảnh.
2. Nạp ≥ 200 tài liệu mẫu: bộ DEP-003 nếu đã có; nếu chưa, sinh bằng `make_sample_data.py --count 200` (T-605) và ghi rõ là dữ liệu tổng hợp.
3. Kết nối SSO môi trường thử (T-006); dịch vụ AI thật chỉ khi đã có DEP-001, chưa có thì `CWD_AI_PROVIDER=fake`.
4. Tạo tài khoản kiểm thử cho 4 vai trò bằng `make add-admin` và API-14; ghi vào `staging-setup.md` (không ghi mật khẩu).
5. Viết cách đặt lại dữ liệu staging (`make db-reset` + nạp lại mẫu).

## Tiêu chí hoàn thành

- [ ] Chạy được luồng tải lên → Sẵn sàng → hỏi đáp có trích dẫn trên staging.
- [ ] Có ≥ 200 tài liệu `READY` cho thử tải.
- [ ] Không dùng tài liệu thật của công ty khi chưa có DEP-001.
- [ ] `staging-setup.md` đủ để người khác đặt lại dữ liệu.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Smoke test | Đăng nhập bằng tài khoản TN; tải `text_12p.pdf`; chờ Sẵn sàng; hỏi "HD-2026-012 có thời hạn bao lâu?" | Câu trả lời có trích dẫn trang 12 |
| Đếm tài liệu | `SELECT count(*) FROM document WHERE status='READY'` | ≥ 200 |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Thử tải (T-608), kiểm tra bảo mật (T-609), telemetry (T-610).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
