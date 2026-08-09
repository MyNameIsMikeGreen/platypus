.PHONY: browser-install check format lock test

browser-install:
	uv run playwright install chromium

check:
	uv lock --check
	uv run ruff format --check .
	uv run ruff check .
	uv run python manage.py check
	uv run pytest

format:
	uv run ruff format .
	uv run ruff check --fix .

lock:
	uv lock

test:
	uv run pytest
