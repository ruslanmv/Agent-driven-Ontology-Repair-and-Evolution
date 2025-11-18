# Multi-stage Dockerfile for ADORE
# Optimized for production deployment

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create app directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system -e .

# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install runtime dependencies (Java for OWL reasoner)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r adore && useradd -r -g adore adore

# Create app directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY examples/ ./examples/

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs /app/.adore_cache && \
    chown -R adore:adore /app

# Switch to non-root user
USER adore

# Set working directory for data
VOLUME ["/app/data", "/app/logs"]

# Expose port (if web interface is added in future)
# EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import adore; print('OK')" || exit 1

# Default command
ENTRYPOINT ["python", "-m", "adore"]
CMD ["--help"]
