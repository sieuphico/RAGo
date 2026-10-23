#!/usr/bin/env bash
# T-601: lint, kiểu, test, coverage cho backend và frontend. Chạy được ở máy cục bộ và trong CI.
# Cần PostgreSQL (dịch vụ CI, hoặc `make db-up` ở máy cục bộ, cổng 5433).
# CWD_COVERAGE_MIN: ngưỡng coverage cho app/worker và app/modules/answer (mặc định 0; đặt 70 cho G7).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== Backend =="
python -m pip install -q -e ".[dev]"
ruff check .
mypy app tests scripts
pytest --cov=app --cov-report=xml --cov-report=term -q

echo "== Coverage riêng (G7) =="
min="${CWD_COVERAGE_MIN:-0}"
for part in "app/worker/*" "app/modules/answer/*"; do
  echo "-- $part (tối thiểu ${min}%)"
  coverage report --include="$part" --fail-under="$min"
done

echo "== Frontend =="
cd frontend
npm ci --no-audit --no-fund
npm run lint
npm run type-check
npm run test
npm run build
echo "== Xong =="
