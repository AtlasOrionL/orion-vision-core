#!/usr/bin/env python3
"""
RabbitMQ Integration Test - Atlas Prompt 1.1.2
Orion Vision Core - Entegrasyon Testi

Bu script, RabbitMQ mesaj gönderme ve alma işlevselliğinin entegrasyon testini yapar.
"""

import unittest
import pika
import json
import time
import threading
from typing import List, Dict, Any
import sys
import os

# Test modüllerini import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rabbitmq_publisher import OrionRabbitMQPublisher
from rabbitmq_consumer import OrionRabbitMQConsumer


class TestRabbitMQIntegration(unittest.TestCase):
    """RabbitMQ entegrasyon test sınıfı"""
    
    @classmethod
    def setUpClass(cls):
        """Test sınıfı kurulumu"""
        cls.test_queue = "orion.test.integration"
        cls.publisher = OrionRabbitMQPublisher()
        cls.consumer = OrionRabbitMQConsumer()
        cls.received_messages = []
        cls.consumer_thread = None
        cls.stop_consumer = False
    
    def setUp(self):
        """Her test öncesi kurulum"""
        # Bağlantıları kur
        self.assertTrue(self.publisher.connect(), "Publisher bağlantısı başarısız")
        self.assertTrue(self.consumer.connect(), "Consumer bağlantısı başarısız")
        
        # Test queue'sunu oluştur
        self.assertTrue(self.publisher.declare_queue(self.test_queue))
        self.assertTrue(self.consumer.declare_queue(self.test_queue))
        
        # Önceki mesajları temizle
        self.purge_queue()
        self.received_messages.clear()
    
    def tearDown(self):
        """Her test sonrası temizlik"""
        self.stop_consumer_thread()
        self.publisher.close()
        self.consumer.close()
    
    def purge_queue(self):
        """Queue'yu temizle"""
        try:
            self.publisher.channel.queue_purge(self.test_queue)
        except Exception as e:
            print(f"Queue temizleme hatası: {e}")
    
    def custom_message_callback(self, channel, method, properties, body):
        """Test için özel mesaj callback'i"""
        try:
            message = json.loads(body.decode('utf-8'))
            self.received_messages.append(message)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Mesaj işleme hatası: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consumer_thread(self):
        """Consumer'ı ayrı thread'de başlat"""
        def consumer_worker():
            try:
                self.consumer.channel.basic_qos(prefetch_count=1)
                self.consumer.channel.basic_consume(
                    queue=self.test_queue,
                    on_message_callback=self.custom_message_callback
                )
                
                while not self.stop_consumer:
                    self.consumer.connection.process_data_events(time_limit=1)
                    
            except Exception as e:
                print(f"Consumer thread hatası: {e}")
        
        self.stop_consumer = False
        self.consumer_thread = threading.Thread(target=consumer_worker)
        self.consumer_thread.daemon = True
        self.consumer_thread.start()
    
    def stop_consumer_thread(self):
        """Consumer thread'ini durdur"""
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.stop_consumer = True
            self.consumer_thread.join(timeout=5)
    
    def test_basic_message_flow(self):
        """Temel mesaj akışı testi"""
        print("\n🧪 Test: Temel mesaj akışı")
        
        # Consumer'ı başlat
        self.start_consumer_thread()
        time.sleep(1)  # Consumer'ın hazır olmasını bekle
        
        # Test mesajı
        test_message = {
            "message_type": "integration_test",
            "content": "Entegrasyon test mesajı",
            "test_id": "basic_flow_001"
        }
        
        # Mesajı gönder
        self.assertTrue(
            self.publisher.publish_message(self.test_queue, test_message),
            "Mesaj gönderimi başarısız"
        )
        
        # Mesajın alınmasını bekle
        time.sleep(2)
        
        # Sonuçları kontrol et
        self.assertEqual(len(self.received_messages), 1, "Mesaj alınamadı")
        received = self.received_messages[0]
        self.assertEqual(received['message_type'], test_message['message_type'])
        self.assertEqual(received['content'], test_message['content'])
        self.assertEqual(received['test_id'], test_message['test_id'])
        self.assertIn('timestamp', received)
        self.assertIn('sender', received)
        
        print("✅ Temel mesaj akışı testi başarılı")
    
    def test_multiple_messages(self):
        """Çoklu mesaj testi"""
        print("\n🧪 Test: Çoklu mesaj gönderimi")
        
        # Consumer'ı başlat
        self.start_consumer_thread()
        time.sleep(1)
        
        # Çoklu test mesajları
        test_messages = [
            {"message_type": "test", "content": f"Test mesajı {i}", "test_id": f"multi_{i}"}
            for i in range(5)
        ]
        
        # Mesajları gönder
        for message in test_messages:
            self.assertTrue(
                self.publisher.publish_message(self.test_queue, message),
                f"Mesaj gönderimi başarısız: {message['test_id']}"
            )
        
        # Tüm mesajların alınmasını bekle
        time.sleep(3)
        
        # Sonuçları kontrol et
        self.assertEqual(len(self.received_messages), len(test_messages), 
                        f"Beklenen {len(test_messages)} mesaj, alınan {len(self.received_messages)}")
        
        # Her mesajın doğru alındığını kontrol et
        received_test_ids = [msg['test_id'] for msg in self.received_messages]
        expected_test_ids = [msg['test_id'] for msg in test_messages]
        
        for test_id in expected_test_ids:
            self.assertIn(test_id, received_test_ids, f"Test ID bulunamadı: {test_id}")
        
        print(f"✅ Çoklu mesaj testi başarılı ({len(test_messages)} mesaj)")
    
    def test_json_serialization(self):
        """JSON serileştirme testi"""
        print("\n🧪 Test: JSON serileştirme")
        
        # Consumer'ı başlat
        self.start_consumer_thread()
        time.sleep(1)
        
        # Karmaşık JSON mesajı
        complex_message = {
            "message_type": "complex_test",
            "content": "Karmaşık JSON testi",
            "test_id": "json_001",
            "nested_data": {
                "numbers": [1, 2, 3, 4, 5],
                "strings": ["a", "b", "c"],
                "boolean": True,
                "null_value": None,
                "nested_object": {
                    "key1": "value1",
                    "key2": 42
                }
            },
            "unicode_text": "Türkçe karakterler: ğüşıöç",
            "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?"
        }
        
        # Mesajı gönder
        self.assertTrue(
            self.publisher.publish_message(self.test_queue, complex_message),
            "Karmaşık mesaj gönderimi başarısız"
        )
        
        # Mesajın alınmasını bekle
        time.sleep(2)
        
        # Sonuçları kontrol et
        self.assertEqual(len(self.received_messages), 1, "Karmaşık mesaj alınamadı")
        received = self.received_messages[0]
        
        # Nested data kontrolü
        self.assertEqual(received['nested_data']['numbers'], [1, 2, 3, 4, 5])
        self.assertEqual(received['nested_data']['strings'], ["a", "b", "c"])
        self.assertTrue(received['nested_data']['boolean'])
        self.assertIsNone(received['nested_data']['null_value'])
        self.assertEqual(received['nested_data']['nested_object']['key1'], "value1")
        self.assertEqual(received['nested_data']['nested_object']['key2'], 42)
        
        # Unicode kontrolü
        self.assertEqual(received['unicode_text'], "Türkçe karakterler: ğüşıöç")
        self.assertEqual(received['special_chars'], "!@#$%^&*()_+-=[]{}|;:,.<>?")
        
        print("✅ JSON serileştirme testi başarılı")
    
    def test_connection_resilience(self):
        """Bağlantı dayanıklılığı testi"""
        print("\n🧪 Test: Bağlantı dayanıklılığı")
        
        # Yeni bağlantılar oluştur
        publisher2 = OrionRabbitMQPublisher()
        consumer2 = OrionRabbitMQConsumer()
        
        try:
            # Bağlantıları test et
            self.assertTrue(publisher2.connect(), "İkinci publisher bağlantısı başarısız")
            self.assertTrue(consumer2.connect(), "İkinci consumer bağlantısı başarısız")
            
            # Queue'ları oluştur
            self.assertTrue(publisher2.declare_queue(self.test_queue))
            self.assertTrue(consumer2.declare_queue(self.test_queue))
            
            # Test mesajı gönder
            test_message = {
                "message_type": "resilience_test",
                "content": "Bağlantı dayanıklılığı testi",
                "test_id": "resilience_001"
            }
            
            self.assertTrue(
                publisher2.publish_message(self.test_queue, test_message),
                "Dayanıklılık testi mesaj gönderimi başarısız"
            )
            
            print("✅ Bağlantı dayanıklılığı testi başarılı")
            
        finally:
            publisher2.close()
            consumer2.close()


def run_integration_tests():
    """Entegrasyon testlerini çalıştır"""
    print("🚀 RabbitMQ Entegrasyon Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test suite oluştur
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRabbitMQIntegration)
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Testleri çalıştır
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 Tüm entegrasyon testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
