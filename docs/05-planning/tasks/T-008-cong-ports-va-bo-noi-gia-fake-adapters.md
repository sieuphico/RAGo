# T-008 · Cổng (ports) và bộ nối giả (fake adapters)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-01, AD-04 |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) |
| Mở khóa | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-112](T-112-bo-noi-kho-tep-storageport.md), [T-206](T-206-ingest-trich-van-ban-theo-trang.md), [T-208](T-208-ingest-nhung-va-lap-chi-muc.md), [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md) |

## Mục tiêu

Định nghĩa các giao diện để AI, OCR, kho tệp và SSO thay được bộ nối; có bản giả để phát triển song song khi chưa chốt nhà cung cấp.

## File cần tạo hoặc sửa

- `backend/app/ports/ai.py`
- `backend/app/ports/ocr.py`
- `backend/app/ports/storage.py`
- `backend/app/ports/idp.py`
- `backend/app/adapters/ai_fake.py`
- `backend/app/adapters/ocr_fake.py`
- `backend/app/adapters/idp_fake.py`
- `backend/tests/unit/test_fakes.py`

## Chữ ký và giao diện

```python
class AiPort(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    def generate(self, prompt: str) -> AsyncIterator[str]: ...

class OcrPort(Protocol):
    async def recognize(self, image: bytes, lang: str) -> OcrResult: ...  # OcrResult(text: str, confidence: float)

class StoragePort(Protocol):
    def save(self, key: str, data: bytes) -> None: ...
    def read(self, key: str, start: int | None = None, end: int | None = None) -> bytes: ...
    def delete(self, key: str) -> None: ...

class IdpPort(Protocol):
    def login_url(self, redirect_uri: str, state: str) -> str: ...
    def complete(self, params: dict[str, str]) -> IdpIdentity: ...  # IdpIdentity(email: str)
```

## Các bước

1. Viết các `Protocol` như phần chữ ký bên dưới.
2. `ai_fake`: vector xác định từ băm văn bản (số chiều lấy từ cấu hình); `generate` trả luồng token cố định có nhãn `[c1]`.
3. `ocr_fake`: trả văn bản cố định và độ tin cậy cấu hình được.
4. `idp_fake`: đăng nhập thành công với email truyền vào.

## Tiêu chí hoàn thành

- [ ] Mọi cổng có kiểu rõ ràng, mypy đạt.
- [ ] Bản giả cho kết quả xác định, dùng được trong test.
- [ ] Lõi nghiệp vụ chỉ nhập từ `app.ports`, không nhập `app.adapters`.

## Kiểm thử cần viết

- `test_fake_embed_is_deterministic`
- `test_fake_generate_streams_labels`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
