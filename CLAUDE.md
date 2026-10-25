# CLAUDE.md

Quy ước chung của dự án nằm ở [AGENTS.md](AGENTS.md) (stack, lệnh, quy ước code, điều cấm, quyền hạn). File này bổ sung mục **Kiểm thử E2E**.

## Kiểm thử

Tài liệu: [test plan](tests/e2e/TEST_PLAN.md) · [spec.json](tests/e2e/spec.json) (AC, TC, kỳ vọng ghi trước; nguồn duy nhất) · [ma trận](tests/e2e/AC_TC_MATRIX.md) (sinh tự động) · [mẫu báo cáo](tests/e2e/report-template.md).

### Môi trường
| Mục | Giá trị |
|---|---|
| URL app test | `http://localhost:5173` (`BASE`); API `http://localhost:8000` |
| Tài khoản (IdP giả, dev) | `minh@congty.vn` (TEAM_LEAD), `lan@congty.vn` (BD_USER), `quantri@congty.vn` (ADMIN); đăng nhập bằng `open "$BASE/auth/login?login_hint=<email>&next=/"` |
| PDF mẫu | `var/sample/text_12p.pdf` (`PDF`); `python scripts/make_sample_data.py --out var/sample` |
| Câu hỏi chuẩn (`QUESTION`) | `Hợp đồng số HD-2026-012 có thời hạn bao lâu?` — đáp án chứa `24 tháng`, trang 12 |
| Khởi động | `make db-up migrate` · `make ai-up ai-pull` · `python -m uvicorn app.main:create_app --factory --port 8000` · `python -m app.worker` · `npm run dev -- --port 5173` (trong `frontend/`) |
| Chuẩn bị dữ liệu (SETUP-1) | `python scripts/e2e/setup_env.py` (thêm `--reset` xóa dữ liệu dev; chỉ chạy khi người yêu cầu) |
| Kiểm tra sống | `curl localhost:8000/healthz` → `{"status":"ok",...}`; `curl localhost:5173`; `curl localhost:11434/api/tags` (hồ sơ ollama) |

Cần `.env` có `CWD_ALLOW_FAKE_IDP=true`, `CWD_AI_PROVIDER=ollama`, `CWD_EMBEDDING_DIM=1024`. IdP giả chỉ dùng ở dev/staging (ADR-0005).

### Công cụ trình duyệt: agent-browser (không dùng Playwright)
`agent-browser` điều khiển Chrome qua CDP, **không** phụ thuộc Playwright; Playwright không nằm trong phụ thuộc của dự án (chưa được duyệt, FQ-07). Cài một lần: `npm i -g agent-browser && agent-browser install` (kiểm bằng `agent-browser doctor`). Cấu hình mỗi lần chạy:
```bash
export AGENT_BROWSER_SESSION="qa-<TC-ID>-<RUN_ID>"   # mỗi TC một phiên riêng, không dùng phiên mặc định
agent-browser set viewport 1400 900                  # NFR-007: Chrome/Edge, ≥ 1280 px
agent-browser open "$BASE/auth/login?login_hint=lan@congty.vn&next=/"
agent-browser snapshot -i                            # cây truy cập có @ref; chụp lại sau mỗi thay đổi trang
agent-browser click|fill|upload|press ...            # thao tác theo spec.json
agent-browser get text|count|attr ...                # lấy giá trị để chấm
agent-browser screenshot reports/<RUN_ID>/<TC-ID>/screenshot.png
agent-browser console; agent-browser errors          # ghi vào bằng chứng
agent-browser close                                  # đóng phiên khi xong TC
```
Dùng selector `[data-testid=...]` đúng như `spec.json`. Cookie phiên có cờ Secure; `localhost` được trình duyệt coi là an toàn nên đăng nhập bình thường.

### Thư mục và mẫu báo cáo
Mọi kết quả ghi vào `./reports/<RUN_ID>/` (`RUN_ID` = `YYYYMMDD-HHMMSS`): `report.md` theo [mẫu](tests/e2e/report-template.md), `results.json`, và `<TC-ID>/` chứa `snapshot-before.txt`, `snapshot-after.txt`, `screenshot.png`, `console.txt`. Không ghi đè một lần chạy cũ.

### Quyền hạn của agent chạy test (`qa-runner`, `.claude/agents/qa-runner.md`)
- **Được:** chạy `agent-browser`, `curl` kiểm sống, `python scripts/e2e/setup_env.py` (không `--reset`), đọc code và `spec.json`, ghi vào `./reports/`, cập nhật file kết quả của lần chạy đó.
- **Không được:** sửa code (`app/`, `frontend/`, `tests/`, `scripts/`, `deploy/`), sửa AC hay `spec.json` trong lúc chạy, sửa kỳ vọng, `git commit/push`, chạy `--reset`, cài thư viện.
- Tự kiểm khi kết thúc: `git status --porcelain` chỉ được liệt kê đường dẫn dưới `reports/`; nếu khác, báo người, không tự hoàn tác.

### Cách thực thi mỗi test case
1. Đọc TC và kỳ vọng từ `spec.json` **trước khi** thao tác; chép nguyên văn vào `report.md` (không diễn đạt lại).
2. Một TC = một phiên agent-browser: `open` → `snapshot` (trước) → thao tác theo `steps` → `snapshot` (sau) → lấy giá trị → chấm từng kỳ vọng.
3. Chấm theo quy tắc ở báo cáo mẫu: PASS (mọi kỳ vọng đúng) / FAIL (kỳ vọng sai, môi trường khỏe) / INCONCLUSIVE. TC có `repeat` chạy đủ số lượt, mỗi lượt phiên mới.
4. Ghi giá trị thực cạnh giá trị kỳ vọng; chỉ ghi điều quan sát được, không suy ra nguyên nhân.

### Dừng và hỏi người (agent không tự diễn giải)
Dừng lại, ghi `INCONCLUSIVE` kèm quan sát và câu hỏi cụ thể, rồi báo người khi:
- môi trường chết (`/healthz` không `ok`, frontend/Ollama không phản hồi, Docker tắt, đăng nhập thất bại);
- kết quả mơ hồ (phần tử không quan sát được, đo thời gian không đáng tin, giá trị không so được với kỳ vọng);
- AC mâu thuẫn nhau hoặc mâu thuẫn với hành vi tài liệu thiết kế, hoặc kỳ vọng trong `spec.json` có vẻ sai.
Không đổi kỳ vọng để TC qua; không tự chạy lại để "chọn" kết quả đẹp (lặp chỉ theo `repeat` của TC).
