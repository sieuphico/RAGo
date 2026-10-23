# T-612 · Hỗ trợ UAT

| Thuộc tính | Giá trị |
|---|---|
| Pha | 6 Vận hành, kiểm thử, ra mắt |
| Ưu tiên | P0 |
| Người làm | Kỹ sư A (back-end chính) |
| Ước lượng | 6 giờ `[Đề xuất]` |
| Tuần dự kiến | W8 (xem PLAN mục 6) |
| Story | — |
| BR | — |
| NFR, EC, cổng | G7, G9, UX-01, UX-02, UX-10 |
| Quyết định kiến trúc | — |
| Phụ thuộc | [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md), [T-615](T-615-kiem-thu-dau-cuoi-2-2-hoi-dap-xem-nguon-cac-trang-thai.md), [T-608](T-608-thu-tai-g4.md), [T-609](T-609-kiem-tra-bao-mat-g6.md), [T-610](T-610-kiem-tra-telemetry-tren-staging-g8.md) |
| Mở khóa | [T-617](T-617-sua-loi-sau-uat-khung-thoi-gian-co-dinh.md) |

## Mục tiêu

Chuẩn bị và hỗ trợ buổi UAT với ≥ 5 thành viên BD, ghi và phân loại lỗi để sửa ở T-617.

## Đọc trước

Chỉ cần các phần dưới đây và file task này; không cần đọc toàn bộ SAD hay Blueprint. Hợp đồng chung: [CONTRACTS.md](../CONTRACTS.md).

- USER_STORIES.md (AC của story P0, P1)
- PRD mục 5.1 dòng G1, G2, G9

## Đầu vào có sẵn từ task trước

Các task dưới đây phải xong trước. Dùng đúng tên và chữ ký của chúng, không viết lại.

- [T-606](T-606-kiem-thu-dau-cuoi-1-2-moi-truong-dang-nhap-tai-len-xoa.md) Kiểm thử đầu cuối (1/2): môi trường, đăng nhập, tải lên, xóa: `frontend/playwright.config.ts`, `frontend/e2e/fixtures.ts`, `frontend/e2e/login.spec.ts`
- [T-615](T-615-kiem-thu-dau-cuoi-2-2-hoi-dap-xem-nguon-cac-trang-thai.md) Kiểm thử đầu cuối (2/2): hỏi đáp, xem nguồn, các trạng thái: `frontend/e2e/ask.spec.ts`, `frontend/e2e/source.spec.ts`, `frontend/e2e/answer_states.spec.ts`
- [T-608](T-608-thu-tai-g4.md) Thử tải (G4): `loadtest/locustfile.py`, `docs/05-planning/evidence/load-test.md`
- [T-609](T-609-kiem-tra-bao-mat-g6.md) Kiểm tra bảo mật (G6): `tests/security/test_authz_matrix.py`, `tests/security/test_prompt_injection.py`, `docs/05-planning/evidence/security-report.md`
- [T-610](T-610-kiem-tra-telemetry-tren-staging-g8.md) Kiểm tra telemetry trên staging (G8): `docs/05-planning/evidence/telemetry-checklist.md`

## File cần tạo hoặc sửa

- `docs/05-planning/evidence/uat-log.md`

## Các bước

1. Viết kịch bản UAT trong `uat-log.md`: 1 kịch bản cho mỗi story P0 và mỗi story P1 đang bật, gồm bước và kết quả mong đợi lấy từ AC của story.
2. Định nghĩa mức lỗi: Sev-1 chặn luồng chính hoặc lộ dữ liệu; Sev-2 sai chức năng chính có cách tránh khó; Sev-3 sai chức năng phụ hoặc có cách tránh dễ; Sev-4 hình thức.
3. Chuẩn bị staging (đặt lại dữ liệu, tài khoản cho ≥ 5 người BD, bộ tài liệu mẫu) và hướng dẫn 1 trang.
4. Hỗ trợ buổi UAT; ghi mỗi lỗi: mô tả, bước tái hiện, mức, người gặp, story liên quan.
5. Sau buổi: phân loại cùng PM; Sev-1/2 chuyển T-617; Sev-3/4 ghi chủ sở hữu và hạn hoặc hoãn có lý do.
6. Tính tỷ lệ AC đạt cho P0 (G1) và P1 (G2); đặt `CWD_COVERAGE_MIN=70` trong CI (G7).

## Tiêu chí hoàn thành

- [ ] Có ≥ 5 người BD tham gia và biên bản UAT (G9).
- [ ] Mọi lỗi có mức và chủ sở hữu.
- [ ] Có tỷ lệ AC đạt cho P0 và P1.
- [ ] Ngưỡng coverage 70% đã bật trong CI.

## Kiểm thử cần viết

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| Kiểm tra biên bản | Mở `uat-log.md` sau buổi UAT | Có danh sách người tham gia (vai trò), kịch bản, kết quả, lỗi có mức |
| Kiểm tra CI | Chạy `ci/run_ci.sh` | Dùng ngưỡng 70% và đạt |

## Ngoài phạm vi

Không làm trong task này (nếu cần, ghi câu hỏi thay vì tự làm):

- Sửa lỗi Sev-1/2 (T-617).
- Đo baseline MET-001 (G11, đội BD).

## Khi làm xong

Áp dụng định nghĩa hoàn thành chung ở [PLAN.md mục 3.3](../PLAN.md). Nếu bị chặn, thấy yêu cầu mâu thuẫn, hoặc cần đổi một mục của CONTRACTS.md, dừng lại và ghi câu hỏi vào task, không tự suy đoán.
