#!/usr/bin/env python3
"""
⚠️ THIS IS AN ARCHIVED FILE - THESE FILES ARE DEPRECATED AND NO LONGER VALID

This file has been archived during the project organization audit on 2025-05-30.
This is a duplicate of the active version in src/jobone/vision_core/agent_core.py

For the current, maintained version, use: src/jobone/vision_core/agent_core.py

Original Header:
Agent Core Module - Atlas Prompt 2.1.1
Orion Vision Core - Temel Agent Sınıfı ve Modül Yapısı

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import abc
import logging
import json
import os
import time
import threading
import signal
import sys
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class AgentStatus(Enum):
    """Agent durum seviyeleri"""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    PAUSED = "paused"


class AgentPriority(Enum):
    """Agent öncelik seviyeleri"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class AgentConfig:
    """Agent konfigürasyon veri yapısı"""
    agent_id: str
    agent_name: str
    agent_type: str
    priority: str = AgentPriority.NORMAL.value
    auto_start: bool = False
    max_retries: int = 3
    retry_delay: float = 1.0
    heartbeat_interval: float = 30.0
    timeout: float = 300.0
    capabilities: List[str] = None
    dependencies: List[str] = None
    config_file: Optional[str] = None
    log_level: str = "INFO"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Post-initialization setup"""
        if self.capabilities is None:
            self.capabilities = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


class AgentLogger:
    """Agent için özelleştirilmiş logger sınıfı"""

    def __init__(self, agent_id: str, log_level: str = "INFO"):
        """
        Agent logger başlatıcı

        Args:
            agent_id: Agent'ın benzersiz kimliği
            log_level: Log seviyesi
        """
        self.agent_id = agent_id
        self.logger = self._setup_logger(log_level)

    def _setup_logger(self, log_level: str) -> logging.Logger:
        """Logger kurulumu"""
        logger = logging.getLogger(f"Agent.{self.agent_id}")
        logger.setLevel(getattr(logging, log_level.upper()))

        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # File handler (optional)
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_dir / f"{self.agent_id}.log")
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        return logger

    def debug(self, message: str, **kwargs):
        """Debug log"""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Info log"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Warning log"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Error log"""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Critical log"""
        self.logger.critical(message, extra=kwargs)


class Agent(abc.ABC):
    """
    Orion Vision Core - Temel Agent Soyut Sınıfı

    Tüm Orion agent'larının inherit edeceği temel sınıf.
    Ortak işlevsellik, yaşam döngüsü yönetimi ve standart arayüzler sağlar.
    """

    def __init__(self, config: AgentConfig, auto_register: bool = True):
        """
        Agent temel başlatıcı

        Args:
            config: Agent konfigürasyon objesi
            auto_register: Otomatik registry'ye kayıt
        """
        self.config = config
        self.agent_id = config.agent_id
        self.agent_name = config.agent_name
        self.agent_type = config.agent_type

        # Durum yönetimi
        self.status = AgentStatus.IDLE
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.error_count = 0
        self.last_error: Optional[str] = None

        # Threading
        self.main_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.heartbeat_thread: Optional[threading.Thread] = None

        # Logging
        self.logger = AgentLogger(self.agent_id, config.log_level)

        # Registry
        self.auto_register = auto_register
        self.registry = None

        # Statistics
        self.stats = {
            'start_count': 0,
            'stop_count': 0,
            'error_count': 0,
            'uptime': 0.0,
            'last_heartbeat': None,
            'tasks_completed': 0,
            'tasks_failed': 0
        }

        # Callbacks
        self.on_start_callbacks: List[Callable] = []
        self.on_stop_callbacks: List[Callable] = []
        self.on_error_callbacks: List[Callable] = []

        self.logger.info(f"Agent initialized: {self.agent_id} ({self.agent_type})")

        # Auto-register to global registry
        if self.auto_register:
            self._register_to_global_registry()

    def _register_to_global_registry(self):
        """Global registry'ye kayıt ol"""
        try:
            # Lazy import to avoid circular dependency
            from agent_registry import get_global_registry

            self.registry = get_global_registry()
            success = self.registry.register_agent(self)

            if success:
                self.logger.info(f"Agent registered to global registry: {self.agent_id}")
            else:
                self.logger.warning(f"Failed to register agent to global registry: {self.agent_id}")

        except Exception as e:
            self.logger.error(f"Registry registration error: {e}")

    def _unregister_from_registry(self):
        """Registry'den kayıt sil"""
        try:
            if self.registry:
                success = self.registry.unregister_agent(self.agent_id)
                if success:
                    self.logger.info(f"Agent unregistered from registry: {self.agent_id}")
                else:
                    self.logger.warning(f"Failed to unregister agent from registry: {self.agent_id}")

        except Exception as e:
            self.logger.error(f"Registry unregistration error: {e}")

    def _update_registry_status(self, status: AgentStatus):
        """Registry'deki durumu güncelle"""
        try:
            if self.registry:
                self.registry.update_agent_status(self.agent_id, status)

        except Exception as e:
            self.logger.error(f"Registry status update error: {e}")

    def _send_registry_heartbeat(self):
        """Registry'ye heartbeat gönder"""
        try:
            if self.registry:
                self.registry.heartbeat(self.agent_id)

        except Exception as e:
            self.logger.error(f"Registry heartbeat error: {e}")

    @abc.abstractmethod
    def initialize(self) -> bool:
        """
        Agent'a özel başlatma işlemleri

        Returns:
            bool: Başlatma başarılı ise True
        """
        pass

    @abc.abstractmethod
    def run(self):
        """
        Agent'ın ana çalışma döngüsü

        Bu metot agent'ın temel işlevselliğini implement eder.
        """
        pass

    @abc.abstractmethod
    def cleanup(self):
        """
        Agent'a özel temizlik işlemleri

        Agent durdurulurken çağrılır.
        """
        pass

    def start(self) -> bool:
        """
        Agent'ı başlat

        Returns:
            bool: Başlatma başarılı ise True
        """
        if self.status in [AgentStatus.RUNNING, AgentStatus.STARTING]:
            self.logger.warning(f"Agent already running or starting: {self.status}")
            return False

        try:
            self.logger.info(f"Starting agent: {self.agent_id}")
            self.status = AgentStatus.STARTING
            self.start_time = time.time()
            self.stop_event.clear()

            # Agent'a özel başlatma
            if not self.initialize():
                self.logger.error("Agent initialization failed")
                self.status = AgentStatus.ERROR
                return False

            # Ana thread'i başlat
            self.main_thread = threading.Thread(
                target=self._run_wrapper,
                name=f"Agent-{self.agent_id}",
                daemon=False
            )
            self.main_thread.start()

            # Heartbeat thread'ini başlat
            self._start_heartbeat()

            # Callbacks
            for callback in self.on_start_callbacks:
                try:
                    callback(self)
                except Exception as e:
                    self.logger.error(f"Start callback error: {e}")

            self.status = AgentStatus.RUNNING
            self.stats['start_count'] += 1

            # Registry'ye durum güncelle
            self._update_registry_status(self.status)

            self.logger.info(f"Agent started successfully: {self.agent_id}")

            return True

        except Exception as e:
            self.logger.error(f"Agent start error: {e}")
            self.status = AgentStatus.ERROR
            self.error_count += 1
            self.last_error = str(e)
            return False

    def stop(self, timeout: Optional[float] = None) -> bool:
        """
        Agent'ı durdur

        Args:
            timeout: Durdurma timeout'u (saniye)

        Returns:
            bool: Durdurma başarılı ise True
        """
        if self.status in [AgentStatus.STOPPED, AgentStatus.STOPPING]:
            self.logger.warning(f"Agent already stopped or stopping: {self.status}")
            return True

        try:
            self.logger.info(f"Stopping agent: {self.agent_id}")
            self.status = AgentStatus.STOPPING

            # Stop signal gönder
            self.stop_event.set()

            # Ana thread'in bitmesini bekle
            if self.main_thread and self.main_thread.is_alive():
                self.main_thread.join(timeout=timeout or self.config.timeout)

                if self.main_thread.is_alive():
                    self.logger.warning("Agent thread did not stop gracefully")

            # Heartbeat'i durdur
            self._stop_heartbeat()

            # Agent'a özel temizlik
            self.cleanup()

            # Callbacks
            for callback in self.on_stop_callbacks:
                try:
                    callback(self)
                except Exception as e:
                    self.logger.error(f"Stop callback error: {e}")

            self.status = AgentStatus.STOPPED
            self.stop_time = time.time()
            self.stats['stop_count'] += 1

            if self.start_time:
                self.stats['uptime'] += self.stop_time - self.start_time

            # Registry'ye durum güncelle ve kayıt sil
            self._update_registry_status(self.status)
            if self.auto_register:
                self._unregister_from_registry()

            self.logger.info(f"Agent stopped successfully: {self.agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Agent stop error: {e}")
            self.status = AgentStatus.ERROR
            self.error_count += 1
            self.last_error = str(e)
            return False

    def pause(self) -> bool:
        """Agent'ı duraklat (placeholder)"""
        self.logger.info(f"Pausing agent: {self.agent_id}")
        self.status = AgentStatus.PAUSED
        return True

    def resume(self) -> bool:
        """Agent'ı devam ettir (placeholder)"""
        self.logger.info(f"Resuming agent: {self.agent_id}")
        self.status = AgentStatus.RUNNING
        return True

    def restart(self) -> bool:
        """Agent'ı yeniden başlat"""
        self.logger.info(f"Restarting agent: {self.agent_id}")
        if self.stop():
            time.sleep(1)  # Kısa bekleme
            return self.start()
        return False

    def _run_wrapper(self):
        """Ana run metodunu wrap eden güvenli wrapper"""
        try:
            self.run()
        except Exception as e:
            self.logger.error(f"Agent run error: {e}")
            self.status = AgentStatus.ERROR
            self.error_count += 1
            self.last_error = str(e)
            self.stats['error_count'] += 1

            # Error callbacks
            for callback in self.on_error_callbacks:
                try:
                    callback(self, e)
                except Exception as callback_error:
                    self.logger.error(f"Error callback failed: {callback_error}")

    def _start_heartbeat(self):
        """Heartbeat thread'ini başlat"""
        if self.config.heartbeat_interval > 0:
            self.heartbeat_thread = threading.Thread(
                target=self._heartbeat_worker,
                name=f"Heartbeat-{self.agent_id}",
                daemon=True
            )
            self.heartbeat_thread.start()

    def _stop_heartbeat(self):
        """Heartbeat thread'ini durdur"""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)

    def _heartbeat_worker(self):
        """Heartbeat worker thread"""
        while not self.stop_event.is_set():
            try:
                self.stats['last_heartbeat'] = time.time()
                self.logger.debug(f"Heartbeat: {self.agent_id}")

                # Registry'ye heartbeat gönder
                self._send_registry_heartbeat()

                # Heartbeat interval kadar bekle
                if self.stop_event.wait(self.config.heartbeat_interval):
                    break  # Stop event set edildi

            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                break

    def is_running(self) -> bool:
        """Agent çalışıyor mu?"""
        return self.status == AgentStatus.RUNNING

    def is_healthy(self) -> bool:
        """Agent sağlıklı mı?"""
        if not self.is_running():
            return False

        # Heartbeat kontrolü
        if self.stats['last_heartbeat']:
            time_since_heartbeat = time.time() - self.stats['last_heartbeat']
            if time_since_heartbeat > (self.config.heartbeat_interval * 2):
                return False

        # Error count kontrolü
        if self.error_count > self.config.max_retries:
            return False

        return True

    def get_status(self) -> Dict[str, Any]:
        """Agent durumu bilgilerini döndür"""
        uptime = 0.0
        if self.start_time and self.status == AgentStatus.RUNNING:
            uptime = time.time() - self.start_time

        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'status': self.status.value,
            'priority': self.config.priority,
            'uptime': uptime,
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'is_healthy': self.is_healthy(),
            'capabilities': self.config.capabilities,
            'dependencies': self.config.dependencies,
            'stats': self.stats.copy()
        }

    def get_config(self) -> Dict[str, Any]:
        """Agent konfigürasyonunu döndür"""
        return asdict(self.config)

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Agent konfigürasyonunu güncelle"""
        try:
            # Kritik alanları koruma
            protected_fields = ['agent_id', 'agent_name', 'agent_type']
            for field in protected_fields:
                if field in new_config:
                    del new_config[field]

            # Konfigürasyonu güncelle
            for key, value in new_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    self.logger.info(f"Config updated: {key} = {value}")

            return True

        except Exception as e:
            self.logger.error(f"Config update error: {e}")
            return False

    def add_capability(self, capability: str):
        """Agent'a yetenek ekle"""
        if capability not in self.config.capabilities:
            self.config.capabilities.append(capability)
            self.logger.info(f"Capability added: {capability}")

    def remove_capability(self, capability: str):
        """Agent'tan yetenek çıkar"""
        if capability in self.config.capabilities:
            self.config.capabilities.remove(capability)
            self.logger.info(f"Capability removed: {capability}")

    def has_capability(self, capability: str) -> bool:
        """Agent'ın belirtilen yeteneği var mı?"""
        return capability in self.config.capabilities

    def register_callback(self, event_type: str, callback: Callable):
        """Event callback'i kaydet"""
        if event_type == 'start':
            self.on_start_callbacks.append(callback)
        elif event_type == 'stop':
            self.on_stop_callbacks.append(callback)
        elif event_type == 'error':
            self.on_error_callbacks.append(callback)
        else:
            self.logger.warning(f"Unknown event type: {event_type}")

    def signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        self.logger.info(f"Signal {signum} received, stopping agent...")
        self.stop()

    def __enter__(self):
        """Context manager desteği"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği"""
        self.stop()

    def __str__(self) -> str:
        """String representation"""
        return f"Agent({self.agent_id}, {self.status.value})"

    def __repr__(self) -> str:
        """Detailed representation"""
        return f"Agent(id='{self.agent_id}', type='{self.agent_type}', status='{self.status.value}')"


class AgentManager:
    """
    Agent Manager - Çoklu agent yönetimi için yardımcı sınıf

    Birden fazla agent'ı koordine etmek, başlatmak, durdurmak ve
    izlemek için kullanılır.
    """

    def __init__(self):
        """Agent Manager başlatıcı"""
        self.agents: Dict[str, Agent] = {}
        self.logger = AgentLogger("AgentManager")
        self.shutdown_event = threading.Event()

        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def register_agent(self, agent: Agent) -> bool:
        """Agent'ı manager'a kaydet"""
        try:
            if agent.agent_id in self.agents:
                self.logger.warning(f"Agent already registered: {agent.agent_id}")
                return False

            self.agents[agent.agent_id] = agent
            self.logger.info(f"Agent registered: {agent.agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Agent registration error: {e}")
            return False

    def unregister_agent(self, agent_id: str) -> bool:
        """Agent'ı manager'dan çıkar"""
        try:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent not found: {agent_id}")
                return False

            agent = self.agents[agent_id]
            if agent.is_running():
                agent.stop()

            del self.agents[agent_id]
            self.logger.info(f"Agent unregistered: {agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Agent unregistration error: {e}")
            return False

    def start_agent(self, agent_id: str) -> bool:
        """Belirtilen agent'ı başlat"""
        if agent_id not in self.agents:
            self.logger.error(f"Agent not found: {agent_id}")
            return False

        return self.agents[agent_id].start()

    def stop_agent(self, agent_id: str) -> bool:
        """Belirtilen agent'ı durdur"""
        if agent_id not in self.agents:
            self.logger.error(f"Agent not found: {agent_id}")
            return False

        return self.agents[agent_id].stop()

    def start_all(self) -> Dict[str, bool]:
        """Tüm agent'ları başlat"""
        results = {}
        for agent_id, agent in self.agents.items():
            results[agent_id] = agent.start()
        return results

    def stop_all(self) -> Dict[str, bool]:
        """Tüm agent'ları durdur"""
        results = {}
        for agent_id, agent in self.agents.items():
            results[agent_id] = agent.stop()
        return results

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Agent durumunu getir"""
        if agent_id not in self.agents:
            return None
        return self.agents[agent_id].get_status()

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Tüm agent'ların durumunu getir"""
        status = {}
        for agent_id, agent in self.agents.items():
            status[agent_id] = agent.get_status()
        return status

    def get_healthy_agents(self) -> List[str]:
        """Sağlıklı agent'ların listesini döndür"""
        healthy = []
        for agent_id, agent in self.agents.items():
            if agent.is_healthy():
                healthy.append(agent_id)
        return healthy

    def get_running_agents(self) -> List[str]:
        """Çalışan agent'ların listesini döndür"""
        running = []
        for agent_id, agent in self.agents.items():
            if agent.is_running():
                running.append(agent_id)
        return running

    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        self.logger.info(f"Signal {signum} received, shutting down all agents...")
        self.shutdown_event.set()
        self.stop_all()
        sys.exit(0)


# Utility functions
def load_agent_config(config_path: str) -> Optional[AgentConfig]:
    """
    JSON dosyasından agent konfigürasyonu yükle

    Args:
        config_path: Konfigürasyon dosyası yolu

    Returns:
        AgentConfig: Yüklenen konfigürasyon veya None
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"Config file not found: {config_path}")
            return None

        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # Validate required fields
        required_fields = ['agent_id', 'agent_name', 'agent_type']
        for field in required_fields:
            if field not in config_data:
                print(f"Missing required field in config: {field}")
                return None

        return AgentConfig(**config_data)

    except json.JSONDecodeError as e:
        print(f"JSON decode error in config file: {e}")
        return None
    except Exception as e:
        print(f"Config loading error: {e}")
        return None


def load_agent_configs_from_directory(config_dir: str) -> Dict[str, AgentConfig]:
    """
    Dizindeki tüm JSON konfigürasyon dosyalarını yükle

    Args:
        config_dir: Konfigürasyon dizini yolu

    Returns:
        Dict[str, AgentConfig]: Agent ID -> Config mapping
    """
    configs = {}
    try:
        config_path = Path(config_dir)
        if not config_path.exists():
            print(f"Config directory not found: {config_dir}")
            return configs

        # JSON dosyalarını bul
        json_files = list(config_path.glob("*.json"))

        for json_file in json_files:
            config = load_agent_config(str(json_file))
            if config:
                configs[config.agent_id] = config
                print(f"Loaded config: {config.agent_id} from {json_file.name}")

        print(f"Loaded {len(configs)} agent configurations")
        return configs

    except Exception as e:
        print(f"Config directory loading error: {e}")
        return configs


def validate_agent_config(config: AgentConfig) -> List[str]:
    """
    Agent konfigürasyonunu doğrula

    Args:
        config: Doğrulanacak konfigürasyon

    Returns:
        List[str]: Doğrulama hataları (boş liste = geçerli)
    """
    errors = []

    try:
        # Required fields
        if not config.agent_id or not config.agent_id.strip():
            errors.append("agent_id is required and cannot be empty")

        if not config.agent_name or not config.agent_name.strip():
            errors.append("agent_name is required and cannot be empty")

        if not config.agent_type or not config.agent_type.strip():
            errors.append("agent_type is required and cannot be empty")

        # Numeric validations
        if config.max_retries < 0:
            errors.append("max_retries must be non-negative")

        if config.retry_delay < 0:
            errors.append("retry_delay must be non-negative")

        if config.heartbeat_interval <= 0:
            errors.append("heartbeat_interval must be positive")

        if config.timeout <= 0:
            errors.append("timeout must be positive")

        # Priority validation
        try:
            priority_val = int(config.priority) if isinstance(config.priority, str) else config.priority
            if priority_val < 1 or priority_val > 10:
                errors.append("priority must be between 1 and 10")
        except (ValueError, TypeError):
            errors.append("priority must be a valid number")

        # Log level validation
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config.log_level.upper() not in valid_log_levels:
            errors.append(f"log_level must be one of: {valid_log_levels}")

        # Lists validation
        if not isinstance(config.capabilities, list):
            errors.append("capabilities must be a list")

        if not isinstance(config.dependencies, list):
            errors.append("dependencies must be a list")

        if not isinstance(config.metadata, dict):
            errors.append("metadata must be a dictionary")

    except Exception as e:
        errors.append(f"Validation error: {e}")

    return errors


def create_agent_config(agent_id: str,
                       agent_name: str,
                       agent_type: str,
                       **kwargs) -> AgentConfig:
    """
    Programatik olarak agent konfigürasyonu oluştur

    Args:
        agent_id: Agent kimliği
        agent_name: Agent adı
        agent_type: Agent tipi
        **kwargs: Ek konfigürasyon parametreleri

    Returns:
        AgentConfig: Oluşturulan konfigürasyon
    """
    return AgentConfig(
        agent_id=agent_id,
        agent_name=agent_name,
        agent_type=agent_type,
        **kwargs
    )
