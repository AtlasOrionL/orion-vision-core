#!/bin/bash
# 🔗 Docker → Native Sync
echo "🔗 DOCKER → NATIVE SYNC!"
echo "💖 DUYGULANDIK! SEN YAPARSIN!"

# Docker'dan native'e kopyala
rsync -av --delete shared/results/ native/results/
rsync -av --delete shared/logs/ native/logs/

echo "✅ Docker → Native sync tamamlandı!"
