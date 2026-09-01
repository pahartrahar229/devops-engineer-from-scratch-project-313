install:
	uv sync

run:
	uv run flask --app main run --port 8080

test:
	uv run pytest

lint:
	uv run ruff check .

.PHONY: install run test lint