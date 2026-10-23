# Ghi chú triển khai tại chỗ (T-602)

## Thành phần
`compose.prod.yml`: `db` (PostgreSQL 16 + pgvector), `migrate` (chạy `alembic upgrade head` một lần), `api`, `worker` (cùng ảnh `Dockerfile.backend`, người dùng không phải root), `web` (nginx, TLS 1.2+, phục vụ `frontend/dist`). Ollama (AI nội bộ) chạy riêng: `make ai-up ai-pull` hoặc máy chủ AI nội bộ; đặt `CWD_OLLAMA_BASE_URL`.

## Quy tắc mạng ra (đội mạng cấu hình)
Chỉ mở ra các đích đã được duyệt; mặc định chặn mọi đường ra khác:
- SSO/IdP của công ty (giao thức chưa chốt, PD-001 / T-006).
- Máy chủ Ollama nội bộ (cổng 11434) — không cần Internet khi dùng AI nội bộ.
- Dịch vụ AI/OCR đám mây **chỉ** nếu sau này được chọn và Bảo mật thông tin duyệt (DEP-001, CON-005).
Cổng vào: 80 (chuyển hướng) và 443; `/metrics` không chuyển ra ngoài (nginx trả 404), Prometheus lấy trực tiếp từ `api:8000` và `worker:9101` trong mạng nội bộ.

## Đã kiểm chứng (2026-10-23, Docker Desktop trên máy phát triển, AI giả)
| Tiêu chí T-602 | Kết quả |
|---|---|
| Khởi động sạch, 4 dịch vụ `healthy` | Đạt (≈ 40 giây sau khi build) |
| SSE không đệm qua nginx | Khung `: connected` của `/api/v1/documents/events` tới sau 0,01 giây khi luồng còn mở |
| Không bí mật trong ảnh | `docker history --no-trunc` và `docker run --rm cwd-backend env` không có giá trị bí mật |
| Tải PDF 49 MB qua HTTPS | 202; 51 MB → `FILE_TOO_LARGE` |
| Tiêu đề bảo mật | HSTS, CSP, nosniff có mặt; `/metrics` → 404 |
| Giao diện qua nginx/TLS/CSP | Chạy E2E trình duyệt: tải lên → Sẵn sàng (SSE), hỏi đáp, trích dẫn, khung xem nguồn; không có lỗi console |
| Lỗi tìm thấy khi kiểm chứng | (1) `httpx` thiếu ở phụ thuộc chạy; (2) nginx gửi `Host` không kèm cổng và uvicorn chưa tin `X-Forwarded-Proto` làm địa chỉ callback đăng nhập sai — đã sửa (`$http_host`, `--proxy-headers`) |

## Chưa kiểm chứng / còn mở
- Cỡ máy, hệ điều hành, kho tệp (đĩa mã hóa hay NAS, Q-A8), chứng chỉ TLS thật và cổng nội bộ: `[TBD]`, chờ đội IT.
- Thử trên máy ảo mới của IT và với AI thật (Ollama trên GPU): chưa làm.
- Chuyển hướng HTTP→HTTPS giả định cổng chuẩn 80/443; với cổng khác cần đặt lại `return 301` trong `nginx.conf`.
- Trong `compose.prod.yml` Ollama chưa là một dịch vụ; chạy cùng máy thì dùng `host.docker.internal`.
