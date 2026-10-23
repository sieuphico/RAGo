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
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-112](T-112-bo-noi-kho-tep-storageport.md), [T-208](T-208-ingest-nhung-va-lap-chi-muc.md), [T-209](T-209-ingest-duong-ocr-cho-pdf-anh-quet.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md) |

## Mục tiêu

Định nghĩa các giao diện để AI, OCR, kho tệp và SSO thay được bộ nối; có bản giả để phát triển song song khi chưa chốt nhà cung cấp.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 (`OcrResult`, `IdpIdentity`)
- CONTRACTS mục 7 (`ai_provider`, `ocr_engine`, `idp`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) Khung mã nguồn backend và công cụ: `create_app`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `OcrResult`, `IdpIdentity`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/ports/ai.py`
- `app/ports/ocr.py`
- `app/ports/storage.py`
- `app/ports/idp.py`
- `app/adapters/ai_fake.py`
- `app/adapters/ocr_fake.py`
- `app/adapters/idp_fake.py`
- `app/core/wiring.py`
- `tests/unit/test_fakes.py`
- `tests/unit/test_import_rules.py`

## Chữ ký và giao diện

```python
class ProviderError(Exception): ...
class ProviderTimeout(ProviderError): ...

class AiPort(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    def generate(self, system: str, user: str) -> AsyncIterator[str]: ...

class OcrPort(Protocol):
    async def recognize(self, image_png: bytes, lang: str = "vie+eng") -> OcrResult: ...

class StoragePort(Protocol):
    def save(self, key: str, data: bytes) -> None: ...
    def read(self, key: str, start: int | None = None, end: int | None = None) -> bytes: ...  # end không bao gồm
    def size(self, key: str) -> int: ...
    def delete(self, key: str) -> None: ...

class IdpPort(Protocol):
    def login_url(self, redirect_uri: str, state: str, login_hint: str | None = None) -> str: ...
    async def complete(self, params: dict[str, str]) -> IdpIdentity: ...
```

## Các bước

1. Viết các `Protocol` và lớp lỗi đúng như mục chữ ký.
2. `AiFake(dim, fail_mode=None, delay_s=0)`: `embed` trả vector độ dài `dim` lấy từ SHA-256 của văn bản (seed cho `random.Random`), chuẩn hóa L2 = 1; `generate` trả lần lượt các token `"Theo "`, `"tài liệu "`, `"[cK]"`, `"."` với `cK` là nhãn đầu tiên tìm thấy trong `user` (không có nhãn thì bỏ token nhãn). `fail_mode="error"` ném `ProviderError`; `"timeout"` ném `ProviderTimeout`; `delay_s` chờ trước mỗi token.
3. `OcrFake(confidence=0.95, text="Văn bản OCR trang {page}")`: trả `OcrResult`.
4. `IdpFake(default_email)`: `login_url(redirect_uri, state, login_hint)` trả `"<redirect_uri>?state=<state>&email=<login_hint hoặc default_email>"`; `complete` đọc `params["email"]`. Chỉ bản giả dùng `login_hint` làm email (E2E đăng nhập nhiều người, T-606); bộ nối thật chỉ chuyển tiếp nó cho IdP.
5. `core/wiring.py`: `build_ai(settings) -> AiPort`, `build_ocr(settings) -> OcrPort`, `build_idp(settings) -> IdpPort`, chọn theo `ai_provider`, `ocr_engine`, `idp`; giá trị `"fake"` trả bản giả, giá trị khác ném `NotImplementedError` cho tới khi có bộ nối thật.
6. Test quy tắc nhập: không file nào trong `app/modules`, `app/api`, `app/worker` nhập `app.adapters` (chỉ `app/core/wiring.py` được nhập).

## Tiêu chí hoàn thành

- [ ] `mypy --strict app/ports app/adapters` không lỗi.
- [ ] Bản giả cho kết quả xác định: cùng đầu vào cho cùng đầu ra.
- [ ] Test quy tắc nhập đạt.
- [ ] `wiring` trả bản giả khi cấu hình `"fake"`.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_fake_embed_is_deterministic` | `AiFake(dim=384)`; gọi `embed(["xin chào"])` hai lần | Hai vector bằng nhau, độ dài 384, chuẩn L2 = 1 ± 1e-6 |
| `test_fake_embed_differs` | `embed(["a", "b"])` | Hai vector khác nhau |
| `test_fake_generate_streams_labels` | `generate("hệ thống", "ngữ cảnh [c2] ... [c1]")` | Nối các token được `"Theo tài liệu [c2]."`, có 4 token |
| `test_fake_generate_error_mode` | `AiFake(dim=8, fail_mode="error")`; đọc `generate` | Ném `ProviderError` |
| `test_import_rules` | Quét câu lệnh `import` trong `app/modules`, `app/api`, `app/worker` | Không có `app.adapters` |
| `test_wiring_fake` | `Settings(ai_provider="fake", ...)`; gọi `build_ai` | Trả thể hiện `AiFake` có `dim == settings.embedding_dim` |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_fakes.py -q
pytest tests/unit/test_import_rules.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Bộ nối thật: AI (T-302, T-315), OCR (T-209), kho tệp (T-112), IdP (T-108 sau T-006).
- Cổng AI có thời hạn và hạn mức (T-301).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
