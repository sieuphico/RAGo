# T-113 · Telemetry: lược đồ sự kiện và API-16

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 7 giờ `[Đề xuất]` |
| Tuần dự kiến | W3 (xem PLAN mục 6) |
| Story | US-051 |
| BR | — |
| NFR, EC, cổng | NFR-008 |
| Quyết định kiến trúc | AD-10 |
| Phụ thuộc | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) |
| Mở khóa | [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-312](T-312-so-lieu-hang-tuan-api-13.md), [T-314](T-314-noi-telemetry-vao-cac-luong-chinh.md), [T-521](T-521-telemetry-phia-giao-dien.md) |

## Mục tiêu

Nhận và ghi sự kiện đo lường chỉ siêu dữ liệu; từ chối mọi trường lạ hay văn bản tự do.

## File cần tạo hoặc sửa

- `backend/app/modules/telemetry/schema.py`
- `backend/app/modules/telemetry/service.py`
- `backend/app/api/telemetry.py`
- `backend/tests/unit/test_telemetry_schema.py`

## Các bước

1. Định nghĩa mô hình Pydantic `extra="forbid"` cho 18 sự kiện ở PRD mục 5.2 (tên và thuộc tính riêng đúng bảng).
2. `anon_user_id = HMAC(email, telemetry_secret)`; thêm các thuộc tính chung `session_id`, `timestamp`, `app_version`.
3. `POST /api/v1/telemetry/events` trả 204; sự kiện sai lược đồ trả 422 và không được ghi.
4. `emit(event_name, **props)` dùng nội bộ máy chủ.

## Tiêu chí hoàn thành

- [ ] Sự kiện có trường lạ bị từ chối (G8).
- [ ] Không trường nào chứa văn bản câu hỏi, câu trả lời hay nội dung tài liệu.
- [ ] `anon_user_id` không đảo ngược được thành email.

## Kiểm thử cần viết

- `test_unknown_field_rejected`
- `test_all_18_events_valid`
- `test_anon_id_stable`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
