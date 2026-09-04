FRAMEWORK ?= fastapi

install: install-backend install-frontend

install-backend:
	uv sync

install-frontend:
	npm install

run:
	uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload

frontend:
	npm run frontend

dev:
	npm run dev

test:
	uv run pytest

lint:
	uv run ruff check .

.PHONY: install install-backend install-frontend run frontend dev test lint