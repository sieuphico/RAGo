# Kịch bản E2E trình duyệt (thủ công)

Kiểm tra cả chuỗi bằng Chromium thật: tải PDF → `Sẵn sàng` qua SSE → hỏi đáp có trích dẫn → khung xem nguồn → đánh giá → câu ngoài phạm vi → nhật ký và số liệu của quản trị viên.

Playwright **chưa** thuộc phụ thuộc của dự án (chưa được duyệt, xem `frontend/OPEN_QUESTIONS.md` FQ-07), nên cài riêng ngoài kho mã:

```bash
mkdir /tmp/pw && cd /tmp/pw && npm init -y && npm i playwright && npx playwright install chromium
cp <repo>/scripts/e2e/e2e.mjs .
```

Chuẩn bị (ở gốc kho): `make db-up migrate`, thêm người dùng minh@ (TEAM_LEAD), lan@ (BD_USER), quantri@ (ADMIN) bằng `python -m app.cli add-admin` rồi màn hình Quản lý người dùng, `python scripts/make_sample_data.py --out var/sample`, chạy `uvicorn app.main:create_app --factory`, `python -m app.worker`, và `npm run dev` trong `frontend/` (hoặc đặt `BASE` tới địa chỉ nginx).

```bash
BASE=http://localhost:5173 PDF=<repo>/var/sample/text_12p.pdf SHOTS=<thư mục ảnh> node e2e.mjs
```

Với AI giả, bước "không tìm thấy" sẽ hết thời gian chờ vì AI giả luôn trả "Theo tài liệu…". Dùng `CWD_AI_PROVIDER=ollama` để chạy đủ.
