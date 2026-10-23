---
description: Chạy các cổng chất lượng và sửa cho đến khi xanh (tối đa 3 vòng)
argument-hint: [log hoặc mô tả lỗi CI]
---

Làm các cổng chất lượng xanh. Ngữ cảnh lỗi: $ARGUMENTS

Vòng lặp (tối đa 3 vòng, sau đó dừng và báo):
1. Chạy theo thứ tự: `ruff check .`, `mypy app tests`, `pytest -q`. Test tích hợp cần `make db-up`; nếu Docker/CSDL không chạy, nói rõ thay vì coi là xanh.
2. Đọc lỗi thật; tìm **nguyên nhân gốc**. Không xóa/skip/nới test, không `# type: ignore` hay `noqa` rộng để qua cổng, không `--no-verify`.
3. Sửa trong `app/`, `tests/`, `migrations/`, `ci/`, `.github/`, `pyproject.toml`. Lỗi do docs/CONTRACTS sai → dừng và hỏi, không sửa docs baseline.
4. Chạy lại cả ba cổng (sửa chỗ này có thể làm hỏng chỗ khác).
5. Khi xanh: tóm tắt nguyên nhân và cách sửa; commit nhỏ `fix(ci): ...` kèm mã task nếu có. Không push.

Nếu lỗi CI chỉ xảy ra ở môi trường CI (khác máy cục bộ), so sánh `.github/workflows/ci.yml` và `ci/run_ci.sh` với lệnh cục bộ trước khi sửa mã.
