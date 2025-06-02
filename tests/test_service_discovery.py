#!/usr/bin/env python3
"""
Service Discovery Tests - Sprint 4.1
Orion Vision Core - Distributed Agent Coordination

Bu modül, Service Discovery sisteminin tüm bileşenlerini test eder.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import unittest
import asyncio
import time
import tempfile
import shutil
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Test edilecek modülleri import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from jobone.vision_core.service_discovery import (
    ServiceInfo,
    ServiceStatus,
    ServiceRegistry,
    HealthMonitor,
    LoadBalancer,
    LoadBalancingStrategy,
    ServiceDiscoveryManager
)


class TestServiceInfo(unittest.TestCase):
    """ServiceInfo testleri"""
    
    def setUp(self):
        """Test setup"""
        self.service_info = ServiceInfo(
            agent_id="test_agent",
            service_name="test_service",
            host="localhost",
            port=8080,
            capabilities=["test", "demo"],
            metadata={"version": "1.0.0"},
            tags=["test"]
        )
    
    def test_service_info_creation(self):
        """ServiceInfo oluşturma testi"""
        self.assertEqual(self.service_info.agent_id, "test_agent")
        self.assertEqual(self.service_info.service_name, "test_service")
        self.assertEqual(self.service_info.host, "localhost")
        self.assertEqual(self.service_info.port, 8080)
        self.assertEqual(self.service_info.capabilities, ["test", "demo"])
        self.assertEqual(self.service_info.metadata["version"], "1.0.0")
        self.assertEqual(self.service_info.tags, ["test"])
    
    def test_service_info_to_dict(self):
        """ServiceInfo to dict conversion testi"""
        data = self.service_info.to_dict()
        
        self.assertIn('service_id', data)
        self.assertEqual(data['agent_id'], "test_agent")
        self.assertEqual(data['service_name'], "test_service")
        self.assertEqual(data['host'], "localhost")
        self.assertEqual(data['port'], 8080)
    
    def test_service_info_from_dict(self):
        """ServiceInfo from dict creation testi"""
        data = {
            'agent_id': 'test_agent_2',
            'service_name': 'test_service_2',
            'host': 'localhost',
            'port': 9090,
            'capabilities': ['test2'],
            'status': 'healthy'
        }
        
        service = ServiceInfo.from_dict(data)
        
        self.assertEqual(service.agent_id, "test_agent_2")
        self.assertEqual(service.service_name, "test_service_2")
        self.assertEqual(service.port, 9090)
        self.assertEqual(service.capabilities, ["test2"])
    
    def test_endpoint_url(self):
        """Endpoint URL testi"""
        url = self.service_info.get_endpoint_url()
        self.assertEqual(url, "http://localhost:8080")
    
    def test_is_healthy(self):
        """Health check testi"""
        # Healthy service
        self.service_info.status = ServiceStatus.HEALTHY
        self.service_info.update_heartbeat()
        self.assertTrue(self.service_info.is_healthy())
        
        # Unhealthy service
        self.service_info.status = ServiceStatus.UNHEALTHY
        self.assertFalse(self.service_info.is_healthy())
        
        # Timeout test
        self.service_info.status = ServiceStatus.HEALTHY
        self.service_info.last_heartbeat = time.time() - 100  # Old heartbeat
        self.assertFalse(self.service_info.is_healthy(timeout=30.0))
    
    def test_update_heartbeat(self):
        """Heartbeat update testi"""
        old_heartbeat = self.service_info.last_heartbeat
        time.sleep(0.1)
        self.service_info.update_heartbeat()
        self.assertGreater(self.service_info.last_heartbeat, old_heartbeat)


class TestServiceRegistry(unittest.TestCase):
    """ServiceRegistry testleri"""
    
    def setUp(self):
        """Test setup"""
        self.registry = ServiceRegistry("test_registry", cleanup_interval=1.0)
        
        self.test_service = ServiceInfo(
            agent_id="test_agent",
            service_name="test_service",
            capabilities=["test"],
            tags=["test"]
        )
    
    def tearDown(self):
        """Test cleanup"""
        asyncio.run(self.registry.stop())
    
    def test_registry_initialization(self):
        """Registry başlatma testi"""
        self.assertEqual(self.registry.registry_id, "test_registry")
        self.assertEqual(self.registry.cleanup_interval, 1.0)
        self.assertFalse(self.registry.running)
        self.assertEqual(len(self.registry.services), 0)
    
    def test_service_registration(self):
        """Service kayıt testi"""
        success = self.registry.register_service(self.test_service)
        
        self.assertTrue(success)
        self.assertEqual(len(self.registry.services), 1)
        self.assertIn(self.test_service.service_id, self.registry.services)
        
        # Stats kontrolü
        stats = self.registry.get_registry_stats()
        self.assertEqual(stats['active_services'], 1)
        self.assertEqual(stats['stats']['total_registrations'], 1)
    
    def test_service_unregistration(self):
        """Service kayıt silme testi"""
        # Önce kaydet
        self.registry.register_service(self.test_service)
        self.assertEqual(len(self.registry.services), 1)
        
        # Sonra sil
        success = self.registry.unregister_service(self.test_service.service_id)
        
        self.assertTrue(success)
        self.assertEqual(len(self.registry.services), 0)
        self.assertNotIn(self.test_service.service_id, self.registry.services)
    
    def test_service_discovery(self):
        """Service keşif testi"""
        # Multiple service'ler kaydet
        service1 = ServiceInfo(agent_id="agent1", service_name="service1", 
                              service_type="type1", capabilities=["cap1"])
        service2 = ServiceInfo(agent_id="agent2", service_name="service2", 
                              service_type="type2", capabilities=["cap2"])
        service3 = ServiceInfo(agent_id="agent3", service_name="service3", 
                              service_type="type1", capabilities=["cap1", "cap2"])
        
        self.registry.register_service(service1)
        self.registry.register_service(service2)
        self.registry.register_service(service3)
        
        # Type-based discovery
        type1_services = self.registry.discover_services(service_type="type1")
        self.assertEqual(len(type1_services), 2)
        
        # Capability-based discovery
        cap1_services = self.registry.discover_services(capability="cap1")
        self.assertEqual(len(cap1_services), 2)
        
        # Combined discovery
        combined_services = self.registry.discover_services(service_type="type1", capability="cap1")
        self.assertEqual(len(combined_services), 2)
    
    def test_heartbeat_update(self):
        """Heartbeat güncelleme testi"""
        self.registry.register_service(self.test_service)
        
        old_heartbeat = self.test_service.last_heartbeat
        time.sleep(0.1)
        
        success = self.registry.heartbeat(self.test_service.service_id)
        
        self.assertTrue(success)
        self.assertGreater(self.test_service.last_heartbeat, old_heartbeat)
    
    def test_service_status_update(self):
        """Service status güncelleme testi"""
        self.registry.register_service(self.test_service)
        
        success = self.registry.update_service_status(
            self.test_service.service_id, 
            ServiceStatus.UNHEALTHY
        )
        
        self.assertTrue(success)
        self.assertEqual(self.test_service.status, ServiceStatus.UNHEALTHY)


class TestHealthMonitor(unittest.IsolatedAsyncioTestCase):
    """HealthMonitor testleri"""
    
    async def asyncSetUp(self):
        """Async test setup"""
        self.registry = ServiceRegistry("test_registry")
        self.health_monitor = HealthMonitor(self.registry, check_interval=1.0)
        
        self.test_service = ServiceInfo(
            agent_id="test_agent",
            service_name="test_service",
            host="localhost",
            port=8080,
            health_check_url="http://localhost:8080/health"
        )
        
        await self.registry.start()
    
    async def asyncTearDown(self):
        """Async test cleanup"""
        await self.health_monitor.stop()
        await self.registry.stop()
    
    def test_health_monitor_initialization(self):
        """Health monitor başlatma testi"""
        self.assertEqual(self.health_monitor.check_interval, 1.0)
        self.assertFalse(self.health_monitor.running)
        self.assertIsNotNone(self.health_monitor.health_checkers)
    
    async def test_health_monitor_start_stop(self):
        """Health monitor start/stop testi"""
        await self.health_monitor.start()
        self.assertTrue(self.health_monitor.running)
        
        await self.health_monitor.stop()
        self.assertFalse(self.health_monitor.running)
    
    @patch('jobone.vision_core.service_discovery.HealthMonitor._http_health_check')
    async def test_service_health_check(self, mock_http_check):
        """Service health check testi"""
        mock_http_check.return_value = True
        
        self.registry.register_service(self.test_service)
        
        result = await self.health_monitor.check_service_health(self.test_service)
        
        self.assertTrue(result)
        mock_http_check.assert_called_once()
        
        # Stats kontrolü
        stats = self.health_monitor.get_health_stats()
        self.assertEqual(stats['stats']['total_checks'], 1)
        self.assertEqual(stats['stats']['successful_checks'], 1)


class TestLoadBalancer(unittest.TestCase):
    """LoadBalancer testleri"""
    
    def setUp(self):
        """Test setup"""
        self.registry = ServiceRegistry("test_registry")
        self.load_balancer = LoadBalancer(self.registry, LoadBalancingStrategy.ROUND_ROBIN)
        
        # Test service'leri oluştur
        self.services = []
        for i in range(3):
            service = ServiceInfo(
                agent_id=f"agent_{i}",
                service_name=f"service_{i}",
                service_type="test",
                capabilities=["test"],
                status=ServiceStatus.HEALTHY
            )
            self.services.append(service)
            self.registry.register_service(service)
    
    def test_load_balancer_initialization(self):
        """Load balancer başlatma testi"""
        self.assertEqual(self.load_balancer.strategy, LoadBalancingStrategy.ROUND_ROBIN)
        self.assertIsNotNone(self.load_balancer.round_robin_counters)
        self.assertIsNotNone(self.load_balancer.connection_counts)
    
    def test_round_robin_selection(self):
        """Round robin selection testi"""
        selected_agents = []
        
        for _ in range(6):  # 2 full rounds
            selected = self.load_balancer.select_service(service_type="test")
            if selected:
                selected_agents.append(selected.agent_id)
                self.load_balancer.release_service(selected.service_id)
        
        # Her agent'ın 2 kez seçildiğini kontrol et
        agent_counts = {}
        for agent_id in selected_agents:
            agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1
        
        for count in agent_counts.values():
            self.assertEqual(count, 2)
    
    def test_least_connections_selection(self):
        """Least connections selection testi"""
        self.load_balancer.change_strategy(LoadBalancingStrategy.LEAST_CONNECTIONS)
        
        # İlk seçim - hepsi 0 connection'a sahip
        selected1 = self.load_balancer.select_service(service_type="test")
        self.assertIsNotNone(selected1)
        
        # İkinci seçim - farklı bir service seçmeli
        selected2 = self.load_balancer.select_service(service_type="test")
        self.assertIsNotNone(selected2)
        self.assertNotEqual(selected1.service_id, selected2.service_id)
        
        # İlk service'i release et
        self.load_balancer.release_service(selected1.service_id)
        
        # Üçüncü seçim - released service'i seçmeli
        selected3 = self.load_balancer.select_service(service_type="test")
        self.assertEqual(selected1.service_id, selected3.service_id)
    
    def test_response_time_recording(self):
        """Response time kayıt testi"""
        service_id = self.services[0].service_id
        
        # Response time'ları kaydet
        self.load_balancer.record_response_time(service_id, 1.5)
        self.load_balancer.record_response_time(service_id, 2.0)
        self.load_balancer.record_response_time(service_id, 1.0)
        
        # Performance stats kontrol et
        perf = self.load_balancer.get_service_performance(service_id)
        
        self.assertEqual(perf['total_requests'], 3)
        self.assertAlmostEqual(perf['avg_response_time'], 1.5, places=2)
        self.assertEqual(perf['min_response_time'], 1.0)
        self.assertEqual(perf['max_response_time'], 2.0)
    
    def test_service_weight_setting(self):
        """Service weight ayarlama testi"""
        service_id = self.services[0].service_id
        
        self.load_balancer.set_service_weight(service_id, 2.5)
        
        stats = self.load_balancer.get_load_balancer_stats()
        self.assertEqual(stats['service_weights'][service_id], 2.5)
    
    def test_strategy_change(self):
        """Strateji değiştirme testi"""
        initial_strategy = self.load_balancer.strategy
        
        self.load_balancer.change_strategy(LoadBalancingStrategy.RANDOM)
        
        self.assertNotEqual(self.load_balancer.strategy, initial_strategy)
        self.assertEqual(self.load_balancer.strategy, LoadBalancingStrategy.RANDOM)
        
        stats = self.load_balancer.get_load_balancer_stats()
        self.assertEqual(stats['stats']['strategy_switches'], 1)


class TestServiceDiscoveryManager(unittest.IsolatedAsyncioTestCase):
    """ServiceDiscoveryManager testleri"""
    
    async def asyncSetUp(self):
        """Async test setup"""
        self.discovery_manager = ServiceDiscoveryManager(
            registry_id="test_manager",
            health_check_interval=5.0,
            cleanup_interval=10.0,
            load_balancing_strategy=LoadBalancingStrategy.ROUND_ROBIN
        )
    
    async def asyncTearDown(self):
        """Async test cleanup"""
        await self.discovery_manager.stop()
    
    def test_discovery_manager_initialization(self):
        """Discovery manager başlatma testi"""
        self.assertEqual(self.discovery_manager.manager_id, "test_manager")
        self.assertFalse(self.discovery_manager.running)
        self.assertIsNotNone(self.discovery_manager.registry)
        self.assertIsNotNone(self.discovery_manager.health_monitor)
        self.assertIsNotNone(self.discovery_manager.load_balancer)
    
    async def test_discovery_manager_start_stop(self):
        """Discovery manager start/stop testi"""
        await self.discovery_manager.start()
        self.assertTrue(self.discovery_manager.running)
        
        await self.discovery_manager.stop()
        self.assertFalse(self.discovery_manager.running)
    
    async def test_agent_registration(self):
        """Agent kayıt testi"""
        await self.discovery_manager.start()
        
        service_id = self.discovery_manager.register_agent_service(
            agent_id="test_agent",
            service_name="test_service",
            capabilities=["test"],
            tags=["demo"]
        )
        
        self.assertIsNotNone(service_id)
        
        # Agent'ı keşfet
        agents = self.discovery_manager.discover_agents(capability="test")
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0].agent_id, "test_agent")
    
    async def test_agent_selection(self):
        """Agent seçim testi"""
        await self.discovery_manager.start()
        
        # Multiple agent'ları kaydet
        for i in range(3):
            self.discovery_manager.register_agent_service(
                agent_id=f"agent_{i}",
                service_name=f"service_{i}",
                capabilities=["test"]
            )
        
        # Agent seç
        selected = self.discovery_manager.select_agent(capability="test")
        self.assertIsNotNone(selected)
        self.assertIn("agent_", selected.agent_id)
        
        # Release et
        self.discovery_manager.release_agent(selected.service_id)
    
    def test_comprehensive_stats(self):
        """Kapsamlı istatistik testi"""
        stats = self.discovery_manager.get_comprehensive_stats()
        
        self.assertIn('manager_id', stats)
        self.assertIn('running', stats)
        self.assertIn('manager_stats', stats)
        self.assertIn('registry_stats', stats)
        self.assertIn('health_stats', stats)
        self.assertIn('load_balancer_stats', stats)


def run_service_discovery_tests():
    """Service Discovery testlerini çalıştır"""
    print("🔍 Service Discovery Tests - Sprint 4.1")
    print("=" * 70)
    
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestServiceInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestServiceRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestLoadBalancer))
    suite.addTests(loader.loadTestsFromTestCase(TestServiceDiscoveryManager))
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Testleri çalıştır
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 Tüm Service Discovery testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_service_discovery_tests()
    sys.exit(0 if success else 1)
