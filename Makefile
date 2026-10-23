.PHONY: install lint type test run

install:
	pip install -e ".[dev]"

lint:
	ruff check .

type:
	mypy app

test:
	pytest -q

run:
	uvicorn app.main:create_app --factory --reload
