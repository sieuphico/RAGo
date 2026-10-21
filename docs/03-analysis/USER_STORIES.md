# USER STORIES – Chat với tài liệu (MVP)

| Thuộc tính | Giá trị |
|---|---|
| Mã tài liệu | USR-CWD-001 |
| Phiên bản | 0.1 |
| Trạng thái | Draft – chờ PM/PO review (SOP 5.3) |
| Ngày | 2026-10-21 |
| Nguồn | [PRD.md](../requirements/PRD.md) mục 3 (PRD-CWD-001 v0.2), [BRD.md](../requirements/BRD.md) (BRD-CWD-001 v0.5), [Blueprint_UIUX_Design.md](../design/Blueprint_UIUX_Design.md) (màn hình S-xx, EC-xx) |
| Prompt | Không có prompt riêng cho user story. Story nằm ở mục 3 "Functional Requirements & User Stories" của `analysis/PRD_prompt.md` và `analysis/PRD_Prompt_IEEE_standard.md`; quy tắc viết story lấy từ SOP 5.3, bước 4 (`AI_SDLC-SOP.md`) |
| Kiểm tra | `analysis/PRD_IEEE_29148_Checklist.xlsx` |

## 0. Quy ước

- **Dạng story:** "Là *vai trò*, tôi muốn *năng lực*, để *lợi ích*" (bản tiếng Việt của "As a / I want / so that"). Mỗi story một kết quả người dùng nhìn thấy được.
- **Mã story** giữ nguyên `US-xxx` của PRD để không gãy truy vết; tài liệu này không đổi mã.
- **Tiêu chí chấp nhận (AC)** viết dạng Given-When-Then. Nguồn của từng AC:
  - `[PRD]` lấy từ PRD mục 3.
  - `[BRD AC-xxx]` lấy từ tiêu chí nghiệm thu BRD.
  - `[Đề xuất]` là AC mới do người viết đề xuất dựa trên EC-xx của PRD hoặc Blueprint, **chưa được PM/PO xác nhận**. PRD chỉ có AC cho một phần các story, nên các story P1 thường có AC loại này.
- **Ưu tiên:** P0 = bắt buộc để ra mắt, P1 = nên có, P2 = có thì tốt (không có story P2 trong MVP).
- **Màn hình:** mã S-xx của Blueprint mục 3.2.3. Prototype tương ứng nằm ở [UI_UX_design](../04-design/UI_UX_design/README.md).
- Mức độ sẵn sàng cho mỗi story: nhỏ đủ để ước lượng và kiểm thử riêng. Story nào còn hai kết quả trong một câu được ghi ở mục 5.

## 1. Tổng hợp theo Epic

| Epic | Tên | Story | P0 | P1 | BR liên quan |
|---|---|---|---|---|---|
| E1 | Truy cập và xác thực | US-001, 002 | 2 | 0 | BR-016 |
| E2 | Quản lý kho tài liệu | US-010 – 017 | 5 | 3 | BR-001 – 007, BR-027, BR-030 |
| E3 | Hỏi đáp có trích dẫn | US-020 – 027 | 5 | 3 | BR-008 – 015, BR-026 |
| E4 | Định hướng người dùng mới | US-030, 031 | 0 | 2 | BR-020, BR-035 |
| E5 | Tóm tắt, lịch sử, sao chép | US-040 – 042 | 0 | 3 | BR-019, 021, 022 |
| E6 | Phản hồi và đo lường | US-050, 051 | 1 | 1 | BR-023, 024 |
| E7 | Quản trị và tuân thủ | US-060 – 064 | 2 | 3 | BR-007, 016 – 018, 028, 029 |
| | **Tổng** | **30** | **15** | **15** | |

## 2. E1 – Truy cập và xác thực

### US-001 · Đăng nhập bằng tài khoản công ty · P0
`E1` · BR-016 · NFR-008 · S-01 · EC-16
> Là **Lan**, tôi muốn đăng nhập bằng tài khoản công ty, để tôi không phải nhớ thêm mật khẩu.

- **Given** Lan có tài khoản công ty hợp lệ và có tên trong danh sách được cấp quyền, **When** Lan đăng nhập, **Then** Lan vào được màn hình chính trong ≤ 5 giây. `[PRD]`
- **Given** phiên đăng nhập đã hết hạn, **When** Lan thực hiện thao tác bất kỳ, **Then** hệ thống chuyển tới đăng nhập, sau đó đưa Lan về đúng màn hình trước đó; câu hỏi đang gõ dở không bị mất. `[PRD]`

### US-002 · Chặn người dùng ngoài danh sách · P0
`E1` · BR-016 · S-02 · EC-17
> Là **Quản trị viên**, tôi muốn chỉ người có tên trong danh sách được cấp quyền mới truy cập được, để tài liệu nội bộ không bị lộ.

- **Given** người dùng đã xác thực nhưng không có trong danh sách, **When** truy cập ứng dụng, **Then** hiển thị "Bạn chưa được cấp quyền. Liên hệ quản trị viên." và không hiện tên tài liệu hay dữ liệu nào. `[PRD]`
- **Given** người dùng chưa xác thực, **When** gọi trực tiếp bất kỳ đường dẫn hay API nào, **Then** bị từ chối; 0/10 lần thử lấy được dữ liệu. `[PRD, BRD AC-016]`

## 3. E2 – Quản lý kho tài liệu

> Chỉ **Trưởng nhóm BD (Minh)** được tải tài liệu lên (DEC-001, BRU-007). Người dùng BD thường và quản trị viên không thấy vùng tải lên; quản trị viên vẫn xóa được mọi tài liệu.

### US-010 · Tải một tệp PDF lên kho · P0
`E2` · BR-001 · S-04 · EC-03
> Là **Minh**, tôi muốn tải một tệp PDF lên kho chung, để cả đội hỏi được về nội dung của nó.

- **Given** Minh đã đăng nhập, **When** chọn một tệp PDF hợp lệ ≤ 50 MB, **Then** tệp xuất hiện trong danh sách với trạng thái "Đang xử lý" trong ≤ 2 giây sau khi tải lên xong. `[PRD]`
- **Given** tệp đã "Sẵn sàng", **When** bất kỳ người dùng nào hỏi về nội dung tệp, **Then** câu trả lời có thể trích dẫn tệp đó. `[PRD]`
- **Given** mất mạng khi đang tải, **When** quá trình bị gián đoạn, **Then** tệp hiển thị "Tải lên bị gián đoạn" kèm nút [Thử lại]; các tệp khác trong lô không bị ảnh hưởng. `[Đề xuất – EC-03]`

### US-011 · Được báo ngay khi tệp không hợp lệ · P0
`E2` · BR-003, BR-004 · S-04 · EC-08
> Là **Minh**, tôi muốn được báo ngay khi tệp không phải PDF hoặc lớn hơn 50 MB, để tôi biết cần xử lý tệp đó thế nào.

- **Given** Minh chọn `.docx`, `.xlsx` hoặc `.png`, **When** gửi, **Then** tệp bị từ chối ngay ở trình duyệt với "Chỉ hỗ trợ tệp PDF"; kho không thay đổi. `[PRD, BRD AC-003]`
- **Given** một PDF 51 MB, **When** gửi, **Then** bị từ chối trước khi tải với "Tệp vượt quá 50 MB"; một PDF 49 MB được tiếp nhận. `[PRD, BRD AC-004]`
- **Given** một tệp đổi đuôi thành `.pdf` nhưng nội dung không phải PDF, **When** gửi, **Then** máy chủ từ chối và tệp có trạng thái "Thất bại – tệp không phải PDF hợp lệ". `[PRD]`

### US-012 · Xem trạng thái xử lý từng tệp · P0
`E2` · BR-005 · S-04 · EC-02, EC-09
> Là **Minh**, tôi muốn thấy trạng thái xử lý của từng tệp (Đang xử lý / Sẵn sàng / Thất bại kèm lý do), để tôi biết khi nào đội có thể hỏi.

- **Given** một tệp đang xử lý, **When** Minh mở danh sách, **Then** tệp hiển thị "Đang xử lý" và tự cập nhật sang trạng thái mới mà không cần tải lại trang. `[PRD]`
- **Given** một PDF bị hỏng hoặc có mật khẩu, **When** xử lý thất bại, **Then** trạng thái là "Thất bại" kèm lý do cụ thể ("Tệp bị hỏng" hoặc "Tệp có mật khẩu"). `[PRD, BRD AC-005]`

### US-013 · Tải lên PDF ảnh quét và được báo rõ khi không đọc được · P0
`E2` · BR-027, BR-030 · NFR-002, NFR-011 · S-04 · EC-09, EC-20
> Là **Minh**, tôi muốn tải lên được cả PDF dạng ảnh quét và hỏi đáp về nội dung của nó, để không phải tìm bản có sẵn văn bản; nếu hệ thống không đọc được thì tôi được báo rõ.

- **Given** một PDF không có lớp văn bản, **When** hệ thống bắt đầu xử lý, **Then** trạng thái là "Đang nhận dạng ký tự (OCR)" kèm "Tài liệu dạng ảnh quét cần thêm thời gian xử lý". `[PRD]`
- **Given** OCR đạt ngưỡng chất lượng, **When** xong, **Then** trạng thái là "Sẵn sàng"; độ chính xác ký tự ≥ 95% trên bộ mẫu `[Đề xuất]`. `[PRD, BRD AC-027]`
- **Given** bản quét mờ, nghiêng hoặc không đạt ngưỡng, **When** xong, **Then** trạng thái là "Thất bại – Không đọc được nội dung", tệp không bao giờ xuất hiện trong trích dẫn và có nút [Xóa]. `[PRD, BRD AC-030]`

### US-014 · Kéo thả tối đa 10 tệp một lần · P1
`E2` · BR-002 · S-04 · EC-08
> Là **Minh**, tôi muốn kéo thả tối đa 10 tệp PDF trong một lần, để không phải tải từng tệp.

- **Given** Minh chọn 10 tệp PDF hợp lệ trong một thao tác, **When** gửi, **Then** cả 10 tệp được tiếp nhận, mỗi tệp có trạng thái riêng, không cần gửi lại. `[BRD AC-002]`
- **Given** Minh chọn 11 tệp, **When** gửi, **Then** hiển thị "Chỉ tải tối đa 10 tệp mỗi lần" và các tệp hợp lệ trong giới hạn vẫn được tải. `[Đề xuất – EC-08]`

### US-015 · Xem danh sách tài liệu trong kho · P0
`E2` · BR-006 · S-04 · EC-01
> Là **Lan**, tôi muốn xem danh sách tài liệu trong kho (tên, người tải lên, thời điểm, số trang), để biết câu trả lời đang dựa trên những tài liệu nào.

- **Given** kho có 3 tài liệu, **When** Lan mở danh sách, **Then** thấy đủ 3 dòng với tên tệp, người tải lên, thời điểm, số trang và trạng thái. `[PRD, BRD AC-006]`
- **Given** kho có hơn 50 tài liệu, **When** Lan gõ vào ô tìm kiếm, **Then** danh sách lọc theo tên tệp ngay khi gõ. `[PRD]`
- **Given** kho trống, **When** Lan mở danh sách, **Then** hiển thị "Chưa có tài liệu." `[Đề xuất – Blueprint 3.2.4]`

### US-016 · Xóa tài liệu do mình tải lên · P1
`E2` · BR-007 · S-04 · EC-14, EC-18
> Là **Minh**, tôi muốn xóa tài liệu do tôi tải lên, để đội không nhận câu trả lời từ tài liệu lỗi thời.

- **Given** Minh là người tải lên tài liệu X, **When** xóa X và xác nhận, **Then** X biến mất khỏi danh sách, mọi câu hỏi sau đó không trích dẫn X, dữ liệu xử lý của X bị xóa trong ≤ 24 giờ. `[PRD, BRD AC-007, AC-029]`
- **Given** Lan không phải người tải lên X và không phải quản trị viên, **When** xem X, **Then** Lan không thấy nút xóa. `[PRD, BRD AC-007]`
- **Given** hai người cùng xóa một tài liệu, **When** người thứ hai xác nhận, **Then** nhận "Tài liệu đã được xóa trước đó" và không báo lỗi. `[Đề xuất – EC-18]`

### US-017 · Được cảnh báo khi tải tệp trùng · P1
`E2` · BR-001 · S-04 · EC-10
> Là **Minh**, tôi muốn được cảnh báo khi tải lên một tệp trùng với tệp đã có trong kho, để kho không bị trùng lặp.

- **Given** tệp cùng tên và cùng kích thước đã có trong kho, **When** Minh chọn tải lên, **Then** hiện hộp thoại "Tài liệu này có thể đã có trong kho" với [Vẫn tải lên] và [Hủy]. `[PRD – PQ-001, EC-10]`
- **Given** hộp thoại đang mở, **When** Minh chọn [Hủy], **Then** kho không thay đổi; chọn [Vẫn tải lên] thì tệp được tải như tệp mới. `[Đề xuất]`

## 4. E3 – Hỏi đáp có trích dẫn

### US-020 · Đặt câu hỏi và nhận câu trả lời từ tài liệu · P0
`E3` · BR-008, BR-013 · NFR-001, NFR-003 · S-03 · EC-04 – EC-07, EC-11
> Là **Lan**, tôi muốn đặt câu hỏi bằng tiếng Việt hoặc tiếng Anh và nhận câu trả lời từ các tài liệu trong kho, để không phải mở từng file.

- **Given** kho có ≥ 1 tài liệu "Sẵn sàng", **When** Lan hỏi bằng tiếng Việt và câu trả lời nằm trong một tài liệu, **Then** câu trả lời lấy nội dung từ tài liệu đó và kèm ≥ 1 trích dẫn. `[PRD]`
- **Given** kho có ≥ 200 tài liệu, **When** chạy toàn bộ bộ câu hỏi chuẩn, **Then** ≥ 90% câu hỏi hiển thị đầy đủ trong ≤ 15 giây. `[PRD, BRD AC-013]`
- **Given** ô nhập trống hoặc chỉ có khoảng trắng, **When** Lan nhấn Enter, **Then** không gửi và nút Gửi bị vô hiệu. `[PRD]`
- **Given** câu hỏi dài hơn 2.000 ký tự, **When** Lan nhập, **Then** bộ đếm chuyển màu cảnh báo, nút Gửi bị vô hiệu. `[Đề xuất – EC-11]`
- **Given** dịch vụ AI lỗi, **When** Lan gửi, **Then** hiện "Dịch vụ hỏi đáp tạm thời gián đoạn. Vui lòng thử lại sau ít phút.", không hiện mã lỗi và câu hỏi được giữ lại. `[Đề xuất – EC-07]`
- **Given** mất mạng khi đang nhận câu trả lời, **When** kết nối đứt, **Then** phần đã nhận được giữ kèm "Mất kết nối – câu trả lời chưa đầy đủ" và nút [Hỏi lại]. `[Đề xuất – EC-04]`

### US-021 · Câu trả lời tổng hợp từ nhiều tài liệu · P0
`E3` · BR-009 · S-03
> Là **Lan**, tôi muốn câu trả lời tổng hợp thông tin từ nhiều tài liệu, để không phải tự ghép thông tin.

- **Given** một câu hỏi chuẩn cần thông tin từ tài liệu A và B, **When** Lan hỏi, **Then** câu trả lời chứa thông tin từ cả A và B kèm trích dẫn cả hai; đạt ở ≥ 7/10 câu hỏi đa tài liệu. `[PRD, BRD AC-009]`

### US-022 · Trích dẫn tên tài liệu và số trang, mở đúng trang · P0
`E3` · BR-010 · S-03, S-05
> Là **Lan**, tôi muốn mỗi câu trả lời có trích dẫn (tên tài liệu và số trang), và bấm vào trích dẫn thì mở đúng trang đó, để tôi kiểm chứng trong vài giây.

- **Given** một câu trả lời (không phải "không tìm thấy"), **When** hiển thị xong, **Then** mỗi ý dựa trên tài liệu có ≥ 1 thẻ dạng `[Tên tài liệu – tr. N]`. `[PRD, BRD AC-010]`
- **Given** Lan bấm một thẻ trích dẫn, **When** khung xem PDF mở, **Then** hiện đúng tài liệu ở đúng trang N trong ≤ 3 giây. `[PRD]`
- **Given** người chấm mở trang được trích dẫn, **When** đối chiếu, **Then** thông tin có ở trang đó với ≥ 90% trích dẫn. `[PRD, BRD AC-010]`
- **Given** tài liệu được trích dẫn đã bị xóa, **When** Lan bấm thẻ, **Then** thẻ hiển thị "Tài liệu đã bị xóa" và không mở được. `[Đề xuất – EC-14]`

### US-023 · Được báo rõ khi không tìm thấy thông tin · P0
`E3` · BR-011 · S-03 · EC-01, EC-13
> Là **Lan**, tôi muốn được báo rõ "Không tìm thấy thông tin trong tài liệu" khi kho không có câu trả lời, để không dùng nhầm thông tin bịa.

- **Given** một câu hỏi về nội dung không có trong kho, **When** Lan hỏi, **Then** hiện "Không tìm thấy thông tin này trong các tài liệu hiện có" và không đưa dữ kiện nào; đạt ở ≥ 9/10 câu ngoài phạm vi. `[PRD, BRD AC-011]`
- **Given** kho không có tài liệu "Sẵn sàng", **When** Lan hỏi, **Then** hiện "Kho chưa có tài liệu sẵn sàng", gợi ý tải tài liệu lên và không gọi dịch vụ AI. `[PRD]`
- **Given** trạng thái "không tìm thấy", **When** hiển thị, **Then** dùng giao diện trung tính, không dùng màu báo lỗi, kèm gợi ý hành động. `[Đề xuất – Blueprint DD-03]`

### US-024 · Nhận câu trả lời bằng ngôn ngữ đã hỏi · P1
`E3` · BR-026 · S-03 · EC-12
> Là **Lan**, tôi muốn nhận câu trả lời bằng ngôn ngữ tôi đã hỏi, để không phải dịch lại.

- **Given** 10 câu hỏi tiếng Việt và 10 câu hỏi tiếng Anh, **When** hỏi, **Then** ≥ 19/20 câu trả lời dùng đúng ngôn ngữ của câu hỏi. `[BRD AC-026]`
- **Given** câu hỏi bằng ngôn ngữ khác Việt và Anh, **When** chất lượng không đảm bảo, **Then** trả lời tiếng Việt kèm "Hiện chỉ hỗ trợ tốt tiếng Việt và tiếng Anh". `[Đề xuất – EC-12]`

### US-025 · Hỏi câu nối tiếp · P1
`E3` · BR-014 · S-03
> Là **Lan**, tôi muốn hỏi câu nối tiếp mà không phải nhắc lại ngữ cảnh, để tra cứu tự nhiên như hỏi đồng nghiệp.

- **Given** Lan hỏi "Hợp đồng với công ty X có giá trị bao nhiêu?" rồi "Thời hạn của nó?", **When** gửi câu thứ hai, **Then** câu trả lời nói về thời hạn hợp đồng với công ty X; đạt ở ≥ 8/10 cặp câu hỏi. `[PRD, BRD AC-014]`

### US-026 · Giới hạn câu hỏi vào một số tài liệu · P1
`E3` · BR-015 · S-03 · EC-15
> Là **Lan**, tôi muốn giới hạn câu hỏi vào một số tài liệu tôi chọn, để câu trả lời không lẫn thông tin từ tài liệu khác.

- **Given** Lan giới hạn phạm vi vào tài liệu A, **When** hỏi câu có thông tin ở cả A và B, **Then** câu trả lời chỉ trích dẫn A. `[BRD AC-015]`
- **Given** phạm vi đã chọn chứa tài liệu vừa bị xóa, **When** Lan gửi câu hỏi, **Then** tài liệu đó bị loại khỏi phạm vi kèm thông báo; nếu phạm vi trống thì về "Tất cả tài liệu". `[Đề xuất – EC-15]`

### US-027 · Thấy câu trả lời xuất hiện dần và có thể dừng · P0
`E3` · BR-013 · NFR-001 · S-03 · EC-06
> Là **Lan**, tôi muốn thấy câu trả lời xuất hiện dần trong khi hệ thống đang soạn, để không phải nhìn màn hình trống.

- **Given** Lan đã gửi câu hỏi, **When** hệ thống bắt đầu xử lý, **Then** trong ≤ 1 giây hiện "Đang tìm trong N tài liệu…" và văn bản bắt đầu xuất hiện dần. `[PRD]`
- **Given** câu trả lời đang được tạo, **When** Lan bấm "Dừng", **Then** việc tạo dừng trong ≤ 1 giây, phần đã hiển thị được giữ kèm nhãn "Đã dừng". `[PRD]`
- **Given** phản hồi mất hơn 15 giây, **When** vẫn chưa xong, **Then** hiện "Câu hỏi đang mất nhiều thời gian hơn bình thường…"; sau 60 giây dừng và báo "Không thể trả lời lúc này" kèm [Thử lại]. `[Đề xuất – EC-06]`

## 5. E4 – Định hướng người dùng mới

### US-030 · Thấy kho có gì và cách đặt câu hỏi ở lần đầu · P1
`E4` · BR-035 · S-03 · EC-01, EC-02
> Là **Lan** lần đầu dùng, tôi muốn thấy kho đang có bao nhiêu tài liệu và cách đặt câu hỏi tốt, để bắt đầu hỏi ngay.

- **Given** Lan đăng nhập lần đầu, **When** vào màn hình hỏi đáp, **Then** thấy số tài liệu sẵn sàng trong kho và ít nhất 3 câu hỏi mẫu. `[BRD AC-035]`
- **Given** kho có tài liệu đang xử lý, **When** Lan mở màn hình, **Then** hiện "N tài liệu đang được xử lý, chưa dùng để trả lời" và ô hỏi vẫn dùng được. `[Đề xuất – EC-02]`

### US-031 · Bấm một lần để hỏi câu hỏi mẫu · P1
`E4` · BR-020 · S-03
> Là **Lan**, tôi muốn thấy ≥ 3 câu hỏi mẫu do hệ thống gợi ý từ nội dung tài liệu trong kho và bấm một lần để hỏi, để biết có thể hỏi gì mà không phải nghĩ câu hỏi.

- **Given** kho có ≥ 1 tài liệu "Sẵn sàng", **When** Lan mở màn hình hỏi đáp trống, **Then** thấy ≥ 3 gợi ý; bấm một gợi ý thì câu hỏi được gửi ngay. `[PRD]`
- **Given** một gợi ý được hỏi, **When** nhận câu trả lời, **Then** đó là câu trả lời có trích dẫn, không phải "không tìm thấy" (≥ 3/3 gợi ý đạt). `[PRD, BRD AC-020]`
- **Given** kho không có tài liệu sẵn sàng, **When** Lan mở màn hình, **Then** không hiện gợi ý. `[PRD]`

## 6. E5 – Tóm tắt, lịch sử, sao chép

### US-040 · Tóm tắt một tài liệu · P1
`E5` · BR-019 · S-04 · S-03
> Là **Lan**, tôi muốn yêu cầu bản tóm tắt một tài liệu, để nắm nhanh tài liệu mới trước khi họp.

- **Given** 5 tài liệu mẫu, **When** Lan yêu cầu tóm tắt từng tài liệu, **Then** người am hiểu đánh giá ≥ 4/5 bản tóm tắt không chứa thông tin sai so với tài liệu gốc. `[BRD AC-019]`
- **Given** một bản tóm tắt, **When** hiển thị, **Then** có trích dẫn số trang như câu trả lời thông thường. `[PRD]`

### US-041 · Xem lại phiên hội thoại 90 ngày · P1
`E5` · BR-021 · S-06 · EC-14
> Là **Lan**, tôi muốn xem lại các phiên hội thoại trong 90 ngày gần nhất, để dùng lại kết quả đã tra cứu.

- **Given** Lan đăng xuất rồi đăng nhập lại, **When** mở lịch sử, **Then** mở được phiên trước với đủ câu hỏi, câu trả lời và trích dẫn; phiên cũ hơn 90 ngày không còn hiển thị. `[BRD AC-021]`
- **Given** một phiên cũ trích dẫn tài liệu đã bị xóa, **When** Lan mở phiên, **Then** thẻ trích dẫn hiện "Tài liệu đã bị xóa" và không mở được. `[PRD]`
- **Given** người dùng khác, **When** mở lịch sử, **Then** chỉ thấy phiên của chính mình. `[Đề xuất – OQ-013, BRU-008]`

### US-042 · Sao chép câu trả lời kèm nguồn · P1
`E5` · BR-022 · S-03
> Là **Lan**, tôi muốn sao chép câu trả lời kèm danh sách nguồn chỉ bằng một lần bấm, để dán vào email hoặc báo cáo.

- **Given** một câu trả lời có trích dẫn, **When** Lan bấm "Sao chép" và dán vào trình soạn thảo, **Then** nội dung chứa đầy đủ câu trả lời và các trích dẫn. `[BRD AC-022]`
- **Given** nội dung sao chép, **When** kiểm tra định dạng, **Then** là văn bản thuần, nguồn ghi dạng `Nguồn: [1] Tên tài liệu, tr. N`. `[PRD]`

## 7. E6 – Phản hồi và đo lường

### US-050 · Đánh giá 👍/👎 câu trả lời · P1
`E6` · BR-023 · S-03
> Là **Lan**, tôi muốn đánh giá 👍/👎 từng câu trả lời (kèm lý do tùy chọn khi chọn 👎), để đội sản phẩm cải thiện chất lượng.

- **Given** một câu trả lời, **When** Lan gửi đánh giá, **Then** đánh giá xuất hiện trong số liệu sử dụng. `[BRD AC-023]`
- **Given** Lan chọn 👎, **When** hộp thoại lý do mở, **Then** có thể chọn một lý do hoặc bỏ qua; cả hai cách đều ghi nhận 👎. `[Đề xuất – Blueprint 4.5]`

### US-051 · Bảng số liệu hàng tuần · P0
`E6` · BR-024 · S-09
> Là **Nhà tài trợ**, tôi muốn có bảng số liệu hàng tuần (WAU, số câu hỏi, thời gian phản hồi p50/p90, tỷ lệ 👍), để đánh giá OKR mà không cần nhờ đội kỹ thuật.

- **Given** thí điểm đã chạy ≥ 1 tuần, **When** nhà tài trợ mở bảng số liệu, **Then** thấy WAU, tổng số câu hỏi, p50/p90, tỷ lệ 👍 theo tuần, cập nhật trong vòng 24 giờ. `[PRD, BRD AC-024]`
- **Given** bảng số liệu, **When** kiểm tra nội dung, **Then** không có văn bản câu hỏi hay câu trả lời nào. `[PRD]`

## 8. E7 – Quản trị và tuân thủ

### US-060 · Nội dung chỉ được xử lý bởi dịch vụ đã phê duyệt · P0
`E7` · BR-017, BR-028 · NFR-008 · (không có màn hình)
> Là **Bảo mật thông tin**, tôi muốn nội dung tài liệu chỉ được xử lý bởi dịch vụ đã được phê duyệt và không bị dùng để huấn luyện mô hình, để tuân thủ chính sách dữ liệu.

- **Given** kiến trúc và hợp đồng dịch vụ AI đã chọn, **When** Bảo mật thông tin/Pháp chế review, **Then** có văn bản phê duyệt xác nhận CON-005 (a), (b), (c) được đáp ứng. `[PRD, BRD AC-017, AC-028]`
- **Given** hệ thống đang chạy, **When** kiểm tra cấu hình, **Then** chỉ các dịch vụ bên ngoài nằm trong danh sách được phê duyệt nhận được nội dung tài liệu. `[PRD]`

### US-061 · Thêm và gỡ người dùng được cấp quyền · P0
`E7` · BR-016 · S-07 · EC-17
> Là **Quản trị viên**, tôi muốn thêm/xóa người khỏi danh sách được cấp quyền, để kiểm soát ai dùng được công cụ.

- **Given** quản trị viên thêm email X, **When** X đăng nhập, **Then** X truy cập được trong ≤ 1 phút sau khi được thêm. `[PRD]`
- **Given** quản trị viên xóa X, **When** X thao tác tiếp, **Then** X bị chặn ở yêu cầu kế tiếp kể cả khi phiên còn hiệu lực, và thấy "Quyền truy cập của bạn đã bị thu hồi". `[PRD, Đề xuất – EC-17]`

### US-062 · Xóa bất kỳ tài liệu nào · P1
`E7` · BR-007 · S-04 · BRU-005
> Là **Quản trị viên**, tôi muốn xóa bất kỳ tài liệu nào, để xử lý tài liệu tải nhầm.

- **Given** tài liệu do Minh tải lên, **When** quản trị viên xóa và xác nhận, **Then** tài liệu biến mất khỏi danh sách và không còn được trích dẫn. `[Đề xuất – BRU-005]`
- **Given** quản trị viên xóa tài liệu, **When** hoàn tất, **Then** hành động được ghi vào nhật ký (US-063). `[Đề xuất]`

### US-063 · Xem nhật ký tải lên và xóa · P1
`E7` · BR-018 · S-08
> Là **Quản trị viên**, tôi muốn xem nhật ký tải lên/xóa tài liệu (ai, khi nào, tài liệu nào), để truy vết khi có sự cố.

- **Given** sau 3 lần tải lên và 1 lần xóa, **When** quản trị viên mở nhật ký, **Then** có đúng 4 bản ghi với đủ người thực hiện, thao tác, tài liệu, thời điểm. `[BRD AC-018]`

### US-064 · Xóa dữ liệu đã xử lý trong 24 giờ · P1
`E7` · BR-029 · (không có màn hình riêng; thông báo ở hộp thoại xóa)
> Là **Bảo mật thông tin**, tôi muốn dữ liệu xử lý của tài liệu bị xóa được xóa hoàn toàn trong ≤ 24 giờ, để thực thi chính sách lưu giữ.

- **Given** tài liệu X đã bị xóa, **When** 24 giờ trôi qua, **Then** kho dữ liệu không còn dữ liệu đã xử lý nào gắn với X; đội kỹ thuật cung cấp bằng chứng kiểm tra. `[BRD AC-029]`
- **Given** bản sao lưu theo chu kỳ, **When** kiểm tra, **Then** ngoại lệ sao lưu đã được ghi nhận và Bảo mật thông tin phê duyệt (SAD Q-A3, BRD OQ-013). `[Đề xuất]`

## 9. Truy vết màn hình → story (SOP 5.4, bước 7)

| Màn hình | Story | Epic | BR | NFR / EC |
|---|---|---|---|---|
| S-01 Đăng nhập | US-001 | E1 | BR-016 | EC-16 |
| S-02 Không có quyền | US-002, US-061 | E1, E7 | BR-016 | EC-17 |
| S-03 Hỏi đáp | US-020 – 027, US-030, 031, 040, 042, 050 | E3, E4, E5, E6 | BR-008 – 015, 019 – 023, 026, 035 | NFR-001, 003 · EC-01 – 07, 11 – 15 |
| S-04 Kho tài liệu | US-010 – 017, US-040, US-062 | E2, E5, E7 | BR-001 – 007, 019, 027, 030 | NFR-002, 004, 011 · EC-02, 03, 08 – 10, 18, 20 |
| S-05 Khung xem nguồn | US-022 | E3 | BR-010 | EC-14, 19 |
| S-06 Lịch sử | US-041 | E5 | BR-021 | EC-14 |
| S-07 Quản lý người dùng | US-061 | E7 | BR-016 | EC-17 |
| S-08 Nhật ký | US-063, US-062 | E7 | BR-018 | – |
| S-09 Số liệu | US-051 | E6 | BR-024 | – |

**Story không có màn hình riêng:** US-060 (phê duyệt bảo mật), US-064 (xóa dữ liệu nền; chỉ có thông báo trong hộp thoại xóa), US-024 (hành vi của máy chủ, giao diện chỉ hiển thị). Đây là hành vi dự kiến, không phải thiếu thiết kế.
**Màn hình không có story:** không có.

## 10. Ghi chú và điểm cần PM/PO xác nhận

1. **BR-006 vẫn là Should trong BRD** nhưng US-015 là P0 trong PRD. Cần BA cập nhật BR-006 hoặc PM/PO xác nhận US-015 là P0.
2. **Story còn ghép hai kết quả:** US-013 (tải bản quét và báo khi không đọc được), US-022 (có trích dẫn và mở đúng trang), US-020 (nhận câu trả lời và xử lý lỗi qua nhiều EC). Tôi giữ nguyên để không đổi mã PRD; nếu cần tách, nên tách thành US-013a/b và US-022a/b trước khi lập kế hoạch (SOP 5.5).
3. **AC `[Đề xuất]`** (21 trên 72 AC) chưa được PM/PO duyệt. Các AC này đến từ EC-xx của PRD và Blueprint; nên rà soát cùng PRD v0.3.
4. Story dùng bộ câu hỏi chuẩn (US-020, 021, 022, 023, 025, 031) phụ thuộc DEP-003 (bộ tài liệu mẫu và bộ câu hỏi chuẩn, hạn 2026-11-27). Chưa có bộ này nên chưa kiểm chứng được các ngưỡng phần trăm.
5. US-050 và US-051 liên quan đến telemetry chỉ siêu dữ liệu (PRD mục 5.2): không ghi nội dung câu hỏi hay câu trả lời vào hệ thống phân tích.
