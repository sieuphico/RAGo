# Prototype UI/UX – Chat với tài liệu (MVP)

| Thuộc tính | Giá trị |
|---|---|
| Nguồn | [Blueprint_UIUX_Design.md](../../design/Blueprint_UIUX_Design.md) (SDD-UIUX-CWD-001 v0.2), persona lấy từ [PRD.md](../../requirements/PRD.md) mục 2.1 (Blueprint không có mục persona riêng) |
| Dạng sản phẩm | Prototype HTML/CSS/JS thuần, bấm được, 9 màn hình, không cần máy chủ |
| Cách xem | Mở [index.html](index.html) bằng Chrome hoặc Edge |
| Trạng thái | Bản dựng để review, chưa phải thiết kế hình ảnh cuối cùng của Designer, chưa kiểm thử với người dùng thật |

**Dữ liệu và câu trả lời trong prototype là dữ liệu minh họa.** Không có máy chủ, AI hay PDF thật phía sau; khung xem nguồn vẽ một trang giả.

## 1. Cách dùng

- Chọn **vai trò** (Người dùng BD, Trưởng nhóm BD, Quản trị viên, Nhà tài trợ) ở [index.html](index.html) hoặc ở thanh **Demo** phía trên mỗi trang. Điều hướng, vùng tải lên và nút Xóa thay đổi theo Blueprint 3.2.2. Vai trò không được phép xem trang sẽ chuyển tới S-02.
- Thanh **Demo** (không thuộc sản phẩm) chuyển nhanh giữa 5 trạng thái bắt buộc của mỗi màn hình (đang tải, trống, có dữ liệu, lỗi, hạn chế quyền) và các tình huống lỗi EC-xx ở màn hình Hỏi đáp.
- Phím tắt: `Enter` gửi, `Shift+Enter` xuống dòng, `Esc` đóng khung xem nguồn hoặc hộp thoại, `/` đưa con trỏ vào ô nhập.
- Bản nháp câu hỏi và vai trò đang chọn chỉ lưu trong bộ nhớ phiên của trình duyệt (DD-07); đóng tab là mất.

## 2. Bản đồ màn hình

| Màn hình | File | Blueprint | Story | Ghi chú |
|---|---|---|---|---|
| S-01 Đăng nhập | [login.html](login.html) | 4.7 | US-001 | Không có ô mật khẩu (DEC-011); EC-16 hết phiên |
| S-02 Không có quyền | [denied.html](denied.html) | 4.6 | US-002 | Không hiện tên tài liệu; EC-17 qua `?reason=revoked` |
| S-03, S-05, S-06 Hỏi đáp, khung xem nguồn, lịch sử | [chat.html](chat.html) | 4.1 – 4.3, 4.8, 4.9 | US-020 – US-027, US-031, US-041, US-042, US-050 | Trả lời dần, trích dẫn, phạm vi tài liệu |
| S-04 Kho tài liệu | [library.html](library.html) | 4.4, 4.5 | US-010 – US-017 | Tải lên chỉ Trưởng nhóm BD; xóa, tóm tắt, tệp trùng |
| S-07 Quản lý người dùng | [users.html](users.html) | 4.6 | US-061 | Tối đa 20 người dùng (ASM-002) |
| S-08 Nhật ký | [audit.html](audit.html) | 4.10 | US-063 | 4 trường: ai, thao tác, tài liệu, thời điểm |
| S-09 Số liệu | [metrics.html](metrics.html) | 4.6 | US-051 | Biểu đồ SVG thuần, có bảng thay thế |

## 3. Trích xuất từ Blueprint và cách thể hiện

### 3.1 Persona (PRD 2.1, DEC-015)

| Persona | Vai trò | Mục tiêu | Nỗi đau | Việc chính trong prototype |
|---|---|---|---|---|
| Lan (P1) | Chuyên viên BD | Có câu trả lời đúng và biết nó nằm ở trang nào | Mở nhiều file, Ctrl+F không ra; sợ AI bịa | Hỏi đáp, bấm trích dẫn, sao chép, đánh giá |
| Minh (P2) | Trưởng nhóm BD | Kho luôn đúng phiên bản | Không biết đội dùng bản nào | Tải nhiều tệp, theo dõi trạng thái, xóa |
| Quản trị viên (P3) | Đội kỹ thuật | Kiểm soát truy cập, truy vết | – | Danh sách cho phép, nhật ký, xóa mọi tài liệu |
| Nhà tài trợ | Ra quyết định đầu tư | Xem OKR không nhờ đội kỹ thuật | – | Bảng số liệu |

Các persona vẫn là giả thuyết cho tới khi xác minh qua phỏng vấn đội BD (OQ-016).

### 3.2 Yêu cầu UX/UI (Blueprint 2.4, 2.5) và mức kiểm chứng

"Đã thử" nghĩa là tôi chạy kịch bản tự động trên Chrome headless; "Chưa" nghĩa là chưa kiểm chứng được ở prototype này.

| ID | Yêu cầu | Thể hiện | Kiểm chứng |
|---|---|---|---|
| UX-01 | Người mới hỏi được trong ≤ 90 giây | Màn hình chào, 3 gợi ý một lần bấm (CMP-23) | Chưa: cần UAT 5 người (G9) |
| UX-02 | Tải 10 tệp, thấy trạng thái cả 10 trên một màn hình | Bảng tài liệu có huy hiệu từng tệp | Đã thử với 3 tệp (1 hợp lệ, 2 bị từ chối); 10 tệp chưa thử |
| UX-03 | Dùng bằng bàn phím; trình đọc màn hình đọc được | Skip link, `role="log"`, thông báo khi trả lời xong, hộp thoại `<dialog>` | Đã thử Esc và trả focus; phím Enter gửi câu hỏi và sao chép vào clipboard chưa thử bằng script; **chưa** thử bằng trình đọc màn hình thật |
| UX-04 | FCP < 1,5 s, LCP < 2,5 s | Không dùng thư viện, font hay script ngoài | Chưa đo |
| UX-05 | Thích ứng 1024 – 2560 px, không cuộn ngang | Viewer thành lớp phủ dưới 1280 px (EC-19) | Đã chụp ở 1024 và 1440 px, không cuộn ngang ở 1024; 1280 và 1920 chưa chụp |
| UX-06 | 100% màu, cỡ chữ lấy từ token | [assets/tokens.css](assets/tokens.css) | Phần lớn; còn vài giá trị cứng (màu SVG biểu đồ, màu hover nút) |
| UX-07 | Mạng đứt giữ phần đã nhận, "Hỏi lại" 1 lần bấm | Tình huống "Đứt giữa chừng (EC-04)" | Đã thử |
| UX-08 | Phản hồi chờ ≤ 300 ms, nút vô hiệu khi không hợp lệ | "Đang tìm…" hiện ngay; Gửi bị khóa khi trống hoặc quá 2.000 ký tự | Đã thử logic; chưa đo thời gian |
| UX-09 | Tới chức năng chính ≤ 2 lần bấm | Thanh điều hướng 1 lần bấm; trích dẫn → viewer 1 lần bấm | Đã thử |
| UX-10 | Phân biệt "có căn cứ" và "không tìm thấy" | Khung xám trung tính, biểu tượng kính lúp, không dùng đỏ | Chưa: cần UAT |
| UX-11 | Chữ Việt có dấu, ngày `dd/MM/yyyy HH:mm` | Font Segoe UI, hàm định dạng ngày | Đã xem ảnh chụp, không mất dấu |
| UX-12 | Đọc được trên điện thoại, vùng bấm ≥ 44 px | – | Chưa thiết kế và chưa kiểm (< 1024 px chỉ có bố cục co lại) |

Ràng buộc 2.5 đã áp dụng: tương phản tính lại cho các màu thêm vào (đều ≥ 4,5:1 với chữ, ≥ 3:1 với thành phần giao diện), chữ phụ ≥ 14 px, vùng bấm chuột ≥ 32 px, thông báo tự ẩn sau 4 giây (lỗi giữ đến khi đóng), `prefers-reduced-motion`, trạng thái luôn có chữ và biểu tượng.

### 3.3 Mô hình trạng thái UI (Blueprint 3.5)

| Trạng thái | Loại | Giá trị | Lưu ở | Phạm vi |
|---|---|---|---|---|
| Trạng thái tài liệu | Dữ liệu máy chủ (giả) | Uploading, Interrupted, Processing, OcrProcessing, Ready, Failed | Bộ nhớ trang | S-04, phạm vi hỏi ở S-03 |
| Trạng thái câu trả lời | Thành phần | Searching, Streaming, Completed, NotFound, Stopped, Interrupted, Failed | DOM | CMP-06 |
| Trạng thái trang | Trang | Đang tải, Trống, Có dữ liệu, Lỗi, Hạn chế quyền | `body[data-state]` | Mọi màn hình S-03 – S-09 |
| Bản nháp câu hỏi | Toàn cục | Chuỗi chưa gửi | `sessionStorage` | Ứng dụng |
| Vai trò | Toàn cục | bd, tn, qt, ntt | `sessionStorage` (chỉ để demo) | Ứng dụng |

### 3.4 Thành phần (Blueprint 3.1)

| CMP | Nơi cài đặt |
|---|---|
| CMP-01, 02, 03 App Shell, Auth Guard, Top Navigation | [assets/app.js](assets/app.js) (`init`, `renderHeader`) |
| CMP-04 – 08 Conversation Pane, Composer, Message, Answer, Citation | [assets/page-chat.js](assets/page-chat.js) |
| CMP-09 Source Viewer | [assets/page-chat.js](assets/page-chat.js) (`openViewer`) |
| CMP-10, 23 Màn hình chào, gợi ý câu hỏi | [assets/page-chat.js](assets/page-chat.js) (`renderSuggestions`) |
| CMP-11 Scope Picker | [assets/page-chat.js](assets/page-chat.js) (`renderScope`) |
| CMP-12 Answer Actions | [assets/page-chat.js](assets/page-chat.js) (`actionsEl`) |
| CMP-13 History List | [assets/page-chat.js](assets/page-chat.js) (`renderHistory`) |
| CMP-14, 15, 16 Drop Zone, Document Table, Status Badge | [assets/page-library.js](assets/page-library.js), `statusBadge` trong [assets/app.js](assets/app.js) |
| CMP-17, 18 Dialog Host, Toast | [assets/app.js](assets/app.js) (`openDialog`, `confirmDialog`, `toast`) |
| CMP-19, 20 Allow-list, Audit Log | [assets/page-admin.js](assets/page-admin.js) |
| CMP-21 KPI Dashboard | [assets/page-metrics.js](assets/page-metrics.js) |

Không có CMP-22 (Service Layer) thật: prototype không gọi API.

### 3.5 Token

Màu, kiểu chữ, khoảng cách, bo góc, bố cục và chuyển động nằm trong [assets/tokens.css](assets/tokens.css), lấy từ Blueprint 3.6.1 và 3.6.2. Giá trị không có trong Blueprint và là `[Đề xuất]`: màu đường kẻ trang trí `#D1D5DB` (không dùng làm viền điều khiển).

## 4. Kết quả kiểm tra

- 31 kiểm tra tương tác tự động đạt (gửi câu hỏi và trả lời dần, mở trích dẫn, Esc và trả focus, 4 tình huống lỗi, EC-01, EC-05, EC-08, EC-11, phân quyền theo vai trò, xóa có xác nhận mặc định ở "Hủy", thêm người dùng, 1024 px không cuộn ngang); không có lỗi JavaScript.
- Mở trang và chụp ảnh đủ 9 màn hình ở Chrome.
- **Chưa kiểm:** Edge, trình đọc màn hình, đo hiệu năng, điện thoại, UAT với người dùng thật.

## 5. Khác biệt so với Blueprint và điểm cần quyết định

1. **Số lượng tài liệu:** prototype có 8 tài liệu mẫu, Blueprint wireframe ghi 125. Số trong giao diện luôn lấy từ dữ liệu mẫu.
2. **Người tải lên:** wireframe 4.4 ghi "Lan" là người tải `BaoCao_Q3.pdf`, mâu thuẫn DEC-001 (chỉ Trưởng nhóm BD tải lên). Prototype dùng "Minh". Đã sửa wireframe 4.4 trong Blueprint thành "Minh".
3. **Thêm so với Blueprint:** sắp xếp bảng theo tên và thời điểm; hộp thoại thêm và gỡ người dùng; hộp thoại tóm tắt (P1) với nội dung giả; nhãn "Trong ngưỡng" cho chỉ số Không tìm thấy ở S-09.
4. **Chưa có Figma:** prototype này là HTML. File Figma hiện chỉ có wireframe thấp độ trung thực, chưa có khung hình ảnh hoàn chỉnh.
5. **Chưa làm hoặc chưa kiểm:** gợi ý câu hỏi sinh từ tài liệu thật (API-17; prototype dùng danh sách cố định); nút Sao chép đã cài đặt nhưng chưa kiểm; bố cục dưới 1024 px chưa được thiết kế đầy đủ.
