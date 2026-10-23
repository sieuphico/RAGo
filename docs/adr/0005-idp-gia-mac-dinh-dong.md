# ADR 0005: IdP giả mặc định đóng; API chạy một tiến trình

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | Đã chấp nhận |
| Ngày | 2026-10-23 |
| Task / Story | T-108, T-602 · US-001, US-002 |
| Liên quan | PD-001, T-006, AD-09, NFR-008, CONTRACTS mục 7 |

## Bối cảnh
SSO thật chưa tích hợp (T-006), nên đăng nhập dùng `IdpFake`: nó nhận email từ `login_hint`/tham số `email` mà không xác thực. Ở môi trường thật, ai biết email của một người trong allow-list (ví dụ quản trị viên) đều mạo danh được. Mặc định cũ là `idp="fake"`, nên một triển khai quên cấu hình sẽ mở toàn bộ hệ thống. Phát hiện khi rà soát cuối trước bàn giao.

## Quyết định
- Thêm khóa `allow_fake_idp` (mặc định `false`, ngoài CONTRACTS mục 7). `build_idp` ném lỗi khi `idp=fake` mà chưa bật; `create_app` gọi nó ở khởi động nên tiến trình dừng ngay với thông báo rõ.
- Dev/staging đặt `CWD_ALLOW_FAKE_IDP=true` có chủ đích; test (`tests/conftest.py`) và `.env` dev đã đặt. `deploy/.env.template` để `false`.
- Hệ quả vận hành: **không triển khai được môi trường thật cho tới khi có IdP thật** (T-006). Đây là chủ ý (fail-closed).
- Ghi chú liên quan: `RunningAnswers` (API-09 Dừng) là bộ nhớ trong một tiến trình, nên API phải chạy **một** tiến trình uvicorn (không dùng `--workers > 1`) cho tới khi chuyển trạng thái chạy sang CSDL/NOTIFY.

## Lựa chọn đã xét
Giữ mặc định `fake` và chỉ ghi cảnh báo trong tài liệu (dễ bị bỏ sót); phát hiện môi trường qua biến `ENV` (thêm khái niệm mới, dễ cấu hình sai theo hướng mở).

## Hệ quả
`deploy/evidence/*` và `AGENTS.md` ghi rõ. Khi có IdP thật, thêm bộ nối `oidc`/`saml` vào `build_idp` và bỏ yêu cầu bật cờ ở môi trường thật.
