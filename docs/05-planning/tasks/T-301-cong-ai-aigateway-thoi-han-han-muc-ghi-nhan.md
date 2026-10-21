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
| Phụ thuộc | [T-002](T-002-nap-cau-hinh-va-bi-mat.md), [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md), [T-107](T-107-hop-dong-loi-va-bo-xu-ly-ngoai-le.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md) |
| Mở khóa | [T-302](T-302-bo-noi-ai-that-ad-06.md), [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md), [T-307](T-307-dich-vu-tra-loi-answerservice.md), [T-402](T-402-goi-y-cau-hoi-mau-api-17.md), [T-403](T-403-tom-tat-tai-lieu-api-12.md), [T-604](T-604-giam-sat-suc-khoe-chi-so-va-canh-bao.md) |

## Mục tiêu

Điểm duy nhất gọi AI: giới hạn thời gian, hạn mức chi phí, ánh xạ lỗi, không ghi nội dung vào nhật ký.

## File cần tạo hoặc sửa

- `backend/app/adapters/ai_gateway.py`
- `backend/tests/unit/test_ai_gateway.py`

## Chữ ký và giao diện

```python
class AiGateway:
    def __init__(self, provider: AiPort, settings: Settings): ...
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    def generate(self, prompt: str) -> AsyncIterator[str]: ...
```

## Các bước

1. Bọc một `AiPort` bên trong; mọi lời gọi qua cổng này.
2. Thời hạn từng lời gọi theo `ai_timeout_s`; hết hạn ném `AppError(TIMEOUT)`.
3. Bộ đếm chi phí ước tính theo token; khi đạt `ai_budget_alert_ratio × ai_monthly_budget_usd` ghi cảnh báo; vượt hạn mức ném `AppError(BUDGET_EXCEEDED)`.
4. Lỗi nhà cung cấp ánh xạ thành `AI_UNAVAILABLE` (`retryable=true`); thử lại có backoff chỉ cho `embed`, không thử lại `generate`.
5. Ngắt mạch: sau N lỗi liên tiếp trả ngay `AI_UNAVAILABLE` trong một khoảng thời gian.
6. Nhật ký không chứa prompt hay văn bản trả về, chỉ độ dài và độ trễ.

## Tiêu chí hoàn thành

- [ ] Chỉ cổng này (không mô-đun khác) nhập bộ nối AI.
- [ ] Cảnh báo 80% và chặn khi vượt 100% hạn mức (G10).
- [ ] `generate` không bị tự thử lại (tránh tính phí hai lần).

## Kiểm thử cần viết

- `test_timeout_maps_to_timeout`
- `test_budget_warning_and_block`
- `test_generate_not_retried`
- `test_logs_have_no_content`
- `test_circuit_opens_after_failures`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
