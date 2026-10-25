# Báo cáo kiểm thử E2E — {RUN_ID}

Người chạy: agent `qa-runner`. Báo cáo này **không được sửa sau khi ghi**; chạy lại thì tạo `reports/{RUN_ID_MỚI}/`.

| Mục | Giá trị |
|---|---|
| Run ID | `YYYYMMDD-HHMMSS` |
| Commit | `git rev-parse --short HEAD` (cây làm việc sạch: có/không) |
| Hồ sơ AI | ollama / fake (mô hình, `CWD_EMBEDDING_DIM`) |
| Đặc tả | `tests/e2e/spec.json` sha256 `…` (ma trận khớp: có/không) |
| Môi trường | API `/healthz`, frontend, Ollama: ok/không (kèm giờ kiểm) |

## Tóm tắt
| Kết quả | Số TC |
|---|---|
| PASS | n |
| FAIL | n |
| INCONCLUSIVE (đã dừng và hỏi người) | n |
| Không chạy | n |

AC đo được đóng bởi TC `full` PASS: liệt kê. AC NOT_MEASURABLE / OUT_OF_SCOPE: không tính, ghi lại nguyên văn từ ma trận.

## Từng test case
### {TC-ID} — {tiêu đề} → **PASS | FAIL | INCONCLUSIVE**
- AC: `{AC}` ({full|partial}) · bắt đầu/kết thúc: `ISO8601` · phiên agent-browser: `{tên}`
- Lệnh đã chạy (đúng thứ tự, kèm thời gian phản hồi từng lệnh quan trọng)
| Kỳ vọng | Mô tả (từ spec) | Giá trị thực | Kết quả |
|---|---|---|---|
| E1 | … | … | true/false |
- Bằng chứng: `reports/{RUN_ID}/{TC-ID}/snapshot-before.txt`, `snapshot-after.txt`, `screenshot.png`, `console.txt`
- Ghi chú: chỉ sự thật quan sát được; không suy diễn nguyên nhân (nguyên nhân do người phân tích).

## Việc cần người quyết định
Danh sách INCONCLUSIVE, AC mâu thuẫn, môi trường chết: mã TC, điều quan sát, câu hỏi cụ thể.

## results.json (cùng thư mục, máy đọc)
```json
{
  "run_id": "YYYYMMDD-HHMMSS", "commit": "abc1234", "profile": "ollama",
  "spec_sha256": "…", "started": "ISO8601", "finished": "ISO8601",
  "tcs": [
    {"id": "TC-UP-01", "ac": "US-010/AC1", "covers": "full", "verdict": "PASS",
     "runs": [{"assertions": [{"id": "E1", "actual": 640, "pass": true}], "evidence": ["TC-UP-01/screenshot.png"]}],
     "notes": ""}
  ]
}
```
Quy tắc chấm: **PASS** khi mọi kỳ vọng của mọi lượt lặp đều đúng. **FAIL** khi có ≥ 1 kỳ vọng sai trong môi trường khỏe. **INCONCLUSIVE** khi môi trường chết, phần tử không quan sát được, hoặc kết quả không so được với kỳ vọng; không bao giờ đổi INCONCLUSIVE thành PASS/FAIL bằng suy đoán.
