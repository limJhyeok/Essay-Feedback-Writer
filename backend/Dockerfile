FROM python:3.10

# Set environment variables
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app/

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Using a wildcard 'uv.lock*' allows the build to continue even if the file is missing.
COPY pyproject.toml uv.lock* README.md* ./

# 2. Sync dependencies BUT skip installing the local project
RUN if [ -f uv.lock ]; then \
        uv sync --frozen --no-install-project $([ "$INSTALL_DEV" != "true" ] && echo "--no-group dev"); \
    else \
        uv sync --no-install-project $([ "$INSTALL_DEV" != "true" ] && echo "--no-group dev"); \
    fi

# Copy the application code
COPY . .

# Make the virtualenv's bin directory available on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port that the app will run on
EXPOSE 8000
