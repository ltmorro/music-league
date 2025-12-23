# syntax=docker/dockerfile:1

# Build stage - install dependencies with uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Copy dependency files and README (required by hatchling build)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies (without dev extras)
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code and install the package
COPY src/ src/
RUN uv sync --frozen --no-dev


# Runtime stage - minimal image
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Install runtime system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set up PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Copy application files
COPY streamlit_app.py .
COPY pages/ pages/
COPY static/ static/
COPY .streamlit/ .streamlit/
COPY src/ src/

# Copy data and cache directories (if they exist and should be bundled)
# These can also be mounted as volumes or loaded from GCS at runtime
COPY data/ data/
COPY cache/ cache/

# Streamlit configuration for Cloud Run
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Cloud Run uses PORT environment variable
EXPOSE 8080

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/_stcore/health || exit 1

# Run the Streamlit app
# Cloud Run sets PORT env var, Streamlit uses STREAMLIT_SERVER_PORT
CMD ["sh", "-c", "streamlit run streamlit_app.py --server.port=${PORT:-8080}"]