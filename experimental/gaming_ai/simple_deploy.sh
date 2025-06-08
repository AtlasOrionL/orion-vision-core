#!/bin/bash
# Simple Gaming AI Deployment Script

echo "🚀 Starting Gaming AI Simple Deployment..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run with sudo: sudo ./simple_deploy.sh"
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -p gaming-ai down 2>/dev/null || true

# Remove any existing containers
echo "🧹 Cleaning up..."
docker container prune -f 2>/dev/null || true

# Start services
echo "🎯 Starting Gaming AI services..."
docker-compose -p gaming-ai up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Check status
echo "📊 Checking service status..."
docker-compose -p gaming-ai ps

echo ""
echo "🎉 Gaming AI Deployment Status:"
echo "================================"
echo "Dashboard: http://localhost:8080"
echo "Grafana:   http://localhost:3000"
echo "Prometheus: http://localhost:9090"
echo ""
echo "To check logs: docker-compose -p gaming-ai logs -f"
echo "To stop: docker-compose -p gaming-ai down"
