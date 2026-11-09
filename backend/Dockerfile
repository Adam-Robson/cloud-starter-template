# base
FROM python:3.13.4-slim

# uv install, pinned so image builds are reproducible
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

# optimize python
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /backend

# install deps first so this layer is cached until uv.lock changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# install the project itself
COPY README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev

# least privilege: run as an unprivileged user
RUN useradd --system --no-create-home app
USER app

# uvicorn bound to Cloud Run's $PORT
CMD exec /backend/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port $PORT
