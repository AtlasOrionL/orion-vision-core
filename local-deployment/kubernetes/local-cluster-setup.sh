#!/bin/bash
# Local Kubernetes Cluster Setup for Orion Vision Core
# Phase 3: Hybrid Local Deployment

set -e

echo "🚀 Setting up Local Kubernetes Cluster for Orion Vision Core"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="orion-local"
NAMESPACE="orion-system"
MINIKUBE_MEMORY="8192"
MINIKUBE_CPUS="4"
MINIKUBE_DISK="50g"

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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    log_success "Docker is installed"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    log_success "kubectl is installed"
    
    # Check if minikube or kind is available
    if command -v minikube &> /dev/null; then
        CLUSTER_TYPE="minikube"
        log_success "Minikube is available"
    elif command -v kind &> /dev/null; then
        CLUSTER_TYPE="kind"
        log_success "Kind is available"
    else
        log_error "Neither minikube nor kind is installed. Please install one of them."
        exit 1
    fi
}

start_cluster() {
    log_info "Starting local Kubernetes cluster..."
    
    if [ "$CLUSTER_TYPE" = "minikube" ]; then
        start_minikube
    elif [ "$CLUSTER_TYPE" = "kind" ]; then
        start_kind
    fi
}

start_minikube() {
    log_info "Starting Minikube cluster..."
    
    # Check if cluster already exists
    if minikube status -p $CLUSTER_NAME &> /dev/null; then
        log_warning "Minikube cluster '$CLUSTER_NAME' already exists"
        minikube start -p $CLUSTER_NAME
    else
        minikube start \
            -p $CLUSTER_NAME \
            --memory=$MINIKUBE_MEMORY \
            --cpus=$MINIKUBE_CPUS \
            --disk-size=$MINIKUBE_DISK \
            --driver=docker \
            --kubernetes-version=v1.28.0
    fi
    
    # Enable addons
    log_info "Enabling Minikube addons..."
    minikube addons enable ingress -p $CLUSTER_NAME
    minikube addons enable metrics-server -p $CLUSTER_NAME
    minikube addons enable dashboard -p $CLUSTER_NAME
    
    # Set kubectl context
    kubectl config use-context $CLUSTER_NAME
    
    log_success "Minikube cluster started successfully"
}

start_kind() {
    log_info "Starting Kind cluster..."
    
    # Create kind config
    cat > /tmp/kind-config.yaml << EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: $CLUSTER_NAME
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 8080
    hostPort: 8080
    protocol: TCP
- role: worker
- role: worker
EOF
    
    # Create cluster
    if kind get clusters | grep -q $CLUSTER_NAME; then
        log_warning "Kind cluster '$CLUSTER_NAME' already exists"
    else
        kind create cluster --config /tmp/kind-config.yaml
    fi
    
    # Install ingress controller
    log_info "Installing NGINX Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    
    log_success "Kind cluster started successfully"
}

create_namespace() {
    log_info "Creating Orion namespace..."
    
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Namespace '$NAMESPACE' created"
}

install_istio() {
    log_info "Installing Istio service mesh..."
    
    # Download and install Istio
    if ! command -v istioctl &> /dev/null; then
        log_info "Downloading Istio..."
        curl -L https://istio.io/downloadIstio | sh -
        export PATH="$PWD/istio-*/bin:$PATH"
    fi
    
    # Install Istio
    istioctl install --set values.defaultRevision=default -y
    
    # Enable sidecar injection for orion namespace
    kubectl label namespace $NAMESPACE istio-injection=enabled --overwrite
    
    # Install Istio addons
    kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.19/samples/addons/prometheus.yaml
    kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.19/samples/addons/grafana.yaml
    kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.19/samples/addons/jaeger.yaml
    kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.19/samples/addons/kiali.yaml
    
    log_success "Istio installed successfully"
}

install_monitoring() {
    log_info "Installing monitoring stack..."
    
    # Create monitoring namespace
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    
    # Install Prometheus Operator (simplified)
    kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml
    
    log_success "Monitoring stack installed"
}

deploy_rabbitmq() {
    log_info "Deploying RabbitMQ..."
    
    cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
      - name: rabbitmq
        image: rabbitmq:3.12-management
        ports:
        - containerPort: 5672
        - containerPort: 15672
        env:
        - name: RABBITMQ_DEFAULT_USER
          value: "orion"
        - name: RABBITMQ_DEFAULT_PASS
          value: "orion123"
        volumeMounts:
        - name: rabbitmq-data
          mountPath: /var/lib/rabbitmq
      volumes:
      - name: rabbitmq-data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq
  namespace: $NAMESPACE
spec:
  selector:
    app: rabbitmq
  ports:
  - name: amqp
    port: 5672
    targetPort: 5672
  - name: management
    port: 15672
    targetPort: 15672
  type: ClusterIP
EOF
    
    log_success "RabbitMQ deployed"
}

create_bridge_service() {
    log_info "Creating Python-Kubernetes bridge service..."
    
    cat << EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: orion-bridge-config
  namespace: $NAMESPACE
data:
  bridge.yaml: |
    bridge:
      enabled: true
      python_endpoint: "http://host.docker.internal:8000"
      kubernetes_endpoint: "https://kubernetes.default.svc"
      rabbitmq_endpoint: "rabbitmq.orion-system.svc.cluster.local:5672"
    
    communication:
      protocols:
        - rabbitmq
        - grpc
        - http
      
    security:
      auth_required: false
      encryption: false
    
    monitoring:
      metrics_enabled: true
      logging_level: "INFO"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orion-bridge
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: orion-bridge
  template:
    metadata:
      labels:
        app: orion-bridge
    spec:
      containers:
      - name: bridge
        image: nginx:alpine  # Placeholder - will be replaced with actual bridge image
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: config
          mountPath: /etc/orion
      volumes:
      - name: config
        configMap:
          name: orion-bridge-config
---
apiVersion: v1
kind: Service
metadata:
  name: orion-bridge
  namespace: $NAMESPACE
spec:
  selector:
    app: orion-bridge
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
EOF
    
    log_success "Bridge service created"
}

setup_ingress() {
    log_info "Setting up ingress..."
    
    cat << EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: orion-ingress
  namespace: $NAMESPACE
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: orion.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: orion-bridge
            port:
              number: 8080
      - path: /rabbitmq
        pathType: Prefix
        backend:
          service:
            name: rabbitmq
            port:
              number: 15672
EOF
    
    # Add to /etc/hosts
    if ! grep -q "orion.local" /etc/hosts; then
        echo "127.0.0.1 orion.local" | sudo tee -a /etc/hosts
    fi
    
    log_success "Ingress configured"
}

print_access_info() {
    echo ""
    echo "🎉 Local Kubernetes cluster setup completed!"
    echo "=============================================="
    echo ""
    echo "📊 Access Information:"
    echo "----------------------"
    echo "• Cluster Type: $CLUSTER_TYPE"
    echo "• Cluster Name: $CLUSTER_NAME"
    echo "• Namespace: $NAMESPACE"
    echo ""
    echo "🌐 Web Interfaces:"
    echo "• Orion Dashboard: http://orion.local"
    echo "• RabbitMQ Management: http://orion.local/rabbitmq (orion/orion123)"
    
    if [ "$CLUSTER_TYPE" = "minikube" ]; then
        echo "• Kubernetes Dashboard: minikube dashboard -p $CLUSTER_NAME"
    fi
    
    echo ""
    echo "🔧 Useful Commands:"
    echo "• Check cluster status: kubectl get nodes"
    echo "• Check Orion pods: kubectl get pods -n $NAMESPACE"
    echo "• View logs: kubectl logs -n $NAMESPACE -l app=orion-bridge"
    echo "• Port forward RabbitMQ: kubectl port-forward -n $NAMESPACE svc/rabbitmq 15672:15672"
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Run Python core: cd local-deployment/python-core && python enhanced_agent_core.py"
    echo "2. Test bridge: curl http://orion.local"
    echo "3. Monitor with: kubectl get pods -n $NAMESPACE -w"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    start_cluster
    create_namespace
    install_istio
    install_monitoring
    deploy_rabbitmq
    create_bridge_service
    setup_ingress
    
    # Wait for pods to be ready
    log_info "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=rabbitmq -n $NAMESPACE --timeout=300s
    
    print_access_info
}

# Run main function
main "$@"
