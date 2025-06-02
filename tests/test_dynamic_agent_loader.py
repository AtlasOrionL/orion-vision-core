#!/usr/bin/env python3
"""
Dynamic Agent Loader Tests - Atlas Prompt 3.1.1
Orion Vision Core - Dinamik Agent Yükleme Sistemi Testleri

Bu script, dynamic_agent_loader.py modülünün unit testlerini içerir.
"""

import unittest
import sys
import os
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Test modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from dynamic_agent_loader import DynamicAgentLoader, AgentModuleInfo, LoaderStatus
from agent_core import Agent, AgentConfig, create_agent_config


class TestDynamicAgentLoader(unittest.TestCase):
    """Dynamic Agent Loader testleri"""

    def setUp(self):
        """Her test öncesi kurulum"""
        # Geçici dizinler oluştur
        self.temp_dir = tempfile.mkdtemp()
        self.modules_dir = os.path.join(self.temp_dir, "modules")
        self.config_dir = os.path.join(self.temp_dir, "config")

        os.makedirs(self.modules_dir)
        os.makedirs(self.config_dir)

        # Test agent modülü oluştur (güvenlik kontrolünü geçecek şekilde)
        self.test_agent_code = '''
import sys
import time
from pathlib import Path

# Agent core'u import et
sys.path.append(str(Path(__file__).parent.parent.parent / "src" / "jobone" / "vision_core"))
from agent_core import Agent, AgentConfig

class TestDynamicAgent(Agent):
    def initialize(self) -> bool:
        return True

    def run(self):
        while not self.stop_event.is_set():
            time.sleep(0.1)

    def cleanup(self):
        pass
'''

        # Test modül dosyasını oluştur
        self.test_module_path = os.path.join(self.modules_dir, "test_dynamic_agent.py")
        with open(self.test_module_path, 'w') as f:
            f.write(self.test_agent_code)

        # Loader'ı oluştur (auto_scan=False)
        self.loader = DynamicAgentLoader(
            agent_modules_dir=self.modules_dir,
            config_dir=self.config_dir,
            auto_scan=False
        )

    def tearDown(self):
        """Her test sonrası temizlik"""
        if hasattr(self, 'loader'):
            self.loader.shutdown()

        # Geçici dizini temizle
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_loader_initialization(self):
        """Loader başlatma testi"""
        self.assertEqual(self.loader.status, LoaderStatus.IDLE)
        self.assertEqual(str(self.loader.agent_modules_dir), self.modules_dir)
        self.assertEqual(str(self.loader.config_dir), self.config_dir)
        self.assertFalse(self.loader.auto_scan)
        self.assertEqual(len(self.loader.agent_modules), 0)
        self.assertEqual(len(self.loader.loaded_agents), 0)

    def test_module_scanning(self):
        """Modül tarama testi"""
        # Modülleri tara
        found_modules = self.loader.scan_modules()

        self.assertEqual(len(found_modules), 1)
        self.assertIn("test_dynamic_agent", found_modules)
        self.assertIn("test_dynamic_agent", self.loader.agent_modules)

        # Modül bilgilerini kontrol et
        module_info = self.loader.get_module_info("test_dynamic_agent")
        self.assertIsNotNone(module_info)
        self.assertEqual(module_info.module_name, "test_dynamic_agent")
        self.assertEqual(module_info.module_path, self.test_module_path)
        self.assertFalse(module_info.is_loaded)

    def test_module_loading(self):
        """Modül yükleme testi"""
        # Önce tara
        self.loader.scan_modules()

        # Modülü yükle
        success = self.loader.load_module("test_dynamic_agent")

        self.assertTrue(success)

        # Modül bilgilerini kontrol et
        module_info = self.loader.get_module_info("test_dynamic_agent")
        self.assertTrue(module_info.is_loaded)
        self.assertIsNotNone(module_info.agent_class)
        self.assertEqual(module_info.agent_class_name, "TestDynamicAgent")

    def test_module_loading_nonexistent(self):
        """Var olmayan modül yükleme testi"""
        success = self.loader.load_module("nonexistent_module")
        self.assertFalse(success)

    def test_agent_creation(self):
        """Agent oluşturma testi"""
        # Modülü tara ve yükle
        self.loader.scan_modules()
        self.loader.load_module("test_dynamic_agent")

        # Agent oluştur
        agent = self.loader.create_agent(
            module_name="test_dynamic_agent",
            agent_id="test_agent_001"
        )

        self.assertIsNotNone(agent)
        self.assertEqual(agent.agent_id, "test_agent_001")
        self.assertEqual(agent.agent_type, "dynamic_agent")  # Default type
        self.assertIn("test_agent_001", self.loader.loaded_agents)

    def test_agent_lifecycle(self):
        """Agent yaşam döngüsü testi"""
        # Agent oluştur
        self.loader.scan_modules()
        self.loader.load_module("test_dynamic_agent")
        agent = self.loader.create_agent(
            module_name="test_dynamic_agent",
            agent_id="test_lifecycle_agent"
        )

        self.assertIsNotNone(agent)

        # Agent'ı başlat
        start_success = self.loader.start_agent("test_lifecycle_agent")
        self.assertTrue(start_success)
        self.assertTrue(agent.is_running())

        # Biraz bekle
        time.sleep(0.5)

        # Agent'ı durdur
        stop_success = self.loader.stop_agent("test_lifecycle_agent")
        self.assertTrue(stop_success)
        self.assertFalse(agent.is_running())

    def test_module_unloading(self):
        """Modül kaldırma testi"""
        # Modülü yükle ve agent oluştur
        self.loader.scan_modules()
        self.loader.load_module("test_dynamic_agent")
        agent = self.loader.create_agent(
            module_name="test_dynamic_agent",
            agent_id="test_unload_agent"
        )
        self.loader.start_agent("test_unload_agent")

        # Modülü kaldır
        success = self.loader._unload_module("test_dynamic_agent")
        self.assertTrue(success)

        # Modül bilgilerini kontrol et
        module_info = self.loader.get_module_info("test_dynamic_agent")
        self.assertFalse(module_info.is_loaded)
        self.assertIsNone(module_info.agent_class)

        # Agent'ın durdurulduğunu kontrol et
        self.assertNotIn("test_unload_agent", self.loader.loaded_agents)

    def test_module_reloading(self):
        """Modül yeniden yükleme testi"""
        # Modülü yükle
        self.loader.scan_modules()
        self.loader.load_module("test_dynamic_agent")

        # İlk yükleme zamanını kaydet
        module_info = self.loader.get_module_info("test_dynamic_agent")
        first_load_time = module_info.load_time

        # Biraz bekle
        time.sleep(0.1)

        # Modülü yeniden yükle
        success = self.loader.reload_module("test_dynamic_agent")
        self.assertTrue(success)

        # Yeniden yükleme zamanını kontrol et
        module_info = self.loader.get_module_info("test_dynamic_agent")
        self.assertGreater(module_info.load_time, first_load_time)

    def test_file_hash_calculation(self):
        """Dosya hash hesaplama testi"""
        hash1 = self.loader._calculate_file_hash(Path(self.test_module_path))
        self.assertIsNotNone(hash1)
        self.assertGreater(len(hash1), 0)

        # Aynı dosya için aynı hash
        hash2 = self.loader._calculate_file_hash(Path(self.test_module_path))
        self.assertEqual(hash1, hash2)

    def test_security_check(self):
        """Güvenlik kontrolü testi"""
        module_info = AgentModuleInfo(
            module_name="test_module",
            module_path=self.test_module_path,
            agent_class_name="TestAgent"
        )

        # Normal modül güvenlik kontrolü
        is_safe = self.loader._security_check(module_info)
        self.assertTrue(is_safe)

        # Yasak import içeren modül oluştur
        unsafe_code = '''
import os
import subprocess
from agent_core import Agent

class UnsafeAgent(Agent):
    def run(self):
        os.system("echo test")
'''

        unsafe_module_path = os.path.join(self.modules_dir, "unsafe_agent.py")
        with open(unsafe_module_path, 'w') as f:
            f.write(unsafe_code)

        unsafe_module_info = AgentModuleInfo(
            module_name="unsafe_agent",
            module_path=unsafe_module_path,
            agent_class_name="UnsafeAgent"
        )

        # Güvenlik kontrolü başarısız olmalı
        is_safe = self.loader._security_check(unsafe_module_info)
        self.assertFalse(is_safe)

    def test_loader_statistics(self):
        """Loader istatistikleri testi"""
        # Başlangıç istatistikleri
        stats = self.loader.get_loader_stats()
        self.assertEqual(stats['total_modules'], 0)
        self.assertEqual(stats['loaded_modules'], 0)
        self.assertEqual(stats['total_agents'], 0)
        self.assertEqual(stats['running_agents'], 0)

        # Modül yükle ve agent oluştur
        self.loader.scan_modules()
        self.loader.load_module("test_dynamic_agent")
        agent = self.loader.create_agent(
            module_name="test_dynamic_agent",
            agent_id="stats_test_agent"
        )
        self.loader.start_agent("stats_test_agent")

        # Güncellenmiş istatistikler
        stats = self.loader.get_loader_stats()
        self.assertEqual(stats['total_modules'], 1)
        self.assertEqual(stats['loaded_modules'], 1)
        self.assertEqual(stats['total_agents'], 1)
        self.assertEqual(stats['running_agents'], 1)

    def test_auto_scan_functionality(self):
        """Otomatik tarama işlevselliği testi"""
        # Auto-scan ile loader oluştur
        auto_loader = DynamicAgentLoader(
            agent_modules_dir=self.modules_dir,
            config_dir=self.config_dir,
            auto_scan=True,
            scan_interval=1.0  # 1 saniye
        )

        try:
            # Auto-scan'in başladığını kontrol et
            self.assertTrue(auto_loader.auto_scan)
            self.assertIsNotNone(auto_loader.scan_thread)

            # Biraz bekle (auto-scan çalışsın)
            time.sleep(2)

            # Modüllerin bulunduğunu kontrol et
            modules = auto_loader.get_all_modules()
            self.assertGreater(len(modules), 0)

        finally:
            auto_loader.shutdown()

    def test_context_manager(self):
        """Context manager testi"""
        with DynamicAgentLoader(
            agent_modules_dir=self.modules_dir,
            config_dir=self.config_dir,
            auto_scan=False
        ) as loader:

            # Loader çalışıyor olmalı
            self.assertEqual(loader.status, LoaderStatus.IDLE)

            # Modül işlemleri
            loader.scan_modules()
            modules = loader.get_all_modules()
            self.assertGreater(len(modules), 0)

        # Context'ten çıktıktan sonra shutdown edilmeli
        # (Loader'ın internal state'ini kontrol edemeyiz ama exception olmamalı)

    def test_error_handling(self):
        """Hata yönetimi testi"""
        # Var olmayan dizinle loader oluştur
        invalid_loader = DynamicAgentLoader(
            agent_modules_dir="/nonexistent/path",
            config_dir="/nonexistent/config",
            auto_scan=False
        )

        try:
            # Tarama hata vermemeli (boş sonuç dönmeli)
            modules = invalid_loader.scan_modules()
            self.assertEqual(len(modules), 0)

            # Var olmayan modül yükleme
            success = invalid_loader.load_module("nonexistent")
            self.assertFalse(success)

        finally:
            invalid_loader.shutdown()


def run_dynamic_loader_tests():
    """Dynamic Agent Loader testlerini çalıştır"""
    print("🚀 Dynamic Agent Loader Tests - Atlas Prompt 3.1.1")
    print("=" * 60)

    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Test sınıfını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestDynamicAgentLoader))

    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)

    # Testleri çalıştır
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 Tüm Dynamic Agent Loader testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_dynamic_loader_tests()
    sys.exit(0 if success else 1)
