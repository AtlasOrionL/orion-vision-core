#!/bin/bash
# 🔄 Hibrit Yaklaşım Setup Script
# 💖 DUYGULANDIK! SEN YAPARSIN! HİBRİT GÜÇLE!

echo "🔄 HİBRİT YAKLAŞIM SETUP BAŞLATIYOR!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"
echo "🌟 WAKE UP ORION! EN İYİ İKİ DÜNYA!"
echo ""

# Hibrit klasör yapısı oluştur
echo "📁 Hibrit klasör yapısı oluşturuluyor..."

# Docker klasörü
mkdir -p docker/{development,testing,production}
mkdir -p docker/configs
mkdir -p docker/scripts

# Native klasörü
mkdir -p native/{development,testing}
mkdir -p native/configs
mkdir -p native/scripts

# Shared klasörü
mkdir -p shared/{data,logs,configs,results}
mkdir -p shared/volumes

# Bridge klasörü
mkdir -p bridge/{sync,monitor,switch}

echo "✅ Hibrit klasör yapısı oluşturuldu!"
echo ""

# Docker files oluştur
echo "🐳 Docker dosyaları oluşturuluyor..."

# Development Dockerfile
cat > docker/development/Dockerfile << 'EOF'
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
EOF

# Testing Dockerfile
cat > docker/testing/Dockerfile << 'EOF'
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
EOF

echo "✅ Docker dosyaları oluşturuldu!"
echo ""

# Docker Compose oluştur
echo "🐳 Docker Compose oluşturuluyor..."

cat > docker-compose.yml << 'EOF'
# 🔄 Hibrit Docker Compose
version: '3.8'

services:
  # Development container
  orion-dev:
    build: 
      context: .
      dockerfile: docker/development/Dockerfile
    container_name: orion-q01-dev
    environment:
      - DISPLAY=:99
      - PYTHONPATH=/app/src
      - ORION_MODE=development
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
      - ./shared:/app/shared
      - ./native:/app/native
    ports:
      - "5900:5900"  # VNC
      - "8888:8888"  # Jupyter
    networks:
      - orion-hybrid
    stdin_open: true
    tty: true

  # Testing container
  orion-test:
    build:
      context: .
      dockerfile: docker/testing/Dockerfile
    container_name: orion-q01-test
    environment:
      - PYTHONPATH=/app/src
      - ORION_MODE=testing
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
      - ./shared/results:/app/results
    networks:
      - orion-hybrid
    depends_on:
      - orion-dev

  # Bridge service
  orion-bridge:
    image: alpine:latest
    container_name: orion-bridge
    command: tail -f /dev/null
    volumes:
      - ./shared:/shared
      - ./bridge:/bridge
    networks:
      - orion-hybrid

networks:
  orion-hybrid:
    driver: bridge
EOF

echo "✅ Docker Compose oluşturuldu!"
echo ""

# Native scripts oluştur
echo "🐧 Native scripts oluşturuluyor..."

cat > native/scripts/dev_setup.sh << 'EOF'
#!/bin/bash
# 🐧 Native Development Setup
echo "🐧 NATIVE DEVELOPMENT SETUP!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"

# Virtual environment oluştur
python3 -m venv native/venv
source native/venv/bin/activate

# Packages kur
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Native development environment hazır!"
EOF

cat > native/scripts/test_runner.sh << 'EOF'
#!/bin/bash
# 🐧 Native Test Runner
echo "🧪 NATIVE TEST RUNNER!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"

source native/venv/bin/activate
export PYTHONPATH=$(pwd)/src

# Tests çalıştır
python -m pytest tests/ -v --cov=src --cov-report=html
echo "✅ Native tests tamamlandı!"
EOF

chmod +x native/scripts/*.sh

echo "✅ Native scripts oluşturuldu!"
echo ""

# Bridge scripts oluştur
echo "🔗 Bridge scripts oluşturuluyor..."

cat > bridge/sync/sync_native_to_docker.sh << 'EOF'
#!/bin/bash
# 🔗 Native → Docker Sync
echo "🔗 NATIVE → DOCKER SYNC!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"

# Shared volume'a kopyala
rsync -av --delete src/ shared/src/
rsync -av --delete tests/ shared/tests/

echo "✅ Native → Docker sync tamamlandı!"
EOF

cat > bridge/sync/sync_docker_to_native.sh << 'EOF'
#!/bin/bash
# 🔗 Docker → Native Sync
echo "🔗 DOCKER → NATIVE SYNC!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"

# Docker'dan native'e kopyala
rsync -av --delete shared/results/ native/results/
rsync -av --delete shared/logs/ native/logs/

echo "✅ Docker → Native sync tamamlandı!"
EOF

chmod +x bridge/sync/*.sh

echo "✅ Bridge scripts oluşturuldu!"
echo ""

# Entrypoint scripts oluştur
echo "🚀 Entrypoint scripts oluşturuluyor..."

cat > docker/development/entrypoint-dev.sh << 'EOF'
#!/bin/bash
# 🐳 Development Entrypoint
echo "🐳 DOCKER DEVELOPMENT BAŞLATIYOR!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"

# Virtual display başlat
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Fluxbox başlat
fluxbox &

# VNC server başlat
x11vnc -display :99 -nopw -listen localhost -xkb &

echo "✅ Docker development environment hazır!"
echo "🌟 WAKE UP ORION! HIBRIT GÜÇLE!"

exec "$@"
EOF

chmod +x docker/development/entrypoint-dev.sh

echo "✅ Entrypoint scripts oluşturuldu!"
echo ""

# Requirements dosyası oluştur
echo "📦 Requirements dosyası oluşturuluyor..."

cat > requirements.txt << 'EOF'
# 🔄 Hibrit Requirements
# 💖 DUYGULANDIK! SEN YAPARSIN!

# Core packages
pillow>=10.0.0
pytesseract>=0.3.10
pynput>=1.8.0
opencv-python>=4.8.0
numpy>=1.24.0

# Development packages
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-html>=3.2.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0

# Monitoring packages
psutil>=5.9.0
memory-profiler>=0.61.0

# Documentation packages
sphinx>=7.1.0
sphinx-rtd-theme>=1.3.0
EOF

echo "✅ Requirements dosyası oluşturuldu!"
echo ""

echo "🎉 HİBRİT SETUP TAMAMLANDI!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"
echo "🌟 WAKE UP ORION! HİBRİT GÜÇLE HAZIR!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. 🐧 Native: ./native/scripts/dev_setup.sh"
echo "2. 🐳 Docker: docker-compose up -d"
echo "3. 🔗 Bridge: ./bridge/sync/sync_native_to_docker.sh"
echo "4. 🧪 Test: docker-compose run orion-test"
echo ""
echo "🚀 HİBRİT YAKLAŞIM AKTIF!"
