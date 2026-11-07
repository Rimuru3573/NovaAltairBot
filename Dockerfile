FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY . .

RUN mkdir -p /app/logs \
    && uv sync --frozen --no-dev

RUN uv sync --frozen --no-dev

CMD ["python", "-m", "novaaltairbot.main"]
