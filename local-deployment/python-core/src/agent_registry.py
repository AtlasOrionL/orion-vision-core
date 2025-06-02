#!/usr/bin/env python3
"""
Agent Registry Module - Atlas Prompt 2.1.2
Orion Vision Core - Agent Kayıt ve Keşif Sistemi

Bu modül, agent'ların dinamik olarak kaydedilmesi, keşfedilmesi ve 
yönetilmesi için merkezi bir registry sistemi sağlar.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import json
import time
import threading
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from agent_core import Agent, AgentConfig, AgentStatus, AgentLogger


class RegistryStatus(Enum):
    """Registry durum seviyeleri"""
    OFFLINE = "offline"
    STARTING = "starting"
    ONLINE = "online"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class AgentRegistryEntry:
    """Agent registry giriş veri yapısı"""
    agent_id: str
    agent_name: str
    agent_type: str
    status: str
    priority: int
    capabilities: List[str]
    dependencies: List[str]
    endpoint: Optional[str] = None
    last_heartbeat: Optional[float] = None
    registration_time: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        if self.registration_time is None:
            self.registration_time = time.time()
        if self.metadata is None:
            self.metadata = {}


class AgentRegistry:
    """
    Agent Registry - Merkezi Agent Kayıt Sistemi
    
    Bu sınıf, sistem içindeki tüm agent'ların kaydedilmesi, keşfedilmesi
    ve durumlarının izlenmesi için merkezi bir registry sağlar.
    """
    
    def __init__(self, registry_file: Optional[str] = None):
        """
        Agent Registry başlatıcı
        
        Args:
            registry_file: Registry verilerinin saklanacağı dosya yolu
        """
        self.registry_file = registry_file or "data/agent_registry.json"
        self.agents: Dict[str, AgentRegistryEntry] = {}
        self.status = RegistryStatus.OFFLINE
        
        # Threading
        self.lock = threading.RLock()
        self.cleanup_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Logging
        self.logger = AgentLogger("AgentRegistry")
        
        # Settings
        self.heartbeat_timeout = 120.0  # 2 dakika
        self.cleanup_interval = 60.0    # 1 dakika
        self.auto_save = True
        
        # Callbacks
        self.on_agent_registered: List[Callable] = []
        self.on_agent_unregistered: List[Callable] = []
        self.on_agent_status_changed: List[Callable] = []
        
        # Registry'yi başlat
        self._initialize()
    
    def _initialize(self):
        """Registry'yi başlat"""
        try:
            self.status = RegistryStatus.STARTING
            
            # Registry dosyasını yükle
            self._load_registry()
            
            # Cleanup thread'ini başlat
            self._start_cleanup_thread()
            
            self.status = RegistryStatus.ONLINE
            self.logger.info("Agent Registry initialized successfully")
            
        except Exception as e:
            self.status = RegistryStatus.ERROR
            self.logger.error(f"Agent Registry initialization failed: {e}")
    
    def register_agent(self, agent: Agent) -> bool:
        """
        Agent'ı registry'ye kaydet
        
        Args:
            agent: Kaydedilecek agent
            
        Returns:
            bool: Kayıt başarılı ise True
        """
        try:
            with self.lock:
                agent_id = agent.agent_id
                
                # Zaten kayıtlı mı kontrol et
                if agent_id in self.agents:
                    self.logger.warning(f"Agent already registered: {agent_id}")
                    return False
                
                # Registry entry oluştur
                entry = AgentRegistryEntry(
                    agent_id=agent.agent_id,
                    agent_name=agent.agent_name,
                    agent_type=agent.agent_type,
                    status=agent.status.value,
                    priority=int(agent.config.priority) if isinstance(agent.config.priority, (int, float)) else 5,
                    capabilities=agent.config.capabilities.copy(),
                    dependencies=agent.config.dependencies.copy(),
                    endpoint=f"orion.agent.{agent_id}",
                    last_heartbeat=time.time(),
                    metadata=agent.config.metadata.copy() if agent.config.metadata else {}
                )
                
                # Registry'ye ekle
                self.agents[agent_id] = entry
                
                # Auto-save
                if self.auto_save:
                    self._save_registry()
                
                # Callbacks
                for callback in self.on_agent_registered:
                    try:
                        callback(entry)
                    except Exception as e:
                        self.logger.error(f"Agent registered callback error: {e}")
                
                self.logger.info(f"Agent registered: {agent_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Agent registration error: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Agent'ı registry'den çıkar
        
        Args:
            agent_id: Çıkarılacak agent ID
            
        Returns:
            bool: Çıkarma başarılı ise True
        """
        try:
            with self.lock:
                if agent_id not in self.agents:
                    self.logger.warning(f"Agent not found in registry: {agent_id}")
                    return False
                
                # Entry'yi al ve sil
                entry = self.agents.pop(agent_id)
                
                # Auto-save
                if self.auto_save:
                    self._save_registry()
                
                # Callbacks
                for callback in self.on_agent_unregistered:
                    try:
                        callback(entry)
                    except Exception as e:
                        self.logger.error(f"Agent unregistered callback error: {e}")
                
                self.logger.info(f"Agent unregistered: {agent_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Agent unregistration error: {e}")
            return False
    
    def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """
        Agent durumunu güncelle
        
        Args:
            agent_id: Agent ID
            status: Yeni durum
            
        Returns:
            bool: Güncelleme başarılı ise True
        """
        try:
            with self.lock:
                if agent_id not in self.agents:
                    self.logger.warning(f"Agent not found for status update: {agent_id}")
                    return False
                
                entry = self.agents[agent_id]
                old_status = entry.status
                entry.status = status.value
                entry.last_heartbeat = time.time()
                
                # Auto-save
                if self.auto_save:
                    self._save_registry()
                
                # Callbacks (sadece durum değiştiyse)
                if old_status != entry.status:
                    for callback in self.on_agent_status_changed:
                        try:
                            callback(entry, old_status, entry.status)
                        except Exception as e:
                            self.logger.error(f"Agent status changed callback error: {e}")
                
                self.logger.debug(f"Agent status updated: {agent_id} -> {status.value}")
                return True
                
        except Exception as e:
            self.logger.error(f"Agent status update error: {e}")
            return False
    
    def heartbeat(self, agent_id: str) -> bool:
        """
        Agent heartbeat güncelle
        
        Args:
            agent_id: Agent ID
            
        Returns:
            bool: Güncelleme başarılı ise True
        """
        try:
            with self.lock:
                if agent_id not in self.agents:
                    return False
                
                self.agents[agent_id].last_heartbeat = time.time()
                return True
                
        except Exception as e:
            self.logger.error(f"Heartbeat update error: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentRegistryEntry]:
        """
        Agent bilgilerini getir
        
        Args:
            agent_id: Agent ID
            
        Returns:
            AgentRegistryEntry: Agent bilgileri veya None
        """
        with self.lock:
            return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, AgentRegistryEntry]:
        """Tüm agent'ları getir"""
        with self.lock:
            return self.agents.copy()
    
    def find_agents_by_type(self, agent_type: str) -> List[AgentRegistryEntry]:
        """
        Belirtilen tipte agent'ları bul
        
        Args:
            agent_type: Agent tipi
            
        Returns:
            List[AgentRegistryEntry]: Bulunan agent'lar
        """
        with self.lock:
            return [entry for entry in self.agents.values() if entry.agent_type == agent_type]
    
    def find_agents_by_capability(self, capability: str) -> List[AgentRegistryEntry]:
        """
        Belirtilen yeteneğe sahip agent'ları bul
        
        Args:
            capability: Aranan yetenek
            
        Returns:
            List[AgentRegistryEntry]: Bulunan agent'lar
        """
        with self.lock:
            return [entry for entry in self.agents.values() if capability in entry.capabilities]
    
    def get_healthy_agents(self) -> List[AgentRegistryEntry]:
        """Sağlıklı agent'ları getir (son heartbeat'i yakın olanlar)"""
        current_time = time.time()
        with self.lock:
            healthy = []
            for entry in self.agents.values():
                if entry.last_heartbeat and (current_time - entry.last_heartbeat) < self.heartbeat_timeout:
                    if entry.status in [AgentStatus.RUNNING.value, AgentStatus.IDLE.value]:
                        healthy.append(entry)
            return healthy
    
    def get_agents_by_priority(self, min_priority: int = 0) -> List[AgentRegistryEntry]:
        """
        Belirtilen öncelik seviyesi ve üstündeki agent'ları getir
        
        Args:
            min_priority: Minimum öncelik seviyesi
            
        Returns:
            List[AgentRegistryEntry]: Öncelik sırasına göre sıralanmış agent'lar
        """
        with self.lock:
            filtered = [entry for entry in self.agents.values() if entry.priority >= min_priority]
            return sorted(filtered, key=lambda x: x.priority, reverse=True)
    
    def _start_cleanup_thread(self):
        """Cleanup thread'ini başlat"""
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_worker,
            name="RegistryCleanup",
            daemon=True
        )
        self.cleanup_thread.start()
    
    def _cleanup_worker(self):
        """Cleanup worker thread - eski/inactive agent'ları temizle"""
        while not self.stop_event.is_set():
            try:
                current_time = time.time()
                to_remove = []
                
                with self.lock:
                    for agent_id, entry in self.agents.items():
                        # Heartbeat timeout kontrolü
                        if entry.last_heartbeat:
                            time_since_heartbeat = current_time - entry.last_heartbeat
                            if time_since_heartbeat > self.heartbeat_timeout:
                                if entry.status not in [AgentStatus.STOPPED.value, AgentStatus.ERROR.value]:
                                    self.logger.warning(f"Agent heartbeat timeout: {agent_id}")
                                    entry.status = AgentStatus.ERROR.value
                                    to_remove.append(agent_id)
                
                # Timeout olan agent'ları kaldır
                for agent_id in to_remove:
                    self.unregister_agent(agent_id)
                
                # Cleanup interval kadar bekle
                if self.stop_event.wait(self.cleanup_interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"Cleanup worker error: {e}")
                time.sleep(5)  # Hata durumunda kısa bekleme
    
    def _load_registry(self):
        """Registry dosyasından verileri yükle"""
        try:
            registry_path = Path(self.registry_file)
            if registry_path.exists():
                with open(registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Agent entry'lerini yükle
                for agent_id, entry_data in data.get('agents', {}).items():
                    entry = AgentRegistryEntry(**entry_data)
                    self.agents[agent_id] = entry
                
                self.logger.info(f"Registry loaded: {len(self.agents)} agents")
            else:
                self.logger.info("No existing registry file found, starting fresh")
                
        except Exception as e:
            self.logger.error(f"Registry loading error: {e}")
    
    def _save_registry(self):
        """Registry verilerini dosyaya kaydet"""
        try:
            registry_path = Path(self.registry_file)
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Registry verilerini hazırla
            data = {
                'version': '1.0',
                'last_updated': time.time(),
                'agents': {
                    agent_id: asdict(entry) 
                    for agent_id, entry in self.agents.items()
                }
            }
            
            # Dosyaya yaz
            with open(registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Registry saved: {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Registry saving error: {e}")
    
    def shutdown(self):
        """Registry'yi kapat"""
        try:
            self.logger.info("Shutting down Agent Registry...")
            self.status = RegistryStatus.STOPPING
            
            # Cleanup thread'ini durdur
            self.stop_event.set()
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5)
            
            # Son kayıt
            if self.auto_save:
                self._save_registry()
            
            self.status = RegistryStatus.OFFLINE
            self.logger.info("Agent Registry shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Registry shutdown error: {e}")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Registry istatistiklerini getir"""
        with self.lock:
            stats = {
                'total_agents': len(self.agents),
                'healthy_agents': len(self.get_healthy_agents()),
                'status': self.status.value,
                'heartbeat_timeout': self.heartbeat_timeout,
                'cleanup_interval': self.cleanup_interval,
                'agent_types': {},
                'agent_statuses': {},
                'capabilities': set()
            }
            
            # Agent tiplerini say
            for entry in self.agents.values():
                agent_type = entry.agent_type
                stats['agent_types'][agent_type] = stats['agent_types'].get(agent_type, 0) + 1
                
                # Agent durumlarını say
                status = entry.status
                stats['agent_statuses'][status] = stats['agent_statuses'].get(status, 0) + 1
                
                # Yetenekleri topla
                stats['capabilities'].update(entry.capabilities)
            
            # Set'i list'e çevir
            stats['capabilities'] = list(stats['capabilities'])
            
            return stats
    
    def __enter__(self):
        """Context manager desteği"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği"""
        self.shutdown()


# Global registry instance
_global_registry: Optional[AgentRegistry] = None


def get_global_registry() -> AgentRegistry:
    """Global registry instance'ını getir"""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry


def set_global_registry(registry: AgentRegistry):
    """Global registry instance'ını ayarla"""
    global _global_registry
    _global_registry = registry
