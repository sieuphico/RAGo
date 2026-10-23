#!/usr/bin/env bash
# T-601 (phần backend). PostgreSQL: dịch vụ CI, hoặc `make db-up` ở máy cục bộ (cổng 5433).
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install -q -e ".[dev]"
ruff check .
mypy app tests scripts
pytest --cov=app --cov-report=xml --cov-report=term -q
