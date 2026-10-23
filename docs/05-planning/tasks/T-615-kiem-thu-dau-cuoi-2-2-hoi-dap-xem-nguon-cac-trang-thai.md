# T-615 · Kiểm thử đầu cuối (2/2): hỏi đáp, xem nguồn, các trạng thái

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | BR-010, BR-011, BR-013, BR-033 |
| NFR, EC, cổng | NFR-007, G1 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md), [T-513](T-513-khung-xem-nguon-s-05.md), [T-525](T-525-hoi-dap-3-3-trang-thai-cua-cau-tra-loi.md), [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-212](T-212-tai-tep-pdf-cho-khung-xem-nguon-api-06.md) |
| Mở khóa | [T-612](T-612-ho-tro-uat.md) |

## Mục tiêu

Kịch bản E2E cho luồng hỏi đáp có trích dẫn, mở trang nguồn, không tìm thấy, dừng và mất kết nối, chạy trên Chrome và Edge ở 3 độ rộng.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- Môi trường và `loginAs` của T-606
- US-020, US-022, US-023, US-027 trong USER_STORIES.md

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) Kiểm thử đầu cuối (1/2): môi trường, đăng nhập, tải lên, xóa: `frontend/playwright.config.ts`, `frontend/e2e/fixtures.ts`, `frontend/e2e/login.spec.ts`
- [T-513](T-513-khung-xem-nguon-s-05.md) Khung xem nguồn (S-05): `SourceViewer.vue`
- [T-525](T-525-hoi-dap-3-3-trang-thai-cua-cau-tra-loi.md) Hỏi đáp (3/3): trạng thái của câu trả lời: `frontend/src/components/AnswerState.vue`, `frontend/src/__tests__/answer_state.spec.ts`
- [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md) API hội thoại: phiên, gửi câu hỏi SSE, dừng (API-07/08/09): `create_session_api`, `ask_api`, `stop_api`, `to_sse_frame`
- [T-212](T-212-tai-tep-pdf-cho-khung-xem-nguon-api-06.md) Tải tệp PDF cho khung xem nguồn (API-06): `get_file`

## File cần tạo hoặc sửa

- `frontend/e2e/ask.spec.ts`
- `frontend/e2e/source.spec.ts`
- `frontend/e2e/answer_states.spec.ts`

## Các bước

1. Dùng môi trường và hàm `loginAs` của T-606.
2. `ask.spec.ts`: lan@ hỏi "Thời hạn hợp đồng HD-2026-012?" → thấy "Đang tìm trong" trong ≤ 1 giây, câu trả lời có ≥ 1 thẻ trích dẫn.
3. `source.spec.ts`: bấm thẻ trích dẫn → khung xem nguồn mở `text_12p.pdf` ở trang 12 trong ≤ 3 giây; `Esc` đóng, focus về thẻ trích dẫn.
4. `answer_states.spec.ts`: câu hỏi ngoài phạm vi (ngưỡng cấu hình cao) → khối "Không tìm thấy" không có màu lỗi; bấm Dừng khi `AiFake(delay_s=1)` → "Đã dừng"; chặn mạng giữa luồng (`page.route` hủy) → "Mất kết nối – câu trả lời chưa đầy đủ." và [Hỏi lại].
5. Chạy mọi kịch bản ở 1280, 1440, 1920 px trên Chrome và Edge (6 cấu hình).

## Tiêu chí hoàn thành

- [ ] 100% kịch bản của task này đạt ở 6 cấu hình (AC-033).
- [ ] Không dùng dịch vụ AI thật.
- [ ] Báo cáo HTML được lưu cho G1.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| ask.spec | `make e2e-up`; `npx playwright test e2e/ask.spec.ts` | "Đang tìm trong" xuất hiện ≤ 1 giây; ≥ 1 thẻ trích dẫn; đạt 6 cấu hình |
| source.spec | `source.spec.ts` | iframe có `#page=12` trong ≤ 3 giây; `Esc` trả focus về thẻ |
| answer_states.spec | `answer_states.spec.ts` | Ba trạng thái Không tìm thấy, Đã dừng, Mất kết nối hiện đúng nội dung |

## Lệnh kiểm tra

```bash
cd frontend && npx playwright test e2e/ask.spec.ts
cd frontend && npx playwright test e2e/source.spec.ts
cd frontend && npx playwright test e2e/answer_states.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Đo chất lượng câu trả lời thật (T-607).
- Thử tải (T-608).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
