# T-107 · Hợp đồng lỗi và bộ xử lý ngoại lệ

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | DD-06 |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) |
| Mở khóa | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md) |

## Mục tiêu

Mã lỗi thống nhất `{code, retryable}` cho toàn bộ API, khớp Blueprint 3.3.3.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 3 (bảng mã lỗi, HTTP, `retryable`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) Khung mã nguồn backend và công cụ: `create_app`

## File cần tạo hoặc sửa

- `app/core/errors.py`
- `tests/unit/test_errors.py`

## Chữ ký và giao diện

```python
class ErrorCode(str, Enum): ...  # đúng CONTRACTS mục 3
ERROR_DEFAULTS: dict[ErrorCode, tuple[int, bool]]

class AppError(Exception):
    def __init__(self, code: ErrorCode, *, retryable: bool | None = None, http_status: int | None = None): ...

def install_error_handlers(app: FastAPI) -> None: ...
```

## Các bước

1. `ErrorCode(str, Enum)` có **đúng** các mã ở CONTRACTS mục 3 (kể cả mã `[Bổ sung]`).
2. `ERROR_DEFAULTS: dict[ErrorCode, tuple[int, bool]]` chép cột HTTP và `retryable`; mã chỉ là lý do (`FILE_*`, `OCR_UNREADABLE`, `PROCESSING_ERROR`) dùng HTTP 400 nếu lỡ bị ném ra API.
3. `AppError(code)` lấy HTTP và `retryable` mặc định từ bảng; cho phép ghi đè.
4. Đăng ký trong `create_app()`: bộ xử lý `AppError`; `RequestValidationError` → 422 `VALIDATION_ERROR`; 404 của Starlette → `NOT_FOUND`; mọi ngoại lệ khác → 500 `INTERNAL` và ghi nhật ký kèm mã yêu cầu (không ghi thân yêu cầu).
5. Thân lỗi luôn đúng `{"code": ..., "retryable": ...}`.

## Tiêu chí hoàn thành

- [ ] Mọi `AppError` trả đúng mã HTTP và thân như CONTRACTS mục 3.
- [ ] Phản hồi lỗi không chứa chuỗi kỹ thuật hay dấu vết ngăn xếp.
- [ ] Tập giá trị `ErrorCode` bằng tập mã ở CONTRACTS mục 3.
- [ ] Lỗi lược đồ và đường dẫn không có đều trả thân chuẩn.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_app_error_serialization` | Router thử ném `AppError(ErrorCode.AUTH_EXPIRED)` | 401, thân đúng `{"code":"AUTH_EXPIRED","retryable":false}` |
| `test_retryable_default` | Ném `AppError(ErrorCode.AI_UNAVAILABLE)` | 503, `retryable` = true |
| `test_validation_error_shape` | POST thân `{"x": 1}` vào router yêu cầu trường `text` | 422, thân đúng `{"code":"VALIDATION_ERROR","retryable":false}` |
| `test_unknown_route` | GET `/api/v1/khong-co` | 404 `NOT_FOUND` |
| `test_unhandled_error_is_generic` | Router ném `RuntimeError("db password=x")` | 500 `INTERNAL`; thân không chứa "password" hay "Traceback" |
| `test_codes_match_contract` | So `{c.value for c in ErrorCode}` với danh sách 27 mã chép từ CONTRACTS mục 3 | Bằng nhau |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_errors.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Thông báo tiếng Việt cho từng mã (giao diện, T-503).
- Mã yêu cầu xuyên suốt và chỉ số lỗi (T-604).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
