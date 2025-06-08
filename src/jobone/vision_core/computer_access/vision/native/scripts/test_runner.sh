#!/bin/bash
# 🐧 Native Test Runner
echo "🧪 NATIVE TEST RUNNER!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"

source native/venv/bin/activate
export PYTHONPATH=$(pwd)/src

# Tests çalıştır
python -m pytest tests/ -v --cov=src --cov-report=html
echo "✅ Native tests tamamlandı!"
