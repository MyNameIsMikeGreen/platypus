.PHONY: browser-install check lock test

browser-install:
	uv run playwright install chromium

check:
	uv lock --check
	uv run python manage.py check
	uv run pytest

lock:
	uv lock

test:
	uv run pytest
