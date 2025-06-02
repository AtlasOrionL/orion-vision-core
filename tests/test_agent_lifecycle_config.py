#!/usr/bin/env python3
"""
Agent Lifecycle and Configuration Tests - Atlas Prompt 2.1.2
Orion Vision Core - Agent Yaşam Döngüsü ve Konfigürasyon Testleri

Bu script, Atlas Prompt 2.1.2 kapsamında geliştirilen özelliklerin
unit testlerini içerir.
"""

import unittest
import sys
import os
import time
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Test modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agent_core import (
    Agent, AgentConfig, AgentStatus, AgentManager,
    load_agent_config, load_agent_configs_from_directory,
    validate_agent_config, create_agent_config
)
from agent_registry import AgentRegistry, AgentRegistryEntry


class MockAgent(Agent):
    """Test için mock agent sınıfı"""
    
    def __init__(self, config: AgentConfig, auto_register: bool = False):
        super().__init__(config, auto_register)
        self.initialized = False
        self.ran = False
        self.cleaned_up = False
    
    def initialize(self) -> bool:
        self.initialized = True
        return True
    
    def run(self):
        self.ran = True
        time.sleep(0.1)
    
    def cleanup(self):
        self.cleaned_up = True


class TestConfigLoading(unittest.TestCase):
    """Konfigürasyon yükleme testleri"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # Test konfigürasyonu
        self.test_config = {
            "agent_id": "test_agent_001",
            "agent_name": "Test Agent",
            "agent_type": "test_agent",
            "priority": 5,
            "auto_start": True,
            "max_retries": 3,
            "retry_delay": 1.0,
            "heartbeat_interval": 10.0,
            "timeout": 60.0,
            "capabilities": ["test_capability"],
            "dependencies": ["test_dependency"],
            "log_level": "INFO",
            "metadata": {"test_key": "test_value"}
        }
    
    def tearDown(self):
        """Her test sonrası temizlik"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_valid_config(self):
        """Geçerli konfigürasyon yükleme testi"""
        # Konfigürasyonu dosyaya yaz
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
        
        # Konfigürasyonu yükle
        config = load_agent_config(self.config_file)
        
        self.assertIsNotNone(config)
        self.assertEqual(config.agent_id, "test_agent_001")
        self.assertEqual(config.agent_name, "Test Agent")
        self.assertEqual(config.agent_type, "test_agent")
        self.assertEqual(config.priority, 5)
        self.assertTrue(config.auto_start)
        self.assertEqual(config.capabilities, ["test_capability"])
        self.assertEqual(config.metadata, {"test_key": "test_value"})
    
    def test_load_invalid_json(self):
        """Geçersiz JSON konfigürasyon testi"""
        # Geçersiz JSON yaz
        with open(self.config_file, 'w') as f:
            f.write("invalid json content")
        
        # Konfigürasyonu yüklemeye çalış
        config = load_agent_config(self.config_file)
        
        self.assertIsNone(config)
    
    def test_load_missing_required_fields(self):
        """Eksik zorunlu alan testi"""
        # agent_id eksik konfigürasyon
        invalid_config = self.test_config.copy()
        del invalid_config['agent_id']
        
        with open(self.config_file, 'w') as f:
            json.dump(invalid_config, f)
        
        config = load_agent_config(self.config_file)
        
        self.assertIsNone(config)
    
    def test_load_nonexistent_file(self):
        """Var olmayan dosya testi"""
        config = load_agent_config("nonexistent_file.json")
        
        self.assertIsNone(config)
    
    def test_load_configs_from_directory(self):
        """Dizinden konfigürasyon yükleme testi"""
        # Birden fazla konfigürasyon dosyası oluştur
        configs = {
            "agent1.json": {**self.test_config, "agent_id": "agent_001"},
            "agent2.json": {**self.test_config, "agent_id": "agent_002"},
            "invalid.json": {"invalid": "config"}  # Geçersiz konfigürasyon
        }
        
        for filename, config_data in configs.items():
            config_path = os.path.join(self.temp_dir, filename)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
        
        # Dizinden konfigürasyonları yükle
        loaded_configs = load_agent_configs_from_directory(self.temp_dir)
        
        # Sadece geçerli konfigürasyonlar yüklenmeli
        self.assertEqual(len(loaded_configs), 2)
        self.assertIn("agent_001", loaded_configs)
        self.assertIn("agent_002", loaded_configs)
        self.assertNotIn("invalid", loaded_configs)


class TestConfigValidation(unittest.TestCase):
    """Konfigürasyon doğrulama testleri"""
    
    def test_valid_config(self):
        """Geçerli konfigürasyon doğrulama testi"""
        config = create_agent_config(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test",
            priority=5,
            max_retries=3,
            heartbeat_interval=10.0,
            timeout=60.0,
            log_level="INFO"
        )
        
        errors = validate_agent_config(config)
        
        self.assertEqual(len(errors), 0)
    
    def test_invalid_agent_id(self):
        """Geçersiz agent_id testi"""
        config = create_agent_config(
            agent_id="",  # Boş agent_id
            agent_name="Test Agent",
            agent_type="test"
        )
        
        errors = validate_agent_config(config)
        
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("agent_id" in error for error in errors))
    
    def test_invalid_numeric_values(self):
        """Geçersiz sayısal değerler testi"""
        config = create_agent_config(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test",
            max_retries=-1,  # Negatif değer
            heartbeat_interval=-5.0,  # Negatif değer
            timeout=0  # Sıfır değer
        )
        
        errors = validate_agent_config(config)
        
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("max_retries" in error for error in errors))
        self.assertTrue(any("heartbeat_interval" in error for error in errors))
        self.assertTrue(any("timeout" in error for error in errors))
    
    def test_invalid_priority(self):
        """Geçersiz öncelik testi"""
        config = create_agent_config(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test",
            priority=15  # Geçerli aralık dışında
        )
        
        errors = validate_agent_config(config)
        
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("priority" in error for error in errors))
    
    def test_invalid_log_level(self):
        """Geçersiz log level testi"""
        config = create_agent_config(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test",
            log_level="INVALID_LEVEL"
        )
        
        errors = validate_agent_config(config)
        
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("log_level" in error for error in errors))


class TestAgentRegistry(unittest.TestCase):
    """Agent Registry testleri"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        self.temp_file = tempfile.mktemp(suffix='.json')
        self.registry = AgentRegistry(self.temp_file)
        
        self.config = create_agent_config(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test"
        )
        self.agent = MockAgent(self.config, auto_register=False)
    
    def tearDown(self):
        """Her test sonrası temizlik"""
        self.registry.shutdown()
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
    
    def test_agent_registration(self):
        """Agent kayıt testi"""
        success = self.registry.register_agent(self.agent)
        
        self.assertTrue(success)
        self.assertIn(self.agent.agent_id, self.registry.agents)
        
        # Aynı agent'ı tekrar kaydetme denemesi
        duplicate_success = self.registry.register_agent(self.agent)
        self.assertFalse(duplicate_success)
    
    def test_agent_unregistration(self):
        """Agent kayıt silme testi"""
        # Önce kaydet
        self.registry.register_agent(self.agent)
        
        # Sonra sil
        success = self.registry.unregister_agent(self.agent.agent_id)
        
        self.assertTrue(success)
        self.assertNotIn(self.agent.agent_id, self.registry.agents)
    
    def test_agent_status_update(self):
        """Agent durum güncelleme testi"""
        # Agent'ı kaydet
        self.registry.register_agent(self.agent)
        
        # Durumu güncelle
        success = self.registry.update_agent_status(self.agent.agent_id, AgentStatus.RUNNING)
        
        self.assertTrue(success)
        entry = self.registry.get_agent(self.agent.agent_id)
        self.assertEqual(entry.status, AgentStatus.RUNNING.value)
    
    def test_agent_heartbeat(self):
        """Agent heartbeat testi"""
        # Agent'ı kaydet
        self.registry.register_agent(self.agent)
        
        # İlk heartbeat zamanını al
        entry = self.registry.get_agent(self.agent.agent_id)
        first_heartbeat = entry.last_heartbeat
        
        # Biraz bekle
        time.sleep(0.1)
        
        # Heartbeat gönder
        success = self.registry.heartbeat(self.agent.agent_id)
        
        self.assertTrue(success)
        entry = self.registry.get_agent(self.agent.agent_id)
        self.assertGreater(entry.last_heartbeat, first_heartbeat)
    
    def test_find_agents_by_type(self):
        """Tip bazlı agent arama testi"""
        # Farklı tipte agent'lar oluştur
        config2 = create_agent_config(
            agent_id="test_agent_2",
            agent_name="Test Agent 2",
            agent_type="different_type"
        )
        agent2 = MockAgent(config2, auto_register=False)
        
        # Agent'ları kaydet
        self.registry.register_agent(self.agent)
        self.registry.register_agent(agent2)
        
        # Tip bazlı arama
        test_agents = self.registry.find_agents_by_type("test")
        different_agents = self.registry.find_agents_by_type("different_type")
        
        self.assertEqual(len(test_agents), 1)
        self.assertEqual(len(different_agents), 1)
        self.assertEqual(test_agents[0].agent_id, "test_agent")
        self.assertEqual(different_agents[0].agent_id, "test_agent_2")
    
    def test_find_agents_by_capability(self):
        """Yetenek bazlı agent arama testi"""
        # Yetenek ekle
        self.agent.add_capability("test_capability")
        
        # Agent'ı kaydet
        self.registry.register_agent(self.agent)
        
        # Yetenek bazlı arama
        capable_agents = self.registry.find_agents_by_capability("test_capability")
        
        self.assertEqual(len(capable_agents), 1)
        self.assertEqual(capable_agents[0].agent_id, "test_agent")
    
    def test_registry_stats(self):
        """Registry istatistikleri testi"""
        # Agent'ı kaydet
        self.registry.register_agent(self.agent)
        
        # İstatistikleri al
        stats = self.registry.get_registry_stats()
        
        self.assertEqual(stats['total_agents'], 1)
        self.assertIn('test', stats['agent_types'])
        self.assertEqual(stats['agent_types']['test'], 1)


class TestAgentRegistryIntegration(unittest.TestCase):
    """Agent ve Registry entegrasyon testleri"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        self.temp_file = tempfile.mktemp(suffix='.json')
        
        # Global registry'yi ayarla
        from agent_registry import set_global_registry
        self.registry = AgentRegistry(self.temp_file)
        set_global_registry(self.registry)
        
        self.config = create_agent_config(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test"
        )
    
    def tearDown(self):
        """Her test sonrası temizlik"""
        self.registry.shutdown()
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
    
    def test_auto_registration(self):
        """Otomatik kayıt testi"""
        # Auto-register=True ile agent oluştur
        agent = MockAgent(self.config, auto_register=True)
        
        # Registry'de olmalı
        self.assertIn(agent.agent_id, self.registry.agents)
        
        # Agent'ı durdur (auto-unregister)
        agent.stop()
        
        # Registry'den silinmeli
        self.assertNotIn(agent.agent_id, self.registry.agents)
    
    def test_status_sync(self):
        """Durum senkronizasyonu testi"""
        agent = MockAgent(self.config, auto_register=True)
        
        # Agent'ı başlat
        agent.start()
        
        # Registry'deki durumu kontrol et
        entry = self.registry.get_agent(agent.agent_id)
        self.assertEqual(entry.status, AgentStatus.RUNNING.value)
        
        # Agent'ı durdur
        agent.stop()
        
        # Registry'den silinmeli (auto-unregister)
        self.assertNotIn(agent.agent_id, self.registry.agents)


def run_lifecycle_config_tests():
    """Agent lifecycle ve config testlerini çalıştır"""
    print("🚀 Agent Lifecycle and Configuration Tests - Atlas Prompt 2.1.2")
    print("=" * 70)
    
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestConfigLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentRegistryIntegration))
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Testleri çalıştır
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 Tüm Agent Lifecycle ve Configuration testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_lifecycle_config_tests()
    sys.exit(0 if success else 1)
