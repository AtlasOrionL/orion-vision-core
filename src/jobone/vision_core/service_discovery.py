#!/usr/bin/env python3
"""
Service Discovery System - Sprint 4.1
Orion Vision Core - Distributed Agent Coordination

Bu modül, agent'ların birbirlerini otomatik olarak keşfetmesi ve
sisteme kaydolması için distributed service discovery sistemi sağlar.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import json
import time
import uuid
import threading
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
import socket
import hashlib
from collections import defaultdict
import logging

# Mevcut modüllerini import et
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from .agent_core import AgentStatus
except ImportError:
    # Fallback for testing
    class AgentStatus:
        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"


class ServiceStatus(Enum):
    """Service durumları"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class DiscoveryProtocol(Enum):
    """Discovery protokolleri"""
    MULTICAST = "multicast"
    CONSUL = "consul"
    ETCD = "etcd"
    CUSTOM = "custom"
    REDIS = "redis"


@dataclass
class ServiceInfo:
    """
    Service Information Structure

    Agent'ların service discovery için gerekli bilgilerini içerir.
    """
    service_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    service_name: str = ""
    service_type: str = "agent"
    host: str = "localhost"
    port: int = 0
    protocol: str = "http"
    status: ServiceStatus = ServiceStatus.STARTING
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    health_check_url: str = ""
    last_heartbeat: float = field(default_factory=time.time)
    registration_time: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Service info'yu dictionary'ye çevir"""
        return {
            'service_id': self.service_id,
            'agent_id': self.agent_id,
            'service_name': self.service_name,
            'service_type': self.service_type,
            'host': self.host,
            'port': self.port,
            'protocol': self.protocol,
            'status': self.status.value,
            'capabilities': self.capabilities,
            'metadata': self.metadata,
            'health_check_url': self.health_check_url,
            'last_heartbeat': self.last_heartbeat,
            'registration_time': self.registration_time,
            'tags': self.tags,
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInfo':
        """Dictionary'den service info oluştur"""
        return cls(
            service_id=data.get('service_id', str(uuid.uuid4())),
            agent_id=data.get('agent_id', ''),
            service_name=data.get('service_name', ''),
            service_type=data.get('service_type', 'agent'),
            host=data.get('host', 'localhost'),
            port=data.get('port', 0),
            protocol=data.get('protocol', 'http'),
            status=ServiceStatus(data.get('status', ServiceStatus.STARTING.value)),
            capabilities=data.get('capabilities', []),
            metadata=data.get('metadata', {}),
            health_check_url=data.get('health_check_url', ''),
            last_heartbeat=data.get('last_heartbeat', time.time()),
            registration_time=data.get('registration_time', time.time()),
            tags=data.get('tags', []),
            version=data.get('version', '1.0.0')
        )

    def get_endpoint_url(self) -> str:
        """Service endpoint URL'ini getir"""
        return f"{self.protocol}://{self.host}:{self.port}"

    def is_healthy(self, timeout: float = 30.0) -> bool:
        """Service'in sağlıklı olup olmadığını kontrol et"""
        if self.status != ServiceStatus.HEALTHY:
            return False

        # Heartbeat timeout kontrolü
        current_time = time.time()
        return (current_time - self.last_heartbeat) < timeout

    def update_heartbeat(self):
        """Heartbeat'i güncelle"""
        self.last_heartbeat = time.time()


class ServiceRegistry:
    """
    Service Registry - Agent Discovery ve Registration

    Agent'ların sisteme kaydolması ve birbirlerini keşfetmesi
    için merkezi registry sistemi.
    """

    def __init__(self, registry_id: str = None, cleanup_interval: float = 60.0):
        """
        Service Registry başlatıcı

        Args:
            registry_id: Registry'nin benzersiz ID'si
            cleanup_interval: Ölü service'leri temizleme aralığı (saniye)
        """
        self.registry_id = registry_id or f"registry_{int(time.time())}"
        self.cleanup_interval = cleanup_interval

        # Service storage
        self.services: Dict[str, ServiceInfo] = {}  # service_id -> ServiceInfo
        self.services_by_agent: Dict[str, Set[str]] = defaultdict(set)  # agent_id -> service_ids
        self.services_by_type: Dict[str, Set[str]] = defaultdict(set)  # service_type -> service_ids
        self.services_by_capability: Dict[str, Set[str]] = defaultdict(set)  # capability -> service_ids

        # Registry state
        self.running = False
        self.cleanup_task = None

        # Thread safety
        self._lock = threading.RLock()

        # Statistics
        self.stats = {
            'total_registrations': 0,
            'active_services': 0,
            'failed_health_checks': 0,
            'cleanup_runs': 0
        }

        print(f"🔍 Service Registry {self.registry_id} initialized")

    async def start(self):
        """Registry'yi başlat"""
        if self.running:
            return

        self.running = True

        # Cleanup task'ını başlat
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

        print(f"🚀 Service Registry {self.registry_id} started")

    async def stop(self):
        """Registry'yi durdur"""
        if not self.running:
            return

        self.running = False

        # Cleanup task'ını durdur
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        print(f"🛑 Service Registry {self.registry_id} stopped")

    def register_service(self, service_info: ServiceInfo) -> bool:
        """
        Service'i registry'ye kaydet

        Args:
            service_info: Service bilgileri

        Returns:
            bool: Kayıt başarısı
        """
        with self._lock:
            try:
                # Service ID kontrolü
                if not service_info.service_id:
                    service_info.service_id = str(uuid.uuid4())

                # Mevcut service kontrolü
                if service_info.service_id in self.services:
                    # Güncelleme
                    old_service = self.services[service_info.service_id]
                    self._remove_from_indexes(old_service)

                # Service'i kaydet
                service_info.registration_time = time.time()
                service_info.update_heartbeat()
                self.services[service_info.service_id] = service_info

                # Index'leri güncelle
                self._add_to_indexes(service_info)

                # İstatistikleri güncelle
                self.stats['total_registrations'] += 1
                self.stats['active_services'] = len(self.services)

                print(f"✅ Service registered: {service_info.service_name} ({service_info.service_id})")
                return True

            except Exception as e:
                print(f"❌ Service registration error: {e}")
                return False

    def unregister_service(self, service_id: str) -> bool:
        """
        Service'i registry'den çıkar

        Args:
            service_id: Service ID

        Returns:
            bool: Çıkarma başarısı
        """
        with self._lock:
            try:
                if service_id not in self.services:
                    return False

                service_info = self.services[service_id]

                # Index'lerden çıkar
                self._remove_from_indexes(service_info)

                # Service'i sil
                del self.services[service_id]

                # İstatistikleri güncelle
                self.stats['active_services'] = len(self.services)

                print(f"🗑️ Service unregistered: {service_info.service_name} ({service_id})")
                return True

            except Exception as e:
                print(f"❌ Service unregistration error: {e}")
                return False

    def discover_services(self,
                         service_type: str = None,
                         capability: str = None,
                         tags: List[str] = None,
                         healthy_only: bool = True) -> List[ServiceInfo]:
        """
        Service'leri keşfet

        Args:
            service_type: Service tipi filtresi
            capability: Capability filtresi
            tags: Tag filtreleri
            healthy_only: Sadece sağlıklı service'ler

        Returns:
            List[ServiceInfo]: Bulunan service'ler
        """
        with self._lock:
            try:
                candidate_ids = set(self.services.keys())

                # Service type filtresi
                if service_type:
                    candidate_ids &= self.services_by_type.get(service_type, set())

                # Capability filtresi
                if capability:
                    candidate_ids &= self.services_by_capability.get(capability, set())

                # Service'leri getir
                services = []
                for service_id in candidate_ids:
                    service = self.services.get(service_id)
                    if not service:
                        continue

                    # Health kontrolü
                    if healthy_only and not service.is_healthy():
                        continue

                    # Tag filtresi
                    if tags:
                        if not all(tag in service.tags for tag in tags):
                            continue

                    services.append(service)

                # Service'leri heartbeat'e göre sırala (en yeni önce)
                services.sort(key=lambda s: s.last_heartbeat, reverse=True)

                return services

            except Exception as e:
                print(f"❌ Service discovery error: {e}")
                return []

    def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """
        Belirli bir service'i getir

        Args:
            service_id: Service ID

        Returns:
            Optional[ServiceInfo]: Service bilgisi
        """
        with self._lock:
            return self.services.get(service_id)

    def update_service_status(self, service_id: str, status: ServiceStatus) -> bool:
        """
        Service durumunu güncelle

        Args:
            service_id: Service ID
            status: Yeni durum

        Returns:
            bool: Güncelleme başarısı
        """
        with self._lock:
            service = self.services.get(service_id)
            if not service:
                return False

            service.status = status
            service.update_heartbeat()

            return True

    def heartbeat(self, service_id: str) -> bool:
        """
        Service heartbeat'ini güncelle

        Args:
            service_id: Service ID

        Returns:
            bool: Güncelleme başarısı
        """
        with self._lock:
            service = self.services.get(service_id)
            if not service:
                return False

            service.update_heartbeat()
            return True

    def _add_to_indexes(self, service_info: ServiceInfo):
        """Service'i index'lere ekle"""
        # Agent index
        self.services_by_agent[service_info.agent_id].add(service_info.service_id)

        # Type index
        self.services_by_type[service_info.service_type].add(service_info.service_id)

        # Capability index
        for capability in service_info.capabilities:
            self.services_by_capability[capability].add(service_info.service_id)

    def _remove_from_indexes(self, service_info: ServiceInfo):
        """Service'i index'lerden çıkar"""
        # Agent index
        self.services_by_agent[service_info.agent_id].discard(service_info.service_id)
        if not self.services_by_agent[service_info.agent_id]:
            del self.services_by_agent[service_info.agent_id]

        # Type index
        self.services_by_type[service_info.service_type].discard(service_info.service_id)
        if not self.services_by_type[service_info.service_type]:
            del self.services_by_type[service_info.service_type]

        # Capability index
        for capability in service_info.capabilities:
            self.services_by_capability[capability].discard(service_info.service_id)
            if not self.services_by_capability[capability]:
                del self.services_by_capability[capability]

    async def _cleanup_loop(self):
        """Ölü service'leri temizleme döngüsü"""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)

                if not self.running:
                    break

                await self._cleanup_dead_services()
                self.stats['cleanup_runs'] += 1

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Cleanup loop error: {e}")

    async def _cleanup_dead_services(self):
        """Ölü service'leri temizle"""
        with self._lock:
            dead_services = []

            for service_id, service in self.services.items():
                if not service.is_healthy():
                    dead_services.append(service_id)

            for service_id in dead_services:
                self.unregister_service(service_id)
                self.stats['failed_health_checks'] += 1

            if dead_services:
                print(f"🧹 Cleaned up {len(dead_services)} dead services")

    def get_registry_stats(self) -> Dict[str, Any]:
        """Registry istatistiklerini getir"""
        with self._lock:
            return {
                'registry_id': self.registry_id,
                'active_services': len(self.services),
                'service_types': len(self.services_by_type),
                'agents': len(self.services_by_agent),
                'capabilities': len(self.services_by_capability),
                'stats': self.stats.copy(),
                'running': self.running
            }

    def get_all_services(self) -> List[ServiceInfo]:
        """Tüm service'leri getir"""
        with self._lock:
            return list(self.services.values())


class HealthMonitor:
    """
    Health Monitor - Agent Health Checking

    Agent'ların sağlık durumunu kontrol eden ve
    otomatik failover sağlayan sistem.
    """

    def __init__(self, registry: ServiceRegistry, check_interval: float = 30.0):
        """
        Health Monitor başlatıcı

        Args:
            registry: Service registry referansı
            check_interval: Health check aralığı (saniye)
        """
        self.registry = registry
        self.check_interval = check_interval

        # Health check state
        self.running = False
        self.health_check_task = None

        # Health check methods
        self.health_checkers = {
            'http': self._http_health_check,
            'tcp': self._tcp_health_check,
            'ping': self._ping_health_check
        }

        # Statistics
        self.health_stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'services_marked_unhealthy': 0
        }

        print(f"🏥 Health Monitor initialized with {check_interval}s interval")

    async def start(self):
        """Health monitor'ı başlat"""
        if self.running:
            return

        self.running = True

        # Health check task'ını başlat
        self.health_check_task = asyncio.create_task(self._health_check_loop())

        print("🚀 Health Monitor started")

    async def stop(self):
        """Health monitor'ı durdur"""
        if not self.running:
            return

        self.running = False

        # Health check task'ını durdur
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        print("🛑 Health Monitor stopped")

    async def check_service_health(self, service_info: ServiceInfo) -> bool:
        """
        Belirli bir service'in sağlığını kontrol et

        Args:
            service_info: Service bilgileri

        Returns:
            bool: Sağlık durumu
        """
        try:
            self.health_stats['total_checks'] += 1

            # Health check URL varsa HTTP check
            if service_info.health_check_url:
                healthy = await self._http_health_check(service_info.health_check_url)
            else:
                # Protocol'e göre health check
                if service_info.protocol == 'http':
                    url = f"http://{service_info.host}:{service_info.port}/health"
                    healthy = await self._http_health_check(url)
                elif service_info.protocol == 'tcp':
                    healthy = await self._tcp_health_check(service_info.host, service_info.port)
                else:
                    # Ping check
                    healthy = await self._ping_health_check(service_info.host)

            # Durumu güncelle
            if healthy:
                self.health_stats['successful_checks'] += 1
                self.registry.update_service_status(service_info.service_id, ServiceStatus.HEALTHY)
                self.registry.heartbeat(service_info.service_id)
            else:
                self.health_stats['failed_checks'] += 1
                self.registry.update_service_status(service_info.service_id, ServiceStatus.UNHEALTHY)
                self.health_stats['services_marked_unhealthy'] += 1

            return healthy

        except Exception as e:
            print(f"❌ Health check error for {service_info.service_name}: {e}")
            self.health_stats['failed_checks'] += 1
            self.registry.update_service_status(service_info.service_id, ServiceStatus.UNHEALTHY)
            return False

    async def _health_check_loop(self):
        """Health check döngüsü"""
        while self.running:
            try:
                await asyncio.sleep(self.check_interval)

                if not self.running:
                    break

                # Tüm service'leri kontrol et
                services = self.registry.get_all_services()

                # Concurrent health checks
                tasks = []
                for service in services:
                    if service.status in [ServiceStatus.HEALTHY, ServiceStatus.UNHEALTHY]:
                        task = asyncio.create_task(self.check_service_health(service))
                        tasks.append(task)

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Health check loop error: {e}")

    async def _http_health_check(self, url: str, timeout: float = 5.0) -> bool:
        """HTTP health check"""
        try:
            import aiohttp

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(url) as response:
                    return response.status == 200

        except ImportError:
            # Fallback to basic HTTP check without aiohttp
            return await self._basic_http_check(url, timeout)
        except Exception:
            return False

    async def _basic_http_check(self, url: str, timeout: float = 5.0) -> bool:
        """Basic HTTP check without external dependencies"""
        try:
            import urllib.request
            import urllib.error

            # Simple HTTP request
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request, timeout=timeout)
            return response.getcode() == 200

        except Exception:
            return False

    async def _tcp_health_check(self, host: str, port: int, timeout: float = 5.0) -> bool:
        """TCP health check"""
        try:
            # TCP connection test
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=timeout)

            writer.close()
            await writer.wait_closed()

            return True

        except Exception:
            return False

    async def _ping_health_check(self, host: str, timeout: float = 5.0) -> bool:
        """Ping health check"""
        try:
            import subprocess

            # Platform-specific ping command
            import platform
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(int(timeout * 1000)), host]
            else:
                cmd = ['ping', '-c', '1', '-W', str(int(timeout)), host]

            # Execute ping
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )

            await asyncio.wait_for(process.wait(), timeout=timeout)
            return process.returncode == 0

        except Exception:
            return False

    def get_health_stats(self) -> Dict[str, Any]:
        """Health monitor istatistiklerini getir"""
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'stats': self.health_stats.copy(),
            'success_rate': (
                self.health_stats['successful_checks'] / max(1, self.health_stats['total_checks'])
            ) * 100
        }


class LoadBalancingStrategy(Enum):
    """Load balancing stratejileri"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"
    HEALTH_BASED = "health_based"
    RESPONSE_TIME = "response_time"


class LoadBalancer:
    """
    Load Balancer - Intelligent Request Distribution

    Service'ler arasında akıllı istek dağıtımı yapan
    load balancing sistemi.
    """

    def __init__(self, registry: ServiceRegistry, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        """
        Load Balancer başlatıcı

        Args:
            registry: Service registry referansı
            strategy: Load balancing stratejisi
        """
        self.registry = registry
        self.strategy = strategy

        # Load balancing state
        self.round_robin_counters: Dict[str, int] = defaultdict(int)
        self.connection_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.service_weights: Dict[str, float] = defaultdict(lambda: 1.0)

        # Statistics
        self.lb_stats = {
            'total_requests': 0,
            'successful_distributions': 0,
            'failed_distributions': 0,
            'strategy_switches': 0
        }

        # Thread safety
        self._lock = threading.RLock()

        print(f"⚖️ Load Balancer initialized with {strategy.value} strategy")

    def select_service(self,
                      service_type: str = None,
                      capability: str = None,
                      tags: List[str] = None,
                      exclude_services: List[str] = None) -> Optional[ServiceInfo]:
        """
        Load balancing stratejisine göre service seç

        Args:
            service_type: Service tipi filtresi
            capability: Capability filtresi
            tags: Tag filtreleri
            exclude_services: Hariç tutulacak service'ler

        Returns:
            Optional[ServiceInfo]: Seçilen service
        """
        with self._lock:
            try:
                self.lb_stats['total_requests'] += 1

                # Uygun service'leri bul
                services = self.registry.discover_services(
                    service_type=service_type,
                    capability=capability,
                    tags=tags,
                    healthy_only=True
                )

                # Exclude edilen service'leri çıkar
                if exclude_services:
                    services = [s for s in services if s.service_id not in exclude_services]

                if not services:
                    self.lb_stats['failed_distributions'] += 1
                    return None

                # Strateji'ye göre service seç
                selected_service = self._apply_strategy(services, service_type or "default")

                if selected_service:
                    self.lb_stats['successful_distributions'] += 1
                    self._update_connection_count(selected_service.service_id, 1)
                else:
                    self.lb_stats['failed_distributions'] += 1

                return selected_service

            except Exception as e:
                print(f"❌ Load balancer selection error: {e}")
                self.lb_stats['failed_distributions'] += 1
                return None

    def release_service(self, service_id: str):
        """
        Service kullanımını bitir (connection count'u azalt)

        Args:
            service_id: Service ID
        """
        with self._lock:
            self._update_connection_count(service_id, -1)

    def record_response_time(self, service_id: str, response_time: float):
        """
        Service response time'ını kaydet

        Args:
            service_id: Service ID
            response_time: Response time (saniye)
        """
        with self._lock:
            self.response_times[service_id].append(response_time)

            # Son 100 response time'ı tut
            if len(self.response_times[service_id]) > 100:
                self.response_times[service_id] = self.response_times[service_id][-100:]

    def set_service_weight(self, service_id: str, weight: float):
        """
        Service weight'ini ayarla

        Args:
            service_id: Service ID
            weight: Weight değeri (0.1 - 10.0)
        """
        with self._lock:
            self.service_weights[service_id] = max(0.1, min(10.0, weight))

    def change_strategy(self, new_strategy: LoadBalancingStrategy):
        """
        Load balancing stratejisini değiştir

        Args:
            new_strategy: Yeni strateji
        """
        with self._lock:
            if self.strategy != new_strategy:
                self.strategy = new_strategy
                self.lb_stats['strategy_switches'] += 1
                print(f"⚖️ Load balancing strategy changed to {new_strategy.value}")

    def _apply_strategy(self, services: List[ServiceInfo], service_key: str) -> Optional[ServiceInfo]:
        """Load balancing stratejisini uygula"""
        if not services:
            return None

        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(services, service_key)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(services)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(services, service_key)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random_select(services)
        elif self.strategy == LoadBalancingStrategy.HEALTH_BASED:
            return self._health_based_select(services)
        elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
            return self._response_time_select(services)
        else:
            return services[0]  # Fallback

    def _round_robin_select(self, services: List[ServiceInfo], service_key: str) -> ServiceInfo:
        """Round robin selection"""
        index = self.round_robin_counters[service_key] % len(services)
        self.round_robin_counters[service_key] += 1
        return services[index]

    def _least_connections_select(self, services: List[ServiceInfo]) -> ServiceInfo:
        """Least connections selection"""
        min_connections = float('inf')
        selected_service = services[0]

        for service in services:
            connections = self.connection_counts[service.service_id]
            if connections < min_connections:
                min_connections = connections
                selected_service = service

        return selected_service

    def _weighted_round_robin_select(self, services: List[ServiceInfo], service_key: str) -> ServiceInfo:
        """Weighted round robin selection"""
        # Weight'lere göre service'leri genişlet
        weighted_services = []
        for service in services:
            weight = int(self.service_weights[service.service_id])
            weighted_services.extend([service] * weight)

        if not weighted_services:
            return services[0]

        index = self.round_robin_counters[service_key] % len(weighted_services)
        self.round_robin_counters[service_key] += 1
        return weighted_services[index]

    def _random_select(self, services: List[ServiceInfo]) -> ServiceInfo:
        """Random selection"""
        import random
        return random.choice(services)

    def _health_based_select(self, services: List[ServiceInfo]) -> ServiceInfo:
        """Health-based selection (en yeni heartbeat)"""
        return max(services, key=lambda s: s.last_heartbeat)

    def _response_time_select(self, services: List[ServiceInfo]) -> ServiceInfo:
        """Response time-based selection"""
        best_service = services[0]
        best_avg_time = float('inf')

        for service in services:
            response_times = self.response_times[service.service_id]
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                if avg_time < best_avg_time:
                    best_avg_time = avg_time
                    best_service = service

        return best_service

    def _update_connection_count(self, service_id: str, delta: int):
        """Connection count'u güncelle"""
        self.connection_counts[service_id] = max(0, self.connection_counts[service_id] + delta)

    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Load balancer istatistiklerini getir"""
        with self._lock:
            return {
                'strategy': self.strategy.value,
                'stats': self.lb_stats.copy(),
                'connection_counts': dict(self.connection_counts),
                'service_weights': dict(self.service_weights),
                'success_rate': (
                    self.lb_stats['successful_distributions'] / max(1, self.lb_stats['total_requests'])
                ) * 100
            }

    def get_service_performance(self, service_id: str) -> Dict[str, Any]:
        """Service performance bilgilerini getir"""
        with self._lock:
            response_times = self.response_times[service_id]

            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
            else:
                avg_response_time = min_response_time = max_response_time = 0.0

            return {
                'service_id': service_id,
                'connection_count': self.connection_counts[service_id],
                'weight': self.service_weights[service_id],
                'avg_response_time': avg_response_time,
                'min_response_time': min_response_time,
                'max_response_time': max_response_time,
                'total_requests': len(response_times)
            }


class ServiceDiscoveryManager:
    """
    Service Discovery Manager - Integrated Service Discovery System

    Service Registry, Health Monitor ve Load Balancer'ı
    entegre eden ana yönetim sistemi.
    """

    def __init__(self,
                 registry_id: str = None,
                 health_check_interval: float = 30.0,
                 cleanup_interval: float = 60.0,
                 load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        """
        Service Discovery Manager başlatıcı

        Args:
            registry_id: Registry ID
            health_check_interval: Health check aralığı
            cleanup_interval: Cleanup aralığı
            load_balancing_strategy: Load balancing stratejisi
        """
        # Core components
        self.registry = ServiceRegistry(registry_id, cleanup_interval)
        self.health_monitor = HealthMonitor(self.registry, health_check_interval)
        self.load_balancer = LoadBalancer(self.registry, load_balancing_strategy)

        # Manager state
        self.running = False
        self.manager_id = registry_id or f"discovery_manager_{int(time.time())}"

        # Statistics
        self.manager_stats = {
            'start_time': 0,
            'uptime': 0,
            'total_service_registrations': 0,
            'total_service_discoveries': 0,
            'total_load_balanced_requests': 0
        }

        print(f"🌐 Service Discovery Manager {self.manager_id} initialized")

    async def start(self):
        """Service Discovery Manager'ı başlat"""
        if self.running:
            return

        self.running = True
        self.manager_stats['start_time'] = time.time()

        # Core component'leri başlat
        await self.registry.start()
        await self.health_monitor.start()

        print(f"🚀 Service Discovery Manager {self.manager_id} started")

    async def stop(self):
        """Service Discovery Manager'ı durdur"""
        if not self.running:
            return

        self.running = False

        # Core component'leri durdur
        await self.health_monitor.stop()
        await self.registry.stop()

        print(f"🛑 Service Discovery Manager {self.manager_id} stopped")

    def register_agent_service(self,
                              agent_id: str,
                              service_name: str,
                              host: str = "localhost",
                              port: int = 0,
                              capabilities: List[str] = None,
                              metadata: Dict[str, Any] = None,
                              tags: List[str] = None) -> str:
        """
        Agent service'ini kaydet

        Args:
            agent_id: Agent ID
            service_name: Service adı
            host: Host adresi
            port: Port numarası
            capabilities: Agent yetenekleri
            metadata: Ek metadata
            tags: Service tag'leri

        Returns:
            str: Service ID
        """
        service_info = ServiceInfo(
            agent_id=agent_id,
            service_name=service_name,
            service_type="agent",
            host=host,
            port=port,
            capabilities=capabilities or [],
            metadata=metadata or {},
            tags=tags or [],
            status=ServiceStatus.HEALTHY
        )

        success = self.registry.register_service(service_info)
        if success:
            self.manager_stats['total_service_registrations'] += 1
            return service_info.service_id
        else:
            raise Exception(f"Failed to register service for agent {agent_id}")

    def unregister_agent_service(self, service_id: str) -> bool:
        """
        Agent service'ini kayıttan çıkar

        Args:
            service_id: Service ID

        Returns:
            bool: Başarı durumu
        """
        return self.registry.unregister_service(service_id)

    def discover_agents(self,
                       capability: str = None,
                       tags: List[str] = None,
                       healthy_only: bool = True) -> List[ServiceInfo]:
        """
        Agent'ları keşfet

        Args:
            capability: Aranan yetenek
            tags: Aranan tag'ler
            healthy_only: Sadece sağlıklı agent'lar

        Returns:
            List[ServiceInfo]: Bulunan agent'lar
        """
        services = self.registry.discover_services(
            service_type="agent",
            capability=capability,
            tags=tags,
            healthy_only=healthy_only
        )

        self.manager_stats['total_service_discoveries'] += 1
        return services

    def select_agent(self,
                    capability: str = None,
                    tags: List[str] = None,
                    exclude_agents: List[str] = None) -> Optional[ServiceInfo]:
        """
        Load balancing ile agent seç

        Args:
            capability: Aranan yetenek
            tags: Aranan tag'ler
            exclude_agents: Hariç tutulacak agent'lar

        Returns:
            Optional[ServiceInfo]: Seçilen agent
        """
        selected = self.load_balancer.select_service(
            service_type="agent",
            capability=capability,
            tags=tags,
            exclude_services=exclude_agents
        )

        if selected:
            self.manager_stats['total_load_balanced_requests'] += 1

        return selected

    def release_agent(self, service_id: str):
        """
        Agent kullanımını bitir

        Args:
            service_id: Service ID
        """
        self.load_balancer.release_service(service_id)

    def record_agent_response_time(self, service_id: str, response_time: float):
        """
        Agent response time'ını kaydet

        Args:
            service_id: Service ID
            response_time: Response time (saniye)
        """
        self.load_balancer.record_response_time(service_id, response_time)

    def set_agent_weight(self, service_id: str, weight: float):
        """
        Agent weight'ini ayarla

        Args:
            service_id: Service ID
            weight: Weight değeri
        """
        self.load_balancer.set_service_weight(service_id, weight)

    def change_load_balancing_strategy(self, strategy: LoadBalancingStrategy):
        """
        Load balancing stratejisini değiştir

        Args:
            strategy: Yeni strateji
        """
        self.load_balancer.change_strategy(strategy)

    def get_agent_health(self, service_id: str) -> Optional[bool]:
        """
        Agent'ın sağlık durumunu getir

        Args:
            service_id: Service ID

        Returns:
            Optional[bool]: Sağlık durumu
        """
        service = self.registry.get_service(service_id)
        if service:
            return service.is_healthy()
        return None

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Kapsamlı sistem istatistiklerini getir"""
        current_time = time.time()
        if self.running:
            self.manager_stats['uptime'] = current_time - self.manager_stats['start_time']

        return {
            'manager_id': self.manager_id,
            'running': self.running,
            'manager_stats': self.manager_stats.copy(),
            'registry_stats': self.registry.get_registry_stats(),
            'health_stats': self.health_monitor.get_health_stats(),
            'load_balancer_stats': self.load_balancer.get_load_balancer_stats()
        }

    def get_all_agents(self) -> List[ServiceInfo]:
        """Tüm agent'ları getir"""
        return self.registry.discover_services(service_type="agent", healthy_only=False)

    def get_agent_performance(self, service_id: str) -> Dict[str, Any]:
        """Agent performance bilgilerini getir"""
        return self.load_balancer.get_service_performance(service_id)


class ServiceDiscovery(ServiceDiscoveryManager):
    """
    Backward compatibility alias for ServiceDiscoveryManager

    This class provides backward compatibility for components that
    expect a ServiceDiscovery class instead of ServiceDiscoveryManager.
    """
    pass


if __name__ == "__main__":
    # Test the service discovery system
    import asyncio

    async def test_service_discovery():
        manager = ServiceDiscoveryManager()

        # Start the system
        await manager.start()

        # Register a test service
        test_service = ServiceInfo(
            service_id="test_service_1",
            service_name="Test Service",
            service_type="test",
            host="localhost",
            port=8080,
            capabilities=["test_capability"],
            tags=["test", "demo"]
        )

        success = manager.register_service(test_service)
        print(f"Service registration: {'Success' if success else 'Failed'}")

        # Discover services
        services = manager.discover_services(service_type="test")
        print(f"Discovered services: {len(services)}")

        # Test load balancing
        selected = manager.select_service(service_type="test")
        if selected:
            print(f"Selected service: {selected.service_name}")

        # Stop the system
        await manager.stop()

    asyncio.run(test_service_discovery())
