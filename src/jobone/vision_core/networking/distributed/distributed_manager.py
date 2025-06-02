"""
Distributed System Manager for Orion Vision Core

This module provides distributed system capabilities including service discovery,
load balancing, and distributed communication.
Part of Sprint 9.3 Advanced Networking & Communication development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.3 - Advanced Networking & Communication
"""

import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class ServiceState(Enum):
    """Service state enumeration"""
    UNKNOWN = "unknown"
    STARTING = "starting"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class LoadBalancingStrategy(Enum):
    """Load balancing strategy enumeration"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"
    HASH = "hash"
    LEAST_RESPONSE_TIME = "least_response_time"


class NodeRole(Enum):
    """Node role enumeration"""
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    OBSERVER = "observer"


@dataclass
class ServiceInstance:
    """Service instance data structure"""
    service_id: str
    service_name: str
    host: str
    port: int
    state: ServiceState = ServiceState.UNKNOWN
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    health_check_url: Optional[str] = None
    weight: int = 1
    registered_at: float = field(default_factory=time.time)
    last_health_check: float = field(default_factory=time.time)
    health_check_failures: int = 0
    request_count: int = 0
    response_time_ms: float = 0.0
    
    def get_endpoint(self) -> str:
        """Get service endpoint"""
        return f"{self.host}:{self.port}"
    
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.state == ServiceState.HEALTHY
    
    def get_uptime(self) -> float:
        """Get service uptime in seconds"""
        return time.time() - self.registered_at


@dataclass
class ClusterNode:
    """Cluster node data structure"""
    node_id: str
    host: str
    port: int
    role: NodeRole = NodeRole.FOLLOWER
    state: ServiceState = ServiceState.UNKNOWN
    last_heartbeat: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    services: Set[str] = field(default_factory=set)
    
    def is_alive(self, heartbeat_timeout: float = 30.0) -> bool:
        """Check if node is alive based on heartbeat"""
        return time.time() - self.last_heartbeat < heartbeat_timeout
    
    def get_endpoint(self) -> str:
        """Get node endpoint"""
        return f"{self.host}:{self.port}"


@dataclass
class DistributedMessage:
    """Distributed system message"""
    message_id: str
    message_type: str
    source_node: str
    target_node: Optional[str] = None
    payload: Any = None
    timestamp: float = field(default_factory=time.time)
    ttl: float = 300.0  # 5 minutes default TTL
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if message is expired"""
        return time.time() > (self.timestamp + self.ttl)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type,
            'source_node': self.source_node,
            'target_node': self.target_node,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'ttl': self.ttl,
            'metadata': self.metadata
        }


class ServiceRegistry:
    """
    Service registry for service discovery
    
    Manages service registration, discovery, and health monitoring.
    """
    
    def __init__(self, logger: Optional[AgentLogger] = None):
        """Initialize service registry"""
        self.logger = logger or AgentLogger("service_registry")
        
        # Service storage
        self.services: Dict[str, ServiceInstance] = {}
        self.service_groups: Dict[str, List[str]] = {}  # service_name -> [service_ids]
        
        # Health monitoring
        self.health_check_interval = 30.0
        self.health_check_timeout = 10.0
        self.max_health_failures = 3
        
        # Thread safety
        self._lock = threading.RLock()
        
        self.logger.info("Service Registry initialized")
    
    def register_service(self, service: ServiceInstance) -> bool:
        """Register service instance"""
        try:
            with self._lock:
                # Store service
                self.services[service.service_id] = service
                
                # Add to service group
                if service.service_name not in self.service_groups:
                    self.service_groups[service.service_name] = []
                
                if service.service_id not in self.service_groups[service.service_name]:
                    self.service_groups[service.service_name].append(service.service_id)
                
                # Set initial state
                service.state = ServiceState.HEALTHY
                
                self.logger.info(
                    "Service registered",
                    service_id=service.service_id,
                    service_name=service.service_name,
                    endpoint=service.get_endpoint()
                )
                
                return True
                
        except Exception as e:
            self.logger.error("Service registration failed", service_id=service.service_id, error=str(e))
            return False
    
    def unregister_service(self, service_id: str) -> bool:
        """Unregister service instance"""
        try:
            with self._lock:
                if service_id not in self.services:
                    self.logger.warning("Service not found", service_id=service_id)
                    return False
                
                service = self.services[service_id]
                
                # Remove from service group
                if service.service_name in self.service_groups:
                    if service_id in self.service_groups[service.service_name]:
                        self.service_groups[service.service_name].remove(service_id)
                    
                    # Clean up empty groups
                    if not self.service_groups[service.service_name]:
                        del self.service_groups[service.service_name]
                
                # Remove service
                del self.services[service_id]
                
                self.logger.info("Service unregistered", service_id=service_id)
                return True
                
        except Exception as e:
            self.logger.error("Service unregistration failed", service_id=service_id, error=str(e))
            return False
    
    def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """Discover healthy service instances by name"""
        with self._lock:
            if service_name not in self.service_groups:
                return []
            
            healthy_services = []
            for service_id in self.service_groups[service_name]:
                if service_id in self.services:
                    service = self.services[service_id]
                    if service.is_healthy():
                        healthy_services.append(service)
            
            return healthy_services
    
    def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """Get service instance by ID"""
        return self.services.get(service_id)
    
    def update_service_health(self, service_id: str, is_healthy: bool, response_time_ms: float = 0.0):
        """Update service health status"""
        with self._lock:
            if service_id not in self.services:
                return
            
            service = self.services[service_id]
            service.last_health_check = time.time()
            service.response_time_ms = response_time_ms
            
            if is_healthy:
                service.state = ServiceState.HEALTHY
                service.health_check_failures = 0
            else:
                service.health_check_failures += 1
                if service.health_check_failures >= self.max_health_failures:
                    service.state = ServiceState.UNHEALTHY
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get service registry statistics"""
        with self._lock:
            total_services = len(self.services)
            healthy_services = sum(1 for s in self.services.values() if s.is_healthy())
            
            return {
                'total_services': total_services,
                'healthy_services': healthy_services,
                'unhealthy_services': total_services - healthy_services,
                'service_groups': len(self.service_groups),
                'health_check_interval': self.health_check_interval
            }


class LoadBalancer:
    """
    Load balancer for distributing requests across service instances
    """
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN,
                 logger: Optional[AgentLogger] = None):
        """Initialize load balancer"""
        self.strategy = strategy
        self.logger = logger or AgentLogger("load_balancer")
        
        # Load balancing state
        self.round_robin_counters: Dict[str, int] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        self.logger.info("Load Balancer initialized", strategy=strategy.value)
    
    def select_service(self, services: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """Select service instance based on load balancing strategy"""
        if not services:
            return None
        
        # Filter healthy services
        healthy_services = [s for s in services if s.is_healthy()]
        if not healthy_services:
            return None
        
        with self._lock:
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._round_robin_select(healthy_services)
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_select(healthy_services)
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_select(healthy_services)
            elif self.strategy == LoadBalancingStrategy.RANDOM:
                return self._random_select(healthy_services)
            elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                return self._least_response_time_select(healthy_services)
            else:
                return healthy_services[0]  # Default to first service
    
    def _round_robin_select(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Round robin selection"""
        if not services:
            return None
        
        service_name = services[0].service_name
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        index = self.round_robin_counters[service_name] % len(services)
        self.round_robin_counters[service_name] += 1
        
        return services[index]
    
    def _least_connections_select(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection"""
        return min(services, key=lambda s: s.request_count)
    
    def _weighted_round_robin_select(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round robin selection"""
        # Simple weighted selection based on service weight
        total_weight = sum(s.weight for s in services)
        if total_weight == 0:
            return services[0]
        
        import random
        weight_sum = 0
        random_weight = random.randint(1, total_weight)
        
        for service in services:
            weight_sum += service.weight
            if random_weight <= weight_sum:
                return service
        
        return services[-1]  # Fallback
    
    def _random_select(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Random selection"""
        import random
        return random.choice(services)
    
    def _least_response_time_select(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Least response time selection"""
        return min(services, key=lambda s: s.response_time_ms)


class DistributedManager:
    """
    Distributed system manager
    
    Provides comprehensive distributed system capabilities including
    service discovery, load balancing, and cluster management.
    """
    
    def __init__(self, node_id: Optional[str] = None,
                 metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize distributed manager"""
        self.node_id = node_id or str(uuid.uuid4())
        self.logger = logger or AgentLogger("distributed_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Components
        self.service_registry = ServiceRegistry(self.logger)
        self.load_balancer = LoadBalancer(logger=self.logger)
        
        # Cluster management
        self.cluster_nodes: Dict[str, ClusterNode] = {}
        self.current_node = ClusterNode(
            node_id=self.node_id,
            host="localhost",
            port=8080,
            role=NodeRole.FOLLOWER
        )
        
        # Message handling
        self.message_handlers: Dict[str, List[Callable]] = {}
        
        # Configuration
        self.heartbeat_interval = 10.0
        self.election_timeout = 30.0
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.distributed_stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'service_requests': 0,
            'load_balancing_decisions': 0,
            'cluster_events': 0,
            'leader_elections': 0
        }
        
        self.logger.info("Distributed Manager initialized", node_id=self.node_id)
    
    def register_service(self, service_name: str, host: str, port: int, 
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """Register service with the distributed system"""
        service_id = str(uuid.uuid4())
        
        service = ServiceInstance(
            service_id=service_id,
            service_name=service_name,
            host=host,
            port=port,
            metadata=metadata or {}
        )
        
        if self.service_registry.register_service(service):
            # Collect metrics
            self.metrics_collector.collect_metric(
                name="distributed.service_registered",
                value=1,
                metric_type=MetricType.COUNTER,
                tags={'service_name': service_name}
            )
            
            return service_id
        
        return None
    
    def discover_service(self, service_name: str) -> Optional[ServiceInstance]:
        """Discover and select service instance"""
        services = self.service_registry.discover_services(service_name)
        
        if not services:
            return None
        
        # Use load balancer to select service
        selected_service = self.load_balancer.select_service(services)
        
        if selected_service:
            # Update request count
            selected_service.request_count += 1
            self.distributed_stats['service_requests'] += 1
            self.distributed_stats['load_balancing_decisions'] += 1
            
            # Collect metrics
            self.metrics_collector.collect_metric(
                name="distributed.service_selected",
                value=1,
                metric_type=MetricType.COUNTER,
                tags={
                    'service_name': service_name,
                    'service_id': selected_service.service_id
                }
            )
        
        return selected_service
    
    def add_cluster_node(self, node: ClusterNode):
        """Add node to cluster"""
        with self._lock:
            self.cluster_nodes[node.node_id] = node
            self.distributed_stats['cluster_events'] += 1
            
            self.logger.info(
                "Cluster node added",
                node_id=node.node_id,
                endpoint=node.get_endpoint(),
                role=node.role.value
            )
    
    def remove_cluster_node(self, node_id: str):
        """Remove node from cluster"""
        with self._lock:
            if node_id in self.cluster_nodes:
                del self.cluster_nodes[node_id]
                self.distributed_stats['cluster_events'] += 1
                
                self.logger.info("Cluster node removed", node_id=node_id)
    
    def send_message(self, message: DistributedMessage) -> bool:
        """Send message to cluster node"""
        try:
            # Simulate message sending
            self.distributed_stats['messages_sent'] += 1
            
            # Collect metrics
            self.metrics_collector.collect_metric(
                name="distributed.message_sent",
                value=1,
                metric_type=MetricType.COUNTER,
                tags={
                    'message_type': message.message_type,
                    'target_node': message.target_node or 'broadcast'
                }
            )
            
            self.logger.debug(
                "Distributed message sent",
                message_id=message.message_id,
                message_type=message.message_type,
                target_node=message.target_node
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to send message", message_id=message.message_id, error=str(e))
            return False
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status"""
        with self._lock:
            alive_nodes = sum(1 for node in self.cluster_nodes.values() if node.is_alive())
            
            return {
                'current_node_id': self.node_id,
                'current_node_role': self.current_node.role.value,
                'total_nodes': len(self.cluster_nodes),
                'alive_nodes': alive_nodes,
                'leader_node': self._get_leader_node_id(),
                'cluster_health': 'healthy' if alive_nodes > len(self.cluster_nodes) / 2 else 'degraded'
            }
    
    def _get_leader_node_id(self) -> Optional[str]:
        """Get current leader node ID"""
        for node_id, node in self.cluster_nodes.items():
            if node.role == NodeRole.LEADER and node.is_alive():
                return node_id
        return None
    
    def get_distributed_stats(self) -> Dict[str, Any]:
        """Get distributed system statistics"""
        with self._lock:
            service_stats = self.service_registry.get_registry_stats()
            cluster_status = self.get_cluster_status()
            
            return {
                'node_id': self.node_id,
                'load_balancing_strategy': self.load_balancer.strategy.value,
                'service_registry': service_stats,
                'cluster_status': cluster_status,
                'stats': self.distributed_stats.copy()
            }
