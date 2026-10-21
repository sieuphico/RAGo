# T-111 · Mô-đun nhật ký kiểm toán (API-15)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 1 Dữ liệu và truy cập |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 4 giờ `[Đề xuất]` |
| Tuần dự kiến | W3–W4 (xem PLAN mục 6) |
| Story | US-063, US-062 |
| BR | BR-018 |
| NFR, EC, cổng | — |
| Quyết định kiến trúc | AD-12 |
| Phụ thuộc | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-hang-doi.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) |
| Mở khóa | [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-203](T-203-xoa-tai-lieu-api-05.md), [T-213](T-213-tac-vu-xoa-du-lieu-trong-24-gio.md), [T-519](T-519-trang-quan-tri-nguoi-dung-s-07-va-nhat-ky-s-08.md) |

## Mục tiêu

Ghi nhật ký tải lên và xóa; API đọc cho Quản trị viên; xóa bản ghi quá 90 ngày.

## File cần tạo hoặc sửa

- `backend/app/modules/audit/service.py`
- `backend/app/api/admin_audit.py`
- `backend/tests/integration/test_audit.py`

## Chữ ký và giao diện

```python
def record(session, actor: str, action: str, doc_id: UUID | None) -> None: ...
```

## Các bước

1. `record(actor, action, doc_id)` gọi từ các luồng tải lên và xóa (T-201, T-203).
2. `GET /api/v1/admin/audit-log?since=&limit=` trả 4 trường: người thực hiện, thao tác, tài liệu, thời điểm.
3. Thêm tác vụ định kỳ xóa bản ghi quá `audit_days` (nối vào scheduler ở T-205).

## Tiêu chí hoàn thành

- [ ] Sau 3 lần tải lên và 1 lần xóa có đúng 4 bản ghi đủ trường (AC-018).
- [ ] Không có API sửa hoặc xóa lẻ.
- [ ] Chỉ ADMIN đọc được.

## Kiểm thử cần viết

- `test_four_records_after_ops`
- `test_audit_admin_only`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
