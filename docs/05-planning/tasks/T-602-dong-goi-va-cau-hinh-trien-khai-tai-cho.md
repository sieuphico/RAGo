# T-602 · Đóng gói và cấu hình triển khai tại chỗ

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | NFR-008, NFR-005 |
| Quyết định kiến trúc | AD-11 |
| Phụ thuộc | [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md), [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md) |
| Mở khóa | [T-603](T-603-sao-luu-khoi-phuc-va-buoi-thu-khoi-phuc.md), [T-604](T-604-giam-sat-suc-khoe-chi-so-va-canh-bao.md), [T-613](T-613-dung-moi-truong-staging.md) |

## Mục tiêu

Ảnh container và cấu hình cho máy chủ web, ứng dụng, worker, CSDL theo physical view.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- SAD mục 5.4 (physical view) và `docs/04-design/diagrams/physical-view.drawio`
- CONTRACTS mục 5 (SSE không được đệm), 7 (biến môi trường)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md) CSDL phát triển, kết nối và Alembic: `get_session`, `engine`, `SessionLocal`
- [T-501](T-501-khung-ma-nguon-frontend-va-cong-cu.md) Khung mã nguồn frontend và công cụ: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`
- [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md) Worker: vòng lặp xử lý và scheduler: `run_worker`, `run_scheduler`

## File cần tạo hoặc sửa

- `deploy/Dockerfile.backend`
- `deploy/compose.prod.yml`
- `deploy/web/`
- `deploy/.env.template`
- `docs/05-planning/evidence/deploy-notes.md`

## Các bước

1. `Dockerfile.backend` nhiều tầng: cài phụ thuộc, sao chép `app/`, `migrations/`; người dùng không phải root; một ảnh cho cả API (`uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000`) và worker (`python -m app.worker`).
2. `deploy/web/`: ảnh nginx phục vụ `frontend/dist`; TLS 1.2+ với chứng chỉ gắn ngoài; `client_max_body_size 55m` (mỗi yêu cầu một tệp ≤ 50 MB); `proxy_buffering off` và `proxy_read_timeout 120s` cho `/api/v1/documents/events` và `/api/v1/chat/sessions/*/messages`; tiêu đề `Content-Security-Policy: default-src 'self'; frame-src 'self'; object-src 'none'`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`.
3. `compose.prod.yml`: dịch vụ `web`, `api`, `worker`, `db` (hoặc trỏ CSDL ngoài), volume kho tệp gắn vào `api` và `worker`; `restart: always`; healthcheck `GET /healthz`; `alembic upgrade head` chạy một lần trước khi `api` khởi động.
4. `.env.template` liệt kê mọi biến ở CONTRACTS mục 7; bí mật nạp từ kho bí mật hoặc tệp quyền 0600, không đưa vào ảnh.
5. Ghi quy tắc mạng ra (chỉ tới SSO và dịch vụ AI/OCR đã duyệt) vào `deploy-notes.md` để đội mạng cấu hình.

## Tiêu chí hoàn thành

- [ ] `docker compose -f deploy/compose.prod.yml up` khởi động đủ dịch vụ trên máy sạch, `/healthz` trả 200.
- [ ] Khung SSE đầu tiên tới trình duyệt trong ≤ 1 giây (không bị đệm).
- [ ] Không có bí mật trong ảnh hay kho mã.
- [ ] Tải tệp 50 MB qua nginx thành công.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Khởi động sạch | Máy ảo mới có Docker; điền `.env`; `compose up -d` | Cả 4 dịch vụ `healthy` trong ≤ 2 phút |
| SSE không đệm | `curl -N` tới API-08 với `AiFake(delay_s=1)` | Dòng `event: status` xuất hiện trước token đầu ≥ 0,5 giây |
| Không bí mật trong ảnh | `docker history --no-trunc` và `docker run --rm <ảnh> env` | Không có giá trị của `CWD_SESSION_SECRET`, `CWD_AI_API_KEY` |
| Tải tệp lớn | Tải PDF 49 MB qua `https://staging/...` | 202 |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Dựng máy staging (T-613).
- Sao lưu (T-603), giám sát (T-604).

## Lưu ý

Cỡ máy, hệ điều hành, cổng nội bộ và kho tệp (Q-A8) còn `[TBD]`; ghi giá trị thật vào `deploy-notes.md` khi đội IT trả lời.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
