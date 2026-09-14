# The server, for development. The distributable artefact is the Python package that
# `make build` produces; this image exists so `docker compose up` gives you a running
# Specdeck without installing uv, Node or pnpm on the machine.
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

# Copying is what a bind mount over /app/src expects, and bytecode makes the start quicker.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# The dependencies first, so editing the code does not re-resolve them. Versions come from
# the lockfile, the same ones a developer gets.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

# The project is installed editable, so the bind mount over /app/src is what actually runs.
COPY src ./src
RUN uv sync --locked

EXPOSE 4820
CMD ["uv", "run", "--no-sync", "specdeck", "serve"]
