# T-301 · Cổng AI (AiGateway): thời hạn, hạn mức, ghi nhận

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W5–W6 (xem PLAN mục 6) |
| Story | US-060 |
| BR | BR-017, BR-028 |
| NFR, EC, cổng | NFR-009, EC-06, EC-07 |
| Quyết định kiến trúc | AD-04 |
| Phụ thuộc | [T-002](T-002-nap-cau-hinh-va-bi-mat.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) |
| Mở khóa | [T-302](T-302-bo-noi-ai-that-1-2-nhung-theo-lo.md), [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md), [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md), [T-402](T-402-goi-y-cau-hoi-mau-api-17.md), [T-403](T-403-tom-tat-tai-lieu-api-12.md), [T-604](T-604-giam-sat-suc-khoe-chi-so-va-canh-bao.md) |

## Mục tiêu

Điểm duy nhất gọi AI: giới hạn thời gian, hạn mức chi phí, ánh xạ lỗi, không ghi nội dung vào nhật ký.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 3 (`AI_UNAVAILABLE`, `BUDGET_EXCEEDED`, `TIMEOUT`)
- CONTRACTS mục 7 (`ai_*`)
- SAD mục 4.2 (chép ở các bước dưới)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-002](T-002-nap-cau-hinh-va-bi-mat.md) Nạp cấu hình và bí mật: `Settings`, `get_settings`
- [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md) Cổng (ports) và bộ nối giả (fake adapters): `ProviderError`, `ProviderTimeout`, `AiPort`, `OcrPort`, `StoragePort`, `IdpPort`
- [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md) Hợp đồng lỗi và bộ xử lý ngoại lệ: `ErrorCode`, `AppError`, `install_error_handlers`, `ERROR_DEFAULTS`
- [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md) Repository quản trị, nhật ký, telemetry, chi phí AI: `get_by_email`, `list_all`, `add`, `remove`, `count`, `count_by_role` …
- [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) Telemetry: lược đồ sự kiện và API-16: `anon_id`, `emit`, `EVENTS`, `CLIENT_EVENTS`

## File cần tạo hoặc sửa

- `app/adapters/ai_gateway.py`
- `tests/unit/test_ai_gateway.py`

## Chữ ký và giao diện

```python
class AiGateway:
    def __init__(self, provider: AiPort, settings: Settings, session_factory: async_sessionmaker[AsyncSession],
                 clock: Callable[[], float] = time.monotonic) -> None: ...
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    def generate(self, system: str, user: str) -> AsyncIterator[str]: ...
```

## Các bước

1. `AiGateway(provider, settings, session_factory, clock=time.monotonic)` bọc một `AiPort`; `wiring.build_gateway(settings)` tạo thể hiện duy nhất. Mọi mô-đun gọi AI qua cổng này.
2. `embed`: thời hạn mỗi lời gọi `ai_timeout_s`; `ProviderError` hoặc hết hạn thì thử lại tối đa 2 lần, chờ 1 rồi 2 giây; hết lượt → `AppError(AI_UNAVAILABLE)` (lỗi) hoặc `AppError(TIMEOUT)` (hết hạn).
3. `generate`: hạn chót = lúc bắt đầu + `ai_timeout_s` cho **toàn bộ** luồng; quá hạn → `AppError(TIMEOUT)`; `ProviderError` → `AppError(AI_UNAVAILABLE)`; **không** thử lại; khi người gọi `aclose()` thì đóng luồng của nhà cung cấp.
4. Hạn mức: trước mỗi lời gọi đọc `usage.get_cost(tháng hiện tại)`; ≥ `ai_monthly_budget_usd` → `AppError(BUDGET_EXCEEDED)`. Sau lời gọi cộng chi phí ước tính = `ceil(ký_tự/4)/1000 × giá` cho đầu vào và đầu ra (giá từ `ai_price_input_usd_per_1k`, `ai_price_output_usd_per_1k`).
5. Lần đầu trong tháng chi phí vượt `ai_budget_alert_ratio × ai_monthly_budget_usd`: ghi nhật ký `WARNING` với sự kiện `ai_budget_alert` (T-604 tạo cảnh báo từ chỉ số).
6. Ngắt mạch: `ai_circuit_failures` lỗi liên tiếp → mở trong `ai_circuit_open_s` giây, mọi lời gọi trả ngay `AI_UNAVAILABLE`; hết thời gian cho đúng một lời gọi thử; thành công thì đóng mạch.
7. Nhật ký mỗi lời gọi chỉ gồm `op`, `chars_in`, `chars_out`, `latency_ms`, `outcome`; không có prompt hay văn bản trả về.

## Tiêu chí hoàn thành

- [ ] Chỉ `app/core/wiring.py` và `ai_gateway.py` nhập bộ nối AI.
- [ ] Vượt 80% hạn mức có một dòng cảnh báo; vượt 100% thì chặn với `BUDGET_EXCEEDED` (G10).
- [ ] `generate` lỗi không bị gọi lại lần hai.
- [ ] Sau 5 lỗi liên tiếp, lời gọi thứ 6 trả `AI_UNAVAILABLE` mà không gọi nhà cung cấp.
- [ ] Nhật ký không chứa văn bản prompt.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_timeout_maps_to_timeout` | `AiFake(delay_s=2)`, `ai_timeout_s=1`; đọc `generate` | `AppError(TIMEOUT)` |
| `test_embed_retried` | Nhà cung cấp giả lỗi 2 lần rồi thành công | `embed` trả kết quả; nhà cung cấp được gọi 3 lần |
| `test_generate_not_retried` | `AiFake(fail_mode="error")`; đọc `generate` | `AppError(AI_UNAVAILABLE)`; nhà cung cấp được gọi đúng 1 lần |
| `test_budget_warning_and_block` | Ngân sách 1 USD; `ai_usage` tháng này 0,85 rồi 1,00 | Ở 0,85: một nhật ký `ai_budget_alert`, lời gọi vẫn chạy; ở 1,00: `AppError(BUDGET_EXCEEDED)` |
| `test_circuit_opens_after_failures` | 5 lỗi liên tiếp; gọi lần 6 ngay sau | `AI_UNAVAILABLE`; bộ đếm gọi nhà cung cấp vẫn là 5; sau `ai_circuit_open_s` (đồng hồ giả) lời gọi thử được thực hiện |
| `test_logs_have_no_content` | `generate("BÍ_MẬT_HỆ_THỐNG", "BÍ_MẬT_NGƯỜI_DÙNG")` với `caplog` | Không dòng nhật ký nào chứa "BÍ_MẬT" |
| `test_cost_accumulates` | Giá vào 0,001, ra 0,002 USD mỗi 1.000 token; vào 4.000 ký tự, ra 400 ký tự | `ai_usage` tăng 0,0012 USD |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_ai_gateway.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Bộ nối nhà cung cấp thật (T-302, T-315).
- Cảnh báo và chỉ số Prometheus (T-604).
- Giới hạn số câu hỏi đồng thời mỗi người (T-308).

## Lưu ý

Thêm hai khóa cấu hình `ai_price_input_usd_per_1k`, `ai_price_output_usd_per_1k` (mặc định 0) vào `Settings` (T-002) theo CONTRACTS mục 7.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
