FROM python:3.10

# Set the working directory
WORKDIR /app/

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY ./pyproject.toml ./uv.lock /app/

# Install dependencies
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        uv sync --frozen --no-install-project; \
    else \
        uv sync --frozen --no-install-project --no-group dev; \
    fi

# Copy the application code
COPY . .

# Make the virtualenv's bin directory available on PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Expose the port that the app will run on
EXPOSE 8000
