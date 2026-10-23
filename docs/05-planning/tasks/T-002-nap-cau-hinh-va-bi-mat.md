# T-002 · Nạp cấu hình và bí mật

| Thuộc tính | Giá trị |
|---|---|
| Pha | 0 Nền tảng và khảo sát |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 3 giờ `[Đề xuất]` |
| Tuần dự kiến | W1 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | NFR-004, NFR-009, NFR-008 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) |
| Mở khóa | [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md), [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-204](T-204-hang-doi-tac-vu-jobs.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-614](T-614-co-tinh-nang-cho-phan-p1.md) |

## Mục tiêu

Một lớp `Settings` đọc cấu hình từ biến môi trường; không có giá trị bí mật mặc định.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 7 (bảng khóa cấu hình)

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-001](T-001-khung-ma-nguon-backend-va-cong-cu.md) Khung mã nguồn backend và công cụ: `create_app`

## File cần tạo hoặc sửa

- `backend/app/core/config.py`
- `backend/tests/unit/test_config.py`
- `backend/.env.example`

## Chữ ký và giao diện

```python
class Settings(BaseSettings): ...

@lru_cache
def get_settings() -> Settings: ...
```

## Các bước

1. Dùng `pydantic-settings` `[Đề xuất]` định nghĩa `Settings` với **đúng** các khóa, kiểu và mặc định ở CONTRACTS mục 7; tiền tố biến môi trường `CWD_`.
2. Khóa bắt buộc (không mặc định): `database_url`, `session_secret`, `telemetry_secret`, `storage_root`, `embedding_dim`. Hai khóa bí mật phải dài ≥ 32 ký tự.
3. `features` đọc từ chuỗi phân tách bằng dấu phẩy (`CWD_FEATURES=summary,history`); không đặt thì bật cả 8 tính năng P1: `suggestions`, `summary`, `history`, `rating`, `copy`, `scope`, `followup`, `duplicateCheck`.
4. `get_settings()` có `@lru_cache`; test dùng `get_settings.cache_clear()`.
5. Viết `.env.example` liệt kê mọi khóa, giá trị trống.

## Tiêu chí hoàn thành

- [ ] Thiếu một khóa bắt buộc thì `Settings()` ném `ValidationError` và thông điệp chứa tên khóa đó.
- [ ] Mọi mặc định bằng đúng giá trị ở CONTRACTS mục 7.
- [ ] Bí mật ngắn hơn 32 ký tự bị từ chối.
- [ ] `.env.example` có đủ mọi khóa của `Settings`, không có giá trị.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_missing_required_env_raises` | Đặt mọi khóa bắt buộc trừ `CWD_DATABASE_URL`; khi tạo `Settings()` | `ValidationError`, thông điệp chứa `database_url` |
| `test_defaults_match_requirements` | Chỉ đặt các khóa bắt buộc | `max_upload_mb == 50`, `max_files == 10`, `max_question_chars == 2000`, `ai_timeout_s == 60`, `history_days == 90`, `purge_hours == 24`, `ai_monthly_budget_usd == 300` |
| `test_secret_min_length` | `CWD_SESSION_SECRET=abc` | `ValidationError` |
| `test_features_parsing` | `CWD_FEATURES=summary,history` | `settings.features == {"summary", "history"}`; không đặt thì có đủ 8 tên |
| `test_env_example_lists_all_keys` | Đọc `.env.example` và `Settings.model_fields` | Hai tập tên khóa (viết hoa, có tiền tố) bằng nhau |

## Lệnh kiểm tra

```bash
cd backend && pytest tests/unit/test_config.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đọc bí mật từ kho bí mật của máy chủ (T-602).
- Ý nghĩa nghiệp vụ của từng khóa (task dùng khóa đó).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
