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
| Phụ thuộc | [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) |
| Mở khóa | [T-301](T-301-cong-ai-aigateway-thoi-han-han-muc-ghi-nhan.md), [T-307](T-307-dich-vu-tra-loi-1-2-luong-chinh-co-trich-dan.md), [T-312](T-312-so-lieu-hang-tuan-api-13.md), [T-313](T-313-danh-gia-api-11.md), [T-314](T-314-noi-telemetry-vao-dang-nhap-tai-len-xu-ly-va-xoa.md), [T-401](T-401-lich-su-hoi-thoai-api-10-va-het-han-90-ngay.md), [T-403](T-403-tom-tat-tai-lieu-api-12.md) |

## Mục tiêu

Nhận và ghi sự kiện đo lường chỉ siêu dữ liệu; từ chối mọi trường lạ hay văn bản tự do.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- CONTRACTS mục 6 (19 sự kiện, nguồn, thuộc tính)
- CONTRACTS mục 4.1 API-16

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-106](T-106-repository-quan-tri-nhat-ky-telemetry-chi-phi-ai.md) Repository quản trị, nhật ký, telemetry, chi phí AI: `get_by_email`, `list_all`, `add`, `remove`, `count`, `count_by_role` …
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-009](T-009-kieu-du-lieu-mien-va-chuyen-trang-thai.md) Kiểu dữ liệu miền và chuyển trạng thái: kiểu ở CONTRACTS mục 2 – `CurrentUser`, `assert_transition`, `InvalidTransition`

## File cần tạo hoặc sửa

- `app/modules/telemetry/schema.py`
- `app/modules/telemetry/service.py`
- `app/api/telemetry.py`
- `tests/unit/test_telemetry_schema.py`

## Chữ ký và giao diện

```python
EVENTS: dict[str, type[BaseModel]]
CLIENT_EVENTS: set[str]

def anon_id(email: str, secret: str) -> str: ...
async def emit(session: AsyncSession, user: CurrentUser, sid: str, event: str, **props: object) -> None: ...
```

## Các bước

1. Viết 19 mô hình Pydantic `extra="forbid"` đúng tên và thuộc tính ở CONTRACTS mục 6; giá trị liệt kê dùng `Literal`; `uuid` dùng kiểu `UUID`.
2. `EVENTS: dict[str, type[BaseModel]]` và `CLIENT_EVENTS: set[str]` (các sự kiện có nguồn "giao diện").
3. `anon_id(email, secret) = hmac.new(secret, email.lower().encode(), sha256).hexdigest()`.
4. `emit(session, user: CurrentUser, sid: str, event, **props)`: kiểm tra lược đồ rồi ghi qua `telemetry.append_event`; lỗi ghi chỉ ghi nhật ký cảnh báo, **không** ném ra ngoài.
5. `POST /api/v1/telemetry/events` thân `{"event", "props"}`: `event` không thuộc `CLIENT_EVENTS` hoặc lược đồ sai → 422; đúng → 204.

## Tiêu chí hoàn thành

- [ ] Sự kiện có trường lạ bị từ chối (G8).
- [ ] Không mô hình nào có trường kiểu chuỗi tự do ngoài các giá trị liệt kê ở CONTRACTS mục 6.
- [ ] `anon_user_id` ổn định cho cùng email và khác nhau giữa hai email.
- [ ] Client gửi sự kiện nguồn "máy chủ" bị từ chối.
- [ ] Lỗi CSDL khi `emit` không làm hỏng lời gọi.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| `test_unknown_field_rejected` | POST `{"event":"citation_clicked","props":{"question_id":"<uuid>","doc_id":"<uuid>","page":3,"text":"abc"}}` | 422 `VALIDATION_ERROR`; không có dòng mới |
| `test_all_19_events_valid` | Với mỗi sự kiện, dựng một mẫu hợp lệ từ CONTRACTS mục 6 và kiểm tra lược đồ | Cả 19 hợp lệ; `len(EVENTS) == 19` |
| `test_server_event_from_client_rejected` | POST `{"event":"answer_completed",...}` hợp lệ về lược đồ | 422 |
| `test_anon_id_stable` | `anon_id("Lan@x.vn", s)` và `anon_id("lan@x.vn", s)`; `anon_id("minh@x.vn", s)` | Hai giá trị đầu bằng nhau; giá trị thứ ba khác |
| `test_emit_failure_swallowed` | Monkeypatch `append_event` ném lỗi; gọi `emit` | Không ngoại lệ; có một dòng nhật ký mức WARNING |

## Lệnh kiểm tra

```bash
pytest tests/unit/test_telemetry_schema.py -q
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Gọi `emit` trong các luồng nghiệp vụ (T-314, T-307, T-316, T-313, T-401, T-403).
- Tổng hợp số liệu tuần (T-312).
- Gửi sự kiện phía giao diện (T-521).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
