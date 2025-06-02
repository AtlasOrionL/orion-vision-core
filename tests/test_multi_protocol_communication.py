#!/usr/bin/env python3
"""
Multi-Protocol Communication Tests - Atlas Prompt 3.2.1
Orion Vision Core - Çoklu Protokol İletişim Sistemi Testleri

Bu script, multi_protocol_communication.py modülünün unit testlerini içerir.
"""

import unittest
import asyncio
import sys
import os
import time
import tempfile
from unittest.mock import Mock, patch, AsyncMock

# Test modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))

from multi_protocol_communication import (
    ProtocolType, ProtocolConfig, MessageRoute, ConnectionStatus,
    ProtocolAdapter, MultiProtocolCommunicationManager,
    WebSocketAdapter, HTTPAdapter, RabbitMQAdapter
)
from communication_agent import OrionMessage, MessageType, MessagePriority


class TestProtocolConfig(unittest.TestCase):
    """Protocol configuration testleri"""
    
    def test_protocol_config_creation(self):
        """Protocol config oluşturma testi"""
        config = ProtocolConfig(
            protocol_type=ProtocolType.WEBSOCKET,
            host="localhost",
            port=8765,
            path="/ws",
            ssl_enabled=True,
            timeout=30.0
        )
        
        self.assertEqual(config.protocol_type, ProtocolType.WEBSOCKET)
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 8765)
        self.assertEqual(config.path, "/ws")
        self.assertTrue(config.ssl_enabled)
        self.assertEqual(config.timeout, 30.0)
        self.assertIsInstance(config.metadata, dict)
    
    def test_protocol_config_defaults(self):
        """Protocol config varsayılan değerler testi"""
        config = ProtocolConfig(protocol_type=ProtocolType.HTTP)
        
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.path, "/")
        self.assertFalse(config.ssl_enabled)
        self.assertEqual(config.timeout, 30.0)
        self.assertEqual(config.retry_attempts, 3)
        self.assertEqual(config.retry_delay, 1.0)


class TestMessageRoute(unittest.TestCase):
    """Message route testleri"""
    
    def test_message_route_creation(self):
        """Message route oluşturma testi"""
        route = MessageRoute(
            source_protocol=ProtocolType.WEBSOCKET,
            target_protocol=ProtocolType.RABBITMQ,
            source_address="ws_queue",
            target_address="rmq_queue"
        )
        
        self.assertEqual(route.source_protocol, ProtocolType.WEBSOCKET)
        self.assertEqual(route.target_protocol, ProtocolType.RABBITMQ)
        self.assertEqual(route.source_address, "ws_queue")
        self.assertEqual(route.target_address, "rmq_queue")
        self.assertIsInstance(route.transformation_rules, dict)


class TestProtocolAdapter(unittest.TestCase):
    """Protocol adapter base class testleri"""
    
    def setUp(self):
        """Test setup"""
        self.config = ProtocolConfig(
            protocol_type=ProtocolType.WEBSOCKET,
            host="localhost",
            port=8765
        )
        
        # Mock adapter oluştur
        class MockAdapter(ProtocolAdapter):
            async def connect(self):
                self.status = ConnectionStatus.CONNECTED
                return True
            
            async def disconnect(self):
                self.status = ConnectionStatus.DISCONNECTED
                return True
            
            async def send_message(self, message, target):
                self.stats['messages_sent'] += 1
                return True
            
            async def start_listening(self):
                return True
            
            async def stop_listening(self):
                return True
        
        self.adapter = MockAdapter(self.config, "test_agent")
    
    def test_adapter_initialization(self):
        """Adapter başlatma testi"""
        self.assertEqual(self.adapter.config.protocol_type, ProtocolType.WEBSOCKET)
        self.assertEqual(self.adapter.agent_id, "test_agent")
        self.assertEqual(self.adapter.status, ConnectionStatus.DISCONNECTED)
        self.assertIsInstance(self.adapter.message_handlers, dict)
        self.assertIsInstance(self.adapter.stats, dict)
    
    def test_adapter_message_handler(self):
        """Message handler ekleme testi"""
        def test_handler(message):
            pass
        
        self.adapter.add_message_handler("test_type", test_handler)
        self.assertIn("test_type", self.adapter.message_handlers)
        self.assertEqual(self.adapter.message_handlers["test_type"], test_handler)
    
    def test_adapter_stats(self):
        """Adapter istatistikleri testi"""
        stats = self.adapter.get_stats()
        
        self.assertIn('protocol', stats)
        self.assertIn('status', stats)
        self.assertIn('agent_id', stats)
        self.assertIn('messages_sent', stats)
        self.assertIn('messages_received', stats)
        
        self.assertEqual(stats['protocol'], ProtocolType.WEBSOCKET.value)
        self.assertEqual(stats['agent_id'], "test_agent")


class TestMultiProtocolCommunicationManager(unittest.TestCase):
    """Multi-protocol communication manager testleri"""
    
    def setUp(self):
        """Test setup"""
        self.manager = MultiProtocolCommunicationManager("test_agent")
    
    def test_manager_initialization(self):
        """Manager başlatma testi"""
        self.assertEqual(self.manager.agent_id, "test_agent")
        self.assertIsInstance(self.manager.adapters, dict)
        self.assertIsInstance(self.manager.routes, list)
        self.assertEqual(self.manager.default_protocol, ProtocolType.RABBITMQ)
        self.assertTrue(self.manager.circuit_breaker_enabled)
        self.assertFalse(self.manager.load_balancer_enabled)
    
    def test_add_protocol(self):
        """Protokol ekleme testi"""
        config = ProtocolConfig(
            protocol_type=ProtocolType.WEBSOCKET,
            host="localhost",
            port=8765
        )
        
        # Mock WebSocketAdapter
        with patch('multi_protocol_communication.WebSocketAdapter') as mock_adapter:
            mock_instance = Mock()
            mock_adapter.return_value = mock_instance
            
            success = self.manager.add_protocol(ProtocolType.WEBSOCKET, config)
            
            self.assertTrue(success)
            self.assertIn(ProtocolType.WEBSOCKET, self.manager.adapters)
            self.assertIn(ProtocolType.WEBSOCKET.value, self.manager.stats['protocol_usage'])
    
    def test_add_message_route(self):
        """Message route ekleme testi"""
        route = MessageRoute(
            source_protocol=ProtocolType.WEBSOCKET,
            target_protocol=ProtocolType.RABBITMQ,
            source_address="*",
            target_address="test_queue"
        )
        
        self.manager.add_message_route(route)
        
        self.assertEqual(len(self.manager.routes), 1)
        self.assertEqual(self.manager.routes[0], route)
    
    def test_global_message_handler(self):
        """Global message handler testi"""
        def test_handler(message):
            pass
        
        # Mock adapter ekle
        mock_adapter = Mock()
        self.manager.adapters[ProtocolType.WEBSOCKET] = mock_adapter
        
        self.manager.add_global_message_handler("test_type", test_handler)
        
        self.assertIn("test_type", self.manager.global_message_handlers)
        mock_adapter.add_message_handler.assert_called_with("test_type", test_handler)
    
    def test_protocol_selection(self):
        """Protokol seçimi testi"""
        # Mock adapters
        mock_ws_adapter = Mock()
        mock_ws_adapter.status = ConnectionStatus.CONNECTED
        mock_rmq_adapter = Mock()
        mock_rmq_adapter.status = ConnectionStatus.CONNECTED
        
        self.manager.adapters[ProtocolType.WEBSOCKET] = mock_ws_adapter
        self.manager.adapters[ProtocolType.RABBITMQ] = mock_rmq_adapter
        
        # Preferred protocol test
        selected = self.manager._select_protocol(ProtocolType.WEBSOCKET, "test_target")
        self.assertEqual(selected, ProtocolType.WEBSOCKET)
        
        # Default protocol test
        selected = self.manager._select_protocol(None, "test_target")
        self.assertEqual(selected, ProtocolType.RABBITMQ)  # Default
    
    def test_circuit_breaker(self):
        """Circuit breaker testi"""
        protocol = ProtocolType.WEBSOCKET
        
        # Initial state
        self.assertTrue(self.manager._check_circuit_breaker(protocol))
        
        # Record failures
        for _ in range(5):
            self.manager._record_circuit_breaker_failure(protocol)
        
        # Circuit breaker should be open
        self.assertFalse(self.manager._check_circuit_breaker(protocol))
        
        # Reset should close circuit breaker
        self.manager._reset_circuit_breaker_failure(protocol)
        self.assertTrue(self.manager._check_circuit_breaker(protocol))
    
    def test_routing_decision_recording(self):
        """Routing decision kayıt testi"""
        protocol = ProtocolType.WEBSOCKET
        target = "test_target"
        
        # Record successful routing
        self.manager._record_routing_decision(protocol, target, True)
        
        key = f"{protocol.value}:{target}"
        self.assertIn(key, self.manager.stats['routing_decisions'])
        self.assertEqual(self.manager.stats['routing_decisions'][key]['success'], 1)
        self.assertEqual(self.manager.stats['routing_decisions'][key]['failure'], 0)
        
        # Record failed routing
        self.manager._record_routing_decision(protocol, target, False)
        self.assertEqual(self.manager.stats['routing_decisions'][key]['failure'], 1)
    
    def test_health_status(self):
        """Health status testi"""
        # Mock adapters
        mock_healthy_adapter = Mock()
        mock_healthy_adapter.status = ConnectionStatus.CONNECTED
        mock_healthy_adapter.stats = {'errors': 0, 'messages_sent': 10, 'messages_received': 5}
        
        mock_unhealthy_adapter = Mock()
        mock_unhealthy_adapter.status = ConnectionStatus.ERROR
        mock_unhealthy_adapter.stats = {'errors': 5, 'messages_sent': 2, 'messages_received': 1}
        
        self.manager.adapters[ProtocolType.WEBSOCKET] = mock_healthy_adapter
        self.manager.adapters[ProtocolType.HTTP] = mock_unhealthy_adapter
        
        health = self.manager.get_health_status()
        
        self.assertEqual(health['connected_protocols'], 1)
        self.assertEqual(health['total_protocols'], 2)
        self.assertEqual(health['overall_health'], 'degraded')  # 1/2 connected
        self.assertTrue(health['protocol_health']['websocket']['healthy'])
        self.assertFalse(health['protocol_health']['http']['healthy'])
    
    def test_comprehensive_stats(self):
        """Kapsamlı istatistik testi"""
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.get_stats.return_value = {
            'protocol': 'websocket',
            'status': 'connected',
            'messages_sent': 10
        }
        mock_adapter.status = ConnectionStatus.CONNECTED
        
        self.manager.adapters[ProtocolType.WEBSOCKET] = mock_adapter
        
        stats = self.manager.get_comprehensive_stats()
        
        self.assertIn('agent_id', stats)
        self.assertIn('manager_stats', stats)
        self.assertIn('adapter_stats', stats)
        self.assertIn('circuit_breaker_state', stats)
        self.assertIn('active_protocols', stats)
        self.assertIn('total_routes', stats)
        
        self.assertEqual(stats['agent_id'], "test_agent")
        self.assertIn('websocket', stats['adapter_stats'])
        self.assertIn('websocket', stats['active_protocols'])


class TestAsyncMethods(unittest.IsolatedAsyncioTestCase):
    """Async method testleri"""
    
    async def asyncSetUp(self):
        """Async test setup"""
        self.manager = MultiProtocolCommunicationManager("async_test_agent")
    
    async def test_connect_all(self):
        """Connect all testi"""
        # Mock adapters
        mock_adapter1 = AsyncMock()
        mock_adapter1.connect.return_value = True
        mock_adapter2 = AsyncMock()
        mock_adapter2.connect.return_value = False
        
        self.manager.adapters[ProtocolType.WEBSOCKET] = mock_adapter1
        self.manager.adapters[ProtocolType.HTTP] = mock_adapter2
        
        results = await self.manager.connect_all()
        
        self.assertTrue(results[ProtocolType.WEBSOCKET])
        self.assertFalse(results[ProtocolType.HTTP])
        mock_adapter1.connect.assert_called_once()
        mock_adapter2.connect.assert_called_once()
    
    async def test_disconnect_all(self):
        """Disconnect all testi"""
        # Mock adapters
        mock_adapter1 = AsyncMock()
        mock_adapter1.disconnect.return_value = True
        mock_adapter2 = AsyncMock()
        mock_adapter2.disconnect.return_value = True
        
        self.manager.adapters[ProtocolType.WEBSOCKET] = mock_adapter1
        self.manager.adapters[ProtocolType.HTTP] = mock_adapter2
        
        results = await self.manager.disconnect_all()
        
        self.assertTrue(results[ProtocolType.WEBSOCKET])
        self.assertTrue(results[ProtocolType.HTTP])
        mock_adapter1.disconnect.assert_called_once()
        mock_adapter2.disconnect.assert_called_once()
    
    async def test_send_message(self):
        """Send message testi"""
        # Mock adapter
        mock_adapter = AsyncMock()
        mock_adapter.status = ConnectionStatus.CONNECTED
        mock_adapter.send_message.return_value = True
        
        self.manager.adapters[ProtocolType.WEBSOCKET] = mock_adapter
        self.manager.default_protocol = ProtocolType.WEBSOCKET
        
        # Test message
        message = OrionMessage(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="Test message",
            sender_id="test_sender",
            priority=MessagePriority.NORMAL.value
        )
        
        success = await self.manager.send_message(message, "test_target")
        
        self.assertTrue(success)
        mock_adapter.send_message.assert_called_once_with(message, "test_target")
        self.assertEqual(self.manager.stats['total_messages_sent'], 1)
    
    async def test_start_all_listening(self):
        """Start all listening testi"""
        # Mock adapters
        mock_adapter1 = AsyncMock()
        mock_adapter1.start_listening.return_value = True
        mock_adapter2 = AsyncMock()
        mock_adapter2.start_listening.return_value = True
        
        self.manager.adapters[ProtocolType.WEBSOCKET] = mock_adapter1
        self.manager.adapters[ProtocolType.HTTP] = mock_adapter2
        
        results = await self.manager.start_all_listening()
        
        self.assertTrue(results[ProtocolType.WEBSOCKET])
        self.assertTrue(results[ProtocolType.HTTP])
        mock_adapter1.start_listening.assert_called_once()
        mock_adapter2.start_listening.assert_called_once()


def run_multi_protocol_tests():
    """Multi-protocol communication testlerini çalıştır"""
    print("🚀 Multi-Protocol Communication Tests - Atlas Prompt 3.2.1")
    print("=" * 70)
    
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestProtocolConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestMessageRoute))
    suite.addTests(loader.loadTestsFromTestCase(TestProtocolAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiProtocolCommunicationManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAsyncMethods))
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Testleri çalıştır
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 Tüm Multi-Protocol Communication testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_multi_protocol_tests()
    sys.exit(0 if success else 1)
