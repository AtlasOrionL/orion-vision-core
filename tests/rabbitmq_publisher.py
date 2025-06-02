#!/usr/bin/env python3
"""
RabbitMQ Publisher Test - Atlas Prompt 1.1.2
Orion Vision Core - Mesaj Gönderme Testi

Bu script, RabbitMQ'ya mesaj gönderme işlevselliğini test eder.
"""

import pika
import json
import sys
import datetime
from typing import Dict, Any


class OrionRabbitMQPublisher:
    """Orion projesi için RabbitMQ mesaj gönderici sınıfı"""
    
    def __init__(self, host='localhost', port=5672, virtual_host='orion_vhost', 
                 username='orion_admin', password='orion_secure_2024'):
        """
        RabbitMQ bağlantı parametrelerini ayarla
        
        Args:
            host: RabbitMQ sunucu adresi
            port: RabbitMQ portu
            virtual_host: Virtual host adı
            username: Kullanıcı adı
            password: Şifre
        """
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
    
    def connect(self) -> bool:
        """
        RabbitMQ'ya bağlan
        
        Returns:
            bool: Bağlantı başarılı ise True
        """
        try:
            # Bağlantı parametrelerini ayarla
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # Bağlantı kur
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            print(f"✅ RabbitMQ'ya başarıyla bağlanıldı: {self.host}:{self.port}/{self.virtual_host}")
            return True
            
        except Exception as e:
            print(f"❌ RabbitMQ bağlantı hatası: {e}")
            return False
    
    def declare_queue(self, queue_name: str, durable: bool = True) -> bool:
        """
        Queue oluştur veya var olanı kontrol et
        
        Args:
            queue_name: Queue adı
            durable: Kalıcı olup olmayacağı
            
        Returns:
            bool: İşlem başarılı ise True
        """
        try:
            self.channel.queue_declare(queue=queue_name, durable=durable)
            print(f"✅ Queue oluşturuldu/kontrol edildi: {queue_name}")
            return True
        except Exception as e:
            print(f"❌ Queue oluşturma hatası: {e}")
            return False
    
    def publish_message(self, queue_name: str, message: Dict[str, Any]) -> bool:
        """
        Mesaj gönder
        
        Args:
            queue_name: Hedef queue adı
            message: Gönderilecek mesaj (dict formatında)
            
        Returns:
            bool: Gönderim başarılı ise True
        """
        try:
            # Mesaja timestamp ekle
            message['timestamp'] = datetime.datetime.now().isoformat()
            message['sender'] = 'orion_publisher_test'
            
            # JSON formatına çevir
            message_body = json.dumps(message, ensure_ascii=False, indent=2)
            
            # Mesajı gönder
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mesajı kalıcı yap
                    content_type='application/json',
                    content_encoding='utf-8'
                )
            )
            
            print(f"✅ Mesaj gönderildi: {queue_name}")
            print(f"📄 Mesaj içeriği: {message_body}")
            return True
            
        except Exception as e:
            print(f"❌ Mesaj gönderme hatası: {e}")
            return False
    
    def close(self):
        """Bağlantıyı kapat"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                print("✅ RabbitMQ bağlantısı kapatıldı")
        except Exception as e:
            print(f"❌ Bağlantı kapatma hatası: {e}")


def main():
    """Ana test fonksiyonu"""
    print("🚀 Orion RabbitMQ Publisher Test Başlatılıyor...")
    print("=" * 50)
    
    # Publisher oluştur
    publisher = OrionRabbitMQPublisher()
    
    try:
        # Bağlan
        if not publisher.connect():
            sys.exit(1)
        
        # Test queue'su oluştur
        test_queue = "orion.test.messages"
        if not publisher.declare_queue(test_queue):
            sys.exit(1)
        
        # Test mesajları gönder
        test_messages = [
            {
                "message_type": "test",
                "content": "Bu bir test mesajıdır",
                "priority": "normal",
                "agent_id": "test_agent_001"
            },
            {
                "message_type": "agent_communication",
                "content": "Agent arası iletişim testi",
                "priority": "high",
                "agent_id": "communication_agent",
                "target_agent": "brain_agent"
            },
            {
                "message_type": "system_status",
                "content": "Sistem durumu raporu",
                "priority": "low",
                "system_info": {
                    "cpu_usage": "15%",
                    "memory_usage": "45%",
                    "active_agents": 3
                }
            }
        ]
        
        # Mesajları gönder
        for i, message in enumerate(test_messages, 1):
            print(f"\n📤 Test Mesajı {i}/{len(test_messages)} gönderiliyor...")
            if not publisher.publish_message(test_queue, message):
                print(f"❌ Mesaj {i} gönderilemedi!")
            else:
                print(f"✅ Mesaj {i} başarıyla gönderildi!")
        
        print("\n" + "=" * 50)
        print("🎉 Tüm test mesajları başarıyla gönderildi!")
        print(f"📊 Toplam gönderilen mesaj sayısı: {len(test_messages)}")
        print(f"🎯 Hedef queue: {test_queue}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Test sırasında hata oluştu: {e}")
        sys.exit(1)
    finally:
        publisher.close()


if __name__ == "__main__":
    main()
