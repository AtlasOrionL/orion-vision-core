#!/bin/bash
# 🔗 Native → Docker Sync
echo "🔗 NATIVE → DOCKER SYNC!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"

# Shared volume'a kopyala
rsync -av --delete src/ shared/src/
rsync -av --delete tests/ shared/tests/

echo "✅ Native → Docker sync tamamlandı!"
