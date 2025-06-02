#!/bin/bash
# Orion Vision Core - Deployment Test Script
# Phase 3: Hybrid Local Deployment Validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TIMEOUT=30
RETRY_COUNT=3
TEST_RESULTS=()

# Functions
log_info() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TEST_RESULTS+=("PASS: $1")
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    TEST_RESULTS+=("FAIL: $1")
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    TEST_RESULTS+=("WARN: $1")
}

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 🧪 ORION DEPLOYMENT TEST                    ║"
    echo "║              Phase 3: Hybrid Local Validation              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=${3:-30}
    
    log_info "Waiting for $service_name to be ready..."
    
    for i in $(seq 1 $max_attempts); do
        if curl -f -s "$url" > /dev/null 2>&1; then
            log_success "$service_name is ready"
            return 0
        fi
        
        if [ $i -eq $max_attempts ]; then
            log_error "$service_name failed to start after $max_attempts attempts"
            return 1
        fi
        
        sleep 2
    done
}

test_docker_services() {
    log_info "Testing Docker services..."
    
    # Check if docker-compose is running
    if ! docker-compose ps > /dev/null 2>&1; then
        log_error "Docker Compose is not running"
        return 1
    fi
    
    # Check individual services
    local services=("rabbitmq" "python-core" "hybrid-bridge" "ollama")
    
    for service in "${services[@]}"; do
        local status=$(docker-compose ps -q $service | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
        
        case $status in
            "healthy")
                log_success "Docker service $service is healthy"
                ;;
            "starting")
                log_warning "Docker service $service is starting"
                ;;
            "unhealthy"|"unknown")
                log_error "Docker service $service is unhealthy or not found"
                ;;
        esac
    done
}

test_api_endpoints() {
    log_info "Testing API endpoints..."
    
    # Test Python Core API
    if wait_for_service "Python Core API" "http://localhost:8001/health"; then
        # Test specific endpoints
        local endpoints=("/health" "/status")
        
        for endpoint in "${endpoints[@]}"; do
            if curl -f -s "http://localhost:8001$endpoint" > /dev/null; then
                log_success "Python Core endpoint $endpoint is responding"
            else
                log_error "Python Core endpoint $endpoint is not responding"
            fi
        done
    fi
    
    # Test Hybrid Bridge API
    if wait_for_service "Hybrid Bridge API" "http://localhost:8000/health"; then
        local endpoints=("/health" "/status" "/api/services")
        
        for endpoint in "${endpoints[@]}"; do
            if curl -f -s "http://localhost:8000$endpoint" > /dev/null; then
                log_success "Bridge endpoint $endpoint is responding"
            else
                log_error "Bridge endpoint $endpoint is not responding"
            fi
        done
    fi
}

test_message_routing() {
    log_info "Testing message routing..."
    
    # Test bridge message routing
    local test_message='{"target": "test_queue", "message": {"test": "deployment_validation", "timestamp": "'$(date -Iseconds)'"}}'
    
    local response=$(curl -s -X POST "http://localhost:8000/api/message" \
        -H "Content-Type: application/json" \
        -d "$test_message" 2>/dev/null)
    
    if echo "$response" | grep -q "routed"; then
        log_success "Message routing is working"
    else
        log_error "Message routing failed: $response"
    fi
}

test_rabbitmq() {
    log_info "Testing RabbitMQ..."
    
    # Test RabbitMQ Management UI
    if wait_for_service "RabbitMQ Management" "http://localhost:15672"; then
        # Test API with credentials
        local auth_response=$(curl -s -u "orion:orion123" "http://localhost:15672/api/overview" 2>/dev/null)
        
        if echo "$auth_response" | grep -q "rabbitmq_version"; then
            log_success "RabbitMQ API is accessible with credentials"
        else
            log_error "RabbitMQ API authentication failed"
        fi
    fi
}

test_ollama() {
    log_info "Testing Ollama LLM..."
    
    if wait_for_service "Ollama" "http://localhost:11434/api/tags"; then
        # Test if models are available
        local models_response=$(curl -s "http://localhost:11434/api/tags" 2>/dev/null)
        
        if echo "$models_response" | grep -q "models"; then
            log_success "Ollama is responding with models list"
        else
            log_warning "Ollama is running but no models found"
        fi
    fi
}

test_monitoring() {
    log_info "Testing monitoring stack..."
    
    # Test Prometheus
    if wait_for_service "Prometheus" "http://localhost:9090/-/healthy" 10; then
        log_success "Prometheus is healthy"
    else
        log_warning "Prometheus is not accessible (optional service)"
    fi
    
    # Test Grafana
    if wait_for_service "Grafana" "http://localhost:3000/api/health" 10; then
        log_success "Grafana is healthy"
    else
        log_warning "Grafana is not accessible (optional service)"
    fi
}

test_web_access() {
    log_info "Testing web access..."
    
    # Test main dashboard
    if curl -f -s "http://orion.local" > /dev/null 2>&1; then
        log_success "Main dashboard is accessible at http://orion.local"
    else
        log_error "Main dashboard is not accessible at http://orion.local"
        
        # Check if nginx is running
        if docker-compose ps nginx | grep -q "Up"; then
            log_info "Nginx is running, checking /etc/hosts..."
            if grep -q "orion.local" /etc/hosts; then
                log_warning "orion.local is in /etc/hosts but not resolving"
            else
                log_error "orion.local is not in /etc/hosts"
            fi
        else
            log_error "Nginx is not running"
        fi
    fi
}

test_kubernetes() {
    log_info "Testing Kubernetes integration..."
    
    # Check if kubectl is available
    if command -v kubectl > /dev/null 2>&1; then
        # Check if cluster is accessible
        if kubectl cluster-info > /dev/null 2>&1; then
            log_success "Kubernetes cluster is accessible"
            
            # Check Orion namespace
            if kubectl get namespace orion-system > /dev/null 2>&1; then
                log_success "Orion namespace exists"
                
                # Check pods
                local pod_count=$(kubectl get pods -n orion-system --no-headers 2>/dev/null | wc -l)
                if [ "$pod_count" -gt 0 ]; then
                    log_success "Found $pod_count pods in orion-system namespace"
                else
                    log_warning "No pods found in orion-system namespace"
                fi
            else
                log_warning "Orion namespace not found"
            fi
        else
            log_warning "Kubernetes cluster is not accessible"
        fi
    else
        log_warning "kubectl not found - Kubernetes tests skipped"
    fi
}

test_performance() {
    log_info "Testing basic performance..."
    
    # Test response times
    local start_time=$(date +%s%N)
    curl -f -s "http://localhost:8000/health" > /dev/null 2>&1
    local end_time=$(date +%s%N)
    local response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [ "$response_time" -lt 1000 ]; then
        log_success "Bridge response time: ${response_time}ms (good)"
    elif [ "$response_time" -lt 5000 ]; then
        log_warning "Bridge response time: ${response_time}ms (acceptable)"
    else
        log_error "Bridge response time: ${response_time}ms (too slow)"
    fi
}

generate_test_report() {
    echo ""
    echo -e "${BLUE}📊 TEST REPORT${NC}"
    echo "=============="
    
    local pass_count=0
    local fail_count=0
    local warn_count=0
    
    for result in "${TEST_RESULTS[@]}"; do
        echo "• $result"
        
        if [[ $result == PASS:* ]]; then
            ((pass_count++))
        elif [[ $result == FAIL:* ]]; then
            ((fail_count++))
        elif [[ $result == WARN:* ]]; then
            ((warn_count++))
        fi
    done
    
    echo ""
    echo -e "${GREEN}✅ Passed: $pass_count${NC}"
    echo -e "${YELLOW}⚠️  Warnings: $warn_count${NC}"
    echo -e "${RED}❌ Failed: $fail_count${NC}"
    
    echo ""
    if [ "$fail_count" -eq 0 ]; then
        echo -e "${GREEN}🎉 DEPLOYMENT TEST SUCCESSFUL!${NC}"
        echo ""
        echo -e "${BLUE}🚀 Next Steps:${NC}"
        echo "1. Open http://orion.local in your browser"
        echo "2. Explore the dashboard and test agent functionality"
        echo "3. Check monitoring at http://localhost:3000"
        echo "4. Proceed with feature integration"
        return 0
    else
        echo -e "${RED}❌ DEPLOYMENT TEST FAILED!${NC}"
        echo ""
        echo -e "${BLUE}🔧 Troubleshooting:${NC}"
        echo "1. Check logs: docker-compose logs -f"
        echo "2. Restart services: docker-compose restart"
        echo "3. Check system resources: docker stats"
        echo "4. Review error messages above"
        return 1
    fi
}

# Main test execution
main() {
    print_banner
    
    log_info "Starting deployment validation..."
    
    # Run all tests
    test_docker_services
    test_api_endpoints
    test_message_routing
    test_rabbitmq
    test_ollama
    test_monitoring
    test_web_access
    test_kubernetes
    test_performance
    
    # Generate report
    generate_test_report
}

# Run tests
main "$@"
