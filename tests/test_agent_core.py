#!/usr/bin/env python3
"""
Agent Core Unit Tests - Atlas Prompt 2.1.1
Orion Vision Core - Agent Core Modül Testleri

Bu script, agent_core.py modülünün unit testlerini içerir.
"""

import unittest
import sys
import os
import time
import threading
from unittest.mock import Mock, patch

# Test modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agent_core import (
    Agent, 
    AgentConfig, 
    AgentStatus, 
    AgentPriority,
    AgentLogger,
    AgentManager,
    create_agent_config,
    load_agent_config
)


class TestAgentConfig(unittest.TestCase):
    """AgentConfig sınıfı testleri"""
    
    def test_config_creation(self):
        """Konfigürasyon oluşturma testi"""
        config = AgentConfig(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test"
        )
        
        self.assertEqual(config.agent_id, "test_agent")
        self.assertEqual(config.agent_name, "Test Agent")
        self.assertEqual(config.agent_type, "test")
        self.assertEqual(config.priority, AgentPriority.NORMAL.value)
        self.assertFalse(config.auto_start)
        self.assertEqual(config.max_retries, 3)
        self.assertIsInstance(config.capabilities, list)
        self.assertIsInstance(config.dependencies, list)
        self.assertIsInstance(config.metadata, dict)
    
    def test_config_with_custom_values(self):
        """Özel değerlerle konfigürasyon testi"""
        config = AgentConfig(
            agent_id="custom_agent",
            agent_name="Custom Agent",
            agent_type="custom",
            priority=AgentPriority.HIGH.value,
            auto_start=True,
            max_retries=5,
            capabilities=["test1", "test2"],
            dependencies=["dep1"],
            metadata={"key": "value"}
        )
        
        self.assertEqual(config.priority, AgentPriority.HIGH.value)
        self.assertTrue(config.auto_start)
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.capabilities, ["test1", "test2"])
        self.assertEqual(config.dependencies, ["dep1"])
        self.assertEqual(config.metadata, {"key": "value"})


class TestAgentLogger(unittest.TestCase):
    """AgentLogger sınıfı testleri"""
    
    def test_logger_creation(self):
        """Logger oluşturma testi"""
        logger = AgentLogger("test_agent", "INFO")
        
        self.assertEqual(logger.agent_id, "test_agent")
        self.assertIsNotNone(logger.logger)
        self.assertEqual(logger.logger.name, "Agent.test_agent")
    
    def test_logging_methods(self):
        """Logging metodları testi"""
        logger = AgentLogger("test_logger", "DEBUG")
        
        # Bu testler exception fırlatmamalı
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")


class MockAgent(Agent):
    """Test için mock agent sınıfı"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.initialized = False
        self.ran = False
        self.cleaned_up = False
        self.run_duration = 0.1
    
    def initialize(self) -> bool:
        self.initialized = True
        return True
    
    def run(self):
        self.ran = True
        time.sleep(self.run_duration)
    
    def cleanup(self):
        self.cleaned_up = True


class TestAgent(unittest.TestCase):
    """Agent sınıfı testleri"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        self.config = create_agent_config(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test",
            heartbeat_interval=1.0,
            timeout=5.0
        )
        self.agent = MockAgent(self.config)
    
    def test_agent_initialization(self):
        """Agent başlatma testi"""
        self.assertEqual(self.agent.agent_id, "test_agent")
        self.assertEqual(self.agent.agent_name, "Test Agent")
        self.assertEqual(self.agent.agent_type, "test")
        self.assertEqual(self.agent.status, AgentStatus.IDLE)
        self.assertIsNone(self.agent.start_time)
        self.assertIsNone(self.agent.stop_time)
        self.assertEqual(self.agent.error_count, 0)
    
    def test_agent_start_stop(self):
        """Agent başlatma/durdurma testi"""
        # Başlat
        success = self.agent.start()
        self.assertTrue(success)
        self.assertEqual(self.agent.status, AgentStatus.RUNNING)
        self.assertTrue(self.agent.initialized)
        self.assertIsNotNone(self.agent.start_time)
        
        # Biraz bekle
        time.sleep(0.5)
        
        # Durdur
        stop_success = self.agent.stop()
        self.assertTrue(stop_success)
        self.assertEqual(self.agent.status, AgentStatus.STOPPED)
        self.assertTrue(self.agent.cleaned_up)
        self.assertIsNotNone(self.agent.stop_time)
    
    def test_agent_status_methods(self):
        """Agent durum metodları testi"""
        # Başlangıçta çalışmıyor
        self.assertFalse(self.agent.is_running())
        
        # Başlat
        self.agent.start()
        self.assertTrue(self.agent.is_running())
        
        # Durdur
        self.agent.stop()
        self.assertFalse(self.agent.is_running())
    
    def test_agent_capabilities(self):
        """Agent yetenek yönetimi testi"""
        # Yetenek ekle
        self.agent.add_capability("test_capability")
        self.assertTrue(self.agent.has_capability("test_capability"))
        self.assertIn("test_capability", self.agent.config.capabilities)
        
        # Yetenek çıkar
        self.agent.remove_capability("test_capability")
        self.assertFalse(self.agent.has_capability("test_capability"))
        self.assertNotIn("test_capability", self.agent.config.capabilities)
    
    def test_agent_config_update(self):
        """Agent konfigürasyon güncelleme testi"""
        # Konfigürasyon güncelle
        new_config = {
            "max_retries": 5,
            "heartbeat_interval": 20.0,
            "log_level": "DEBUG"
        }
        
        success = self.agent.update_config(new_config)
        self.assertTrue(success)
        self.assertEqual(self.agent.config.max_retries, 5)
        self.assertEqual(self.agent.config.heartbeat_interval, 20.0)
        self.assertEqual(self.agent.config.log_level, "DEBUG")
    
    def test_agent_callbacks(self):
        """Agent callback testi"""
        start_called = False
        stop_called = False
        error_called = False
        
        def start_callback(agent):
            nonlocal start_called
            start_called = True
        
        def stop_callback(agent):
            nonlocal stop_called
            stop_called = True
        
        def error_callback(agent, error):
            nonlocal error_called
            error_called = True
        
        # Callback'leri kaydet
        self.agent.register_callback('start', start_callback)
        self.agent.register_callback('stop', stop_callback)
        self.agent.register_callback('error', error_callback)
        
        # Agent'ı başlat ve durdur
        self.agent.start()
        time.sleep(0.2)
        self.agent.stop()
        
        # Callback'lerin çağrıldığını kontrol et
        self.assertTrue(start_called)
        self.assertTrue(stop_called)
    
    def test_agent_restart(self):
        """Agent yeniden başlatma testi"""
        # İlk başlatma
        self.agent.start()
        first_start_time = self.agent.start_time
        time.sleep(0.2)
        
        # Yeniden başlat
        restart_success = self.agent.restart()
        self.assertTrue(restart_success)
        self.assertEqual(self.agent.status, AgentStatus.RUNNING)
        self.assertNotEqual(self.agent.start_time, first_start_time)
        
        # Temizlik
        self.agent.stop()
    
    def test_agent_context_manager(self):
        """Agent context manager testi"""
        with MockAgent(self.config) as agent:
            self.assertTrue(agent.is_running())
            self.assertTrue(agent.initialized)
        
        # Context'ten çıktıktan sonra durdurulmalı
        self.assertEqual(agent.status, AgentStatus.STOPPED)
        self.assertTrue(agent.cleaned_up)


class TestAgentManager(unittest.TestCase):
    """AgentManager sınıfı testleri"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        self.manager = AgentManager()
        
        # Test agent'ları oluştur
        self.agents = []
        for i in range(3):
            config = create_agent_config(
                agent_id=f"test_agent_{i}",
                agent_name=f"Test Agent {i}",
                agent_type="test",
                heartbeat_interval=1.0
            )
            agent = MockAgent(config)
            agent.run_duration = 0.1  # Kısa çalışma süresi
            self.agents.append(agent)
    
    def tearDown(self):
        """Her test sonrası temizlik"""
        self.manager.stop_all()
    
    def test_agent_registration(self):
        """Agent kayıt testi"""
        agent = self.agents[0]
        
        # Agent'ı kaydet
        success = self.manager.register_agent(agent)
        self.assertTrue(success)
        self.assertIn(agent.agent_id, self.manager.agents)
        
        # Aynı agent'ı tekrar kaydetme denemesi
        duplicate_success = self.manager.register_agent(agent)
        self.assertFalse(duplicate_success)
    
    def test_agent_unregistration(self):
        """Agent kayıt silme testi"""
        agent = self.agents[0]
        
        # Agent'ı kaydet ve sil
        self.manager.register_agent(agent)
        unregister_success = self.manager.unregister_agent(agent.agent_id)
        self.assertTrue(unregister_success)
        self.assertNotIn(agent.agent_id, self.manager.agents)
        
        # Var olmayan agent'ı silme denemesi
        not_found_success = self.manager.unregister_agent("nonexistent")
        self.assertFalse(not_found_success)
    
    def test_start_stop_single_agent(self):
        """Tek agent başlatma/durdurma testi"""
        agent = self.agents[0]
        self.manager.register_agent(agent)
        
        # Agent'ı başlat
        start_success = self.manager.start_agent(agent.agent_id)
        self.assertTrue(start_success)
        self.assertTrue(agent.is_running())
        
        # Agent'ı durdur
        stop_success = self.manager.stop_agent(agent.agent_id)
        self.assertTrue(stop_success)
        self.assertFalse(agent.is_running())
    
    def test_start_stop_all_agents(self):
        """Tüm agent'ları başlatma/durdurma testi"""
        # Tüm agent'ları kaydet
        for agent in self.agents:
            self.manager.register_agent(agent)
        
        # Tüm agent'ları başlat
        start_results = self.manager.start_all()
        self.assertEqual(len(start_results), len(self.agents))
        
        for agent_id, success in start_results.items():
            self.assertTrue(success)
        
        # Çalışan agent'ları kontrol et
        running_agents = self.manager.get_running_agents()
        self.assertEqual(len(running_agents), len(self.agents))
        
        # Tüm agent'ları durdur
        stop_results = self.manager.stop_all()
        self.assertEqual(len(stop_results), len(self.agents))
        
        for agent_id, success in stop_results.items():
            self.assertTrue(success)
    
    def test_agent_status_queries(self):
        """Agent durum sorguları testi"""
        agent = self.agents[0]
        self.manager.register_agent(agent)
        
        # Agent durumunu al
        status = self.manager.get_agent_status(agent.agent_id)
        self.assertIsNotNone(status)
        self.assertEqual(status['agent_id'], agent.agent_id)
        
        # Var olmayan agent durumu
        no_status = self.manager.get_agent_status("nonexistent")
        self.assertIsNone(no_status)
        
        # Tüm agent durumları
        all_status = self.manager.get_all_status()
        self.assertIn(agent.agent_id, all_status)


class TestUtilityFunctions(unittest.TestCase):
    """Yardımcı fonksiyon testleri"""
    
    def test_create_agent_config(self):
        """create_agent_config fonksiyonu testi"""
        config = create_agent_config(
            agent_id="util_test",
            agent_name="Utility Test Agent",
            agent_type="utility",
            priority=AgentPriority.HIGH.value,
            auto_start=True
        )
        
        self.assertIsInstance(config, AgentConfig)
        self.assertEqual(config.agent_id, "util_test")
        self.assertEqual(config.agent_name, "Utility Test Agent")
        self.assertEqual(config.agent_type, "utility")
        self.assertEqual(config.priority, AgentPriority.HIGH.value)
        self.assertTrue(config.auto_start)


def run_agent_core_tests():
    """Agent Core testlerini çalıştır"""
    print("🚀 Agent Core Unit Tests - Atlas Prompt 2.1.1")
    print("=" * 60)
    
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestAgentConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentManager))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Testleri çalıştır
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 Tüm Agent Core testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_agent_core_tests()
    sys.exit(0 if success else 1)
