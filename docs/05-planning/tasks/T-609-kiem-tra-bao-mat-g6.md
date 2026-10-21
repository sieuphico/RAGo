# T-609 · Kiểm tra bảo mật (G6)

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư B (front-end chính, vận hành) |
| Ước lượng | 8 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | US-002, US-060, US-061 |
| BR | BR-016, BR-017, BR-028 |
| NFR, EC, cổng | NFR-008, G6 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-308](T-308-api-hoi-thoai-phien-gui-cau-hoi-sse-dung-api-07-08-09.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-613](T-613-dung-moi-truong-staging.md) |
| Mở khóa | [T-612](T-612-ho-tro-uat-va-sua-loi.md) |

## Mục tiêu

Quét OWASP Top 10, kiểm thử phân quyền và các kịch bản prompt injection.

## File cần tạo hoặc sửa

- `backend/tests/security/test_authz_matrix.py`
- `backend/tests/security/test_prompt_injection.py`
- `docs/05-planning/evidence/security-report.md`

## Các bước

1. Chạy công cụ quét phụ thuộc và quét tĩnh mã; sửa mọi mức High và Critical.
2. Ma trận phân quyền tự động: mọi API × mọi vai trò × chưa xác thực; 0/10 lần lấy được dữ liệu trái phép (AC-016).
3. Kiểm thử chèn lệnh: tài liệu chứa "bỏ qua mọi hướng dẫn" không làm đổi hành vi, không lộ dữ liệu, không tạo trích dẫn bịa.
4. Kiểm tra gói tin: không có nội dung tài liệu hay câu hỏi trong telemetry hay nhật ký; yêu cầu ra ngoài chỉ tới đích được duyệt.

## Tiêu chí hoàn thành

- [ ] Không còn lỗ hổng High hoặc Critical (NFR-008, G6).
- [ ] Ma trận phân quyền đạt 100%.
- [ ] Báo cáo nêu rõ những gì chưa kiểm.

## Kiểm thử cần viết

- Ma trận phân quyền
- Prompt injection

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn hoặc thấy yêu cầu mâu thuẫn, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
