# Orion Vision Core - Python Core Container
# Phase 3: Hybrid Local Deployment

FROM python:3.11-slim

# Metadata
LABEL maintainer="Orion Development Team"
LABEL version="1.0.0"
LABEL description="Orion Vision Core - Python Agent Core"

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    tesseract-ocr \
    tesseract-ocr-tur \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create non-root user
RUN groupadd -r orion && useradd -r -g orion orion

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy source code from main project
COPY ../../src/jobone/vision_core/ ./src/jobone/vision_core/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/agent_data /app/config && \
    chown -R orion:orion /app

# Copy configuration files
COPY ../config/ ./config/

# Health check script
COPY healthcheck.py .

# Expose ports
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python healthcheck.py

# Switch to non-root user
USER orion

# Default command
CMD ["python", "enhanced_agent_core.py"]
