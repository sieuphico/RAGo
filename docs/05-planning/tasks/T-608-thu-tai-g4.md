# T-608 · Thử tải (G4)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W7–W8 (xem PLAN mục 6) |
| Story | — |
| BR | BR-013 |
| NFR, EC, cổng | NFR-001, NFR-003, NFR-002, G4 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-613](T-613-dung-moi-truong-staging.md) |
| Mở khóa | [T-612](T-612-ho-tro-uat.md) |

## Mục tiêu

Chứng minh NFR-001 và NFR-003 với kho ≥ 200 tài liệu và 20 người dùng đồng thời.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- NFR-001 (p90 ≤ 15 giây, trạng thái ≤ 1 giây), NFR-003 (20 người đồng thời) trong BRD
- PRD mục 5.1 dòng G4

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) Ingest: điều phối và chuyển trạng thái: `handle_ingest`
- [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md) API hội thoại: phiên, gửi câu hỏi SSE, dừng (API-07/08/09): `create_session_api`, `ask_api`, `stop_api`, `to_sse_frame`
- [T-613](T-613-dung-moi-truong-staging.md) Dựng môi trường staging: `docs/05-planning/evidence/staging-setup.md`

## File cần tạo hoặc sửa

- `backend/loadtest/locustfile.py`
- `docs/05-planning/evidence/load-test.md`

## Các bước

1. `locustfile.py` `[Đề xuất: Locust]`: mỗi người dùng ảo đăng nhập bằng `login_hint` (staging dùng `CWD_IDP=fake` cho phiên thử tải) hoặc cookie tạo sẵn; tạo phiên; mỗi 60 giây gửi 1 câu hỏi từ danh sách 30 câu mẫu, đọc hết luồng SSE bằng `httpx.stream`.
2. Đo thời gian tới khung `status` và tới khung `done`/`error`; ghi thành sự kiện tùy chỉnh của Locust để có p50, p90.
3. Kịch bản A: 20 người, 15 phút, kho ≥ 200 tài liệu `READY`. Kịch bản B: như A, cộng một người tải 10 tệp 100 trang ở phút thứ 5.
4. Chạy với nhà cung cấp AI thật nếu đã có DEP-001; nếu không, `AiFake(delay_s=0.05)` và ghi rõ kết quả không chứng minh độ trễ AI.
5. Ghi cấu hình máy, kết quả, điểm nghẽn (CPU, kết nối CSDL, độ trễ AI) vào `load-test.md`.

## Tiêu chí hoàn thành

- [ ] p90 tới `done` ≤ 15 giây và p90 tới `status` ≤ 1 giây với 20 người (NFR-001, NFR-003).
- [ ] Kịch bản B không làm p90 vượt ngưỡng.
- [ ] Báo cáo có số đo thật và nói rõ dùng AI thật hay giả lập.
- [ ] Tỷ lệ lỗi < 2%.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Kịch bản A | `locust -u 20 -r 2 -t 15m` trên staging | Bảng p50, p90 cho `status` và `done`; tỷ lệ lỗi |
| Kịch bản B | Như A, thêm tải lên 10 tệp ở phút 5 | p90 trong 10 phút sau khi tải lên vẫn ≤ ngưỡng |

## Lệnh kiểm tra

```bash
make lint type test
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Tối ưu hiệu năng (tạo task riêng nếu không đạt).
- Thử tải phần tải lên (NFR-002 đo trong T-004, T-010).

## Lưu ý

Kết quả với AI giả lập không chứng minh độ trễ thật; cần chạy lại với nhà cung cấp đã chọn trước G4.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
