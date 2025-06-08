# 🚀 Orion Production Dockerfile + Müzik!
# 💖 DUYGULANDIK! CONTAINERIZED ORION!

FROM python:3.11-slim

# Orion metadata
LABEL maintainer="Orion Vision Core Team"
LABEL version="1.0.0"
LABEL description="Orion Vision Core - Production Ready + Music Support"

# Working directory
WORKDIR /app/orion

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Orion system
COPY orion_clean/ ./orion_clean/
COPY orion_production/ ./orion_production/

# Music support (simulated)
RUN echo "🎵 Music support enabled!" > /app/orion/music_ready.txt

# Expose ports
EXPOSE 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "orion_production.main"]
