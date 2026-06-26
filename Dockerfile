# ── stage 1: install dependencies ────────────────────────────────────────────
FROM python:3.13-slim AS deps

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project


# ── stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

COPY --from=deps /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    HF_HOME=/app/.cache/huggingface \
    STORAGE=/app/storage

COPY api/         api/
COPY ingestion_app/ ingestion_app/

RUN mkdir -p /app/storage /app/.cache/huggingface


VOLUME ["/app/storage"]

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
