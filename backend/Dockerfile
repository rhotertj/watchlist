FROM python:3-slim AS build-env
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd -m -u 1000 appuser
USER appuser
COPY --chown=appuser:appuser . /project
WORKDIR /project

RUN uv sync --frozen --no-cache

CMD [".venv/bin/uvicorn", "app.main:app", "--port", "80", "--host", "0.0.0.0"] 