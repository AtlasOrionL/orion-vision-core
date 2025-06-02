# 🚀 Orion Vision Core - Hybrid Local Deployment

**Phase 3: Python Core + Local Kubernetes Integration**

Bu deployment, mevcut Python-based agent sistemini local Kubernetes ile entegre ederek hybrid bir mimari sağlar.

## 🎯 Mimari Özeti

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID LOCAL ORION                      │
├─────────────────────────────────────────────────────────────┤
│  PYTHON CORE (High Performance)    │  KUBERNETES (Advanced) │
│  ├── Agent Core                    │  ├── Security Policies │
│  ├── LLM Integration               │  ├── Compliance Auto   │
│  ├── Task Orchestration           │  ├── Threat Detection  │
│  ├── Communication Hub            │  ├── Monitoring Stack  │
│  └── Real-time Processing         │  └── Service Mesh      │
├─────────────────────────────────────────────────────────────┤
│              LOCAL BRIDGE LAYER                             │
│  ├── RabbitMQ ↔ Istio gRPC                                │
│  ├── Python APIs ↔ K8s Services                           │
│  └── Shared Storage & Config                               │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Gereksinimler

### Minimal Setup:
- **CPU:** 4 cores
- **RAM:** 8GB
- **Disk:** 50GB SSD
- **OS:** Windows/Linux/Mac + Docker

### Yazılım Gereksinimleri:
- Docker Desktop
- Docker Compose
- kubectl
- Minikube veya Kind (Kubernetes için)

## 🚀 Hızlı Başlangıç

### 1. Repository'yi Clone Edin
```bash
git clone https://github.com/krozenking/Orion.git
cd Orion/local-deployment
```

### 2. Deployment Script'ini Çalıştırın
```bash
# Hybrid deployment (önerilen)
chmod +x deploy-hybrid-local.sh
./deploy-hybrid-local.sh

# Sadece Python Core
./deploy-hybrid-local.sh python-only

# Sadece Kubernetes
./deploy-hybrid-local.sh k8s-only
```

### 3. Servislere Erişin
- **Ana Dashboard:** http://orion.local
- **Python Core API:** http://localhost:8001
- **RabbitMQ Management:** http://localhost:15672 (orion/orion123)
- **Grafana:** http://localhost:3000 (admin/orion123)
- **Prometheus:** http://localhost:9090

## 📁 Dosya Yapısı

```
local-deployment/
├── python-core/                 # Python Core Agent System
│   ├── enhanced_agent_core.py   # Enhanced agent framework
│   ├── Dockerfile               # Python core container
│   ├── requirements.txt         # Python dependencies
│   └── healthcheck.py           # Health check script
├── bridge/                      # Hybrid Bridge Service
│   ├── hybrid_bridge.py         # Python ↔ K8s bridge
│   ├── Dockerfile               # Bridge container
│   └── requirements.txt         # Bridge dependencies
├── kubernetes/                  # Kubernetes Setup
│   └── local-cluster-setup.sh   # K8s cluster setup script
├── config/                      # Configuration Files
│   └── rabbitmq/               # RabbitMQ configuration
├── monitoring/                  # Monitoring Stack
│   ├── prometheus/             # Prometheus config
│   └── grafana/               # Grafana dashboards
├── docker-compose.yml          # Docker services
├── deploy-hybrid-local.sh      # Main deployment script
└── README.md                   # This file
```

## 🔧 Servis Detayları

### Python Core Services

#### 1. **Enhanced Agent Core**
- **Port:** 8001
- **Özellikler:** 
  - Legacy agent framework
  - LLM integration (Ollama)
  - Task orchestration
  - Multi-protocol communication
  - Kubernetes bridge support

#### 2. **Hybrid Bridge**
- **Port:** 8000
- **Özellikler:**
  - Python ↔ Kubernetes integration
  - Message routing
  - Protocol translation
  - Service discovery

#### 3. **RabbitMQ**
- **Ports:** 5672 (AMQP), 15672 (Management)
- **Credentials:** orion/orion123
- **Özellikler:**
  - Message queuing
  - Agent communication
  - Kubernetes integration

#### 4. **Ollama LLM**
- **Port:** 11434
- **Özellikler:**
  - Local LLM inference
  - Mistral model support
  - No internet required

### Kubernetes Services

#### 1. **Istio Service Mesh**
- **Özellikler:**
  - Service-to-service communication
  - mTLS encryption
  - Traffic management
  - Observability

#### 2. **Security Stack**
- **Özellikler:**
  - Zero-trust policies
  - OPA Gatekeeper
  - Falco runtime security
  - Compliance automation

#### 3. **Monitoring Stack**
- **Prometheus:** Metrics collection
- **Grafana:** Visualization
- **Jaeger:** Distributed tracing
- **Kiali:** Service mesh observability

## 🔍 Monitoring & Observability

### Grafana Dashboards
- **Orion Overview:** Genel sistem durumu
- **Agent Performance:** Agent metrikleri
- **Communication Flow:** Mesaj akışı
- **Resource Usage:** Kaynak kullanımı

### Prometheus Metrics
- Agent lifecycle events
- Message queue statistics
- LLM inference metrics
- Bridge communication stats

### Log Aggregation
- Structured logging
- Kubernetes integration
- Real-time log streaming
- Error tracking

## 🛡️ Güvenlik

### Local Security Features
- **Network Isolation:** Docker networks
- **Authentication:** RabbitMQ credentials
- **Encryption:** TLS/mTLS support
- **Access Control:** Role-based permissions

### Kubernetes Security
- **RBAC:** Role-based access control
- **Network Policies:** Traffic segmentation
- **Pod Security:** Security contexts
- **Secret Management:** Kubernetes secrets

## 🔧 Troubleshooting

### Yaygın Sorunlar

#### 1. **Port Çakışması**
```bash
# Kullanılan portları kontrol et
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001

# Servisleri yeniden başlat
docker-compose restart
```

#### 2. **Kubernetes Bağlantı Sorunu**
```bash
# Cluster durumunu kontrol et
kubectl cluster-info
kubectl get nodes

# Minikube'u yeniden başlat
minikube stop -p orion-local
minikube start -p orion-local
```

#### 3. **RabbitMQ Bağlantı Sorunu**
```bash
# RabbitMQ loglarını kontrol et
docker-compose logs rabbitmq

# RabbitMQ'yu yeniden başlat
docker-compose restart rabbitmq
```

#### 4. **Disk Alanı Sorunu**
```bash
# Docker temizliği
docker system prune -a

# Volume temizliği
docker volume prune
```

### Log Kontrolü
```bash
# Tüm servislerin logları
docker-compose logs -f

# Belirli servis logları
docker-compose logs -f python-core
docker-compose logs -f hybrid-bridge

# Kubernetes logları
kubectl logs -n orion-system -l app=orion-bridge
```

## 🚀 Geliştirme

### Local Development
```bash
# Development mode'da başlat
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Code changes için hot reload
docker-compose restart python-core
```

### Testing
```bash
# Health check
curl http://localhost:8000/health
curl http://localhost:8001/health

# API test
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d '{"target": "test", "message": {"hello": "world"}}'
```

### Performance Tuning
```bash
# Resource monitoring
docker stats

# Kubernetes resource usage
kubectl top pods -n orion-system
kubectl top nodes
```

## 📚 Daha Fazla Bilgi

- **Orion Documentation:** `../docs/`
- **API Reference:** http://localhost:8000/docs
- **Architecture Guide:** `../docs/architecture.md`
- **Troubleshooting Guide:** `../docs/troubleshooting.md`

## 🤝 Katkıda Bulunma

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test locally
5. Submit pull request

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

**🎯 Sonuç:** Bu hybrid local deployment, mevcut Python-based agent sisteminin gücünü Kubernetes'in modern altyapı yetenekleriyle birleştirerek optimal bir local development ve production ortamı sağlar!
