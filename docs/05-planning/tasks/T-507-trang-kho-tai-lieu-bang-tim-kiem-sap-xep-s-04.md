# T-507 · Trang Kho tài liệu: bảng, tìm kiếm, sắp xếp (S-04)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W5 (xem PLAN mục 6) |
| Story | US-015 |
| BR | BR-006 |
| NFR, EC, cổng | UX-11, NFR-004 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-202](T-202-danh-sach-tai-lieu-api-03.md), [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md), [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) |
| Mở khóa | [T-508](T-508-tai-len-vung-keo-tha-kiem-tra-phia-trinh-duyet-trang-thai-tu.md), [T-509](T-509-cap-nhat-trang-thai-tai-lieu-theo-thoi-gian-thuc.md), [T-510](T-510-hop-thoai-xoa-va-tep-trung-thao-tac-theo-vai-tro.md), [T-518](T-518-hop-thoai-tom-tat-tai-lieu.md), [T-522](T-522-ra-soat-kha-nang-tiep-can-va-dap-ung.md) |

## Mục tiêu

Hiển thị danh sách tài liệu với 5 trạng thái màn hình (đang tải, trống, dữ liệu, lỗi, hạn chế quyền).

## File cần tạo hoặc sửa

- `frontend/src/views/LibraryView.vue`
- `frontend/src/stores/documents.ts`
- `frontend/src/components/DocumentTable.vue`
- `frontend/src/__tests__/library.spec.ts`

## Các bước

1. Dựng theo prototype `docs/04-design/UI_UX_design/library.html` và Blueprint 4.4.
2. Cột: tên (rút gọn giữa, đầy đủ ở tooltip), trang, người tải, thời điểm `dd/MM/yyyy HH:mm`, trạng thái, thao tác.
3. Tìm theo tên lọc ngay khi gõ; sắp xếp theo tên và thời điểm với `aria-sort`.
4. Trạng thái trống "Chưa có tài liệu.", lỗi "Không tải được danh sách" kèm [Thử lại], khung xương 5 dòng.

## Tiêu chí hoàn thành

- [ ] Kho có 3 tài liệu hiển thị đủ 3 dòng với đúng trường (AC-006).
- [ ] Có đủ 5 trạng thái màn hình.
- [ ] Người dùng BD thấy dòng "Chỉ Trưởng nhóm BD tải được tài liệu lên."

## Kiểm thử cần viết

- `renders_rows_with_fields`
- `search_filters_by_name`
- `shows_empty_and_error_states`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
