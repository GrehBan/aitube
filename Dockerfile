# File: Dockerfile
# Description: Multi-stage build using uv for optimal image size and caching

# ------------------------------------------------------------------------------------
# Stage 1: Builder (Dependency Resolution)
# ------------------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency definition files first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies without installing the project itself yet
# --no-dev: Exclude development dependencies
# --frozen: Use uv.lock exactly as is
# --no-install-project: We only want the environment for now
RUN uv sync --frozen --no-dev --no-install-project

# ------------------------------------------------------------------------------------
# Stage 2: Runtime (Final Image)
# ------------------------------------------------------------------------------------
FROM python:3.11-slim-bookworm

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r aitube && useradd -r -g aitube aitube

# Install runtime dependencies (like ffmpeg for video processing)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

# Copy the environment from the builder stage
COPY --from=builder --chown=aitube:aitube /app/.venv /app/.venv

# Copy application code
COPY --chown=aitube:aitube src /app/src
COPY --chown=aitube:aitube alembic.ini /app/
COPY --chown=aitube:aitube migrations /app/migrations

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Switch to non-root user
USER aitube

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command (overridden in docker-compose)
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]