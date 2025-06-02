#!/usr/bin/env python3
"""
Simple Consume Messages Test - Atlas Prompt 1.2.2
Orion Vision Core - Basit Mesaj Dinleme Testi

Bu script, consume_messages() metodunun basit bir testini yapar.
"""

import sys
import os
import time
import threading

# Communication agent'ı import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agents.communication_agent import (
    CommunicationAgent, 
    OrionMessage, 
    MessageType, 
    MessagePriority,
    create_message
)


def test_simple_consume():
    """Basit consume testi"""
    print("🧪 Test: Basit mesaj dinleme")
    
    # Producer ve consumer oluştur
    producer = CommunicationAgent("simple_producer")
    consumer = CommunicationAgent("simple_consumer")
    
    received_messages = []
    
    def simple_handler(message):
        """Basit mesaj handler'ı"""
        received_messages.append(message)
        print(f"📨 Received: {message.content}")
    
    try:
        # Bağlantıları kur
        print("📡 Connecting agents...")
        assert producer.connect(), "Producer connection failed"
        assert consumer.connect(), "Consumer connection failed"
        
        # Handler kaydet
        consumer.register_message_handler(
            MessageType.AGENT_COMMUNICATION.value,
            simple_handler
        )
        
        # Test queue oluştur
        test_queue = "orion.test.simple_consume"
        producer.declare_queue(test_queue)
        consumer.declare_queue(test_queue)
        
        # Consumer'ı başlat
        print("🎧 Starting consumer...")
        assert consumer.consume_messages(test_queue), "Consumer start failed"
        
        # Biraz bekle
        time.sleep(2)
        
        # Test mesajı gönder
        print("📤 Sending test message...")
        test_message = create_message(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="Simple test message",
            sender_id="simple_producer"
        )
        
        success = producer.publish_message(test_queue, test_message)
        assert success, "Message send failed"
        
        # Mesajın işlenmesini bekle
        print("⏳ Waiting for message processing...")
        time.sleep(3)
        
        # Consumer'ı durdur
        print("🛑 Stopping consumer...")
        consumer.stop_consuming_messages()
        
        # Sonuçları kontrol et
        print(f"📊 Received {len(received_messages)} messages")
        
        if len(received_messages) > 0:
            print("✅ Simple consume test successful!")
            return True
        else:
            print("❌ No messages received")
            return False
            
    except Exception as e:
        print(f"❌ Simple consume test failed: {e}")
        return False
    finally:
        producer.disconnect()
        consumer.disconnect()


def test_publish_only():
    """Sadece publish testi"""
    print("\n🧪 Test: Sadece mesaj gönderme")
    
    producer = CommunicationAgent("test_producer")
    
    try:
        print("📡 Connecting producer...")
        assert producer.connect(), "Producer connection failed"
        
        # Test queue oluştur
        test_queue = "orion.test.publish_only"
        producer.declare_queue(test_queue)
        
        # Test mesajları gönder
        for i in range(3):
            message = create_message(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content=f"Test message {i+1}",
                sender_id="test_producer"
            )
            
            success = producer.publish_message(test_queue, message)
            assert success, f"Message {i+1} send failed"
            print(f"📤 Sent message {i+1}")
        
        print("✅ Publish only test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Publish only test failed: {e}")
        return False
    finally:
        producer.disconnect()


def main():
    """Ana test fonksiyonu"""
    print("🚀 Simple Consume Messages Test - Atlas Prompt 1.2.2")
    print("=" * 60)
    
    tests = [
        test_publish_only,
        test_simple_consume
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
