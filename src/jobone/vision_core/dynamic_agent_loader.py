#!/usr/bin/env python3
"""
Dynamic Agent Loader Module - Atlas Prompt 3.1.1
Orion Vision Core - Dinamik Agent Yükleme ve Yürütme Mekanizması

Bu modül, sistemin yeni veya güncellenmiş agent'ları çalışma zamanında
dinamik olarak yükleyip yönetebilme yeteneği sağlar. Python'ın importlib
mekanizması kullanılarak güvenli ve esnek agent yükleme işlemleri gerçekleştirilir.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import importlib
import importlib.util
import inspect
import os
import sys
import time
import threading
import hashlib
from typing import Dict, List, Optional, Any, Type, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from .agent_core import Agent, AgentConfig, AgentLogger, load_agent_config
from .agent_registry import get_global_registry


class LoaderStatus(Enum):
    """Dynamic loader durum seviyeleri"""
    IDLE = "idle"
    SCANNING = "scanning"
    LOADING = "loading"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class AgentModuleInfo:
    """Agent modül bilgi veri yapısı"""
    module_name: str
    module_path: str
    agent_class_name: str
    agent_class: Optional[Type[Agent]] = None
    config_path: Optional[str] = None
    last_modified: Optional[float] = None
    file_hash: Optional[str] = None
    load_time: Optional[float] = None
    is_loaded: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Post-initialization setup"""
        if self.metadata is None:
            self.metadata = {}


class DynamicAgentLoader:
    """
    Dynamic Agent Loader

    Bu sınıf, agent modüllerini çalışma zamanında dinamik olarak yükler,
    günceller ve yönetir. Hot-loading, güvenlik ve hata izolasyonu sağlar.
    """

    def __init__(self,
                 agent_modules_dir: str = "agents/dynamic",
                 config_dir: str = "config/agents",
                 auto_scan: bool = True,
                 scan_interval: float = 30.0):
        """
        Dynamic Agent Loader başlatıcı

        Args:
            agent_modules_dir: Agent modüllerinin bulunduğu dizin
            config_dir: Agent konfigürasyon dosyalarının dizini
            auto_scan: Otomatik dosya tarama
            scan_interval: Tarama aralığı (saniye)
        """
        self.agent_modules_dir = Path(agent_modules_dir)
        self.config_dir = Path(config_dir)
        self.auto_scan = auto_scan
        self.scan_interval = scan_interval

        # Status ve threading
        self.status = LoaderStatus.IDLE
        self.lock = threading.RLock()
        self.scan_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # Logging
        self.logger = AgentLogger("DynamicAgentLoader")

        # Agent modül bilgileri
        self.agent_modules: Dict[str, AgentModuleInfo] = {}
        self.loaded_agents: Dict[str, Agent] = {}

        # Registry
        self.registry = get_global_registry()

        # Security settings
        self.allowed_base_classes = [Agent]
        self.forbidden_imports = ['subprocess', 'eval', 'exec', '__import__']
        self.max_module_size = 1024 * 1024  # 1MB

        # Callbacks
        self.on_module_loaded: List[Callable] = []
        self.on_module_unloaded: List[Callable] = []
        self.on_agent_created: List[Callable] = []

        self.logger.info(f"Dynamic Agent Loader initialized")
        self.logger.info(f"Modules dir: {self.agent_modules_dir}")
        self.logger.info(f"Config dir: {self.config_dir}")

        # Dizinleri oluştur
        self._ensure_directories()

        # Auto-scan başlat
        if self.auto_scan:
            self.start_auto_scan()

    def _ensure_directories(self):
        """Gerekli dizinleri oluştur"""
        try:
            self.agent_modules_dir.mkdir(parents=True, exist_ok=True)
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Directories ensured")
        except Exception as e:
            self.logger.error(f"Directory creation error: {e}")

    def start_auto_scan(self):
        """Otomatik dosya taramayı başlat"""
        if self.scan_thread and self.scan_thread.is_alive():
            self.logger.warning("Auto-scan already running")
            return

        self.stop_event.clear()
        self.scan_thread = threading.Thread(
            target=self._scan_worker,
            name="DynamicAgentScanner",
            daemon=True
        )
        self.scan_thread.start()
        self.logger.info("Auto-scan started")

    def stop_auto_scan(self):
        """Otomatik dosya taramayı durdur"""
        self.stop_event.set()
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=5)
        self.logger.info("Auto-scan stopped")

    def _scan_worker(self):
        """Otomatik tarama worker thread"""
        while not self.stop_event.is_set():
            try:
                self.scan_modules()

                # Scan interval kadar bekle
                if self.stop_event.wait(self.scan_interval):
                    break

            except Exception as e:
                self.logger.error(f"Scan worker error: {e}")
                time.sleep(5)  # Hata durumunda kısa bekleme

    def scan_modules(self) -> List[str]:
        """
        Agent modüllerini tara ve değişiklikleri tespit et

        Returns:
            List[str]: Bulunan modül isimleri
        """
        try:
            with self.lock:
                self.status = LoaderStatus.SCANNING
                self.logger.debug("Scanning for agent modules...")

                found_modules = []

                # Python dosyalarını tara
                for py_file in self.agent_modules_dir.glob("*.py"):
                    if py_file.name.startswith("__"):
                        continue  # __init__.py, __pycache__ vb. atla

                    module_name = py_file.stem
                    found_modules.append(module_name)

                    # Modül bilgilerini güncelle
                    self._update_module_info(module_name, py_file)

                # Artık var olmayan modülleri temizle
                self._cleanup_removed_modules(found_modules)

                self.status = LoaderStatus.IDLE
                self.logger.debug(f"Scan completed: {len(found_modules)} modules found")

                return found_modules

        except Exception as e:
            self.status = LoaderStatus.ERROR
            self.logger.error(f"Module scanning error: {e}")
            return []

    def _update_module_info(self, module_name: str, module_path: Path):
        """Modül bilgilerini güncelle"""
        try:
            # Dosya bilgilerini al
            stat = module_path.stat()
            last_modified = stat.st_mtime
            file_size = stat.st_size

            # Güvenlik kontrolü - dosya boyutu
            if file_size > self.max_module_size:
                self.logger.warning(f"Module too large: {module_name} ({file_size} bytes)")
                return

            # Dosya hash'ini hesapla
            file_hash = self._calculate_file_hash(module_path)

            # Mevcut modül bilgilerini kontrol et
            if module_name in self.agent_modules:
                existing_info = self.agent_modules[module_name]

                # Değişiklik var mı?
                if (existing_info.last_modified == last_modified and
                    existing_info.file_hash == file_hash):
                    return  # Değişiklik yok

                self.logger.info(f"Module changed detected: {module_name}")

                # Eski modülü kaldır
                if existing_info.is_loaded:
                    self._unload_module(module_name)

            # Yeni modül bilgisi oluştur
            module_info = AgentModuleInfo(
                module_name=module_name,
                module_path=str(module_path),
                agent_class_name="",  # Henüz bilinmiyor
                last_modified=last_modified,
                file_hash=file_hash
            )

            self.agent_modules[module_name] = module_info
            self.logger.debug(f"Module info updated: {module_name}")

        except Exception as e:
            self.logger.error(f"Module info update error for {module_name}: {e}")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Dosya hash'ini hesapla"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            self.logger.error(f"File hash calculation error: {e}")
            return ""

    def _cleanup_removed_modules(self, found_modules: List[str]):
        """Artık var olmayan modülleri temizle"""
        try:
            removed_modules = set(self.agent_modules.keys()) - set(found_modules)

            for module_name in removed_modules:
                self.logger.info(f"Module removed: {module_name}")

                # Yüklü ise kaldır
                if self.agent_modules[module_name].is_loaded:
                    self._unload_module(module_name)

                # Modül bilgisini sil
                del self.agent_modules[module_name]

        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    def load_module(self, module_name: str) -> bool:
        """
        Belirtilen modülü yükle

        Args:
            module_name: Yüklenecek modül adı

        Returns:
            bool: Yükleme başarılı ise True
        """
        try:
            with self.lock:
                if module_name not in self.agent_modules:
                    self.logger.error(f"Module not found: {module_name}")
                    return False

                module_info = self.agent_modules[module_name]

                if module_info.is_loaded:
                    self.logger.warning(f"Module already loaded: {module_name}")
                    return True

                self.status = LoaderStatus.LOADING
                self.logger.info(f"Loading module: {module_name}")

                # Güvenlik kontrolü
                if not self._security_check(module_info):
                    self.logger.error(f"Security check failed for module: {module_name}")
                    return False

                # Modülü import et
                agent_class = self._import_module(module_info)
                if not agent_class:
                    return False

                # Modül bilgilerini güncelle
                module_info.agent_class = agent_class
                module_info.agent_class_name = agent_class.__name__
                module_info.is_loaded = True
                module_info.load_time = time.time()
                module_info.error_message = None

                # Callbacks
                for callback in self.on_module_loaded:
                    try:
                        callback(module_info)
                    except Exception as e:
                        self.logger.error(f"Module loaded callback error: {e}")

                self.status = LoaderStatus.IDLE
                self.logger.info(f"Module loaded successfully: {module_name}")

                return True

        except Exception as e:
            self.status = LoaderStatus.ERROR
            self.logger.error(f"Module loading error for {module_name}: {e}")

            # Hata bilgisini kaydet
            if module_name in self.agent_modules:
                self.agent_modules[module_name].error_message = str(e)

            return False

    def _security_check(self, module_info: AgentModuleInfo) -> bool:
        """Modül güvenlik kontrolü"""
        try:
            # Dosya boyutu kontrolü
            file_size = os.path.getsize(module_info.module_path)
            if file_size > self.max_module_size:
                self.logger.warning(f"Module too large: {file_size} bytes")
                return False

            # Dosya içeriği kontrolü (basit)
            with open(module_info.module_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Yasak import'ları kontrol et
            for forbidden in self.forbidden_imports:
                if f"import {forbidden}" in content or f"from {forbidden}" in content:
                    self.logger.warning(f"Forbidden import detected: {forbidden}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Security check error: {e}")
            return False

    def _import_module(self, module_info: AgentModuleInfo) -> Optional[Type[Agent]]:
        """Modülü import et ve Agent sınıfını bul"""
        try:
            # Modül spec'ini oluştur
            spec = importlib.util.spec_from_file_location(
                module_info.module_name,
                module_info.module_path
            )

            if not spec or not spec.loader:
                self.logger.error(f"Failed to create module spec: {module_info.module_name}")
                return None

            # Modülü yükle
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Agent sınıfını bul
            agent_class = self._find_agent_class(module)
            if not agent_class:
                self.logger.error(f"No valid Agent class found in module: {module_info.module_name}")
                return None

            return agent_class

        except Exception as e:
            self.logger.error(f"Module import error: {e}")
            return None

    def _find_agent_class(self, module) -> Optional[Type[Agent]]:
        """Modülde Agent sınıfını bul"""
        try:
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Agent'tan türemiş sınıfları bul
                if (issubclass(obj, Agent) and
                    obj != Agent and
                    obj.__module__ == module.__name__):

                    self.logger.debug(f"Found Agent class: {name}")
                    return obj

            return None

        except Exception as e:
            self.logger.error(f"Agent class search error: {e}")
            return None

    def _unload_module(self, module_name: str) -> bool:
        """
        Modülü kaldır

        Args:
            module_name: Kaldırılacak modül adı

        Returns:
            bool: Kaldırma başarılı ise True
        """
        try:
            with self.lock:
                if module_name not in self.agent_modules:
                    self.logger.warning(f"Module not found for unloading: {module_name}")
                    return False

                module_info = self.agent_modules[module_name]

                if not module_info.is_loaded:
                    self.logger.warning(f"Module not loaded: {module_name}")
                    return True

                self.logger.info(f"Unloading module: {module_name}")

                # Bu modülden oluşturulan agent'ları durdur
                agents_to_stop = []
                for agent_id, agent in self.loaded_agents.items():
                    if agent.__class__.__name__ == module_info.agent_class_name:
                        agents_to_stop.append(agent_id)

                for agent_id in agents_to_stop:
                    self._stop_and_remove_agent(agent_id)

                # Modül bilgilerini güncelle
                module_info.agent_class = None
                module_info.agent_class_name = ""
                module_info.is_loaded = False
                module_info.error_message = None

                # Callbacks
                for callback in self.on_module_unloaded:
                    try:
                        callback(module_info)
                    except Exception as e:
                        self.logger.error(f"Module unloaded callback error: {e}")

                self.logger.info(f"Module unloaded successfully: {module_name}")
                return True

        except Exception as e:
            self.logger.error(f"Module unloading error for {module_name}: {e}")
            return False

    def create_agent(self, module_name: str, agent_id: str, config_path: str = None) -> Optional[Agent]:
        """
        Belirtilen modülden agent oluştur

        Args:
            module_name: Agent modülü adı
            agent_id: Oluşturulacak agent ID
            config_path: Konfigürasyon dosyası yolu

        Returns:
            Agent: Oluşturulan agent veya None
        """
        try:
            with self.lock:
                # Modül yüklü mü kontrol et
                if module_name not in self.agent_modules:
                    self.logger.error(f"Module not found: {module_name}")
                    return None

                module_info = self.agent_modules[module_name]

                if not module_info.is_loaded:
                    # Modülü yükle
                    if not self.load_module(module_name):
                        return None

                # Agent sınıfını al
                agent_class = module_info.agent_class
                if not agent_class:
                    self.logger.error(f"Agent class not available: {module_name}")
                    return None

                # Konfigürasyon yükle
                config = self._load_agent_config(agent_id, config_path)
                if not config:
                    return None

                # Agent oluştur
                agent = agent_class(config, auto_register=True)

                # Agent'ı kaydet
                self.loaded_agents[agent_id] = agent

                # Callbacks
                for callback in self.on_agent_created:
                    try:
                        callback(agent)
                    except Exception as e:
                        self.logger.error(f"Agent created callback error: {e}")

                self.logger.info(f"Agent created successfully: {agent_id} from {module_name}")
                return agent

        except Exception as e:
            self.logger.error(f"Agent creation error: {e}")
            return None

    def _load_agent_config(self, agent_id: str, config_path: str = None) -> Optional[AgentConfig]:
        """Agent konfigürasyonunu yükle"""
        try:
            if config_path:
                # Belirtilen dosyadan yükle
                config = load_agent_config(config_path)
            else:
                # Varsayılan konumdan yükle
                default_config_path = self.config_dir / f"{agent_id}.json"
                if default_config_path.exists():
                    config = load_agent_config(str(default_config_path))
                else:
                    # Basit konfigürasyon oluştur
                    from agent_core import create_agent_config
                    config = create_agent_config(
                        agent_id=agent_id,
                        agent_name=f"Dynamic Agent {agent_id}",
                        agent_type="dynamic_agent"
                    )

            return config

        except Exception as e:
            self.logger.error(f"Config loading error: {e}")
            return None

    def start_agent(self, agent_id: str) -> bool:
        """
        Agent'ı başlat

        Args:
            agent_id: Başlatılacak agent ID

        Returns:
            bool: Başlatma başarılı ise True
        """
        try:
            if agent_id not in self.loaded_agents:
                self.logger.error(f"Agent not found: {agent_id}")
                return False

            agent = self.loaded_agents[agent_id]
            success = agent.start()

            if success:
                self.logger.info(f"Agent started: {agent_id}")
            else:
                self.logger.error(f"Agent start failed: {agent_id}")

            return success

        except Exception as e:
            self.logger.error(f"Agent start error: {e}")
            return False

    def stop_agent(self, agent_id: str) -> bool:
        """
        Agent'ı durdur

        Args:
            agent_id: Durdurulacak agent ID

        Returns:
            bool: Durdurma başarılı ise True
        """
        try:
            if agent_id not in self.loaded_agents:
                self.logger.error(f"Agent not found: {agent_id}")
                return False

            agent = self.loaded_agents[agent_id]
            success = agent.stop()

            if success:
                self.logger.info(f"Agent stopped: {agent_id}")
            else:
                self.logger.error(f"Agent stop failed: {agent_id}")

            return success

        except Exception as e:
            self.logger.error(f"Agent stop error: {e}")
            return False

    def _stop_and_remove_agent(self, agent_id: str):
        """Agent'ı durdur ve kaldır"""
        try:
            if agent_id in self.loaded_agents:
                agent = self.loaded_agents[agent_id]
                agent.stop()
                del self.loaded_agents[agent_id]
                self.logger.info(f"Agent stopped and removed: {agent_id}")
        except Exception as e:
            self.logger.error(f"Agent stop and remove error: {e}")

    def reload_module(self, module_name: str) -> bool:
        """
        Modülü yeniden yükle

        Args:
            module_name: Yeniden yüklenecek modül adı

        Returns:
            bool: Yeniden yükleme başarılı ise True
        """
        try:
            self.logger.info(f"Reloading module: {module_name}")

            # Önce kaldır
            if not self._unload_module(module_name):
                return False

            # Sonra yükle
            return self.load_module(module_name)

        except Exception as e:
            self.logger.error(f"Module reload error: {e}")
            return False

    def get_module_info(self, module_name: str) -> Optional[AgentModuleInfo]:
        """Modül bilgilerini getir"""
        return self.agent_modules.get(module_name)

    def get_all_modules(self) -> Dict[str, AgentModuleInfo]:
        """Tüm modül bilgilerini getir"""
        return self.agent_modules.copy()

    def get_loaded_modules(self) -> List[str]:
        """Yüklü modüllerin listesini getir"""
        return [name for name, info in self.agent_modules.items() if info.is_loaded]

    def get_loaded_agents(self) -> Dict[str, Agent]:
        """Yüklü agent'ların listesini getir"""
        return self.loaded_agents.copy()

    def get_loader_stats(self) -> Dict[str, Any]:
        """Loader istatistiklerini getir"""
        total_modules = len(self.agent_modules)
        loaded_modules = len(self.get_loaded_modules())
        total_agents = len(self.loaded_agents)
        running_agents = sum(1 for agent in self.loaded_agents.values() if agent.is_running())

        return {
            'status': self.status.value,
            'total_modules': total_modules,
            'loaded_modules': loaded_modules,
            'total_agents': total_agents,
            'running_agents': running_agents,
            'auto_scan': self.auto_scan,
            'scan_interval': self.scan_interval,
            'modules_dir': str(self.agent_modules_dir),
            'config_dir': str(self.config_dir)
        }

    def shutdown(self):
        """Loader'ı kapat"""
        try:
            self.logger.info("Shutting down Dynamic Agent Loader...")

            # Auto-scan'i durdur
            self.stop_auto_scan()

            # Tüm agent'ları durdur
            for agent_id in list(self.loaded_agents.keys()):
                self._stop_and_remove_agent(agent_id)

            # Tüm modülleri kaldır
            for module_name in list(self.agent_modules.keys()):
                if self.agent_modules[module_name].is_loaded:
                    self._unload_module(module_name)

            self.status = LoaderStatus.IDLE
            self.logger.info("Dynamic Agent Loader shutdown completed")

        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

    def __enter__(self):
        """Context manager desteği"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği"""
        self.shutdown()


# Global loader instance
_global_loader: Optional[DynamicAgentLoader] = None


def get_global_loader() -> DynamicAgentLoader:
    """Global loader instance'ını getir"""
    global _global_loader
    if _global_loader is None:
        _global_loader = DynamicAgentLoader()
    return _global_loader


def set_global_loader(loader: DynamicAgentLoader):
    """Global loader instance'ını ayarla"""
    global _global_loader
    _global_loader = loader
