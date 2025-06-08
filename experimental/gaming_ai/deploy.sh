#!/bin/bash
# 🚀 Gaming AI Production Deployment Script
# Automated deployment for Gaming AI system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="gaming-ai"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deployment.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    echo "[ERROR] $1" >> "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
    echo "[WARNING] $1" >> "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
    echo "[INFO] $1" >> "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    log "✅ Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log "📁 Creating necessary directories..."
    
    mkdir -p logs data config backups
    mkdir -p docker/nginx docker/grafana/dashboards docker/grafana/datasources
    
    log "✅ Directories created"
}

# Generate configuration files
generate_configs() {
    log "⚙️ Generating configuration files..."
    
    # Generate .env file if not exists
    if [ ! -f .env ]; then
        cat > .env << EOF
# Gaming AI Production Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# Database
POSTGRES_DB=gaming_ai
POSTGRES_USER=gaming_ai
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Redis
REDIS_PASSWORD=$(openssl rand -base64 32)

# Security
SECRET_KEY=$(openssl rand -base64 64)
JWT_SECRET=$(openssl rand -base64 64)

# Ollama
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b

# Monitoring
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)

# Ports
DASHBOARD_PORT=8080
API_PORT=8081
METRICS_PORT=8082
EOF
        log "✅ Generated .env file"
    else
        info ".env file already exists"
    fi
    
    # Generate nginx config
    cat > docker/nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream gaming_ai_backend {
        server gaming-ai-core:8080;
    }
    
    upstream gaming_ai_api {
        server gaming-ai-core:8081;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://gaming_ai_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /api/ {
            proxy_pass http://gaming_ai_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /ws {
            proxy_pass http://gaming_ai_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
EOF
    
    log "✅ Generated nginx configuration"
}

# Build and deploy
deploy() {
    log "🚀 Starting Gaming AI deployment..."
    
    # Pull latest images
    log "📥 Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" pull
    
    # Build custom images
    log "🔨 Building Gaming AI images..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache
    
    # Start services
    log "🎯 Starting services..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
    
    # Wait for services to be ready
    log "⏳ Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_health
    
    log "🎉 Gaming AI deployment completed successfully!"
}

# Check service health
check_health() {
    log "🏥 Checking service health..."
    
    local services=("gaming-ai-core" "gaming-ai-ollama" "gaming-ai-redis" "gaming-ai-postgres")
    local failed_services=()
    
    for service in "${services[@]}"; do
        if docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps "$service" | grep -q "Up"; then
            log "✅ $service is running"
        else
            error "❌ $service is not running"
            failed_services+=("$service")
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        log "✅ All services are healthy"
        
        # Test API endpoint
        if curl -f http://localhost:8080/api/status &> /dev/null; then
            log "✅ API endpoint is responding"
        else
            warning "⚠️ API endpoint is not responding yet"
        fi
    else
        error "❌ Some services failed to start: ${failed_services[*]}"
        return 1
    fi
}

# Backup data
backup() {
    log "💾 Creating backup..."
    
    local backup_name="gaming_ai_backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup database
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T postgres pg_dump -U gaming_ai gaming_ai > "$backup_path/database.sql"
    
    # Backup volumes
    docker run --rm -v gaming_ai_data:/data -v "$PWD/$backup_path":/backup alpine tar czf /backup/data.tar.gz -C /data .
    
    log "✅ Backup created: $backup_path"
}

# Stop services
stop() {
    log "🛑 Stopping Gaming AI services..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    log "✅ Services stopped"
}

# Restart services
restart() {
    log "🔄 Restarting Gaming AI services..."
    stop
    deploy
}

# Show logs
logs() {
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "${1:-gaming-ai-core}"
}

# Show status
status() {
    log "📊 Gaming AI Status:"
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
    
    echo ""
    log "🌐 Service URLs:"
    echo "  Dashboard: http://localhost:8080"
    echo "  Grafana:   http://localhost:3000"
    echo "  Prometheus: http://localhost:9090"
}

# Main script
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_directories
            generate_configs
            deploy
            status
            ;;
        "stop")
            stop
            ;;
        "restart")
            restart
            ;;
        "backup")
            backup
            ;;
        "logs")
            logs "$2"
            ;;
        "status")
            status
            ;;
        "health")
            check_health
            ;;
        *)
            echo "Usage: $0 {deploy|stop|restart|backup|logs|status|health}"
            echo ""
            echo "Commands:"
            echo "  deploy  - Deploy Gaming AI (default)"
            echo "  stop    - Stop all services"
            echo "  restart - Restart all services"
            echo "  backup  - Create backup"
            echo "  logs    - Show logs [service]"
            echo "  status  - Show service status"
            echo "  health  - Check service health"
            exit 1
            ;;
    esac
}

# Create log directory
mkdir -p logs

# Run main function
main "$@"
