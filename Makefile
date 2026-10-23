.PHONY: install lint type test run

install:
	cd backend && pip install -e ".[dev]"

lint:
	cd backend && ruff check .

type:
	cd backend && mypy app

test:
	cd backend && pytest -q

run:
	cd backend && uvicorn app.main:create_app --factory --reload
