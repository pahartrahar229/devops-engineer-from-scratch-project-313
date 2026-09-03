install:
	uv sync

run:
	uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload

test:
	uv run pytest

lint:
	uv run ruff check .

.PHONY: install run test lint