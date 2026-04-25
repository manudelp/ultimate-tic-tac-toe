FROM python:3.11-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD uv run gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:${PORT:-5000} app:app
