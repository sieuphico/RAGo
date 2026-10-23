# T-302 · Bộ nối AI thật (1/2): nhúng theo lô

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-060, US-020 |
| BR | BR-017, BR-028 |
| NFR, EC, cổng | NFR-001 |
| Quyết định kiến trúc | AD-06 |
| Phụ thuộc | [T-011](T-011-khao-sat-ai-2-2-sinh-cau-tra-loi-do-tre-chi-phi-khuyen-nghi.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md) |
| Mở khóa | [T-315](T-315-bo-noi-ai-that-2-2-sinh-cau-tra-loi-dang-luong.md) |

## Mục tiêu

Cài đặt `AiPort.embed` cho nhà cung cấp đã chọn ở AD-06 và kiểm tra số chiều vector khi khởi động.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- docs/05-planning/spikes/AI-provider.md mục "Khuyến nghị AD-06"
- CONTRACTS mục 7 (`ai_provider`, `ai_api_key`, `embedding_dim`)
- Chữ ký `AiPort` ở T-008

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-011](T-011-khao-sat-ai-2-2-sinh-cau-tra-loi-do-tre-chi-phi-khuyen-nghi.md) Khảo sát AI (2/2): sinh câu trả lời, độ trễ, chi phí, khuyến nghị AD-06: `docs/05-planning/spikes/AI-provider.md`, `scripts/ai_trial.py`
- [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md) Cổng AI (AiGateway): thời hạn, hạn mức, ghi nhận: `AiGateway`

## File cần tạo hoặc sửa

- `app/adapters/ai_provider.py`
- `app/core/wiring.py`
- `tests/unit/test_ai_provider_embed.py`

## Chữ ký và giao diện

```python
class ProviderAi:
    def __init__(self, settings: Settings) -> None: ...
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    async def self_check(self) -> None: ...
```

## Các bước

1. Tạo lớp `ProviderAi(settings)` dùng `httpx.AsyncClient` (thời hạn kết nối 5 giây, đọc `ai_timeout_s`); khóa từ `settings.ai_api_key`, không ghi nhật ký.
2. `embed(texts)` gọi API nhúng theo lô (tối đa `embed_batch_size` văn bản mỗi yêu cầu), giữ đúng thứ tự.
3. Ánh xạ lỗi: HTTP 429, 5xx, lỗi mạng → `ProviderError`; hết thời gian → `ProviderTimeout`; HTTP 401/403 → `ProviderError` và nhật ký `ai_auth_failed` (không kèm khóa).
4. `async def self_check()`: nhúng chuỗi "kiểm tra"; độ dài vector khác `embedding_dim` → ném `RuntimeError` để tiến trình dừng khi khởi động.
5. Đăng ký trong `wiring.build_ai` khi `ai_provider` bằng tên nhà cung cấp; chỉ gửi văn bản, không gửi email, mã người dùng hay tên tệp.

## Tiêu chí hoàn thành

- [ ] Test đơn vị (dùng `respx`) đạt cho lô, thứ tự và ánh xạ lỗi.
- [ ] `self_check` dừng khởi động khi số chiều sai.
- [ ] Không có khóa trong mã, nhật ký hay thông điệp lỗi.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_embed_batches_and_order` | 40 văn bản, `embed_batch_size=32`; `respx` trả vector theo chỉ số | 2 yêu cầu HTTP; 40 vector đúng thứ tự |
| `test_http_errors_mapped` | `respx` trả 429, 503, rồi lỗi mạng | Ba lần đều `ProviderError` |
| `test_timeout_mapped` | `respx` chờ quá thời hạn đọc | `ProviderTimeout` |
| `test_embed_dimension` | `self_check` khi máy chủ giả trả vector 10 chiều, `embedding_dim=384` | `RuntimeError` |
| `test_request_has_no_identifiers` | Bắt thân yêu cầu gửi đi | Chỉ có trường mô hình và `input`; không có chuỗi `@` |
| `test_key_not_logged` | Khóa `sk-TEST`; gây lỗi 401 với `caplog` | Không dòng nhật ký nào chứa `sk-TEST` |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_ai_provider_embed.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Sinh câu trả lời dạng luồng (T-315).
- Thời hạn tổng, hạn mức, ngắt mạch (T-301).
- Phê duyệt dùng dữ liệu thật (DEP-001).

## Lưu ý

Chỉ bắt đầu sau AD-06 (T-011). Dùng dữ liệu thật chỉ sau DEP-001. Trước đó hệ thống chạy với `AiFake`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
