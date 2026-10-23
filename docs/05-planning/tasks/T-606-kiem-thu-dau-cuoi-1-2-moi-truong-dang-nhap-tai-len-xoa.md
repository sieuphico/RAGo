# T-606 · Kiểm thử đầu cuối (1/2): môi trường, đăng nhập, tải lên, xóa

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 5 giờ `[Đề xuất]` |
| Tuần dự kiến | W7 (xem PLAN mục 6) |
| Story | — |
| BR | BR-033 |
| NFR, EC, cổng | NFR-007, G1 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md), [T-523](T-523-tai-len-2-2-hang-doi-tien-do-va-thu-lai-tung-tep.md), [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md), [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md), [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md), [T-201](T-201-tai-len-tai-lieu-api-02.md), [T-202](T-202-danh-sach-tai-lieu-api-03.md), [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md), [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md) |
| Mở khóa | [T-522](T-522-ra-soat-kha-nang-tiep-can-va-dap-ung.md), [T-612](T-612-ho-tro-uat.md), [T-615](T-615-kiem-thu-dau-cuoi-2-2-hoi-dap-xem-nguon-cac-trang-thai.md) |

## Mục tiêu

Dựng môi trường E2E với bộ nối giả và viết kịch bản cho đăng nhập, bị từ chối, tải lên hợp lệ và không hợp lệ, xóa tài liệu.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- `IdpFake` và tham số `login_hint` (T-008, T-108)
- Tệp mẫu của T-605
- US-001, US-002, US-010, US-011, US-016 trong USER_STORIES.md

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-505](T-505-kho-trang-thai-dang-nhap-bao-ve-route-s-01-va-s-02.md) Kho trạng thái đăng nhập, bảo vệ route, S-01 và S-02: `useAuthStore`, `installGuards`
- [T-523](T-523-tai-len-2-2-hang-doi-tien-do-va-thu-lai-tung-tep.md) Tải lên (2/2): hàng đợi, tiến độ và thử lại từng tệp: `UploadItem`, `useUpload`
- [T-605](T-605-du-lieu-mau-va-fixture-kiem-thu.md) Dữ liệu mẫu và fixture kiểm thử: `backend/scripts/make_sample_data.py`, `backend/tests/fixtures/README.md`
- [T-108](T-108-dang-nhap-sso-phien-va-get-me-api-01.md) Đăng nhập SSO, phiên và `GET /me` (API-01): `SessionData`, `issue_cookie`, `read_cookie`, `complete_login`
- [T-109](T-109-kiem-tra-quyen-authz-va-chong-csrf.md) Kiểm tra quyền (AuthZ) và chống CSRF: `current_user`, `require_roles`, `CsrfMiddleware`
- [T-201](T-201-tai-len-tai-lieu-api-02.md) Tải lên tài liệu (API-02): `upload_documents`
- [T-202](T-202-danh-sach-tai-lieu-api-03.md) Danh sách tài liệu (API-03): `list_documents_api`
- [T-210](T-210-ingest-dieu-phoi-va-chuyen-trang-thai.md) Ingest: điều phối và chuyển trạng thái: `handle_ingest`
- [T-211](T-211-su-kien-trang-thai-tai-lieu-api-04-sse.md) Sự kiện trạng thái tài liệu (API-04, SSE): `publish_status`, `StatusHub`

## File cần tạo hoặc sửa

- `frontend/playwright.config.ts`
- `frontend/e2e/fixtures.ts`
- `frontend/e2e/login.spec.ts`
- `frontend/e2e/upload.spec.ts`
- `frontend/e2e/delete.spec.ts`
- `deploy/compose.e2e.yml`
- `Makefile`

## Các bước

1. `compose.e2e.yml` + đích `make e2e-up`: CSDL mới, `api`, `worker`, frontend đã build, với `CWD_AI_PROVIDER=fake`, `CWD_OCR_ENGINE=fake`, `CWD_IDP=fake`; nạp allow-list: lan@ (BD_USER), minh@ (TEAM_LEAD), quantri@ (ADMIN), ntt@ (SPONSOR).
2. `fixtures.ts`: `loginAs(page, email)` mở `/auth/login?next=/&login_hint=<email>` (IdpFake dùng `login_hint` làm email).
3. Playwright `[Đề xuất]`: 6 project = Chrome, Edge × 1280, 1440, 1920 px; lưu báo cáo HTML.
4. `login.spec.ts`: lan@ vào được S-03; x@ (ngoài danh sách) thấy "Bạn chưa được cấp quyền".
5. `upload.spec.ts`: minh@ thả `text_1p.pdf` + `a.png` → `a.png` hiện "Chỉ hỗ trợ tệp PDF.", `text_1p.pdf` tới "Sẵn sàng" không tải lại trang; lan@ không thấy vùng tải lên.
6. `delete.spec.ts` (chỉ chạy khi T-510 xong): minh@ xóa tài liệu của mình qua hộp thoại; lan@ không thấy mục Xóa.

## Tiêu chí hoàn thành

- [ ] 100% kịch bản của task này đạt ở 6 cấu hình (AC-033).
- [ ] Không phụ thuộc dịch vụ AI, OCR hay SSO thật.
- [ ] `make e2e-up` dựng môi trường sạch bằng một lệnh.
- [ ] Báo cáo được lưu cho G1.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| login.spec | `make e2e-up`; chạy `npx playwright test e2e/login.spec.ts` | Đạt ở 6 cấu hình |
| upload.spec | Như trên với `upload.spec.ts` | Tài liệu tới "Sẵn sàng" trong ≤ 30 giây; tệp PNG bị từ chối với lý do |
| delete.spec | Như trên với `delete.spec.ts` | Dòng biến mất sau xác nhận; lan@ không có mục Xóa |

## Lệnh kiểm tra

```bash
cd frontend && npx playwright test e2e/login.spec.ts
cd frontend && npx playwright test e2e/upload.spec.ts
cd frontend && npx playwright test e2e/delete.spec.ts
cd frontend && npm run lint && npm run type-check && npm run test && npm run build
```

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Hỏi đáp, xem nguồn, trạng thái câu trả lời (T-615).
- Quét khả năng tiếp cận (T-522).

## Lưu ý

Cần thêm tham số tùy chọn `login_hint` vào `IdpPort.login_url` và cho `/auth/login` chuyển tiếp tham số này (T-008, T-108); bộ nối thật (OIDC) cũng hỗ trợ `login_hint`.

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
