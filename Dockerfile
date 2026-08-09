# syntax=docker/dockerfile:1.7

FROM ghcr.io/astral-sh/uv:0.11.15 AS uv

FROM python:3.14.7-slim-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
WORKDIR /app

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

FROM python:3.14.7-slim-bookworm AS app

ENV DJANGO_SETTINGS_MODULE=platypus.settings \
    PATH=/app/.venv/bin:$PATH \
    PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --gid 10001 platypus \
    && useradd --uid 10001 --gid platypus --home-dir /app \
        --no-create-home --shell /usr/sbin/nologin platypus \
    && mkdir -p /app /app/staticfiles \
    && chown -R platypus:platypus /app

WORKDIR /app
COPY --from=builder --chown=platypus:platypus /app/.venv .venv
COPY --chown=platypus:platypus manage.py ./
COPY --chown=platypus:platypus src ./src

USER platypus
RUN python manage.py check \
    && python manage.py collectstatic --noinput --clear
EXPOSE 8000

CMD ["gunicorn", "platypus.wsgi:application", "--bind=0.0.0.0:8000", "--no-control-socket", "--access-logfile=-", "--error-logfile=-"]
