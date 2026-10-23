# Sổ tay vận hành — Chat với tài liệu (MVP)

Mỗi mục: dấu hiệu → kiểm tra → xử lý → xác nhận. Lệnh giả định chạy ở thư mục cài đặt (chứa `deploy/`), với
`C="docker compose -p cwd -f deploy/compose.prod.yml --env-file deploy/.env"`. Không ghi bí mật vào kho mã.

## 1. Khởi động, dừng, cập nhật
| Việc | Lệnh | Xác nhận |
|---|---|---|
| Khởi động | `$C up -d --build` (chạy `migrate` một lần trước `api`) | `$C ps`: `db`, `api`, `worker`, `web` đều `healthy` trong ≤ 2 phút; `curl -k https://localhost/healthz` → `{"status":"ok","db":"ok","queue":"ok"}` |
| Dừng | `$C stop` (dữ liệu nằm ở volume `cwd_pgdata`, `cwd_storage`) | `$C ps` không còn dịch vụ chạy |
| Cập nhật phiên bản | `git pull`, sao lưu (mục 4), `$C up -d --build` | Healthcheck xanh; đăng nhập và hỏi thử một câu |
| Quay lại bản cũ | `git checkout <thẻ cũ>`, `$C up -d --build`; nếu migration đã đổi lược đồ thì khôi phục bản sao lưu (mục 5) | Như trên |

## 2. Thêm quản trị viên đầu tiên
`$C run --rm --no-deps api python -m app.cli add-admin quantri@congty.vn` (chạy lại không lỗi). Sau đó quản trị viên tự thêm người dùng ở màn hình Quản lý người dùng (tối đa 20).

## 3. Sự cố thường gặp
| Dấu hiệu | Kiểm tra | Xử lý | Xác nhận |
|---|---|---|---|
| Hỏi đáp báo "Dịch vụ hỏi đáp tạm thời gián đoạn" | `$C logs api \| grep "app.ai"`; `curl $CWD_OLLAMA_BASE_URL/api/tags`; chỉ số `cwd_errors_total{code="AI_UNAVAILABLE"}` | Khởi động lại Ollama / kiểm tra mạng tới dịch vụ AI; ngắt mạch tự đóng sau `ai_circuit_open_s` giây | Một câu hỏi thử có trả lời |
| Hạn mức chi phí (`BUDGET_EXCEEDED`, cảnh báo ChiPhiAiGanHanMuc) | `cwd_ai_cost_usd_month`; bảng `ai_usage` | Báo nhà tài trợ; tăng `CWD_AI_MONTHLY_BUDGET_USD` khi được duyệt rồi `$C up -d api worker` | Gauge giảm về dưới hạn mức hoặc câu hỏi chạy lại |
| SSO lỗi, mọi người bị đưa về trang đăng nhập | Nhật ký `api` quanh `/auth/callback`; đồng hồ máy chủ lệch | Đúng đồng hồ (NTP); kiểm tra cấu hình IdP (`CWD_IDP`) | Đăng nhập thử |
| Tài liệu kẹt `Đang xử lý` | `/healthz` báo `queue: backlog`; `SELECT status, count(*) FROM job GROUP BY 1`; `$C logs worker` | Khởi động lại worker (`$C restart worker`); tác vụ `RUNNING` quá `job_stale_after_s` tự về hàng đợi mỗi 60 giây (`release_stale_jobs`) | Tài liệu sang `Sẵn sàng`/`Thất bại` |
| Đĩa gần đầy (cảnh báo KhoTepSapDay) | `cwd_disk_free_bytes`; `docker system df`; kích thước volume `cwd_storage` | Dọn bản sao lưu cũ, `docker image prune`, mở rộng ổ; xóa tài liệu không cần (quản trị viên) | `cwd_disk_free_bytes` ≥ 5 GB |
| Cổng 5432/443 bị chiếm | `netstat -ano \| findstr :443` | Đổi `WEB_HTTPS_PORT` trong `deploy/.env` | `$C up -d web` |

## 4. Sao lưu
Chạy hằng ngày 01:00: `0 1 * * * cd /opt/cwd && BACKUP_DIR=/var/backups/cwd TEXTFILE_DIR=/var/lib/node_exporter deploy/backup/backup.sh`.
Giữ 7 bản gần nhất. Thất bại → mã thoát khác 0, tệp `$BACKUP_DIR/last_failure` và chỉ số `cwd_backup_last_failure_timestamp_seconds > 0` (cảnh báo SaoLuuThatBai). Xác nhận: có thư mục `YYYYMMDD-HHMMSS` chứa `db.dump` và `storage.tar` khác rỗng.
**Ngoại lệ BR-029 (chờ Bảo mật thông tin duyệt, Q-A3):** bản sao lưu ≤ 7 ngày có thể còn dữ liệu của tài liệu đã xóa.

## 5. Khôi phục
`deploy/backup/restore.sh /var/backups/cwd/<bản>`: dừng `api`/`worker`/`web`, `pg_restore --clean`, nạp lại kho tệp, khởi động lại; in thời gian từng bước. Xác nhận: danh sách tài liệu đủ, một câu hỏi trả lời có trích dẫn, mở được PDF từ thẻ trích dẫn. RPO ≤ 24 giờ, RTO ≤ 1 ngày làm việc (NFR-006). Biên bản buổi thử: `deploy/evidence/restore-drill.md`.

## 6. Thu hồi và thay khóa
- `CWD_SESSION_SECRET`: đổi giá trị trong `deploy/.env`, `$C up -d api worker` → mọi phiên đăng nhập bị hủy (người dùng đăng nhập lại).
- `CWD_TELEMETRY_SECRET`: đổi sẽ làm `anon_user_id` mới không khớp lịch sử; chỉ đổi khi nghi lộ khóa và chấp nhận ngắt chuỗi số liệu WAU.
- `CWD_AI_API_KEY` (nhà cung cấp AI ngoài): thu hồi ở nhà cung cấp, đặt khóa mới, `$C up -d api worker`.
- Gỡ quyền một người: Quản lý người dùng → Gỡ; có hiệu lực ở yêu cầu kế tiếp (EC-17).

## 7. Chỉ số, cảnh báo và liên hệ
| Chỉ số (`/metrics` của api cổng 8000 và worker cổng 9101, chỉ mạng nội bộ) | Cảnh báo (`deploy/alerts.yml`) |
|---|---|
| `cwd_http_request_seconds`, `cwd_answer_first_token_seconds`, `cwd_questions_total`, `cwd_errors_total{code}`, `cwd_jobs_queued`, `cwd_document_processing_seconds{ocr}`, `cwd_ai_cost_usd_month`, `cwd_disk_free_bytes` | ChiPhiAiGanHanMuc, LoiXuLyTaiLieuNhieu, KhoTepSapDay, PhanHoiDauTienCham, SaoLuuThatBai, HangDoiTacVuTichTu |

Liên hệ theo vai trò (không ghi số cá nhân vào kho mã): Trưởng đội kỹ thuật (sự cố ứng dụng), Đội IT (mạng, đĩa, chứng chỉ TLS), Bảo mật thông tin (khóa, ngoại lệ sao lưu), PM (thông báo người dùng).
