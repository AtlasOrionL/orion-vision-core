#!/usr/bin/env python3
"""
RabbitMQ Consumer Test - Atlas Prompt 1.1.2
Orion Vision Core - Mesaj Alma Testi

Bu script, RabbitMQ'dan mesaj alma işlevselliğini test eder.
"""

import pika
import json
import sys
import signal
from typing import Dict, Any


class OrionRabbitMQConsumer:
    """Orion projesi için RabbitMQ mesaj alıcı sınıfı"""
    
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
        self.message_count = 0
        self.is_consuming = False
    
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
    
    def message_callback(self, channel, method, properties, body):
        """
        Mesaj geldiğinde çağrılacak callback fonksiyonu
        
        Args:
            channel: RabbitMQ kanalı
            method: Mesaj metodu
            properties: Mesaj özellikleri
            body: Mesaj içeriği
        """
        try:
            self.message_count += 1
            
            # Mesajı JSON olarak parse et
            message = json.loads(body.decode('utf-8'))
            
            print(f"\n📨 Mesaj #{self.message_count} alındı!")
            print(f"🏷️  Delivery Tag: {method.delivery_tag}")
            print(f"📄 Content Type: {properties.content_type}")
            print(f"🕒 Timestamp: {message.get('timestamp', 'N/A')}")
            print(f"👤 Sender: {message.get('sender', 'N/A')}")
            print(f"📝 Message Type: {message.get('message_type', 'N/A')}")
            print(f"💬 Content: {message.get('content', 'N/A')}")
            print(f"⚡ Priority: {message.get('priority', 'N/A')}")
            
            # Eğer agent_id varsa göster
            if 'agent_id' in message:
                print(f"🤖 Agent ID: {message['agent_id']}")
            
            # Eğer target_agent varsa göster
            if 'target_agent' in message:
                print(f"🎯 Target Agent: {message['target_agent']}")
            
            # Eğer system_info varsa göster
            if 'system_info' in message:
                print(f"💻 System Info: {json.dumps(message['system_info'], indent=2)}")
            
            print("-" * 40)
            
            # Mesajı acknowledge et (başarıyla işlendiğini belirt)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            print(f"✅ Mesaj #{self.message_count} başarıyla işlendi")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse hatası: {e}")
            print(f"📄 Raw message: {body}")
            # Hatalı mesajı da acknowledge et (sonsuz döngüyü önlemek için)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"❌ Mesaj işleme hatası: {e}")
            # Hata durumunda mesajı reject et
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self, queue_name: str):
        """
        Mesaj dinlemeye başla
        
        Args:
            queue_name: Dinlenecek queue adı
        """
        try:
            # QoS ayarla (aynı anda en fazla 1 mesaj işle)
            self.channel.basic_qos(prefetch_count=1)
            
            # Consumer'ı ayarla
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self.message_callback
            )
            
            self.is_consuming = True
            print(f"🎧 Mesaj dinleme başlatıldı: {queue_name}")
            print("⏳ Mesajlar bekleniyor... (Çıkmak için Ctrl+C)")
            print("=" * 50)
            
            # Mesaj dinlemeye başla
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            print("\n⚠️ Mesaj dinleme kullanıcı tarafından durduruldu")
            self.stop_consuming()
        except Exception as e:
            print(f"❌ Mesaj dinleme hatası: {e}")
            self.stop_consuming()
    
    def stop_consuming(self):
        """Mesaj dinlemeyi durdur"""
        try:
            if self.is_consuming and self.channel:
                self.channel.stop_consuming()
                self.is_consuming = False
                print("🛑 Mesaj dinleme durduruldu")
        except Exception as e:
            print(f"❌ Mesaj dinleme durdurma hatası: {e}")
    
    def close(self):
        """Bağlantıyı kapat"""
        try:
            self.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                print("✅ RabbitMQ bağlantısı kapatıldı")
        except Exception as e:
            print(f"❌ Bağlantı kapatma hatası: {e}")


def signal_handler(signum, frame):
    """Signal handler for graceful shutdown"""
    print("\n🛑 Çıkış sinyali alındı...")
    sys.exit(0)


def main():
    """Ana test fonksiyonu"""
    print("🚀 Orion RabbitMQ Consumer Test Başlatılıyor...")
    print("=" * 50)
    
    # Signal handler'ı ayarla
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Consumer oluştur
    consumer = OrionRabbitMQConsumer()
    
    try:
        # Bağlan
        if not consumer.connect():
            sys.exit(1)
        
        # Test queue'su oluştur
        test_queue = "orion.test.messages"
        if not consumer.declare_queue(test_queue):
            sys.exit(1)
        
        # Mesaj dinlemeye başla
        consumer.start_consuming(test_queue)
        
    except Exception as e:
        print(f"\n❌ Test sırasında hata oluştu: {e}")
        sys.exit(1)
    finally:
        consumer.close()
        print(f"\n📊 Toplam işlenen mesaj sayısı: {consumer.message_count}")
        print("👋 Consumer test tamamlandı!")


if __name__ == "__main__":
    main()
