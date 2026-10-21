# T-107 · Hợp đồng lỗi và bộ xử lý ngoại lệ

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | DD-06 |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) |
| Mở khóa | [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) |

## Mục tiêu

Mã lỗi thống nhất `{code, retryable}` cho toàn bộ API, khớp Blueprint 3.3.3.

## File cần tạo hoặc sửa

- `backend/app/core/errors.py`
- `backend/tests/unit/test_errors.py`

## Chữ ký và giao diện

```python
class ErrorCode(str, Enum): ...
class AppError(Exception):
    def __init__(self, code: ErrorCode, *, retryable: bool = False, http_status: int = 400): ...
```

## Các bước

1. Định nghĩa `ErrorCode` gồm: AUTH_EXPIRED, AUTH_FORBIDDEN, FILE_NOT_PDF, FILE_TOO_LARGE, FILE_TOO_MANY, OCR_UNREADABLE, FILE_CORRUPTED, FILE_ENCRYPTED, DOC_NOT_FOUND, QUESTION_EMPTY, QUESTION_TOO_LONG, AI_UNAVAILABLE, BUDGET_EXCEEDED, TIMEOUT.
2. `AppError(code, retryable, http_status)`; bộ xử lý đăng ký ở `create_app()` trả JSON `{code, retryable}`.
3. Lỗi không lường trước trả 500 với `{code: "INTERNAL", retryable: false}` và không lộ chi tiết kỹ thuật.

## Tiêu chí hoàn thành

- [ ] Mọi `AppError` trả đúng JSON và mã HTTP.
- [ ] Phản hồi lỗi không chứa chuỗi kỹ thuật hay dấu vết ngăn xếp.
- [ ] Danh sách mã khớp bảng ở Blueprint 3.3.3.

## Kiểm thử cần viết

- `test_app_error_serialization`
- `test_unhandled_error_is_generic`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
