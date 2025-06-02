#!/bin/bash
# Orion Vision Core - Production Deployment Script
# Sprint 4.3 - Production Deployment & Advanced Monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" >&2
}

info() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️  $1${NC}"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-production}"
NAMESPACE="${NAMESPACE:-orion-system}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-orion-registry.company.com}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
KUBECTL_CONTEXT="${KUBECTL_CONTEXT:-production-cluster}"

# Deployment options
DEPLOY_MONITORING="${DEPLOY_MONITORING:-true}"
DEPLOY_LOGGING="${DEPLOY_LOGGING:-true}"
DEPLOY_TRACING="${DEPLOY_TRACING:-true}"
ENABLE_AUTOSCALING="${ENABLE_AUTOSCALING:-true}"
DRY_RUN="${DRY_RUN:-false}"

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check required tools
    local required_tools=("kubectl" "docker" "helm")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "$tool is not installed or not in PATH"
            exit 1
        fi
    done
    
    # Check kubectl context
    local current_context=$(kubectl config current-context)
    if [ "$current_context" != "$KUBECTL_CONTEXT" ]; then
        warn "Current kubectl context is '$current_context', expected '$KUBECTL_CONTEXT'"
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Function to build and push Docker image
build_and_push_image() {
    log "Building and pushing Docker image..."
    
    local image_name="$DOCKER_REGISTRY/orion-vision-core:$IMAGE_TAG"
    
    # Build image
    log "Building Docker image: $image_name"
    docker build \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VERSION="$IMAGE_TAG" \
        --build-arg VCS_REF="$(git rev-parse HEAD)" \
        -t "$image_name" \
        -f "$PROJECT_ROOT/docker/Dockerfile" \
        "$PROJECT_ROOT"
    
    # Push image
    if [ "$DRY_RUN" != "true" ]; then
        log "Pushing Docker image: $image_name"
        docker push "$image_name"
    else
        info "DRY RUN: Would push image $image_name"
    fi
    
    success "Docker image built and pushed"
}

# Function to create namespace
create_namespace() {
    log "Creating namespace: $NAMESPACE"
    
    if [ "$DRY_RUN" != "true" ]; then
        kubectl apply -f "$SCRIPT_DIR/kubernetes/namespace.yaml"
    else
        info "DRY RUN: Would create namespace"
        kubectl apply -f "$SCRIPT_DIR/kubernetes/namespace.yaml" --dry-run=client
    fi
    
    success "Namespace created"
}

# Function to deploy configuration
deploy_configuration() {
    log "Deploying configuration..."
    
    if [ "$DRY_RUN" != "true" ]; then
        kubectl apply -f "$SCRIPT_DIR/kubernetes/configmap.yaml"
    else
        info "DRY RUN: Would deploy configuration"
        kubectl apply -f "$SCRIPT_DIR/kubernetes/configmap.yaml" --dry-run=client
    fi
    
    success "Configuration deployed"
}

# Function to deploy storage
deploy_storage() {
    log "Deploying storage resources..."
    
    if [ "$DRY_RUN" != "true" ]; then
        kubectl apply -f "$SCRIPT_DIR/kubernetes/storage.yaml"
    else
        info "DRY RUN: Would deploy storage"
        kubectl apply -f "$SCRIPT_DIR/kubernetes/storage.yaml" --dry-run=client
    fi
    
    success "Storage resources deployed"
}

# Function to deploy core application
deploy_core_application() {
    log "Deploying core application..."
    
    # Update image tag in deployment
    local temp_deployment=$(mktemp)
    sed "s|orion-vision-core:1.0.0|$DOCKER_REGISTRY/orion-vision-core:$IMAGE_TAG|g" \
        "$SCRIPT_DIR/kubernetes/deployment.yaml" > "$temp_deployment"
    
    if [ "$DRY_RUN" != "true" ]; then
        kubectl apply -f "$temp_deployment"
    else
        info "DRY RUN: Would deploy core application"
        kubectl apply -f "$temp_deployment" --dry-run=client
    fi
    
    rm "$temp_deployment"
    success "Core application deployed"
}

# Function to deploy services
deploy_services() {
    log "Deploying services..."
    
    if [ "$DRY_RUN" != "true" ]; then
        kubectl apply -f "$SCRIPT_DIR/kubernetes/service.yaml"
    else
        info "DRY RUN: Would deploy services"
        kubectl apply -f "$SCRIPT_DIR/kubernetes/service.yaml" --dry-run=client
    fi
    
    success "Services deployed"
}

# Function to deploy ingress
deploy_ingress() {
    log "Deploying ingress..."
    
    if [ "$DRY_RUN" != "true" ]; then
        kubectl apply -f "$SCRIPT_DIR/kubernetes/ingress.yaml"
    else
        info "DRY RUN: Would deploy ingress"
        kubectl apply -f "$SCRIPT_DIR/kubernetes/ingress.yaml" --dry-run=client
    fi
    
    success "Ingress deployed"
}

# Function to deploy autoscaling
deploy_autoscaling() {
    if [ "$ENABLE_AUTOSCALING" != "true" ]; then
        info "Autoscaling disabled, skipping..."
        return
    fi
    
    log "Deploying autoscaling resources..."
    
    if [ "$DRY_RUN" != "true" ]; then
        kubectl apply -f "$SCRIPT_DIR/kubernetes/autoscaling.yaml"
    else
        info "DRY RUN: Would deploy autoscaling"
        kubectl apply -f "$SCRIPT_DIR/kubernetes/autoscaling.yaml" --dry-run=client
    fi
    
    success "Autoscaling resources deployed"
}

# Function to deploy monitoring
deploy_monitoring() {
    if [ "$DEPLOY_MONITORING" != "true" ]; then
        info "Monitoring disabled, skipping..."
        return
    fi
    
    log "Deploying monitoring stack..."
    
    # Deploy Prometheus
    if [ "$DRY_RUN" != "true" ]; then
        helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
            --namespace monitoring \
            --create-namespace \
            --values "$SCRIPT_DIR/../monitoring/prometheus/values.yaml" \
            --wait
    else
        info "DRY RUN: Would deploy Prometheus"
    fi
    
    success "Monitoring stack deployed"
}

# Function to wait for deployment
wait_for_deployment() {
    log "Waiting for deployment to be ready..."
    
    if [ "$DRY_RUN" != "true" ]; then
        kubectl rollout status deployment/orion-core -n "$NAMESPACE" --timeout=600s
        kubectl rollout status deployment/orion-redis -n "$NAMESPACE" --timeout=300s
    else
        info "DRY RUN: Would wait for deployment"
    fi
    
    success "Deployment is ready"
}

# Function to run health checks
run_health_checks() {
    log "Running health checks..."
    
    if [ "$DRY_RUN" == "true" ]; then
        info "DRY RUN: Would run health checks"
        return
    fi
    
    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=orion-vision-core -n "$NAMESPACE" --timeout=300s
    
    # Check service endpoints
    local service_ip=$(kubectl get service orion-core-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    
    # Health check
    if kubectl run health-check --rm -i --restart=Never --image=curlimages/curl -- \
        curl -f "http://$service_ip:8000/health" --max-time 10; then
        success "Health check passed"
    else
        error "Health check failed"
        exit 1
    fi
}

# Function to display deployment info
display_deployment_info() {
    log "Deployment Information"
    echo
    info "Namespace: $NAMESPACE"
    info "Image: $DOCKER_REGISTRY/orion-vision-core:$IMAGE_TAG"
    info "Environment: $DEPLOYMENT_ENV"
    echo
    
    if [ "$DRY_RUN" != "true" ]; then
        info "Pods:"
        kubectl get pods -n "$NAMESPACE" -o wide
        echo
        
        info "Services:"
        kubectl get services -n "$NAMESPACE"
        echo
        
        info "Ingress:"
        kubectl get ingress -n "$NAMESPACE"
        echo
        
        if [ "$ENABLE_AUTOSCALING" == "true" ]; then
            info "HPA Status:"
            kubectl get hpa -n "$NAMESPACE"
            echo
        fi
    fi
}

# Function to cleanup on failure
cleanup_on_failure() {
    error "Deployment failed, cleaning up..."
    
    if [ "$DRY_RUN" != "true" ]; then
        kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    fi
}

# Main deployment function
main() {
    echo -e "${PURPLE}"
    echo "🚀 Orion Vision Core - Production Deployment"
    echo "Sprint 4.3 - Production Deployment & Advanced Monitoring"
    echo "=============================================="
    echo -e "${NC}"
    
    info "Deployment Configuration:"
    info "  Environment: $DEPLOYMENT_ENV"
    info "  Namespace: $NAMESPACE"
    info "  Image Tag: $IMAGE_TAG"
    info "  Registry: $DOCKER_REGISTRY"
    info "  Monitoring: $DEPLOY_MONITORING"
    info "  Autoscaling: $ENABLE_AUTOSCALING"
    info "  Dry Run: $DRY_RUN"
    echo
    
    # Trap for cleanup on failure
    trap cleanup_on_failure ERR
    
    # Deployment steps
    check_prerequisites
    build_and_push_image
    create_namespace
    deploy_configuration
    deploy_storage
    deploy_core_application
    deploy_services
    deploy_ingress
    deploy_autoscaling
    deploy_monitoring
    wait_for_deployment
    run_health_checks
    display_deployment_info
    
    success "🎉 Orion Vision Core deployed successfully!"
    
    echo
    info "Access URLs:"
    if [ "$DRY_RUN" != "true" ]; then
        local ingress_ip=$(kubectl get ingress orion-core-ingress -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [ -n "$ingress_ip" ]; then
            info "  API: https://$ingress_ip"
            info "  Discovery: https://$ingress_ip:8001"
            info "  Orchestration: https://$ingress_ip:8002"
        else
            info "  Use port-forward: kubectl port-forward service/orion-core-service 8000:8000 -n $NAMESPACE"
        fi
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --no-monitoring)
            DEPLOY_MONITORING="false"
            shift
            ;;
        --no-autoscaling)
            ENABLE_AUTOSCALING="false"
            shift
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --registry)
            DOCKER_REGISTRY="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --dry-run           Perform a dry run without making changes"
            echo "  --no-monitoring     Skip monitoring stack deployment"
            echo "  --no-autoscaling    Skip autoscaling configuration"
            echo "  --tag TAG           Docker image tag (default: latest)"
            echo "  --namespace NS      Kubernetes namespace (default: orion-system)"
            echo "  --registry REG      Docker registry (default: orion-registry.company.com)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
