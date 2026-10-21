# T-521 · Telemetry phía giao diện

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W6 (xem PLAN mục 6) |
| Story | US-051 |
| BR | — |
| NFR, EC, cổng | NFR-008 |
| Quyết định kiến trúc | AD-10 |
| Phụ thuộc | [T-113](T-113-telemetry-luoc-do-su-kien-va-api-16.md), [T-503](T-503-client-api-va-bang-anh-xa-ma-loi.md) |
| Mở khóa | [T-610](T-610-kiem-tra-telemetry-tren-staging-g8.md) |

## Mục tiêu

Gửi các sự kiện phía giao diện qua API-16, chỉ siêu dữ liệu.

## File cần tạo hoặc sửa

- `frontend/src/api/telemetry.ts`
- `frontend/src/__tests__/telemetry.spec.ts`

## Các bước

1. `track(event, props)` kiểm tra tên và thuộc tính theo lược đồ chung trước khi gửi.
2. Gửi: `onboarding_viewed`, `citation_clicked`, `answer_copied`, `answer_rated`, `answer_stopped`, `suggestion_clicked` (không gửi nội dung gợi ý).
3. Gửi bằng `sendBeacon` hoặc `fetch` không chặn; lỗi gửi không ảnh hưởng giao diện.

## Tiêu chí hoàn thành

- [ ] Không sự kiện nào chứa văn bản câu hỏi, câu trả lời hay tên tệp.
- [ ] Sự kiện sai lược đồ bị loại ngay ở giao diện.
- [ ] Lỗi mạng không hiển thị lỗi cho người dùng.

## Kiểm thử cần viết

- `rejects_free_text_props`
- `failure_is_silent`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
