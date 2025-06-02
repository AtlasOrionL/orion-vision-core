#!/bin/bash
# Orion Vision Core - Hybrid Local Deployment Script
# Phase 3: Python Core + Local Kubernetes Integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_MODE=${1:-"hybrid"}  # hybrid, python-only, k8s-only
PROJECT_ROOT=$(pwd)
CLUSTER_NAME="orion-local"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 🚀 ORION VISION CORE                        ║"
    echo "║              Phase 3: Hybrid Local Deployment              ║"
    echo "║                                                              ║"
    echo "║  Python Core + Local Kubernetes Integration                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_prerequisites() {
    log_step "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        missing_tools+=("docker-compose")
    fi
    
    # Check kubectl (for hybrid/k8s mode)
    if [[ "$DEPLOYMENT_MODE" != "python-only" ]] && ! command -v kubectl &> /dev/null; then
        missing_tools+=("kubectl")
    fi
    
    # Check minikube or kind (for hybrid/k8s mode)
    if [[ "$DEPLOYMENT_MODE" != "python-only" ]]; then
        if ! command -v minikube &> /dev/null && ! command -v kind &> /dev/null; then
            missing_tools+=("minikube or kind")
        fi
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install the missing tools and try again."
        exit 1
    fi
    
    log_success "All prerequisites satisfied"
}

setup_directories() {
    log_step "Setting up directories..."
    
    # Create necessary directories
    mkdir -p logs data config monitoring/prometheus monitoring/grafana nginx/conf.d
    
    # Set permissions
    chmod 755 logs data
    
    log_success "Directories created"
}

deploy_python_core() {
    log_step "Deploying Python Core services..."
    
    # Copy source code
    if [ -d "../src/jobone/vision_core" ]; then
        cp -r ../src/jobone/vision_core/* python-core/src/
        log_info "Source code copied from ../src/"
    else
        log_warning "Source code not found at ../src/, using local files"
    fi
    
    # Start Python services
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d rabbitmq ollama python-core hybrid-bridge
    else
        docker compose up -d rabbitmq ollama python-core hybrid-bridge
    fi
    
    log_success "Python Core services started"
}

deploy_monitoring() {
    log_step "Deploying monitoring stack..."
    
    # Create Prometheus config if not exists
    if [ ! -f "monitoring/prometheus/prometheus.yml" ]; then
        cat > monitoring/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'orion-python-core'
    static_configs:
      - targets: ['python-core:8001']
  
  - job_name: 'orion-bridge'
    static_configs:
      - targets: ['hybrid-bridge:8000']
  
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq:15692']
EOF
    fi
    
    # Start monitoring services
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d prometheus grafana
    else
        docker compose up -d prometheus grafana
    fi
    
    log_success "Monitoring stack deployed"
}

deploy_kubernetes() {
    log_step "Deploying local Kubernetes cluster..."
    
    # Run Kubernetes setup script
    if [ -f "kubernetes/local-cluster-setup.sh" ]; then
        chmod +x kubernetes/local-cluster-setup.sh
        ./kubernetes/local-cluster-setup.sh
    else
        log_error "Kubernetes setup script not found"
        return 1
    fi
    
    log_success "Kubernetes cluster deployed"
}

setup_networking() {
    log_step "Setting up networking..."
    
    # Create nginx config if not exists
    if [ ! -f "nginx/conf.d/orion.conf" ]; then
        cat > nginx/conf.d/orion.conf << EOF
upstream python_core {
    server python-core:8001;
}

upstream hybrid_bridge {
    server hybrid-bridge:8000;
}

upstream grafana {
    server grafana:3000;
}

server {
    listen 80;
    server_name orion.local;
    
    location / {
        proxy_pass http://hybrid_bridge;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
    
    location /api/python/ {
        proxy_pass http://python_core/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /grafana/ {
        proxy_pass http://grafana/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /rabbitmq/ {
        proxy_pass http://rabbitmq:15672/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
    fi
    
    # Start nginx
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d nginx
    else
        docker compose up -d nginx
    fi
    
    # Add to /etc/hosts if not exists
    if ! grep -q "orion.local" /etc/hosts; then
        echo "127.0.0.1 orion.local" | sudo tee -a /etc/hosts
        log_info "Added orion.local to /etc/hosts"
    fi
    
    log_success "Networking configured"
}

wait_for_services() {
    log_step "Waiting for services to be ready..."
    
    local services=("rabbitmq:15672" "python-core:8001" "hybrid-bridge:8000")
    
    for service in "${services[@]}"; do
        local host=$(echo $service | cut -d: -f1)
        local port=$(echo $service | cut -d: -f2)
        
        log_info "Waiting for $host:$port..."
        
        for i in {1..30}; do
            if docker exec orion-$host curl -f http://localhost:$port/health &> /dev/null; then
                log_success "$host is ready"
                break
            fi
            
            if [ $i -eq 30 ]; then
                log_warning "$host is not responding after 30 attempts"
            fi
            
            sleep 2
        done
    done
}

test_deployment() {
    log_step "Testing deployment..."
    
    # Test Python Core
    if curl -f http://localhost:8001/health &> /dev/null; then
        log_success "✅ Python Core is responding"
    else
        log_error "❌ Python Core is not responding"
    fi
    
    # Test Bridge
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "✅ Hybrid Bridge is responding"
    else
        log_error "❌ Hybrid Bridge is not responding"
    fi
    
    # Test RabbitMQ
    if curl -f http://localhost:15672 &> /dev/null; then
        log_success "✅ RabbitMQ Management is accessible"
    else
        log_error "❌ RabbitMQ Management is not accessible"
    fi
    
    # Test Nginx
    if curl -f http://orion.local &> /dev/null; then
        log_success "✅ Nginx reverse proxy is working"
    else
        log_error "❌ Nginx reverse proxy is not working"
    fi
}

print_access_info() {
    echo ""
    echo -e "${GREEN}🎉 Orion Vision Core Hybrid Local Deployment Completed!${NC}"
    echo "=================================================================="
    echo ""
    echo -e "${BLUE}📊 Access Information:${NC}"
    echo "• Main Dashboard: http://orion.local"
    echo "• Python Core API: http://localhost:8001"
    echo "• Hybrid Bridge: http://localhost:8000"
    echo "• RabbitMQ Management: http://localhost:15672 (orion/orion123)"
    echo "• Prometheus: http://localhost:9090"
    echo "• Grafana: http://localhost:3000 (admin/orion123)"
    echo ""
    echo -e "${BLUE}🔧 Useful Commands:${NC}"
    echo "• View logs: docker-compose logs -f [service-name]"
    echo "• Check status: docker-compose ps"
    echo "• Stop services: docker-compose down"
    echo "• Restart service: docker-compose restart [service-name]"
    
    if [[ "$DEPLOYMENT_MODE" != "python-only" ]]; then
        echo "• Check K8s pods: kubectl get pods -n orion-system"
        echo "• K8s dashboard: minikube dashboard -p $CLUSTER_NAME"
    fi
    
    echo ""
    echo -e "${BLUE}🚀 Next Steps:${NC}"
    echo "1. Open http://orion.local in your browser"
    echo "2. Check service health at http://orion.local/status"
    echo "3. Monitor with Grafana at http://localhost:3000"
    echo "4. Test agent communication via the dashboard"
    echo ""
}

cleanup_on_error() {
    log_error "Deployment failed. Cleaning up..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    exit 1
}

# Main deployment function
main() {
    # Set error handler
    trap cleanup_on_error ERR
    
    print_banner
    
    log_info "Deployment mode: $DEPLOYMENT_MODE"
    
    check_prerequisites
    setup_directories
    
    case "$DEPLOYMENT_MODE" in
        "python-only")
            deploy_python_core
            deploy_monitoring
            setup_networking
            ;;
        "k8s-only")
            deploy_kubernetes
            ;;
        "hybrid"|*)
            deploy_python_core
            deploy_monitoring
            deploy_kubernetes
            setup_networking
            ;;
    esac
    
    wait_for_services
    test_deployment
    print_access_info
}

# Show usage if help requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [deployment-mode]"
    echo ""
    echo "Deployment modes:"
    echo "  hybrid      - Python Core + Local Kubernetes (default)"
    echo "  python-only - Only Python Core services"
    echo "  k8s-only    - Only Kubernetes cluster"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy in hybrid mode"
    echo "  $0 python-only       # Deploy only Python services"
    echo "  $0 k8s-only          # Deploy only Kubernetes"
    exit 0
fi

# Run main function
main "$@"
