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
| Mở khóa | [T-003](T-003-csdl-phat-trien-ket-noi-va-alembic.md), [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-205](T-205-worker-vong-lap-xu-ly-va-scheduler.md), [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-614](T-614-co-tinh-nang-cho-phan-p1.md) |

## Mục tiêu

Một lớp `Settings` đọc cấu hình từ biến môi trường; không có giá trị bí mật mặc định.

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

1. Dùng `pydantic-settings` `[Đề xuất]` để định nghĩa `Settings`.
2. Các giá trị bắt buộc (không mặc định): `database_url`, `session_secret`, `storage_root`.
3. Các giá trị có mặc định theo yêu cầu: `max_upload_mb=50`, `max_files=10`, `max_question_chars=2000`, `ai_timeout_s=60`, `ai_slow_notice_s=15`, `ai_monthly_budget_usd=300`, `ai_budget_alert_ratio=0.8`, `history_days=90`, `audit_days=90`, `purge_hours=24`, `embedding_dim` (không mặc định, phụ thuộc AD-06).
4. `get_settings()` có bộ nhớ đệm.

## Tiêu chí hoàn thành

- [ ] Thiếu biến bắt buộc thì khởi động lỗi rõ ràng.
- [ ] Các giá trị mặc định khớp NFR-004, NFR-009, PQ-005.
- [ ] `.env.example` liệt kê đủ biến, không có giá trị thật.

## Kiểm thử cần viết

- `test_missing_required_env_raises`
- `test_defaults_match_requirements`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
