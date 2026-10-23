# T-009 · Kiểu dữ liệu miền và chuyển trạng thái

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 3 giờ `[Đề xuất]` |
| Tuần dự kiến | W2 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-01 |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) |
| Mở khóa | [T-008](T-008-cong-ports-va-bo-noi-gia-fake-adapters.md), [T-101](T-101-migration-001-tai-lieu-chunk-goi-y.md), [T-102](T-102-migration-002-phien-hoi-thoai-va-tin-nhan.md), [T-104](T-104-mo-hinh-orm-va-repository-tai-lieu.md), [T-105](T-105-repository-hoi-thoai.md), [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md), [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-110](T-110-api-quan-ly-allow-list-api-14.md), [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-204](T-204-hang-doi-tac-vu-jobs.md), [T-206](T-206-ingest-trich-van-ban-theo-trang.md), [T-207](T-207-ingest-chia-chunk-theo-trang.md), [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md), [T-303](T-303-truy-xuat-lai-vector-tu-khoa-theo-pham-vi.md), [T-304](T-304-nguong-lien-quan-va-quyet-dinh-khong-tim-thay.md), [T-305](T-305-dung-prompt-voi-nhan-chunk.md), [T-306](T-306-kiem-tra-va-anh-xa-trich-dan.md), [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md) |

## Mục tiêu

Tạo một nơi duy nhất cho enum, dataclass và sự kiện câu trả lời mà mọi mô-đun backend dùng chung (CONTRACTS mục 2).

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 2 và 2.1

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) Khung mã nguồn backend và công cụ: `create_app`

## File cần tạo hoặc sửa

- `backend/app/domain/__init__.py`
- `backend/app/domain/types.py`
- `backend/app/domain/status.py`
- `backend/tests/unit/test_domain.py`

## Chữ ký và giao diện

```python
def assert_transition(old: DocumentStatus | None, new: DocumentStatus) -> None: ...
class InvalidTransition(Exception): ...
```

## Các bước

1. Chép nguyên văn khối mã ở CONTRACTS mục 2 vào `types.py`; không thêm, bớt hay đổi tên trường.
2. Viết `status.py`: hằng `ALLOWED` đúng bảng CONTRACTS mục 2.1, lớp `InvalidTransition(Exception)` và hàm `assert_transition(old, new)`.
3. `assert_transition(None, PROCESSING)` hợp lệ (tạo mới); mọi cặp không có trong bảng ném `InvalidTransition` với thông điệp `"<old> -> <new>"`.
4. Xuất lại các tên công khai trong `app/domain/__init__.py`.

## Tiêu chí hoàn thành

- [ ] Mọi tên kiểu và giá trị enum khớp từng chữ với CONTRACTS mục 2.
- [ ] `assert_transition` chấp nhận đúng 9 cặp ở bảng 2.1 và từ chối mọi cặp khác.
- [ ] Dataclass có `frozen=True` không gán lại được trường.
- [ ] `mypy --strict app/domain` không lỗi.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_enum_values_match_contract` | Liệt kê thành viên `Role`, `DocumentStatus`, `FailureReason`, `MessageStatus` | Đúng tập giá trị ở CONTRACTS mục 2 (4, 5, 4, 7 giá trị) |
| `test_allowed_transitions` | Gọi `assert_transition` cho 9 cặp ở bảng 2.1 (kể cả `None → PROCESSING`) | Không ném lỗi |
| `test_invalid_transition_raises` | `assert_transition(READY, PROCESSING)` | `InvalidTransition` với thông điệp `"READY -> PROCESSING"` |
| `test_frozen_dataclass` | Tạo `PageText(1, "a", True)` rồi gán `.page = 2` | `FrozenInstanceError` |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/unit/test_domain.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Mô hình ORM (T-104, T-105, T-106).
- Mô hình Pydantic vào/ra của API (đặt trong router của từng task).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
