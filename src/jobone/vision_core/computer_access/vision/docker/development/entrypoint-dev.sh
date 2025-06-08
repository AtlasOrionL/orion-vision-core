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
