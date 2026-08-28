# Development

## Prerequisites

Install Python 3.14 and [uv](https://docs.astral.sh/uv/getting-started/installation/). Docker is
optional for local code work and required to validate the
[deployment image](deployment.md).

## Setup

```shell
uv sync
make browser-install
uv run python manage.py collectstatic --noinput
uv run python manage.py runserver
```

`collectstatic` must be rerun whenever static files under `src/recipes/static/` change; static
assets are served through whitenoise's manifest storage, so requests fail with a 500 until the
manifest exists in `staticfiles/`.

The application reads the checked-in recipe catalog directly and does not require a database or
external service. Follow [`recipes.md`](recipes.md) when changing catalog data and
[`architecture.md`](architecture.md) before changing runtime components.

## Quality checks

Run the complete fast feedback suite:

```shell
make check
```

Individual commands are:

```shell
uv run pytest
uv run python manage.py check
```

Update dependencies intentionally with `uv lock --upgrade`, review `uv.lock`, and rerun
`make check`.

Tests use in-memory recipe objects, [pytest](https://docs.pytest.org/en/stable/), and a real
[Playwright](https://playwright.dev/python/) browser for interactive behavior. They test
application behavior, catalog rules, critical security settings, and deployment hardening rather
than the wording or number of real recipes.

## PyCharm and IntelliJ IDEA

Open the repository root, then select `.venv/bin/python` as the project interpreter after
`uv sync`. Mark `src` as a Sources Root if the IDE does not infer it from `pyproject.toml`.
Configure pytest as the test runner and `platypus.settings` as `DJANGO_SETTINGS_MODULE` for
Django-aware run configurations. JetBrains documents the corresponding
[Django project setup](https://www.jetbrains.com/help/pycharm/creating-and-running-your-first-django-project.html)
and [pytest configuration](https://www.jetbrains.com/help/pycharm/pytest.html).

Any change that introduces writes, accounts, private data, or public exposure must first follow
[`security-boundary.md`](security-boundary.md).

Do not commit `.idea`, `.env`, or generated static files; they are ignored.
