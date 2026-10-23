.PHONY: install lint type test run db-up db-down migrate db-reset

install:
	pip install -e ".[dev]"

lint:
	ruff check .

type:
	mypy app tests

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
