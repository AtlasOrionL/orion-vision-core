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
