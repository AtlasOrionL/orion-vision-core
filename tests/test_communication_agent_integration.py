#!/usr/bin/env python3
"""
Communication Agent Integration Test - Atlas Prompt 1.2.1
Orion Vision Core - Gerçek RabbitMQ ile Entegrasyon Testi

Bu script, CommunicationAgent sınıfının gerçek RabbitMQ ile entegrasyonunu test eder.
"""

import sys
import os
import time
import threading

# Test modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agents.communication_agent import (
    CommunicationAgent,
    OrionMessage,
    MessageType,
    MessagePriority,
    create_message
)


def test_basic_communication():
    """Temel iletişim testi"""
    print("🧪 Test: Temel Communication Agent iletişimi")

    # İki agent oluştur
    agent1 = CommunicationAgent("test_agent_1")
    agent2 = CommunicationAgent("test_agent_2")

    try:
        # Bağlantıları kur
        print("📡 Agent bağlantıları kuruluyor...")
        assert agent1.connect(), "Agent 1 bağlantısı başarısız"
        assert agent2.connect(), "Agent 2 bağlantısı başarısız"

        # Test queue'su oluştur
        test_queue = "orion.test.communication_agent"
        assert agent1.declare_queue(test_queue), "Queue oluşturma başarısız"
        assert agent2.declare_queue(test_queue), "Queue oluşturma başarısız"

        # Test mesajı oluştur
        test_message = create_message(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="Communication Agent test mesajı",
            sender_id="test_agent_1",
            target_agent="test_agent_2",
            priority=MessagePriority.HIGH.value,
            test_data="integration_test"
        )

        # Mesajı gönder
        print("📤 Mesaj gönderiliyor...")
        success = agent1.publish_message(test_queue, test_message)
        assert success, "Mesaj gönderimi başarısız"

        print("✅ Temel iletişim testi başarılı!")
        return True

    except Exception as e:
        print(f"❌ Temel iletişim testi başarısız: {e}")
        return False
    finally:
        agent1.disconnect()
        agent2.disconnect()


def test_message_types():
    """Farklı mesaj tiplerini test et"""
    print("\n🧪 Test: Farklı mesaj tipleri")

    agent = CommunicationAgent("message_type_test_agent")

    try:
        assert agent.connect(), "Agent bağlantısı başarısız"

        test_queue = "orion.test.message_types"
        assert agent.declare_queue(test_queue), "Queue oluşturma başarısız"

        # Farklı mesaj tiplerini test et
        message_types = [
            (MessageType.AGENT_COMMUNICATION.value, "Agent iletişim testi"),
            (MessageType.SYSTEM_STATUS.value, "Sistem durumu testi"),
            (MessageType.TASK_REQUEST.value, "Görev isteği testi"),
            (MessageType.TASK_RESPONSE.value, "Görev yanıtı testi"),
            (MessageType.ERROR_REPORT.value, "Hata raporu testi"),
            (MessageType.HEARTBEAT.value, "Heartbeat testi"),
            (MessageType.DISCOVERY.value, "Keşif testi")
        ]

        for msg_type, content in message_types:
            message = create_message(
                message_type=msg_type,
                content=content,
                sender_id="message_type_test_agent",
                priority=MessagePriority.NORMAL.value
            )

            success = agent.publish_message(test_queue, message)
            assert success, f"Mesaj gönderimi başarısız: {msg_type}"
            print(f"  ✅ {msg_type} mesajı gönderildi")

        print("✅ Mesaj tipleri testi başarılı!")
        return True

    except Exception as e:
        print(f"❌ Mesaj tipleri testi başarısız: {e}")
        return False
    finally:
        agent.disconnect()


def test_priority_levels():
    """Farklı öncelik seviyelerini test et"""
    print("\n🧪 Test: Mesaj öncelik seviyeleri")

    agent = CommunicationAgent("priority_test_agent")

    try:
        assert agent.connect(), "Agent bağlantısı başarısız"

        test_queue = "orion.test.priorities"
        assert agent.declare_queue(test_queue), "Queue oluşturma başarısız"

        # Farklı öncelik seviyelerini test et
        priorities = [
            (MessagePriority.LOW.value, "Düşük öncelik mesajı"),
            (MessagePriority.NORMAL.value, "Normal öncelik mesajı"),
            (MessagePriority.HIGH.value, "Yüksek öncelik mesajı"),
            (MessagePriority.CRITICAL.value, "Kritik öncelik mesajı")
        ]

        for priority, content in priorities:
            message = create_message(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content=content,
                sender_id="priority_test_agent",
                priority=priority
            )

            success = agent.publish_message(test_queue, message)
            assert success, f"Mesaj gönderimi başarısız: {priority}"
            print(f"  ✅ {priority} öncelikli mesaj gönderildi")

        print("✅ Öncelik seviyeleri testi başarılı!")
        return True

    except Exception as e:
        print(f"❌ Öncelik seviyeleri testi başarısız: {e}")
        return False
    finally:
        agent.disconnect()


def test_heartbeat_functionality():
    """Heartbeat işlevselliğini test et"""
    print("\n🧪 Test: Heartbeat işlevselliği")

    agent = CommunicationAgent("heartbeat_test_agent")

    try:
        assert agent.connect(), "Agent bağlantısı başarısız"

        # İlk heartbeat gönder
        success1 = agent.send_heartbeat()
        assert success1, "İlk heartbeat gönderimi başarısız"

        # Biraz bekle
        time.sleep(1)

        # İkinci heartbeat gönder
        success2 = agent.send_heartbeat()
        assert success2, "İkinci heartbeat gönderimi başarısız"

        # İstatistikleri kontrol et
        stats = agent.get_stats()
        assert stats['last_heartbeat'] is not None, "Heartbeat timestamp güncellenmedi"
        assert stats['messages_sent'] >= 2, "Heartbeat mesajları sayılmadı"

        print("✅ Heartbeat işlevselliği testi başarılı!")
        return True

    except Exception as e:
        print(f"❌ Heartbeat işlevselliği testi başarısız: {e}")
        return False
    finally:
        agent.disconnect()


def test_context_manager():
    """Context manager işlevselliğini test et"""
    print("\n🧪 Test: Context manager işlevselliği")

    try:
        with CommunicationAgent("context_test_agent") as agent:
            assert agent.is_connected, "Context manager bağlantısı başarısız"

            # Test mesajı gönder
            test_queue = "orion.test.context_manager"
            assert agent.declare_queue(test_queue), "Queue oluşturma başarısız"

            message = create_message(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content="Context manager test mesajı",
                sender_id="context_test_agent"
            )

            success = agent.publish_message(test_queue, message)
            assert success, "Context manager mesaj gönderimi başarısız"

        # Context'ten çıktıktan sonra bağlantı kapatılmalı
        print("✅ Context manager işlevselliği testi başarılı!")
        return True

    except Exception as e:
        print(f"❌ Context manager işlevselliği testi başarısız: {e}")
        return False


def test_error_handling():
    """Hata yönetimi testi"""
    print("\n🧪 Test: Hata yönetimi")

    # Yanlış bağlantı bilgileri ile agent oluştur
    agent = CommunicationAgent(
        "error_test_agent",
        host="nonexistent_host",
        port=9999,
        username="wrong_user",
        password="wrong_pass"
    )

    try:
        # Bağlantı başarısız olmalı
        success = agent.connect()
        assert not success, "Yanlış bilgilerle bağlantı başarılı olmamalı"

        # İstatistiklerde hata sayısı artmalı
        stats = agent.get_stats()
        assert stats['connection_errors'] > 0, "Bağlantı hatası sayılmadı"

        # Bağlantı olmadan mesaj gönderme denemesi
        message = create_message(
            message_type=MessageType.ERROR_REPORT.value,
            content="Test error message",
            sender_id="error_test_agent"
        )

        publish_success = agent.publish_message("test_queue", message)
        assert not publish_success, "Bağlantı olmadan mesaj gönderimi başarılı olmamalı"

        print("✅ Hata yönetimi testi başarılı!")
        return True

    except Exception as e:
        print(f"❌ Hata yönetimi testi başarısız: {e}")
        return False
    finally:
        agent.disconnect()


def test_statistics_tracking():
    """İstatistik takibi testi"""
    print("\n🧪 Test: İstatistik takibi")

    agent = CommunicationAgent("stats_test_agent")

    try:
        # Başlangıç istatistikleri
        initial_stats = agent.get_stats()
        assert initial_stats['messages_sent'] == 0, "Başlangıç mesaj sayısı sıfır olmalı"
        assert initial_stats['connection_errors'] == 0, "Başlangıç hata sayısı sıfır olmalı"

        # Bağlan
        assert agent.connect(), "Agent bağlantısı başarısız"

        # Bağlantı sonrası istatistikler
        connected_stats = agent.get_stats()
        assert connected_stats['is_connected'], "Bağlantı durumu güncellenmedi"

        # Mesaj gönder
        test_queue = "orion.test.statistics"
        assert agent.declare_queue(test_queue), "Queue oluşturma başarısız"

        message = create_message(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="İstatistik test mesajı",
            sender_id="stats_test_agent"
        )

        assert agent.publish_message(test_queue, message), "Mesaj gönderimi başarısız"

        # Mesaj sonrası istatistikler
        final_stats = agent.get_stats()
        assert final_stats['messages_sent'] == 1, "Mesaj sayısı güncellenmedi"

        print("✅ İstatistik takibi testi başarılı!")
        return True

    except Exception as e:
        print(f"❌ İstatistik takibi testi başarısız: {e}")
        return False
    finally:
        agent.disconnect()


def test_consume_messages():
    """Mesaj dinleme işlevselliğini test et"""
    print("\n🧪 Test: Mesaj dinleme işlevselliği")

    # Producer ve consumer agent'ları oluştur
    producer = CommunicationAgent("producer_agent")
    consumer = CommunicationAgent("consumer_agent")

    received_messages = []

    def message_handler(message):
        """Test mesaj handler'ı"""
        received_messages.append(message)
        print(f"  📨 Received: {message.content} from {message.sender_id}")

    try:
        # Bağlantıları kur
        assert producer.connect(), "Producer bağlantısı başarısız"
        assert consumer.connect(), "Consumer bağlantısı başarısız"

        # Consumer'a handler kaydet
        consumer.register_message_handler(
            MessageType.AGENT_COMMUNICATION.value,
            message_handler
        )

        # Consumer'ı başlat
        test_queue = "orion.test.consume_messages"
        assert consumer.declare_queue(test_queue), "Queue oluşturma başarısız"
        assert consumer.consume_messages(test_queue), "Consumer başlatma başarısız"

        # Biraz bekle (consumer'ın hazır olması için)
        time.sleep(2)

        # Test mesajları gönder
        test_messages = [
            "Test message 1",
            "Test message 2",
            "Test message 3"
        ]

        for i, content in enumerate(test_messages, 1):
            message = create_message(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content=content,
                sender_id="producer_agent",
                target_agent="consumer_agent"
            )

            success = producer.publish_message(test_queue, message)
            assert success, f"Mesaj {i} gönderimi başarısız"
            print(f"  📤 Sent: {content}")

        # Mesajların işlenmesini bekle
        time.sleep(3)

        # Consumer'ı durdur
        consumer.stop_consuming_messages()

        # Sonuçları kontrol et
        assert len(received_messages) == len(test_messages), \
            f"Beklenen {len(test_messages)} mesaj, alınan {len(received_messages)}"

        for i, received in enumerate(received_messages):
            expected_content = test_messages[i]
            assert received.content == expected_content, \
                f"Mesaj içeriği uyuşmuyor: beklenen '{expected_content}', alınan '{received.content}'"

        print("✅ Mesaj dinleme işlevselliği testi başarılı!")
        return True

    except Exception as e:
        print(f"❌ Mesaj dinleme işlevselliği testi başarısız: {e}")
        return False
    finally:
        producer.disconnect()
        consumer.disconnect()


def test_bidirectional_communication():
    """İki yönlü iletişim testi"""
    print("\n🧪 Test: İki yönlü iletişim")

    agent1 = CommunicationAgent("agent_1")
    agent2 = CommunicationAgent("agent_2")

    agent1_messages = []
    agent2_messages = []

    def agent1_handler(message):
        agent1_messages.append(message)
        print(f"  📨 Agent1 received: {message.content}")

    def agent2_handler(message):
        agent2_messages.append(message)
        print(f"  📨 Agent2 received: {message.content}")

    try:
        # Bağlantıları kur
        assert agent1.connect(), "Agent1 bağlantısı başarısız"
        assert agent2.connect(), "Agent2 bağlantısı başarısız"

        # Handler'ları kaydet
        agent1.register_message_handler(MessageType.AGENT_COMMUNICATION.value, agent1_handler)
        agent2.register_message_handler(MessageType.AGENT_COMMUNICATION.value, agent2_handler)

        # Consumer'ları başlat
        assert agent1.consume_messages(), "Agent1 consumer başlatma başarısız"
        assert agent2.consume_messages(), "Agent2 consumer başlatma başarısız"

        time.sleep(2)  # Consumer'ların hazır olması için

        # Agent1'den Agent2'ye mesaj gönder
        message1to2 = create_message(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="Hello from Agent1 to Agent2",
            sender_id="agent_1",
            target_agent="agent_2"
        )

        agent2_queue = "orion.agent.agent_2"
        success = agent1.publish_message(agent2_queue, message1to2)
        assert success, "Agent1->Agent2 mesaj gönderimi başarısız"
        print("  📤 Agent1 -> Agent2: Hello from Agent1 to Agent2")

        time.sleep(1)

        # Agent2'den Agent1'e mesaj gönder
        message2to1 = create_message(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="Hello from Agent2 to Agent1",
            sender_id="agent_2",
            target_agent="agent_1"
        )

        agent1_queue = "orion.agent.agent_1"
        success = agent2.publish_message(agent1_queue, message2to1)
        assert success, "Agent2->Agent1 mesaj gönderimi başarısız"
        print("  📤 Agent2 -> Agent1: Hello from Agent2 to Agent1")

        # Mesajların işlenmesini bekle
        time.sleep(3)

        # Sonuçları kontrol et
        assert len(agent1_messages) == 1, f"Agent1 1 mesaj almalı, {len(agent1_messages)} aldı"
        assert len(agent2_messages) == 1, f"Agent2 1 mesaj almalı, {len(agent2_messages)} aldı"

        assert agent1_messages[0].content == "Hello from Agent2 to Agent1"
        assert agent2_messages[0].content == "Hello from Agent1 to Agent2"

        print("✅ İki yönlü iletişim testi başarılı!")
        return True

    except Exception as e:
        print(f"❌ İki yönlü iletişim testi başarısız: {e}")
        return False
    finally:
        agent1.stop_consuming_messages()
        agent2.stop_consuming_messages()
        agent1.disconnect()
        agent2.disconnect()


def run_all_integration_tests():
    """Tüm entegrasyon testlerini çalıştır"""
    print("🚀 Communication Agent Entegrasyon Testleri Başlatılıyor...")
    print("=" * 70)

    tests = [
        test_basic_communication,
        test_message_types,
        test_priority_levels,
        test_heartbeat_functionality,
        test_context_manager,
        test_error_handling,
        test_statistics_tracking,
        test_consume_messages,
        test_bidirectional_communication
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

    print("\n" + "=" * 70)
    print(f"📊 Test Sonuçları:")
    print(f"✅ Başarılı: {passed}")
    print(f"❌ Başarısız: {failed}")
    print(f"📈 Başarı Oranı: {(passed/(passed+failed)*100):.1f}%")

    if failed == 0:
        print("🎉 Tüm entegrasyon testleri başarılı!")
        return True
    else:
        print("⚠️ Bazı testler başarısız oldu!")
        return False


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)
