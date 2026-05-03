.PHONY: migrate run test lint

migrate:
	alembic upgrade head

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	python -m compileall -q main.py core models repositories routers schemas services utils alembic
