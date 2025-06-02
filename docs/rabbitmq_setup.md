# RabbitMQ Kurulum ve Yapılandırma Kılavuzu

## Genel Bakış

Bu doküman, Orion Vision Core projesi için RabbitMQ mesaj kuyruğu sisteminin kurulumu ve yapılandırmasını açıklar. RabbitMQ, dağıtık ajanlar arası güvenilir ve esnek mesaj alışverişi için kullanılacaktır.

## Sistem Gereksinimleri

- Docker ve Docker Compose kurulu olmalı
- En az 512MB RAM (geliştirme ortamı için)
- En az 1GB disk alanı
- Port 5672 (AMQP) ve 15672 (Management UI) açık olmalı

## Docker Kurulumu (Ubuntu/Debian)

Eğer Docker kurulu değilse, aşağıdaki adımları takip edin:

```bash
# Docker kurulumu
sudo apt update
sudo apt install -y docker.io docker-compose

# Docker servisini başlat
sudo systemctl start docker
sudo systemctl enable docker

# Kullanıcıyı docker grubuna ekle (logout/login gerekli)
sudo usermod -aG docker $USER

# Kurulumu test et
docker --version
docker-compose --version
```

## Alternatif: Native RabbitMQ Kurulumu

Docker kullanmak istemiyorsanız, RabbitMQ'yu doğrudan kurabilirsiniz:

```bash
# Ubuntu/Debian için
sudo apt update
sudo apt install -y rabbitmq-server

# Servisi başlat
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Management plugin'i aktif et
sudo rabbitmq-plugins enable rabbitmq_management

# Kullanıcı oluştur
sudo rabbitmqctl add_user orion_admin orion_secure_2024
sudo rabbitmqctl set_user_tags orion_admin administrator
sudo rabbitmqctl add_vhost orion_vhost
sudo rabbitmqctl set_permissions -p orion_vhost orion_admin ".*" ".*" ".*"
```

## Kurulum Adımları

### 1. Docker Compose ile Kurulum

Proje kök dizininde aşağıdaki komutu çalıştırın:

```bash
docker-compose up -d rabbitmq
```

### 2. Kurulum Doğrulama

RabbitMQ'nun başarıyla başlatıldığını kontrol edin:

```bash
docker-compose ps
docker-compose logs rabbitmq
```

### 3. Management UI Erişimi

Tarayıcınızda şu adrese gidin: http://localhost:15672

**Giriş Bilgileri:**
- Kullanıcı Adı: `orion_admin`
- Şifre: `orion_secure_2024`
- Virtual Host: `orion_vhost`

## Yapılandırma Detayları

### Bağlantı Bilgileri

- **AMQP URL:** `amqp://orion_admin:orion_secure_2024@localhost:5672/orion_vhost`
- **Host:** localhost
- **Port:** 5672
- **Virtual Host:** orion_vhost
- **Username:** orion_admin
- **Password:** orion_secure_2024

### Güvenlik Ayarları

- Varsayılan kullanıcı ve şifre environment variables ile ayarlanmıştır
- Production ortamında mutlaka güçlü şifreler kullanın
- Virtual host izolasyonu aktif

### Performans Optimizasyonları

- Memory watermark %60 olarak ayarlandı (geliştirme ortamı için)
- Connection pool 10 acceptor ile sınırlandırıldı
- Heartbeat 60 saniye olarak ayarlandı

## Temel Kullanım

### Queue Oluşturma

Management UI üzerinden veya programatik olarak queue oluşturabilirsiniz:

1. Management UI'da "Queues" sekmesine gidin
2. "Add a new queue" butonuna tıklayın
3. Queue adını girin (örn: `orion.agent.communication`)
4. Durability: `Durable` seçin
5. "Add queue" butonuna tıklayın

### Exchange Oluşturma

Mesaj yönlendirme için exchange'ler oluşturun:

1. Management UI'da "Exchanges" sekmesine gidin
2. "Add a new exchange" butonuna tıklayın
3. Exchange adını girin (örn: `orion.agents`)
4. Type: `topic` seçin
5. Durability: `Durable` seçin
6. "Add exchange" butonuna tıklayın

## Sorun Giderme

### Container Başlatma Sorunları

```bash
# Container durumunu kontrol edin
docker-compose ps

# Logları inceleyin
docker-compose logs rabbitmq

# Container'ı yeniden başlatın
docker-compose restart rabbitmq
```

### Port Çakışması

Eğer 5672 veya 15672 portları kullanımda ise, `docker-compose.yml` dosyasında port mapping'i değiştirin:

```yaml
ports:
  - "5673:5672"     # AMQP port
  - "15673:15672"   # Management UI port
```

### Bağlantı Sorunları

1. Firewall ayarlarını kontrol edin
2. Docker network ayarlarını kontrol edin
3. Kullanıcı adı/şifre doğruluğunu kontrol edin

## Güvenlik Notları

- **Geliştirme Ortamı:** Mevcut ayarlar geliştirme için uygundur
- **Production Ortamı:** Production'da mutlaka:
  - Güçlü şifreler kullanın
  - SSL/TLS aktif edin
  - Network güvenliği sağlayın
  - Monitoring aktif edin

## Monitoring ve Bakım

### Health Check

RabbitMQ health check otomatik olarak yapılandırılmıştır:

```bash
docker-compose exec rabbitmq rabbitmq-diagnostics ping
```

### Backup

Önemli veriler için düzenli backup alın:

```bash
docker-compose exec rabbitmq rabbitmqctl export_definitions /tmp/definitions.json
```

## Sonraki Adımlar

1. Python Pika kütüphanesi ile entegrasyon
2. Temel mesaj gönderme/alma testleri
3. `communication_agent.py` modülü geliştirme

## Kaynaklar

- [RabbitMQ Resmi Dokümantasyon](https://www.rabbitmq.com/documentation.html)
- [Docker Hub RabbitMQ](https://hub.docker.com/_/rabbitmq)
- [Pika Python Client](https://pika.readthedocs.io/)
