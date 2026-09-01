install:
	uv sync

run:
	uv run flask --app main run --port 8080

lint:
	uv run ruff check .

.PHONY: install run lint