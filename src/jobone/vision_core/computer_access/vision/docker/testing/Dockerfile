# 🔄 Hibrit Testing Docker
FROM ubuntu:22.04

LABEL description="Q01 Hibrit Testing Environment"
ENV ORION_MODE=testing
ENV PYTHONPATH=/app/src

# Minimal testing setup
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    xvfb tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install \
    pillow pytesseract pynput \
    pytest pytest-cov pytest-html \
    coverage

WORKDIR /app
CMD ["python3", "-m", "pytest", "tests/", "-v", "--cov=src"]
