# 🚀 Gaming AI Deployment Guide

Complete guide for deploying Gaming AI in production environments.

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB available space
- **CPU**: 4+ cores recommended
- **GPU**: NVIDIA GPU (optional, for Ollama AI)

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl

## Installation

### 1. Install Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Clone Repository
```bash
git clone <repository-url>
cd gaming_ai
```

## Deployment

### Quick Deployment
```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy with default settings
./deploy.sh deploy
```

### Custom Deployment
```bash
# Edit environment variables
cp .env.example .env
nano .env

# Deploy with custom configuration
./deploy.sh deploy
```

## Configuration

### Environment Variables (.env)
```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# Database
POSTGRES_DB=gaming_ai
POSTGRES_USER=gaming_ai
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_redis_password

# Security
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret

# AI
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b

# Monitoring
GRAFANA_ADMIN_PASSWORD=your_grafana_password
```

### Docker Compose Override
Create `docker-compose.override.yml` for custom configurations:
```yaml
version: '3.8'
services:
  gaming-ai-core:
    environment:
      - CUSTOM_SETTING=value
    ports:
      - "8080:8080"
```

## Service Management

### Start Services
```bash
./deploy.sh deploy
```

### Stop Services
```bash
./deploy.sh stop
```

### Restart Services
```bash
./deploy.sh restart
```

### View Logs
```bash
# All services
./deploy.sh logs

# Specific service
./deploy.sh logs gaming-ai-core
```

### Check Status
```bash
./deploy.sh status
```

### Health Check
```bash
./deploy.sh health
```

## Monitoring

### Access Points
- **Dashboard**: http://localhost:8080
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

### Grafana Setup
1. Login with admin/gaming_ai_admin
2. Import dashboards from `/docker/grafana/dashboards/`
3. Configure data sources

### Prometheus Metrics
- Application metrics: http://localhost:8082/metrics
- System metrics: Node Exporter
- Container metrics: cAdvisor

## Backup & Recovery

### Create Backup
```bash
./deploy.sh backup
```

### Restore from Backup
```bash
# Stop services
./deploy.sh stop

# Restore database
docker-compose exec postgres psql -U gaming_ai -d gaming_ai < backup.sql

# Restore volumes
docker run --rm -v gaming_ai_data:/data -v ./backup:/backup alpine tar xzf /backup/data.tar.gz -C /data

# Start services
./deploy.sh deploy
```

## Security

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### SSL/TLS Setup
```bash
# Generate certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048   -keyout docker/nginx/ssl/gaming-ai.key   -out docker/nginx/ssl/gaming-ai.crt

# Update nginx configuration
# Uncomment SSL sections in docker/nginx/nginx.conf
```

### Security Best Practices
- Change default passwords
- Use strong secrets
- Enable firewall
- Regular updates
- Monitor logs

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8080

# Kill the process or change port in docker-compose.yml
```

#### Out of Memory
```bash
# Check memory usage
docker stats

# Increase Docker memory limits
# Edit /etc/docker/daemon.json
```

#### Permission Denied
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

#### Service Won't Start
```bash
# Check logs
./deploy.sh logs service-name

# Check configuration
docker-compose config
```

### Log Analysis
```bash
# Application logs
./deploy.sh logs gaming-ai-core

# System logs
journalctl -u docker

# Container logs
docker logs gaming-ai-core
```

## Performance Tuning

### Docker Optimization
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
```

### Database Tuning
```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

### Redis Optimization
```bash
# Redis configuration
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
```

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  gaming-ai-core:
    deploy:
      replicas: 3
```

### Load Balancing
```nginx
upstream gaming_ai_backend {
    server gaming-ai-core-1:8080;
    server gaming-ai-core-2:8080;
    server gaming-ai-core-3:8080;
}
```

## Maintenance

### Regular Tasks
- Monitor disk space
- Check logs for errors
- Update containers
- Backup data
- Security updates

### Update Procedure
```bash
# Backup first
./deploy.sh backup

# Pull latest images
docker-compose pull

# Restart with new images
./deploy.sh restart
```
