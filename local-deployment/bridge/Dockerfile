# Orion Vision Core - Hybrid Bridge Container
# Phase 3: Python ↔ Kubernetes Integration

FROM python:3.11-slim

# Metadata
LABEL maintainer="Orion Development Team"
LABEL version="1.0.0"
LABEL description="Orion Hybrid Bridge - Python to Kubernetes Integration"

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create non-root user
RUN groupadd -r bridge && useradd -r -g bridge bridge

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/config && \
    chown -R bridge:bridge /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER bridge

# Default command
CMD ["python", "hybrid_bridge.py"]
