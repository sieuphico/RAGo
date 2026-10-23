# T-315 · Bộ nối AI thật (2/2): sinh câu trả lời dạng luồng

| Thuộc tính | Giá trị |
|---|---|
| Pha | 3 Hỏi đáp có trích dẫn |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-020, US-027 |
| BR | BR-017, BR-028 |
| NFR, EC, cổng | NFR-001 |
| Quyết định kiến trúc | AD-04, AD-06 |
| Phụ thuộc | [T-302](T-302-bo-noi-ai-that-1-2-nhung-theo-lo.md) |
| Mở khóa | [T-607](T-607-bo-danh-gia-chat-luong-tra-loi-g3.md) |

## Mục tiêu

Cài đặt `AiPort.generate` cho nhà cung cấp đã chọn: gửi chỉ dẫn hệ thống và nội dung người dùng, nhận token theo luồng, hủy được giữa chừng.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- Chữ ký `AiPort.generate` ở T-008
- Tài liệu API luồng của nhà cung cấp chọn ở T-011

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-302](T-302-bo-noi-ai-that-1-2-nhung-theo-lo.md) Bộ nối AI thật (1/2): nhúng theo lô: `ProviderAi`

## File cần tạo hoặc sửa

- `app/adapters/ai_provider.py`
- `tests/unit/test_ai_provider_generate.py`
- `tests/integration/test_ai_provider_live.py`

## Chữ ký và giao diện

```python
class ProviderAi:  # cùng lớp với T-302
    def generate(self, system: str, user: str) -> AsyncIterator[str]: ...
```

## Các bước

1. Thêm `generate(system, user)` vào lớp bộ nối của T-302: gọi API sinh văn bản chế độ luồng qua `httpx.AsyncClient.stream`, `temperature=0.1`, `max_tokens=800` `[Đề xuất]`.
2. Phân tích định dạng luồng của nhà cung cấp (SSE hoặc JSON từng dòng) và chỉ `yield` phần văn bản mới.
3. Người gọi `aclose()` trình lặp thì đóng luồng HTTP ngay (không đọc tiếp, không bị tính thêm token).
4. Ánh xạ lỗi giống T-302: HTTP 429, 5xx, lỗi mạng → `ProviderError`; hết thời gian đọc → `ProviderTimeout`; lỗi giữa luồng → `ProviderError`.
5. Test đơn vị dùng `respx` với luồng mẫu chép từ tài liệu của nhà cung cấp; test thật đánh dấu `@pytest.mark.provider`, chỉ chạy khi có `CWD_AI_API_KEY`.

## Tiêu chí hoàn thành

- [ ] Token được trả dần, nối lại đúng văn bản mẫu.
- [ ] `aclose()` sau token thứ hai đóng kết nối HTTP.
- [ ] Lỗi 503 giữa luồng thành `ProviderError`.
- [ ] Thân yêu cầu chỉ có chỉ dẫn hệ thống, nội dung người dùng và tham số mô hình.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_generate_streams` | `respx` trả luồng mẫu 3 phần "Xin ", "chào ", "[c1]." | Trình lặp trả đúng 3 chuỗi theo thứ tự |
| `test_aclose_closes_http` | Đọc 2 phần rồi `aclose()` | Phản hồi HTTP được đóng (`response.is_closed`) |
| `test_error_mid_stream` | Luồng mẫu bị ngắt sau phần đầu (lỗi kết nối) | `ProviderError` |
| `test_request_body_shape` | Bắt thân yêu cầu | Chỉ có `system`/`messages` (tùy nhà cung cấp), mô hình, `temperature=0.1`, `max_tokens=800`, `stream=true` |
| `test_generate_live` | `@pytest.mark.provider`, có khóa thật; prompt ngắn có `[c1]` | Nhận ≥ 1 token trong ≤ 15 giây |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_ai_provider_generate.py -q
pytest tests/integration/test_ai_provider_live.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Kiểm tra trích dẫn trong đầu ra (T-306).
- Thời hạn tổng và hạn mức (T-301).

## Lưu ý

Chỉ bắt đầu sau khi chốt AD-06 (T-011). Trước đó hệ thống chạy với `AiFake`, không chặn task khác.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
