# T-522 · Rà soát khả năng tiếp cận và đáp ứng

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W7–W8 (xem PLAN mục 6) |
| Story | — |
| BR | BR-033 |
| NFR, EC, cổng | UX-03, UX-05, NFR-007 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md), [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md), [T-513](T-513-khung-xem-nguon-s-05.md), [T-525](T-525-hoi-dap-3-3-trang-thai-cua-cau-tra-loi.md), [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) |
| Mở khóa | — |

## Mục tiêu

Kiểm tra và sửa theo WCAG 2.1 AA, bàn phím, độ rộng 1024 – 1920 px.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- Blueprint 3.8.2 (khả năng tiếp cận) và 3.8.3 (đáp ứng theo độ rộng)
- Môi trường E2E của T-606

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04): `useDocumentsStore`, `truncateMiddle`, `formatDateTime`, `DocumentTable.vue`
- [T-512](T-512-hien-thi-tin-nhan-tra-loi-dan-va-the-trich-dan.md) Hiển thị tin nhắn: trả lời dần và thẻ trích dẫn: `AnswerPart`, `splitAnswer`, `CitationChip.vue`, `MessageList.vue`
- [T-513](T-513-khung-xem-nguon-s-05.md) Khung xem nguồn (S-05): `SourceViewer.vue`
- [T-525](T-525-hoi-dap-3-3-trang-thai-cua-cau-tra-loi.md) Hỏi đáp (3/3): trạng thái của câu trả lời: `frontend/src/components/AnswerState.vue`, `frontend/src/__tests__/answer_state.spec.ts`
- [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) Kiểm thử đầu cuối (1/2): môi trường, đăng nhập, tải lên, xóa: `frontend/playwright.config.ts`, `frontend/e2e/fixtures.ts`, `frontend/e2e/login.spec.ts`

## File cần tạo hoặc sửa

- `frontend/e2e/a11y.spec.ts`
- `docs/05-planning/evidence/a11y-report.md`

## Các bước

1. Thêm `@axe-core/playwright` `[Đề xuất]`; `a11y.spec.ts` quét S-01, S-02, S-03 (có câu trả lời), S-04, S-05 mở, S-07, S-08, S-09 trong môi trường E2E; sửa mọi lỗi mức `serious` và `critical`.
2. Kiểm tra bàn phím luồng hỏi đáp: Tab theo thứ tự trực quan; vòng focus luôn thấy; `/` focus ô nhập; `Esc` đóng khung xem nguồn và hộp thoại.
3. Kiểm tra bố cục ở 1024, 1280, 1440, 1920 px: `document.documentElement.scrollWidth <= innerWidth`.
4. Kiểm tra `prefers-reduced-motion: reduce` (Playwright `reducedMotion`) và phóng to 200% ở 1280 px.
5. Viết `a11y-report.md`: kết quả từng trang, lỗi đã sửa, phần chưa kiểm bằng trình đọc màn hình thật.

## Tiêu chí hoàn thành

- [ ] 0 lỗi mức serious hoặc critical khi quét tự động (UX-03).
- [ ] Không cuộn ngang ở 4 độ rộng (UX-05).
- [ ] Báo cáo ghi rõ phần chưa kiểm bằng trình đọc màn hình thật.
- [ ] Luồng hỏi đáp làm được chỉ bằng bàn phím.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| axe scan of main views | Chạy `a11y.spec.ts` trên 8 trang | 0 vi phạm `serious`/`critical` |
| no horizontal scroll | 4 độ rộng × 4 trang chính | `scrollWidth <= innerWidth` |
| keyboard flow | Chỉ dùng phím: `/`, gõ câu hỏi, Enter, Tab tới thẻ trích dẫn, Enter, Esc | Câu trả lời hiện, khung xem nguồn mở rồi đóng, focus về thẻ |
| zoom 200 | 1280 px, zoom 200% | Không cuộn ngang; ô nhập và nút Gửi nhìn thấy |

## Lệnh kiểm tra

```bash
cd frontend && npx playwright test e2e/a11y.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Kiểm tra bằng trình đọc màn hình thật (ghi là chưa làm nếu không có thời gian).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
