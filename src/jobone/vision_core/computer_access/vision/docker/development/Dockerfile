# 🔄 Hibrit Development Docker
FROM ubuntu:22.04

LABEL maintainer="Orion Vision Core Team"
LABEL description="Q01 Hibrit Development Environment"
LABEL version="1.0.0"

# 💖 DUYGULANDIK! SEN YAPARSIN!
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV PYTHONPATH=/app/src
ENV ORION_MODE=development

# System packages
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev \
    build-essential cmake pkg-config \
    libx11-dev libxtst-dev libxrandr-dev \
    xvfb x11vnc fluxbox \
    tesseract-ocr tesseract-ocr-eng \
    git vim nano htop \
    && rm -rf /var/lib/apt/lists/*

# Python packages
RUN pip3 install \
    pillow pytesseract pynput \
    opencv-python numpy \
    pytest pytest-cov \
    black flake8 mypy

WORKDIR /app
COPY entrypoint-dev.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
