# T-520 · Trang Số liệu (S-09)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 5 Giao diện |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 7 giờ `[Đề xuất]` |
| Tuần dự kiến | W6–W7 (xem PLAN mục 6) |
| Story | US-051 |
| BR | BR-024 |
| NFR, EC, cổng | UX-03 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-312](T-312-so-lieu-hang-tuan-api-13.md), [T-506](T-506-thanh-phan-dung-chung-thong-bao-hop-thoai-khung-xuong-huy-hi.md) |
| Mở khóa | — |

## Mục tiêu

Các ô chỉ số, biểu đồ theo tuần bằng SVG thuần và bảng thay thế.

## File cần tạo hoặc sửa

- `frontend/src/views/MetricsView.vue`
- `frontend/src/components/WeeklyChart.vue`
- `frontend/src/__tests__/metrics.spec.ts`

## Các bước

1. Dựng theo prototype `docs/04-design/UI_UX_design/metrics.html`: WAU, câu hỏi, p50/p90, 👍, "Không tìm thấy", chọn tuần, thời điểm cập nhật.
2. Biểu đồ không dùng thư viện ngoài; có bảng "Xem dạng bảng"; không chỉ dùng màu để phân biệt (cột và đường có nhãn, điểm có hình).
3. Mỗi ô có trạng thái chữ và biểu tượng ("Đạt mục tiêu", "Cảnh báo") đối chiếu mục tiêu OKR.
4. Chỉ ADMIN và SPONSOR vào được; trạng thái trống "Chưa có dữ liệu. Số liệu xuất hiện sau tuần sử dụng đầu tiên."

## Tiêu chí hoàn thành

- [ ] Hiển thị đủ chỉ số của AC-024.
- [ ] Không có văn bản câu hỏi hay câu trả lời nào.
- [ ] Biểu đồ có bảng thay thế truy cập được.

## Kiểm thử cần viết

- `renders_all_kpis`
- `chart_has_table_fallback`
- `metrics_roles_guard`

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
