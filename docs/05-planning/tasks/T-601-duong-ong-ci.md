# T-601 · Đường ống CI

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | G7 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md), [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md) |
| Mở khóa | — |

## Mục tiêu

Mỗi thay đổi tự chạy lint, kiểm tra kiểu, test và build cho cả backend và frontend.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- Makefile (T-001, T-003)
- package.json (T-501)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) Khung mã nguồn backend và công cụ: `create_app`
- [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md) Khung mã nguồn frontend và công cụ: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`

## File cần tạo hoặc sửa

- `ci/run_ci.sh`
- `ci/pipeline.yml`
- `Makefile`

## Các bước

1. `ci/run_ci.sh` chạy được ở máy cục bộ và trong CI: dựng PostgreSQL thử (`docker compose -f deploy/compose.dev.yml up -d`), `make install lint type`, `make migrate`, `pytest --cov=app --cov-report=xml`, rồi `npm ci && npm run lint type-check test build` trong `frontend/`.
2. Báo cáo coverage riêng cho `app/worker` và `app/modules/answer` (`coverage report --include=...`); in tỷ lệ; tham số `CWD_COVERAGE_MIN` (mặc định 0, đặt 70 ở T-612 cho G7).
3. `ci/pipeline.yml`: mẫu cho GitLab CI `[Đề xuất, đổi theo hệ thống CI tại chỗ]` gọi `ci/run_ci.sh` trên mọi nhánh và yêu cầu gộp; lưu `coverage.xml` và báo cáo Playwright làm artifact.
4. Không có bí mật trong tệp; biến cần thiết đọc từ biến CI.

## Tiêu chí hoàn thành

- [ ] `ci/run_ci.sh` trả mã 0 trên nhánh chính sạch và khác 0 khi có một test hỏng.
- [ ] Có số coverage cho `app/worker` và `app/modules/answer`.
- [ ] Không có bí mật trong tệp cấu hình.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Chạy xanh | Máy có Docker; chạy `ci/run_ci.sh` trên nhánh chính | Mã 0; in tỷ lệ coverage hai thư mục |
| Chạy đỏ | Thêm tạm một test `assert False` | Mã khác 0 |
| Ngưỡng coverage | `CWD_COVERAGE_MIN=99` | Mã khác 0 với thông báo thiếu coverage |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Chạy E2E và thử tải trong CI (chạy tay ở T-606, T-608).
- Triển khai tự động (ngoài MVP).

## Lưu ý

Hệ thống CI tại chỗ chưa xác định `[TBD]`; hỏi đội IT. Nếu chưa có CI, `ci/run_ci.sh` chạy tay trước mỗi lần gộp là đủ cho MVP.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
