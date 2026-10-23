# T-614 · Cờ tính năng cho phần P1

| Thuộc tính | Giá trị |
|---|---|
| Pha | 4 Tính năng P1 phía máy chủ |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | DD-08 |
| Phụ thuộc | [T-002](T-002-nap-cau-hinh-va-bi-mat.md) |
| Mở khóa | [T-310](T-310-cau-hoi-noi-tiep-trong-phien.md), [T-311](T-311-pham-vi-tai-lieu-trong-api-08-va-ec-15.md), [T-313](T-313-danh-gia-api-11.md), [T-401](T-401-lich-su-hoi-thoai-api-10-va-het-han-90-ngay.md), [T-402](T-402-goi-y-cau-hoi-mau-api-17.md), [T-403](T-403-tom-tat-tai-lieu-api-12.md) |

## Mục tiêu

Bật tắt từng tính năng P1 mà không phá luồng P0 (DD-08, RSK-005).

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 4.1 (`GET /api/v1/features`)
- CONTRACTS mục 7 (`features`)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-002](T-002-nap-cau-hinh-va-bi-mat.md) Nạp cấu hình và bí mật: `Settings`, `get_settings`

## File cần tạo hoặc sửa

- `app/core/features.py`
- `app/api/features.py`
- `tests/unit/test_features.py`

## Chữ ký và giao diện

```python
ALL_P1: tuple[str, ...]
def is_enabled(name: str) -> bool: ...
def require_feature(name: str) -> Callable[[], None]: ...
```

## Các bước

1. `features.py`: `ALL_P1 = ("suggestions", "summary", "history", "rating", "copy", "scope", "followup", "duplicateCheck")`; `is_enabled(name)` đọc `get_settings().features`; tên không có trong `ALL_P1` → `ValueError`.
2. `require_feature(name)` là dependency FastAPI: tắt → `AppError(NOT_FOUND)`.
3. `GET /api/v1/features` (đã xác thực) trả đủ 8 khóa kiểu bool.
4. Worker: handler của tính năng tắt gọi `complete` ngay (T-402 dùng).

## Tiêu chí hoàn thành

- [ ] Tắt một cờ làm route tương ứng trả 404 và không ảnh hưởng route P0.
- [ ] API trả đủ 8 khóa.
- [ ] Cờ đổi bằng biến môi trường `CWD_FEATURES` khi khởi động lại.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_disabled_feature_404` | `CWD_FEATURES=history`; route thử dùng `require_feature("summary")` | 404 `NOT_FOUND`; route `require_feature("history")` 200 |
| `test_features_endpoint` | `CWD_FEATURES=summary` | 200 với 8 khóa; chỉ `summary` là `true` |
| `test_unknown_feature` | `is_enabled("abc")` | `ValueError` |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_features.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đọc cờ ở giao diện (T-505).
- Ẩn thành phần giao diện khi cờ tắt (mỗi task giao diện P1).

## Lưu ý

Thứ tự cắt khi trễ theo BRD: BR-020 (gợi ý) → BR-019 (tóm tắt) → BR-021 (lịch sử) → BR-022 (sao chép).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
