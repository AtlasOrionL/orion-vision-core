#!/usr/bin/env python3
"""
Communication Agent Test - Atlas Prompt 1.2.1
Orion Vision Core - Communication Agent Sınıf Testi

Bu script, CommunicationAgent sınıfının temel işlevselliğini test eder.
"""

import unittest
import sys
import os
import time
import json
from unittest.mock import Mock, patch

# Test modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agents.communication_agent import (
    CommunicationAgent, 
    OrionMessage, 
    MessageType, 
    MessagePriority,
    create_message
)


class TestOrionMessage(unittest.TestCase):
    """OrionMessage sınıfı testleri"""
    
    def test_message_creation(self):
        """Mesaj oluşturma testi"""
        message = OrionMessage(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="Test mesajı",
            sender_id="test_agent"
        )
        
        self.assertEqual(message.message_type, MessageType.AGENT_COMMUNICATION.value)
        self.assertEqual(message.content, "Test mesajı")
        self.assertEqual(message.sender_id, "test_agent")
        self.assertEqual(message.priority, MessagePriority.NORMAL.value)
        self.assertIsNotNone(message.timestamp)
        self.assertIsNotNone(message.metadata)
    
    def test_message_to_dict(self):
        """Mesaj dictionary dönüşümü testi"""
        message = OrionMessage(
            message_type="test",
            content="Test content",
            sender_id="test_sender",
            target_agent="test_target"
        )
        
        message_dict = message.to_dict()
        
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['message_type'], "test")
        self.assertEqual(message_dict['content'], "Test content")
        self.assertEqual(message_dict['sender_id'], "test_sender")
        self.assertEqual(message_dict['target_agent'], "test_target")
    
    def test_message_from_dict(self):
        """Dictionary'den mesaj oluşturma testi"""
        data = {
            'message_type': 'test',
            'content': 'Test content',
            'sender_id': 'test_sender',
            'priority': 'high',
            'timestamp': '2025-05-29T15:30:00Z'
        }
        
        message = OrionMessage.from_dict(data)
        
        self.assertEqual(message.message_type, 'test')
        self.assertEqual(message.content, 'Test content')
        self.assertEqual(message.sender_id, 'test_sender')
        self.assertEqual(message.priority, 'high')
        self.assertEqual(message.timestamp, '2025-05-29T15:30:00Z')
    
    def test_message_json_serialization(self):
        """JSON serileştirme testi"""
        message = OrionMessage(
            message_type="test",
            content="Test content",
            sender_id="test_sender"
        )
        
        json_str = message.to_json()
        self.assertIsInstance(json_str, str)
        
        # JSON'ın geçerli olduğunu kontrol et
        parsed = json.loads(json_str)
        self.assertEqual(parsed['message_type'], "test")
        self.assertEqual(parsed['content'], "Test content")


class TestCommunicationAgent(unittest.TestCase):
    """CommunicationAgent sınıfı testleri"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        self.agent = CommunicationAgent(
            agent_id="test_agent",
            host="localhost",
            port=5672,
            virtual_host="orion_vhost",
            username="orion_admin",
            password="orion_secure_2024"
        )
    
    def test_agent_initialization(self):
        """Agent başlatma testi"""
        self.assertEqual(self.agent.agent_id, "test_agent")
        self.assertEqual(self.agent.host, "localhost")
        self.assertEqual(self.agent.port, 5672)
        self.assertEqual(self.agent.virtual_host, "orion_vhost")
        self.assertEqual(self.agent.username, "orion_admin")
        self.assertFalse(self.agent.is_connected)
        self.assertFalse(self.agent.is_consuming)
    
    def test_logger_setup(self):
        """Logger kurulum testi"""
        self.assertIsNotNone(self.agent.logger)
        self.assertEqual(self.agent.logger.name, "CommunicationAgent.test_agent")
    
    def test_stats_initialization(self):
        """İstatistik başlatma testi"""
        stats = self.agent.get_stats()
        
        self.assertEqual(stats['agent_id'], "test_agent")
        self.assertFalse(stats['is_connected'])
        self.assertFalse(stats['is_consuming'])
        self.assertEqual(stats['messages_sent'], 0)
        self.assertEqual(stats['messages_received'], 0)
        self.assertEqual(stats['connection_errors'], 0)
    
    def test_priority_value_mapping(self):
        """Öncelik değeri mapping testi"""
        self.assertEqual(self.agent._get_priority_value(MessagePriority.LOW.value), 1)
        self.assertEqual(self.agent._get_priority_value(MessagePriority.NORMAL.value), 5)
        self.assertEqual(self.agent._get_priority_value(MessagePriority.HIGH.value), 8)
        self.assertEqual(self.agent._get_priority_value(MessagePriority.CRITICAL.value), 10)
        self.assertEqual(self.agent._get_priority_value("unknown"), 5)  # Default
    
    def test_message_handler_registration(self):
        """Mesaj handler kayıt testi"""
        def test_handler(message):
            pass
        
        self.agent.register_message_handler("test_type", test_handler)
        self.assertIn("test_type", self.agent.message_handlers)
        self.assertEqual(self.agent.message_handlers["test_type"], test_handler)
    
    @patch('pika.BlockingConnection')
    def test_connection_success(self, mock_connection):
        """Başarılı bağlantı testi"""
        # Mock setup
        mock_conn_instance = Mock()
        mock_channel = Mock()
        mock_conn_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn_instance
        
        # Test
        result = self.agent.connect()
        
        # Assertions
        self.assertTrue(result)
        self.assertTrue(self.agent.is_connected)
        self.assertIsNotNone(self.agent.connection)
        self.assertIsNotNone(self.agent.channel)
        mock_channel.queue_declare.assert_called()
    
    @patch('pika.BlockingConnection')
    def test_connection_failure(self, mock_connection):
        """Bağlantı hatası testi"""
        # Mock setup - exception fırlat
        mock_connection.side_effect = Exception("Connection failed")
        
        # Test
        result = self.agent.connect()
        
        # Assertions
        self.assertFalse(result)
        self.assertFalse(self.agent.is_connected)
        self.assertEqual(self.agent.stats['connection_errors'], 1)
    
    def test_disconnect_without_connection(self):
        """Bağlantı olmadan disconnect testi"""
        # Bu test exception fırlatmamalı
        self.agent.disconnect()
        self.assertFalse(self.agent.is_connected)
    
    @patch('pika.BlockingConnection')
    def test_queue_declaration(self, mock_connection):
        """Queue oluşturma testi"""
        # Mock setup
        mock_conn_instance = Mock()
        mock_channel = Mock()
        mock_conn_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn_instance
        
        # Bağlan
        self.agent.connect()
        
        # Test
        result = self.agent.declare_queue("test_queue")
        
        # Assertions
        self.assertTrue(result)
        mock_channel.queue_declare.assert_called_with(queue="test_queue", durable=True)
    
    def test_queue_declaration_without_connection(self):
        """Bağlantı olmadan queue oluşturma testi"""
        result = self.agent.declare_queue("test_queue")
        self.assertFalse(result)
    
    @patch('pika.BlockingConnection')
    def test_publish_message(self, mock_connection):
        """Mesaj gönderme testi"""
        # Mock setup
        mock_conn_instance = Mock()
        mock_channel = Mock()
        mock_conn_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn_instance
        
        # Bağlan
        self.agent.connect()
        
        # Test mesajı oluştur
        message = OrionMessage(
            message_type="test",
            content="Test message",
            sender_id="original_sender"
        )
        
        # Test
        result = self.agent.publish_message("test_queue", message)
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(self.agent.stats['messages_sent'], 1)
        self.assertEqual(message.sender_id, "test_agent")  # Agent ID ile güncellenmeli
        mock_channel.basic_publish.assert_called_once()
    
    def test_publish_message_without_connection(self):
        """Bağlantı olmadan mesaj gönderme testi"""
        message = OrionMessage(
            message_type="test",
            content="Test message",
            sender_id="test_sender"
        )
        
        result = self.agent.publish_message("test_queue", message)
        self.assertFalse(result)
        self.assertEqual(self.agent.stats['messages_sent'], 0)
    
    @patch('pika.BlockingConnection')
    def test_heartbeat(self, mock_connection):
        """Heartbeat gönderme testi"""
        # Mock setup
        mock_conn_instance = Mock()
        mock_channel = Mock()
        mock_conn_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn_instance
        
        # Bağlan
        self.agent.connect()
        
        # Test
        result = self.agent.send_heartbeat()
        
        # Assertions
        self.assertTrue(result)
        self.assertIsNotNone(self.agent.stats['last_heartbeat'])
        mock_channel.basic_publish.assert_called()
    
    @patch('pika.BlockingConnection')
    def test_context_manager(self, mock_connection):
        """Context manager testi"""
        # Mock setup
        mock_conn_instance = Mock()
        mock_channel = Mock()
        mock_conn_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn_instance
        
        # Test
        with CommunicationAgent("context_test_agent") as agent:
            self.assertTrue(agent.is_connected)
        
        # Context'ten çıktıktan sonra bağlantı kapatılmalı
        # (Mock olduğu için gerçek kapatma olmayacak ama metot çağrılacak)


class TestConvenienceFunctions(unittest.TestCase):
    """Yardımcı fonksiyon testleri"""
    
    def test_create_message_function(self):
        """create_message fonksiyonu testi"""
        message = create_message(
            message_type="test",
            content="Test content",
            sender_id="test_sender",
            target_agent="test_target",
            priority=MessagePriority.HIGH.value,
            custom_field="custom_value"
        )
        
        self.assertIsInstance(message, OrionMessage)
        self.assertEqual(message.message_type, "test")
        self.assertEqual(message.content, "Test content")
        self.assertEqual(message.sender_id, "test_sender")
        self.assertEqual(message.target_agent, "test_target")
        self.assertEqual(message.priority, MessagePriority.HIGH.value)
        self.assertEqual(message.metadata["custom_field"], "custom_value")


def run_communication_agent_tests():
    """Communication Agent testlerini çalıştır"""
    print("🚀 Communication Agent Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestOrionMessage))
    suite.addTests(loader.loadTestsFromTestCase(TestCommunicationAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Testleri çalıştır
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 Tüm Communication Agent testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_communication_agent_tests()
    sys.exit(0 if success else 1)
