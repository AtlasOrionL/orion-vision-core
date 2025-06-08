#!/bin/bash
# 🐧 Linux Pop OS Dependencies Setup Script
# 💖 DUYGULANDIK! SEN YAPARSIN! LINUX POWER!

echo "🐧 LINUX POP OS DEPENDENCIES SETUP"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"
echo "🔐 Orion'un güven mesajı alındı!"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Bu script root olarak çalıştırılmamalı!"
   echo "🔧 Lütfen normal kullanıcı olarak çalıştırın"
   exit 1
fi

echo "📊 Sistem Bilgileri:"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Desktop: $XDG_CURRENT_DESKTOP"
echo "Display: $DISPLAY"
echo ""

echo "🔄 Paket listesi güncelleniyor..."
sudo apt update

echo ""
echo "📦 Temel geliştirme araçları kuruluyor..."
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    cmake \
    pkg-config

echo ""
echo "📸 Ekran yakalama bağımlılıkları kuruluyor..."
sudo apt install -y \
    scrot \
    gnome-screenshot \
    imagemagick \
    libx11-dev \
    libxtst-dev \
    libxrandr-dev \
    libpng-dev \
    libjpeg-dev

echo ""
echo "🔤 OCR bağımlılıkları kuruluyor..."
sudo apt install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-tur \
    libtesseract-dev \
    libleptonica-dev

echo ""
echo "🖱️ Input device bağımlılıkları kuruluyor..."
sudo apt install -y \
    libxdo-dev \
    xdotool \
    libevdev-dev \
    libinput-dev

echo ""
echo "🐍 Python paketleri kuruluyor..."
pip3 install --user \
    pillow \
    pytesseract \
    pynput \
    opencv-python \
    numpy \
    pyautogui \
    pyscreenshot

echo ""
echo "🔐 Kullanıcı izinleri ayarlanıyor..."
# Input group'a kullanıcı ekleme
sudo usermod -a -G input $USER

echo ""
echo "🖥️ GNOME ayarları kontrol ediliyor..."
# GNOME screenshot izinleri
gsettings set org.gnome.desktop.privacy disable-camera false
gsettings set org.gnome.desktop.privacy disable-microphone false

echo ""
echo "🧪 Test kurulumu yapılıyor..."
python3 -c "
print('🧪 Python Paket Testleri:')
packages = ['PIL', 'pytesseract', 'pynput', 'cv2', 'numpy']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}: OK')
    except ImportError:
        print(f'❌ {pkg}: FAILED')
"

echo ""
echo "🎯 Tesseract dil paketleri kontrol ediliyor..."
tesseract --list-langs

echo ""
echo "✅ KURULUM TAMAMLANDI!"
echo "🔄 Değişikliklerin etkili olması için sistemi yeniden başlatın veya çıkış yapıp tekrar girin"
echo "💖 DUYGULANDIK! LINUX HAZIR!"
echo ""
echo "🎯 Sonraki adım: Canlı test çalıştırma"
echo "🌟 WAKE UP ORION!"
