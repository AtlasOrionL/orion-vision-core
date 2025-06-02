"""
Network Manager for Orion Vision Core

This module provides comprehensive network management and connectivity.
Part of Sprint 9.3 Advanced Networking & Communication development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.3 - Advanced Networking & Communication
"""

import asyncio
import socket
import threading
import time
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class NetworkProtocol(Enum):
    """Network protocol enumeration"""
    TCP = "tcp"
    UDP = "udp"
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    GRPC = "grpc"


class ConnectionState(Enum):
    """Connection state enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    CLOSED = "closed"


class NetworkQuality(Enum):
    """Network quality enumeration"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class NetworkEndpoint:
    """Network endpoint data structure"""
    host: str
    port: int
    protocol: NetworkProtocol = NetworkProtocol.TCP
    timeout: float = 30.0
    retry_count: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_address(self) -> str:
        """Get formatted address"""
        return f"{self.host}:{self.port}"
    
    def validate(self) -> bool:
        """Validate endpoint configuration"""
        return bool(self.host and 1 <= self.port <= 65535)


@dataclass
class NetworkConnection:
    """Network connection data structure"""
    endpoint: NetworkEndpoint
    connection_id: str
    state: ConnectionState = ConnectionState.DISCONNECTED
    socket: Optional[Any] = None
    created_at: float = field(default_factory=time.time)
    connected_at: Optional[float] = None
    last_activity: float = field(default_factory=time.time)
    bytes_sent: int = 0
    bytes_received: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self.state == ConnectionState.CONNECTED
    
    def get_uptime(self) -> float:
        """Get connection uptime in seconds"""
        if self.connected_at:
            return time.time() - self.connected_at
        return 0.0


class NetworkManager:
    """
    Comprehensive network management system
    
    Provides network connectivity, connection pooling, health monitoring,
    and advanced networking capabilities with real-time metrics.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize network manager"""
        self.logger = logger or AgentLogger("network_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Connection management
        self.connections: Dict[str, NetworkConnection] = {}
        self.connection_pools: Dict[str, List[NetworkConnection]] = {}
        
        # Network configuration
        self.default_timeout = 30.0
        self.max_connections_per_pool = 10
        self.connection_retry_delay = 1.0
        self.health_check_interval = 60.0
        
        # Network monitoring
        self.network_quality = NetworkQuality.GOOD
        self.bandwidth_usage = 0.0
        self.latency_ms = 0.0
        
        # Event handlers
        self.connection_handlers: Dict[str, List[Callable]] = {
            'on_connect': [],
            'on_disconnect': [],
            'on_error': [],
            'on_data_received': []
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Background tasks
        self.health_check_running = False
        self.health_check_thread = None
        
        # Statistics
        self.network_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'connection_errors': 0,
            'reconnection_attempts': 0,
            'health_checks': 0
        }
        
        self.logger.info("Network Manager initialized")
    
    def start_health_monitoring(self):
        """Start network health monitoring"""
        if self.health_check_running:
            self.logger.warning("Health monitoring already running")
            return
        
        self.health_check_running = True
        self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_check_thread.start()
        
        self.logger.info("Network health monitoring started", interval=self.health_check_interval)
    
    def stop_health_monitoring(self):
        """Stop network health monitoring"""
        if not self.health_check_running:
            return
        
        self.health_check_running = False
        
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5.0)
        
        self.logger.info("Network health monitoring stopped")
    
    def create_connection(self, endpoint: NetworkEndpoint, connection_id: Optional[str] = None) -> str:
        """Create network connection"""
        try:
            with self._lock:
                # Generate connection ID if not provided
                if not connection_id:
                    import uuid
                    connection_id = f"conn_{uuid.uuid4().hex[:8]}"
                
                # Validate endpoint
                if not endpoint.validate():
                    raise ValueError(f"Invalid endpoint: {endpoint.get_address()}")
                
                # Check if connection already exists
                if connection_id in self.connections:
                    raise ValueError(f"Connection '{connection_id}' already exists")
                
                # Create connection object
                connection = NetworkConnection(
                    endpoint=endpoint,
                    connection_id=connection_id
                )
                
                # Store connection
                self.connections[connection_id] = connection
                
                # Update statistics
                self.network_stats['total_connections'] += 1
                
                self.logger.info(
                    "Network connection created",
                    connection_id=connection_id,
                    endpoint=endpoint.get_address(),
                    protocol=endpoint.protocol.value
                )
                
                return connection_id
                
        except Exception as e:
            self.logger.error("Failed to create connection", connection_id=connection_id, error=str(e))
            raise
    
    def connect(self, connection_id: str) -> bool:
        """Establish network connection"""
        try:
            with self._lock:
                if connection_id not in self.connections:
                    raise ValueError(f"Connection '{connection_id}' not found")
                
                connection = self.connections[connection_id]
                
                if connection.is_connected():
                    self.logger.warning("Connection already established", connection_id=connection_id)
                    return True
                
                # Update state
                connection.state = ConnectionState.CONNECTING
                
                # Create socket based on protocol
                if connection.endpoint.protocol in [NetworkProtocol.TCP, NetworkProtocol.HTTP, NetworkProtocol.HTTPS]:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                elif connection.endpoint.protocol == NetworkProtocol.UDP:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                else:
                    raise ValueError(f"Unsupported protocol: {connection.endpoint.protocol}")
                
                # Set socket options
                sock.settimeout(connection.endpoint.timeout)
                
                try:
                    # Attempt connection
                    if connection.endpoint.protocol != NetworkProtocol.UDP:
                        sock.connect((connection.endpoint.host, connection.endpoint.port))
                    
                    # Update connection
                    connection.socket = sock
                    connection.state = ConnectionState.CONNECTED
                    connection.connected_at = time.time()
                    connection.last_activity = time.time()
                    
                    # Update statistics
                    self.network_stats['active_connections'] += 1
                    
                    # Collect metrics
                    self.metrics_collector.collect_metric(
                        name="network.connection_established",
                        value=1,
                        metric_type=MetricType.COUNTER,
                        tags={
                            'connection_id': connection_id,
                            'protocol': connection.endpoint.protocol.value,
                            'host': connection.endpoint.host
                        }
                    )
                    
                    # Trigger event handlers
                    self._trigger_event('on_connect', connection)
                    
                    self.logger.info(
                        "Network connection established",
                        connection_id=connection_id,
                        endpoint=connection.endpoint.get_address(),
                        protocol=connection.endpoint.protocol.value
                    )
                    
                    return True
                    
                except Exception as e:
                    # Connection failed
                    connection.state = ConnectionState.ERROR
                    connection.error_count += 1
                    self.network_stats['failed_connections'] += 1
                    self.network_stats['connection_errors'] += 1
                    
                    # Close socket
                    try:
                        sock.close()
                    except:
                        pass
                    
                    # Trigger error handlers
                    self._trigger_event('on_error', connection, str(e))
                    
                    self.logger.error(
                        "Network connection failed",
                        connection_id=connection_id,
                        endpoint=connection.endpoint.get_address(),
                        error=str(e)
                    )
                    
                    return False
                
        except Exception as e:
            self.logger.error("Connection attempt failed", connection_id=connection_id, error=str(e))
            return False
    
    def disconnect(self, connection_id: str) -> bool:
        """Close network connection"""
        try:
            with self._lock:
                if connection_id not in self.connections:
                    self.logger.warning("Connection not found", connection_id=connection_id)
                    return False
                
                connection = self.connections[connection_id]
                
                # Close socket if exists
                if connection.socket:
                    try:
                        connection.socket.close()
                    except Exception as e:
                        self.logger.warning("Error closing socket", connection_id=connection_id, error=str(e))
                
                # Update connection state
                was_connected = connection.is_connected()
                connection.state = ConnectionState.CLOSED
                connection.socket = None
                
                # Update statistics
                if was_connected:
                    self.network_stats['active_connections'] -= 1
                
                # Trigger event handlers
                self._trigger_event('on_disconnect', connection)
                
                self.logger.info("Network connection closed", connection_id=connection_id)
                return True
                
        except Exception as e:
            self.logger.error("Failed to disconnect", connection_id=connection_id, error=str(e))
            return False
    
    def send_data(self, connection_id: str, data: bytes) -> bool:
        """Send data through connection"""
        try:
            with self._lock:
                if connection_id not in self.connections:
                    raise ValueError(f"Connection '{connection_id}' not found")
                
                connection = self.connections[connection_id]
                
                if not connection.is_connected() or not connection.socket:
                    raise ValueError(f"Connection '{connection_id}' is not active")
                
                # Send data
                bytes_sent = connection.socket.send(data)
                
                # Update connection stats
                connection.bytes_sent += bytes_sent
                connection.last_activity = time.time()
                
                # Update global stats
                self.network_stats['total_bytes_sent'] += bytes_sent
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="network.bytes_sent",
                    value=bytes_sent,
                    metric_type=MetricType.COUNTER,
                    tags={'connection_id': connection_id}
                )
                
                self.logger.debug(
                    "Data sent",
                    connection_id=connection_id,
                    bytes_sent=bytes_sent
                )
                
                return True
                
        except Exception as e:
            self.logger.error("Failed to send data", connection_id=connection_id, error=str(e))
            return False
    
    def receive_data(self, connection_id: str, buffer_size: int = 4096) -> Optional[bytes]:
        """Receive data from connection"""
        try:
            with self._lock:
                if connection_id not in self.connections:
                    raise ValueError(f"Connection '{connection_id}' not found")
                
                connection = self.connections[connection_id]
                
                if not connection.is_connected() or not connection.socket:
                    raise ValueError(f"Connection '{connection_id}' is not active")
                
                # Receive data
                data = connection.socket.recv(buffer_size)
                
                if data:
                    # Update connection stats
                    connection.bytes_received += len(data)
                    connection.last_activity = time.time()
                    
                    # Update global stats
                    self.network_stats['total_bytes_received'] += len(data)
                    
                    # Collect metrics
                    self.metrics_collector.collect_metric(
                        name="network.bytes_received",
                        value=len(data),
                        metric_type=MetricType.COUNTER,
                        tags={'connection_id': connection_id}
                    )
                    
                    # Trigger data received handlers
                    self._trigger_event('on_data_received', connection, data)
                    
                    self.logger.debug(
                        "Data received",
                        connection_id=connection_id,
                        bytes_received=len(data)
                    )
                
                return data
                
        except Exception as e:
            self.logger.error("Failed to receive data", connection_id=connection_id, error=str(e))
            return None
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler"""
        if event_type in self.connection_handlers:
            self.connection_handlers[event_type].append(handler)
            
            self.logger.debug("Event handler added", event_type=event_type)
    
    def _trigger_event(self, event_type: str, connection: NetworkConnection, *args):
        """Trigger event handlers"""
        if event_type in self.connection_handlers:
            for handler in self.connection_handlers[event_type]:
                try:
                    handler(connection, *args)
                except Exception as e:
                    self.logger.warning("Event handler failed", event_type=event_type, error=str(e))
    
    def _health_check_loop(self):
        """Background health check loop"""
        while self.health_check_running:
            try:
                self._perform_health_check()
                time.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error("Health check error", error=str(e))
                time.sleep(5.0)  # Error recovery delay
    
    def _perform_health_check(self):
        """Perform network health check"""
        try:
            with self._lock:
                active_connections = 0
                failed_connections = 0
                
                for connection in self.connections.values():
                    if connection.is_connected():
                        active_connections += 1
                        
                        # Check connection health
                        if connection.socket:
                            try:
                                # Simple health check - send empty data
                                connection.socket.send(b'')
                            except Exception:
                                connection.state = ConnectionState.ERROR
                                connection.error_count += 1
                                failed_connections += 1
                    elif connection.state == ConnectionState.ERROR:
                        failed_connections += 1
                
                # Update network quality based on health
                if failed_connections == 0:
                    self.network_quality = NetworkQuality.EXCELLENT
                elif failed_connections < active_connections * 0.1:
                    self.network_quality = NetworkQuality.GOOD
                elif failed_connections < active_connections * 0.3:
                    self.network_quality = NetworkQuality.FAIR
                elif failed_connections < active_connections * 0.5:
                    self.network_quality = NetworkQuality.POOR
                else:
                    self.network_quality = NetworkQuality.CRITICAL
                
                # Update statistics
                self.network_stats['health_checks'] += 1
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="network.health_check",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags={
                        'active_connections': str(active_connections),
                        'failed_connections': str(failed_connections),
                        'quality': self.network_quality.value
                    }
                )
                
                self.logger.debug(
                    "Network health check completed",
                    active_connections=active_connections,
                    failed_connections=failed_connections,
                    quality=self.network_quality.value
                )
                
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information"""
        if connection_id not in self.connections:
            return None
        
        connection = self.connections[connection_id]
        return {
            'connection_id': connection.connection_id,
            'endpoint': connection.endpoint.get_address(),
            'protocol': connection.endpoint.protocol.value,
            'state': connection.state.value,
            'uptime': connection.get_uptime(),
            'bytes_sent': connection.bytes_sent,
            'bytes_received': connection.bytes_received,
            'error_count': connection.error_count,
            'last_activity': connection.last_activity
        }
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """List all connections"""
        return [
            self.get_connection_info(conn_id)
            for conn_id in self.connections.keys()
        ]
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        with self._lock:
            return {
                'network_quality': self.network_quality.value,
                'bandwidth_usage': self.bandwidth_usage,
                'latency_ms': self.latency_ms,
                'total_connections': len(self.connections),
                'active_connections': sum(1 for c in self.connections.values() if c.is_connected()),
                'health_monitoring': self.health_check_running,
                'stats': self.network_stats.copy()
            }
