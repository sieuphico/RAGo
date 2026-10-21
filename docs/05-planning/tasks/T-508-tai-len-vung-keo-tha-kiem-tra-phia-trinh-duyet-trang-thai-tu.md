# T-508 · Tải lên: vùng kéo thả, kiểm tra phía trình duyệt, trạng thái từng tệp

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 10 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-010, US-011, US-014 |
| BR | BR-001, BR-002, BR-003, BR-004 |
| NFR, EC, cổng | EC-03, EC-08, UX-02 |
| Quyết định kiến trúc | DD-05 |
| Phụ thuộc | [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-507](T-507-trang-kho-tai-lieu-bang-tim-kiem-sap-xep-s-04.md) |
| Mở khóa | [T-606](T-606-kiem-thu-dau-cuoi-e2e-luong-p0.md) |

## Mục tiêu

Chỉ Trưởng nhóm BD thấy vùng tải lên; kiểm tra từng tệp trước khi gửi; tiến độ và thử lại từng tệp.

## File cần tạo hoặc sửa

- `frontend/src/components/DropZone.vue`
- `frontend/src/composables/useUpload.ts`
- `frontend/src/__tests__/upload.spec.ts`

## Các bước

1. Kiểm tra: đuôi `.pdf`, ≤ 50 MB, ≤ 10 tệp; mỗi tệp lỗi hiện lý do riêng ("Chỉ hỗ trợ tệp PDF.", "Tệp vượt quá 50 MB.", "Chỉ tải tối đa 10 tệp mỗi lần."); tệp hợp lệ vẫn được tải.
2. Gọi API-02, hiển thị tiến độ phần trăm và trạng thái `Đang tải lên` từng tệp.
3. Mất mạng: `Tải lên bị gián đoạn` kèm nút [Thử lại] cho từng tệp, các tệp khác không ảnh hưởng (EC-03).
4. Vùng kéo thả ẩn với vai trò khác TEAM_LEAD.

## Tiêu chí hoàn thành

- [ ] Chọn 10 tệp hợp lệ trong một thao tác, cả 10 được tiếp nhận (AC-002).
- [ ] Tệp không phải PDF và tệp quá 50 MB bị chặn ngay ở trình duyệt, kho không đổi.
- [ ] Một tệp lỗi mạng không chặn các tệp còn lại.

## Kiểm thử cần viết

- `rejects_non_pdf_and_oversize`
- `keeps_valid_files_in_batch`
- `retry_single_failed_file`
- `hidden_for_non_team_lead`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
