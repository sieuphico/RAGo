.PHONY: sample-data gate install lint type test run db-up db-down migrate db-reset

install:
	pip install -e ".[dev]"

lint:
	ruff check .

type:
	mypy app tests scripts

test:
	pytest -q

run:
	uvicorn app.main:create_app --factory --reload

db-up:
	docker compose -f deploy/compose.dev.yml up -d --wait

db-down:
	docker compose -f deploy/compose.dev.yml down

migrate:
	alembic upgrade head

db-reset:
	docker compose -f deploy/compose.dev.yml down -v
	docker compose -f deploy/compose.dev.yml up -d --wait
	alembic upgrade head

gate: lint type test

sample-data:
	python scripts/make_sample_data.py --out tests/fixtures/generated
