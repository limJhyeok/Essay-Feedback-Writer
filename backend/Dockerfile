FROM python:3.10

# Set environment variables
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app/

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Using a wildcard 'uv.lock*' allows the build to continue even if the file is missing.
COPY ./pyproject.toml ./uv.lock* /app/ ./

RUN if [ "$INSTALL_DEV" = "true" ]; then \
        uv sync --frozen --no-install-project; \
    else \
        uv sync --frozen --no-install-project --no-group dev; \
    fi
# Copy the application code
COPY . .

# Make the virtualenv's bin directory available on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port that the app will run on
EXPOSE 8000
