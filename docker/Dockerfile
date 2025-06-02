# Orion Vision Core - Production Dockerfile
# Sprint 4.3 - Production Deployment & Advanced Monitoring
# 
# Multi-stage build for optimized production container

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY examples/ ./examples/
COPY tests/ ./tests/

# Run tests during build
RUN python -m pytest tests/ -v

# Production stage
FROM python:3.11-slim as production

# Set metadata labels
LABEL maintainer="Orion Development Team" \
      version="${VERSION}" \
      description="Orion Vision Core - Enterprise Agent Coordination Platform" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    ORION_ENV=production \
    ORION_LOG_LEVEL=INFO

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r orion \
    && useradd -r -g orion orion

# Create app directory and set permissions
WORKDIR /app
RUN chown -R orion:orion /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=orion:orion src/ ./src/
COPY --chown=orion:orion config/ ./config/
COPY --chown=orion:orion docker/entrypoint.sh ./entrypoint.sh
COPY --chown=orion:orion docker/healthcheck.py ./healthcheck.py

# Make scripts executable
RUN chmod +x ./entrypoint.sh ./healthcheck.py

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data && \
    chown -R orion:orion /app/logs /app/data

# Switch to non-root user
USER orion

# Expose ports
EXPOSE 8000 8001 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python healthcheck.py

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command
CMD ["agent-manager"]
