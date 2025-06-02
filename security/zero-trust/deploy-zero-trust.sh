#!/bin/bash
# Zero Trust Architecture Deployment Script
# Sprint 6.1 - Epic 1: Zero Trust Architecture Foundation
# Orion Vision Core - Zero Trust Implementation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACE_NETWORK="zero-trust-network"
NAMESPACE_IAM="zero-trust-iam"
NAMESPACE_DEVICES="zero-trust-devices"
ISTIO_VERSION="1.20.0"
CERT_MANAGER_VERSION="v1.13.0"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed. Please install kubectl first."
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        error "helm is not installed. Please install helm first."
    fi
    
    # Check if istioctl is installed
    if ! command -v istioctl &> /dev/null; then
        warn "istioctl is not installed. Installing Istio ${ISTIO_VERSION}..."
        install_istio
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    fi
    
    log "Prerequisites check completed successfully"
}

# Install Istio
install_istio() {
    log "Installing Istio ${ISTIO_VERSION}..."
    
    # Download Istio
    curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh -
    
    # Add istioctl to PATH
    export PATH="$PWD/istio-${ISTIO_VERSION}/bin:$PATH"
    
    # Install Istio
    istioctl install --set values.defaultRevision=default -y
    
    # Enable Istio injection for default namespace
    kubectl label namespace default istio-injection=enabled --overwrite
    
    log "Istio installation completed"
}

# Install cert-manager
install_cert_manager() {
    log "Installing cert-manager ${CERT_MANAGER_VERSION}..."
    
    # Add cert-manager repository
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    
    # Install cert-manager
    helm upgrade --install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --version ${CERT_MANAGER_VERSION} \
        --set installCRDs=true \
        --wait
    
    log "cert-manager installation completed"
}

# Generate certificates
generate_certificates() {
    log "Generating TLS certificates..."
    
    # Create certificate issuer
    kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-issuer
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: zero-trust-ca
  namespace: cert-manager
spec:
  isCA: true
  commonName: zero-trust-ca
  secretName: zero-trust-ca-secret
  privateKey:
    algorithm: ECDSA
    size: 256
  issuerRef:
    name: selfsigned-issuer
    kind: ClusterIssuer
    group: cert-manager.io
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: zero-trust-ca-issuer
spec:
  ca:
    secretName: zero-trust-ca-secret
EOF
    
    # Wait for CA certificate to be ready
    kubectl wait --for=condition=Ready certificate/zero-trust-ca -n cert-manager --timeout=300s
    
    log "TLS certificates generated successfully"
}

# Create namespaces
create_namespaces() {
    log "Creating Zero Trust namespaces..."
    
    # Create namespaces
    kubectl create namespace ${NAMESPACE_NETWORK} --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace ${NAMESPACE_IAM} --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace ${NAMESPACE_DEVICES} --dry-run=client -o yaml | kubectl apply -f -
    
    # Label namespaces for Istio injection
    kubectl label namespace ${NAMESPACE_NETWORK} istio-injection=enabled --overwrite
    kubectl label namespace ${NAMESPACE_IAM} istio-injection=enabled --overwrite
    kubectl label namespace ${NAMESPACE_DEVICES} istio-injection=enabled --overwrite
    
    log "Namespaces created successfully"
}

# Deploy network segmentation
deploy_network_segmentation() {
    log "Deploying Zero Trust network segmentation..."
    
    # Apply network segmentation configuration
    kubectl apply -f "${SCRIPT_DIR}/network-segmentation.yaml"
    
    # Wait for deployments to be ready
    kubectl wait --for=condition=available --timeout=300s deployment --all -n ${NAMESPACE_NETWORK}
    
    log "Network segmentation deployed successfully"
}

# Deploy IAM system
deploy_iam_system() {
    log "Deploying Zero Trust IAM system..."
    
    # Generate IAM certificates
    kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: identity-verifier-certs
  namespace: ${NAMESPACE_IAM}
spec:
  secretName: identity-verifier-certs
  issuerRef:
    name: zero-trust-ca-issuer
    kind: ClusterIssuer
    group: cert-manager.io
  commonName: identity-verifier.${NAMESPACE_IAM}.svc.cluster.local
  dnsNames:
  - identity-verifier.${NAMESPACE_IAM}.svc.cluster.local
  - iam.orion.zero-trust.local
EOF
    
    # Apply IAM configuration
    kubectl apply -f "${SCRIPT_DIR}/iam-system.yaml"
    
    # Wait for deployments to be ready
    kubectl wait --for=condition=available --timeout=300s deployment --all -n ${NAMESPACE_IAM}
    
    log "IAM system deployed successfully"
}

# Deploy device trust system
deploy_device_trust() {
    log "Deploying Zero Trust device trust system..."
    
    # Generate device trust certificates
    kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: edr-server-certs
  namespace: ${NAMESPACE_DEVICES}
spec:
  secretName: edr-server-certs
  issuerRef:
    name: zero-trust-ca-issuer
    kind: ClusterIssuer
    group: cert-manager.io
  commonName: edr-server.${NAMESPACE_DEVICES}.svc.cluster.local
  dnsNames:
  - edr-server.${NAMESPACE_DEVICES}.svc.cluster.local
EOF
    
    # Apply device trust configuration
    kubectl apply -f "${SCRIPT_DIR}/device-trust.yaml"
    
    # Wait for deployments to be ready
    kubectl wait --for=condition=available --timeout=300s deployment --all -n ${NAMESPACE_DEVICES}
    
    log "Device trust system deployed successfully"
}

# Verify deployment
verify_deployment() {
    log "Verifying Zero Trust deployment..."
    
    # Check namespace status
    info "Checking namespace status..."
    kubectl get namespaces ${NAMESPACE_NETWORK} ${NAMESPACE_IAM} ${NAMESPACE_DEVICES}
    
    # Check pod status
    info "Checking pod status..."
    kubectl get pods -n ${NAMESPACE_NETWORK}
    kubectl get pods -n ${NAMESPACE_IAM}
    kubectl get pods -n ${NAMESPACE_DEVICES}
    
    # Check service status
    info "Checking service status..."
    kubectl get services -n ${NAMESPACE_NETWORK}
    kubectl get services -n ${NAMESPACE_IAM}
    kubectl get services -n ${NAMESPACE_DEVICES}
    
    # Check Istio configuration
    info "Checking Istio configuration..."
    kubectl get peerauthentication -n ${NAMESPACE_NETWORK}
    kubectl get authorizationpolicy -n ${NAMESPACE_NETWORK}
    
    # Check network policies
    info "Checking network policies..."
    kubectl get networkpolicy -n ${NAMESPACE_NETWORK}
    
    log "Deployment verification completed"
}

# Generate deployment report
generate_report() {
    log "Generating deployment report..."
    
    REPORT_FILE="zero-trust-deployment-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "${REPORT_FILE}" <<EOF
# Zero Trust Architecture Deployment Report
Generated: $(date)
Deployment Script: $0

## Deployment Summary
- Network Segmentation: ✅ Deployed
- IAM System: ✅ Deployed  
- Device Trust: ✅ Deployed
- Istio Service Mesh: ✅ Configured
- Certificate Management: ✅ Configured

## Namespaces Created
- ${NAMESPACE_NETWORK}
- ${NAMESPACE_IAM}
- ${NAMESPACE_DEVICES}

## Components Deployed
$(kubectl get all -n ${NAMESPACE_NETWORK} -o wide)

$(kubectl get all -n ${NAMESPACE_IAM} -o wide)

$(kubectl get all -n ${NAMESPACE_DEVICES} -o wide)

## Security Policies
$(kubectl get networkpolicy --all-namespaces)

$(kubectl get peerauthentication --all-namespaces)

$(kubectl get authorizationpolicy --all-namespaces)

## Certificates
$(kubectl get certificates --all-namespaces)

## Next Steps
1. Configure identity providers
2. Enroll devices for trust verification
3. Test zero trust policies
4. Monitor security metrics
5. Tune policy configurations

EOF
    
    log "Deployment report generated: ${REPORT_FILE}"
}

# Cleanup function
cleanup() {
    warn "Cleaning up Zero Trust deployment..."
    
    kubectl delete namespace ${NAMESPACE_NETWORK} --ignore-not-found=true
    kubectl delete namespace ${NAMESPACE_IAM} --ignore-not-found=true
    kubectl delete namespace ${NAMESPACE_DEVICES} --ignore-not-found=true
    
    log "Cleanup completed"
}

# Main deployment function
main() {
    log "Starting Zero Trust Architecture deployment..."
    
    # Parse command line arguments
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            install_cert_manager
            generate_certificates
            create_namespaces
            deploy_network_segmentation
            deploy_iam_system
            deploy_device_trust
            verify_deployment
            generate_report
            log "🎉 Zero Trust Architecture deployment completed successfully!"
            ;;
        "cleanup")
            cleanup
            ;;
        "verify")
            verify_deployment
            ;;
        "report")
            generate_report
            ;;
        *)
            echo "Usage: $0 [deploy|cleanup|verify|report]"
            echo "  deploy  - Deploy Zero Trust Architecture (default)"
            echo "  cleanup - Remove Zero Trust deployment"
            echo "  verify  - Verify deployment status"
            echo "  report  - Generate deployment report"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
