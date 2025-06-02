"""
Integration Manager for Orion Vision Core

This module provides comprehensive integration management including
service integration, API management, and system coordination.
Part of Sprint 9.9 Advanced Integration & Deployment development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.9 - Advanced Integration & Deployment
"""

import time
import threading
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class IntegrationType(Enum):
    """Integration type enumeration"""
    API = "api"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    EXTERNAL_SERVICE = "external_service"
    MICROSERVICE = "microservice"
    WEBHOOK = "webhook"
    STREAM = "stream"


class IntegrationStatus(Enum):
    """Integration status enumeration"""
    INACTIVE = "inactive"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ConnectionProtocol(Enum):
    """Connection protocol enumeration"""
    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    UDP = "udp"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    MQTT = "mqtt"
    AMQP = "amqp"


@dataclass
class IntegrationConfig:
    """Integration configuration data structure"""
    integration_id: str
    integration_name: str
    integration_type: IntegrationType
    protocol: ConnectionProtocol
    endpoint: str
    port: Optional[int] = None
    credentials: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: float = 30.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    health_check_interval: float = 60.0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate integration configuration"""
        if not self.integration_name or not self.integration_id:
            return False
        if not self.endpoint:
            return False
        if self.timeout_seconds <= 0 or self.retry_attempts < 0:
            return False
        return True


@dataclass
class IntegrationMetrics:
    """Integration metrics data structure"""
    integration_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    last_request_time: Optional[float] = None
    last_success_time: Optional[float] = None
    last_error_time: Optional[float] = None
    uptime_percentage: float = 0.0
    error_rate: float = 0.0
    
    def update_success(self, response_time_ms: float):
        """Update metrics for successful request"""
        self.total_requests += 1
        self.successful_requests += 1
        self.last_request_time = time.time()
        self.last_success_time = time.time()
        
        # Update average response time
        if self.total_requests == 1:
            self.average_response_time_ms = response_time_ms
        else:
            self.average_response_time_ms = (
                (self.average_response_time_ms * (self.total_requests - 1) + response_time_ms) / 
                self.total_requests
            )
        
        # Update error rate
        self.error_rate = (self.failed_requests / self.total_requests) * 100
    
    def update_failure(self):
        """Update metrics for failed request"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_request_time = time.time()
        self.last_error_time = time.time()
        
        # Update error rate
        self.error_rate = (self.failed_requests / self.total_requests) * 100


@dataclass
class IntegrationEvent:
    """Integration event data structure"""
    event_id: str
    integration_id: str
    event_type: str
    event_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    processed: bool = False


class IntegrationManager:
    """
    Comprehensive integration management system
    
    Provides service integration, API management, system coordination,
    and real-time integration monitoring with health checks.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize integration manager"""
        self.logger = logger or AgentLogger("integration_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Integration management
        self.integrations: Dict[str, IntegrationConfig] = {}
        self.integration_metrics: Dict[str, IntegrationMetrics] = {}
        self.integration_status: Dict[str, IntegrationStatus] = {}
        self.integration_connections: Dict[str, Any] = {}
        
        # Event management
        self.integration_events: List[IntegrationEvent] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Health monitoring
        self.health_check_active = False
        self.health_check_thread: Optional[threading.Thread] = None
        
        # Configuration
        self.max_events_history = 1000
        self.default_timeout = 30.0
        self.connection_pool_size = 10
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.integration_stats = {
            'total_integrations': 0,
            'active_integrations': 0,
            'connected_integrations': 0,
            'failed_integrations': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time_ms': 0.0,
            'uptime_percentage': 0.0
        }
        
        self.logger.info("Integration Manager initialized")
    
    def register_integration(self, config: IntegrationConfig) -> bool:
        """Register new integration"""
        try:
            # Validate configuration
            if not config.validate():
                self.logger.error("Invalid integration configuration", integration_id=config.integration_id)
                return False
            
            with self._lock:
                # Check if integration already exists
                if config.integration_id in self.integrations:
                    self.logger.warning("Integration already exists", integration_id=config.integration_id)
                    return False
                
                # Register integration
                self.integrations[config.integration_id] = config
                self.integration_metrics[config.integration_id] = IntegrationMetrics(
                    integration_id=config.integration_id
                )
                self.integration_status[config.integration_id] = IntegrationStatus.INACTIVE
                
                # Update statistics
                self.integration_stats['total_integrations'] += 1
                if config.enabled:
                    self.integration_stats['active_integrations'] += 1
            
            self.logger.info(
                "Integration registered",
                integration_id=config.integration_id,
                integration_name=config.integration_name,
                integration_type=config.integration_type.value,
                protocol=config.protocol.value,
                endpoint=config.endpoint
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Integration registration failed", integration_id=config.integration_id, error=str(e))
            return False
    
    def connect_integration(self, integration_id: str) -> bool:
        """Connect to integration"""
        try:
            if integration_id not in self.integrations:
                self.logger.error("Integration not found", integration_id=integration_id)
                return False
            
            config = self.integrations[integration_id]
            
            # Update status to connecting
            self.integration_status[integration_id] = IntegrationStatus.CONNECTING
            
            self.logger.info(
                "Integration connection started",
                integration_id=integration_id,
                endpoint=config.endpoint,
                protocol=config.protocol.value
            )
            
            # Simulate connection process
            connection_success = self._establish_connection(config)
            
            if connection_success:
                with self._lock:
                    self.integration_status[integration_id] = IntegrationStatus.CONNECTED
                    self.integration_stats['connected_integrations'] += 1
                
                self.logger.info(
                    "Integration connected successfully",
                    integration_id=integration_id,
                    integration_name=config.integration_name
                )
                
                # Emit connection event
                self._emit_event(integration_id, "connection_established", {
                    "endpoint": config.endpoint,
                    "protocol": config.protocol.value
                })
                
                return True
            else:
                with self._lock:
                    self.integration_status[integration_id] = IntegrationStatus.ERROR
                    self.integration_stats['failed_integrations'] += 1
                
                self.logger.error("Integration connection failed", integration_id=integration_id)
                return False
                
        except Exception as e:
            self.integration_status[integration_id] = IntegrationStatus.ERROR
            self.logger.error("Integration connection error", integration_id=integration_id, error=str(e))
            return False
    
    def disconnect_integration(self, integration_id: str) -> bool:
        """Disconnect from integration"""
        try:
            if integration_id not in self.integrations:
                self.logger.error("Integration not found", integration_id=integration_id)
                return False
            
            # Close connection
            if integration_id in self.integration_connections:
                # Simulate connection cleanup
                del self.integration_connections[integration_id]
            
            with self._lock:
                self.integration_status[integration_id] = IntegrationStatus.DISCONNECTED
                if self.integration_stats['connected_integrations'] > 0:
                    self.integration_stats['connected_integrations'] -= 1
            
            self.logger.info("Integration disconnected", integration_id=integration_id)
            
            # Emit disconnection event
            self._emit_event(integration_id, "connection_closed", {})
            
            return True
            
        except Exception as e:
            self.logger.error("Integration disconnection error", integration_id=integration_id, error=str(e))
            return False
    
    def send_request(self, integration_id: str, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send request to integration"""
        try:
            if integration_id not in self.integrations:
                self.logger.error("Integration not found", integration_id=integration_id)
                return None
            
            if self.integration_status[integration_id] != IntegrationStatus.CONNECTED:
                self.logger.error("Integration not connected", integration_id=integration_id)
                return None
            
            config = self.integrations[integration_id]
            metrics = self.integration_metrics[integration_id]
            
            start_time = time.time()
            
            # Simulate request processing
            response = self._process_request(config, request_data)
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if response:
                # Update success metrics
                metrics.update_success(response_time_ms)
                
                with self._lock:
                    self.integration_stats['successful_requests'] += 1
                    self.integration_stats['total_requests'] += 1
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="integration.request.success",
                    value=response_time_ms,
                    metric_type=MetricType.TIMER,
                    tags={
                        'integration_id': integration_id,
                        'integration_type': config.integration_type.value
                    }
                )
                
                self.logger.debug(
                    "Integration request successful",
                    integration_id=integration_id,
                    response_time_ms=f"{response_time_ms:.2f}"
                )
                
                return response
            else:
                # Update failure metrics
                metrics.update_failure()
                
                with self._lock:
                    self.integration_stats['failed_requests'] += 1
                    self.integration_stats['total_requests'] += 1
                
                self.logger.error("Integration request failed", integration_id=integration_id)
                return None
                
        except Exception as e:
            self.logger.error("Integration request error", integration_id=integration_id, error=str(e))
            return None
    
    def _establish_connection(self, config: IntegrationConfig) -> bool:
        """Establish connection to integration"""
        try:
            # Simulate connection establishment based on protocol
            if config.protocol in [ConnectionProtocol.HTTP, ConnectionProtocol.HTTPS]:
                # HTTP/HTTPS connection simulation
                connection = {
                    'type': 'http_client',
                    'endpoint': config.endpoint,
                    'timeout': config.timeout_seconds,
                    'headers': config.headers
                }
            elif config.protocol == ConnectionProtocol.WEBSOCKET:
                # WebSocket connection simulation
                connection = {
                    'type': 'websocket_client',
                    'endpoint': config.endpoint,
                    'timeout': config.timeout_seconds
                }
            elif config.protocol == ConnectionProtocol.GRPC:
                # gRPC connection simulation
                connection = {
                    'type': 'grpc_client',
                    'endpoint': config.endpoint,
                    'port': config.port or 50051
                }
            else:
                # Generic connection simulation
                connection = {
                    'type': 'generic_client',
                    'endpoint': config.endpoint,
                    'protocol': config.protocol.value
                }
            
            # Store connection
            self.integration_connections[config.integration_id] = connection
            
            # Simulate connection delay
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.logger.error("Connection establishment failed", integration_id=config.integration_id, error=str(e))
            return False
    
    def _process_request(self, config: IntegrationConfig, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process request to integration"""
        try:
            # Simulate request processing based on integration type
            if config.integration_type == IntegrationType.API:
                # API request simulation
                response = {
                    'status': 'success',
                    'data': {'result': 'api_response'},
                    'timestamp': time.time()
                }
            elif config.integration_type == IntegrationType.DATABASE:
                # Database query simulation
                response = {
                    'status': 'success',
                    'rows_affected': 1,
                    'data': [{'id': 1, 'value': 'database_result'}]
                }
            elif config.integration_type == IntegrationType.MESSAGE_QUEUE:
                # Message queue simulation
                response = {
                    'status': 'success',
                    'message_id': str(uuid.uuid4()),
                    'queue': 'default_queue'
                }
            else:
                # Generic response simulation
                response = {
                    'status': 'success',
                    'integration_type': config.integration_type.value,
                    'processed_data': request_data
                }
            
            # Simulate processing delay
            time.sleep(0.05)
            
            return response
            
        except Exception as e:
            self.logger.error("Request processing failed", integration_id=config.integration_id, error=str(e))
            return None
    
    def _emit_event(self, integration_id: str, event_type: str, event_data: Dict[str, Any]):
        """Emit integration event"""
        try:
            event = IntegrationEvent(
                event_id=str(uuid.uuid4()),
                integration_id=integration_id,
                event_type=event_type,
                event_data=event_data
            )
            
            with self._lock:
                self.integration_events.append(event)
                
                # Cleanup old events
                if len(self.integration_events) > self.max_events_history:
                    self.integration_events = self.integration_events[-self.max_events_history:]
            
            # Call event handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        self.logger.error("Event handler error", event_type=event_type, error=str(e))
            
            self.logger.debug(
                "Integration event emitted",
                integration_id=integration_id,
                event_type=event_type,
                event_id=event.event_id
            )
            
        except Exception as e:
            self.logger.error("Event emission failed", integration_id=integration_id, error=str(e))
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        
        self.logger.info("Event handler registered", event_type=event_type)
    
    def start_health_monitoring(self) -> bool:
        """Start health monitoring"""
        try:
            if self.health_check_active:
                self.logger.warning("Health monitoring already active")
                return True
            
            self.health_check_active = True
            
            # Start health check thread
            self.health_check_thread = threading.Thread(
                target=self._health_check_loop,
                name="IntegrationHealthCheck",
                daemon=True
            )
            self.health_check_thread.start()
            
            self.logger.info("Integration health monitoring started")
            return True
            
        except Exception as e:
            self.logger.error("Failed to start health monitoring", error=str(e))
            return False
    
    def stop_health_monitoring(self) -> bool:
        """Stop health monitoring"""
        try:
            if not self.health_check_active:
                self.logger.warning("Health monitoring not active")
                return True
            
            self.health_check_active = False
            
            # Wait for health check thread to finish
            if self.health_check_thread and self.health_check_thread.is_alive():
                self.health_check_thread.join(timeout=5.0)
            
            self.logger.info("Integration health monitoring stopped")
            return True
            
        except Exception as e:
            self.logger.error("Failed to stop health monitoring", error=str(e))
            return False
    
    def _health_check_loop(self):
        """Health check loop"""
        while self.health_check_active:
            try:
                # Check health of all connected integrations
                for integration_id, status in self.integration_status.items():
                    if status == IntegrationStatus.CONNECTED:
                        self._perform_health_check(integration_id)
                
                # Update global statistics
                self._update_global_stats()
                
                time.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                self.logger.error("Error in health check loop", error=str(e))
                time.sleep(30)
    
    def _perform_health_check(self, integration_id: str):
        """Perform health check for integration"""
        try:
            config = self.integrations[integration_id]
            
            # Send health check request
            health_response = self.send_request(integration_id, {'health_check': True})
            
            if health_response:
                self.logger.debug("Health check passed", integration_id=integration_id)
            else:
                self.logger.warning("Health check failed", integration_id=integration_id)
                # Could trigger reconnection logic here
                
        except Exception as e:
            self.logger.error("Health check error", integration_id=integration_id, error=str(e))
    
    def _update_global_stats(self):
        """Update global integration statistics"""
        try:
            with self._lock:
                # Calculate average response time
                total_requests = sum(m.total_requests for m in self.integration_metrics.values())
                if total_requests > 0:
                    total_response_time = sum(
                        m.average_response_time_ms * m.total_requests 
                        for m in self.integration_metrics.values()
                    )
                    self.integration_stats['average_response_time_ms'] = total_response_time / total_requests
                
                # Calculate uptime percentage
                connected_count = sum(1 for status in self.integration_status.values() 
                                    if status == IntegrationStatus.CONNECTED)
                total_active = self.integration_stats['active_integrations']
                
                if total_active > 0:
                    self.integration_stats['uptime_percentage'] = (connected_count / total_active) * 100
                
        except Exception as e:
            self.logger.error("Global stats update failed", error=str(e))
    
    def get_integration_status(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get integration status"""
        if integration_id not in self.integrations:
            return None
        
        config = self.integrations[integration_id]
        metrics = self.integration_metrics[integration_id]
        status = self.integration_status[integration_id]
        
        return {
            'integration_id': integration_id,
            'integration_name': config.integration_name,
            'integration_type': config.integration_type.value,
            'protocol': config.protocol.value,
            'status': status.value,
            'endpoint': config.endpoint,
            'total_requests': metrics.total_requests,
            'successful_requests': metrics.successful_requests,
            'failed_requests': metrics.failed_requests,
            'error_rate': metrics.error_rate,
            'average_response_time_ms': metrics.average_response_time_ms,
            'last_success_time': metrics.last_success_time,
            'enabled': config.enabled
        }
    
    def list_integrations(self) -> List[Dict[str, Any]]:
        """List all integrations"""
        integrations = []
        
        for integration_id in self.integrations.keys():
            integration_info = self.get_integration_status(integration_id)
            if integration_info:
                integrations.append(integration_info)
        
        return sorted(integrations, key=lambda x: x['integration_name'])
    
    def get_integration_events(self, integration_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get integration events"""
        events = []
        
        filtered_events = self.integration_events
        if integration_id:
            filtered_events = [e for e in self.integration_events if e.integration_id == integration_id]
        
        # Sort by timestamp (newest first)
        sorted_events = sorted(filtered_events, key=lambda x: x.timestamp, reverse=True)
        
        for event in sorted_events[:limit]:
            events.append({
                'event_id': event.event_id,
                'integration_id': event.integration_id,
                'event_type': event.event_type,
                'event_data': event.event_data,
                'timestamp': event.timestamp,
                'processed': event.processed
            })
        
        return events
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration manager statistics"""
        with self._lock:
            return {
                'health_monitoring_active': self.health_check_active,
                'max_events_history': self.max_events_history,
                'default_timeout': self.default_timeout,
                'connection_pool_size': self.connection_pool_size,
                'total_events': len(self.integration_events),
                'event_handlers_count': len(self.event_handlers),
                'supported_types': [t.value for t in IntegrationType],
                'supported_protocols': [p.value for p in ConnectionProtocol],
                'stats': self.integration_stats.copy()
            }
