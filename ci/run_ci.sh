#!/usr/bin/env bash
# T-601 (phần backend). Frontend (T-501) và PostgreSQL thử (T-003) thêm khi có.
set -euo pipefail
cd "$(dirname "$0")/../backend"
python -m pip install -q -e ".[dev]"
ruff check .
mypy app
pytest --cov=app --cov-report=xml --cov-report=term -q
