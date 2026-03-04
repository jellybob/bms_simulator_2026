FROM python:3.13-slim

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV UV_CACHE_DIR=/var/uv/cache
ENV UV_PROJECT_ENVIRONMENT=/var/uv/venv

WORKDIR /app

# Copy dependency files first for better caching
COPY uv.lock .
COPY pyproject.toml .
COPY README.md .

# Install dependencies (creates venv at /var/uv/venv and installs everything)
RUN uv sync

# Copy the rest of the application
COPY . .

# Add the venv to PATH so we can run commands directly
ENV PATH="${UV_PROJECT_ENVIRONMENT}/bin:$PATH"

# Now you can run without `uv run`
CMD ["python", "-m", "bms_simulator"]
