# T-604 · Giám sát: sức khỏe, chỉ số và cảnh báo

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | NFR-005, NFR-009 |
| Quyết định kiến trúc | AD-04 |
| Phụ thuộc | [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md), [T-204](T-204-hang-doi-tac-vu-jobs.md) |
| Mở khóa | [T-611](T-611-so-tay-van-hanh-va-ghi-chu-phat-hanh.md) |

## Mục tiêu

Điểm cuối sức khỏe, chỉ số Prometheus và cảnh báo theo SAD mục 4.3.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 9 (sức khỏe và tên chỉ số)
- SAD mục 4.3 (chép ở các bước)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md) Cổng AI (AiGateway): thời hạn, hạn mức, ghi nhận: `AiGateway`
- [T-602](T-602-dong-goi-va-cau-hinh-trien-khai-tai-cho.md) Đóng gói và cấu hình triển khai tại chỗ: `deploy/Dockerfile.backend`, `deploy/compose.prod.yml`, `deploy/web/`
- [T-204](T-204-hang-doi-tac-vu-jobs.md) Hàng đợi tác vụ (jobs): `enqueue`, `claim`, `complete`, `fail`, `release_stale`

## File cần tạo hoặc sửa

- `app/api/health.py`
- `app/core/metrics.py`
- `deploy/alerts.yml`
- `tests/integration/test_health_metrics.py`

## Chữ ký và giao diện

```python
def install_metrics(app: FastAPI) -> None: ...
AI_COST: Gauge
FIRST_TOKEN: Histogram
ERRORS: Counter
```

## Các bước

1. Mở rộng `/healthz` (T-001): kiểm tra `SELECT 1` (thời hạn 2 giây) và đếm tác vụ `QUEUED` quá 30 phút; trả đúng CONTRACTS mục 9; CSDL lỗi → 503.
2. `core/metrics.py` dùng `prometheus-client` `[Đề xuất]`: các chỉ số ở CONTRACTS mục 9; middleware đo `cwd_http_request_seconds` với nhãn `route` là mẫu đường dẫn (`/api/v1/documents/{doc_id}`), không phải đường dẫn thật.
3. `AiGateway` và `AnswerService` cập nhật `cwd_ai_cost_usd_month`, `cwd_answer_first_token_seconds`, `cwd_errors_total{code}`; worker cập nhật `cwd_jobs_queued`, `cwd_document_processing_seconds{ocr}`.
4. `GET /metrics` chỉ mở trên cổng nội bộ (nginx không chuyển tiếp ra ngoài).
5. `alerts.yml` (quy tắc Prometheus): `cwd_ai_cost_usd_month >= 0.8 * 300`; `increase(cwd_errors_total{code="PROCESSING_ERROR"}[1h]) > 3`; `cwd_disk_free_bytes < 5e9`; tệp `last_failure` của sao lưu tồn tại; `histogram_quantile(0.9, rate(cwd_answer_first_token_seconds_bucket[15m])) > 15`.

## Tiêu chí hoàn thành

- [ ] Có cảnh báo khi chi phí AI đạt 80% hạn mức (G10).
- [ ] Không nhãn chỉ số nào chứa email, mã tài liệu hay nội dung.
- [ ] `/healthz` trả 503 khi CSDL mất kết nối.
- [ ] `/metrics` không truy cập được từ ngoài qua nginx.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_healthz_db_down` | Monkeypatch `SELECT 1` ném lỗi | 503 `{"status":"degraded","db":"down",...}` |
| `test_healthz_ok` | CSDL chạy | 200 `{"status":"ok","db":"ok","queue":"ok"}` |
| `test_metrics_no_content_labels` | Gọi `GET /api/v1/documents/<uuid>` rồi đọc `/metrics` | Nhãn `route="/api/v1/documents/{doc_id}"`; không có chuỗi UUID hay `@` |
| `test_cost_gauge` | `AiGateway` cộng 1,5 USD | `cwd_ai_cost_usd_month` = 1,5 |
| Kiểm tra quy tắc | `promtool check rules deploy/alerts.yml` | Hợp lệ |

## Lệnh kiểm tra

```bash
pytest tests/integration/test_health_metrics.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Hệ thống Prometheus/Alertmanager của IT (giả định có sẵn; nếu chưa có, ghi vào sổ tay T-611).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
