"""
Metrics Collector for Orion Vision Core

This module provides comprehensive system metrics collection and monitoring.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.2 - Advanced Features & Enhanced Capabilities
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

from ...agent.core.agent_logger import AgentLogger


class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class MetricLevel(Enum):
    """Metric importance level"""
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


@dataclass
class Metric:
    """Individual metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    level: MetricLevel = MetricLevel.INFO
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate metric after initialization"""
        if not self.name:
            raise ValueError("Metric name cannot be empty")
        if not isinstance(self.value, (int, float)):
            raise ValueError("Metric value must be numeric")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'level': self.level.value,
            'timestamp': self.timestamp,
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metric':
        """Create metric from dictionary"""
        return cls(
            name=data['name'],
            value=data['value'],
            metric_type=MetricType(data['type']),
            level=MetricLevel(data['level']),
            timestamp=data.get('timestamp', time.time()),
            tags=data.get('tags', {}),
            metadata=data.get('metadata', {})
        )


class MetricsCollector:
    """
    Comprehensive metrics collection system
    
    Collects system, application, and custom metrics with real-time monitoring.
    """
    
    def __init__(self, logger: Optional[AgentLogger] = None):
        """Initialize metrics collector"""
        self.logger = logger or AgentLogger("metrics_collector")
        
        # Metric storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.metric_handlers: Dict[str, Callable] = {}
        self.aggregated_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Collection configuration
        self.collection_interval = 1.0  # seconds
        self.retention_period = 3600.0  # 1 hour
        self.max_metrics_per_type = 1000
        
        # Collection state
        self.collecting = False
        self.collection_thread = None
        
        # System metrics
        self.system_metrics_enabled = True
        self.custom_metrics_enabled = True
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.collector_stats = {
            'total_metrics_collected': 0,
            'metrics_per_second': 0.0,
            'collection_errors': 0,
            'last_collection_time': None,
            'active_metric_types': 0
        }
        
        self.logger.info("Metrics Collector initialized")
    
    def start_collection(self):
        """Start metrics collection"""
        if self.collecting:
            self.logger.warning("Metrics collection already running")
            return
        
        self.collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        
        self.logger.info("Metrics collection started", interval=self.collection_interval)
    
    def stop_collection(self):
        """Stop metrics collection"""
        if not self.collecting:
            self.logger.debug("Metrics collection not running")
            return
        
        self.collecting = False
        
        if self.collection_thread:
            self.collection_thread.join(timeout=5.0)
        
        self.logger.info("Metrics collection stopped")
    
    def collect_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                      level: MetricLevel = MetricLevel.INFO, tags: Optional[Dict[str, str]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Collect a single metric"""
        try:
            with self._lock:
                metric = Metric(
                    name=name,
                    value=value,
                    metric_type=metric_type,
                    level=level,
                    tags=tags or {},
                    metadata=metadata or {}
                )
                
                # Store metric
                self.metrics[name].append(metric)
                
                # Update statistics
                self.collector_stats['total_metrics_collected'] += 1
                self.collector_stats['last_collection_time'] = time.time()
                
                # Call metric handler if registered
                if name in self.metric_handlers:
                    try:
                        self.metric_handlers[name](metric)
                    except Exception as e:
                        self.logger.error("Metric handler failed", metric_name=name, error=str(e))
                
                # Update aggregated metrics
                self._update_aggregated_metrics(name, value, metric_type)
                
                self.logger.debug(
                    "Metric collected",
                    metric_name=name,
                    value=value,
                    type=metric_type.value,
                    level=level.value
                )
                
                return True
                
        except Exception as e:
            self.collector_stats['collection_errors'] += 1
            self.logger.error("Failed to collect metric", metric_name=name, error=str(e))
            return False
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            memory_available_mb = memory.available / 1024 / 1024
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used_gb = disk.used / 1024 / 1024 / 1024
            disk_free_gb = disk.free / 1024 / 1024 / 1024
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                bytes_sent = network.bytes_sent
                bytes_recv = network.bytes_recv
            except:
                bytes_sent = bytes_recv = 0
            
            # Process metrics
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / 1024 / 1024
            process_cpu_percent = process.cpu_percent()
            
            system_metrics = {
                'system.cpu.percent': cpu_percent,
                'system.cpu.count': cpu_count,
                'system.memory.percent': memory_percent,
                'system.memory.used_mb': memory_used_mb,
                'system.memory.available_mb': memory_available_mb,
                'system.disk.percent': disk_percent,
                'system.disk.used_gb': disk_used_gb,
                'system.disk.free_gb': disk_free_gb,
                'system.network.bytes_sent': bytes_sent,
                'system.network.bytes_recv': bytes_recv,
                'process.memory.mb': process_memory_mb,
                'process.cpu.percent': process_cpu_percent
            }
            
            # Collect all system metrics
            for metric_name, value in system_metrics.items():
                self.collect_metric(
                    name=metric_name,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    tags={'source': 'system'}
                )
            
            return system_metrics
            
        except Exception as e:
            self.logger.error("Failed to collect system metrics", error=str(e))
            return {}
    
    def register_metric_handler(self, metric_name: str, handler: Callable[[Metric], None]):
        """Register a handler for specific metric"""
        self.metric_handlers[metric_name] = handler
        
        self.logger.info(
            "Metric handler registered",
            metric_name=metric_name,
            handler_name=handler.__name__
        )
    
    def get_metrics(self, metric_name: Optional[str] = None, 
                   since: Optional[float] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get collected metrics"""
        with self._lock:
            if metric_name:
                # Get specific metric
                if metric_name not in self.metrics:
                    return {}
                
                metrics_list = list(self.metrics[metric_name])
                if since:
                    metrics_list = [m for m in metrics_list if m.timestamp >= since]
                
                return {metric_name: [m.to_dict() for m in metrics_list]}
            
            else:
                # Get all metrics
                result = {}
                for name, metrics_deque in self.metrics.items():
                    metrics_list = list(metrics_deque)
                    if since:
                        metrics_list = [m for m in metrics_list if m.timestamp >= since]
                    
                    result[name] = [m.to_dict() for m in metrics_list]
                
                return result
    
    def get_aggregated_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get aggregated metrics (avg, min, max, etc.)"""
        with self._lock:
            return dict(self.aggregated_metrics)
    
    def get_latest_metrics(self) -> Dict[str, float]:
        """Get latest value for each metric"""
        with self._lock:
            latest = {}
            for name, metrics_deque in self.metrics.items():
                if metrics_deque:
                    latest[name] = metrics_deque[-1].value
            return latest
    
    def clear_metrics(self, metric_name: Optional[str] = None):
        """Clear collected metrics"""
        with self._lock:
            if metric_name:
                if metric_name in self.metrics:
                    self.metrics[metric_name].clear()
                    if metric_name in self.aggregated_metrics:
                        del self.aggregated_metrics[metric_name]
            else:
                self.metrics.clear()
                self.aggregated_metrics.clear()
        
        self.logger.info("Metrics cleared", metric_name=metric_name or "all")
    
    def _collection_loop(self):
        """Main collection loop"""
        last_collection = time.time()
        
        while self.collecting:
            try:
                current_time = time.time()
                
                # Collect system metrics if enabled
                if self.system_metrics_enabled:
                    self.collect_system_metrics()
                
                # Calculate metrics per second
                time_diff = current_time - last_collection
                if time_diff > 0:
                    self.collector_stats['metrics_per_second'] = (
                        self.collector_stats['total_metrics_collected'] / time_diff
                    )
                
                # Update active metric types count
                self.collector_stats['active_metric_types'] = len(self.metrics)
                
                # Clean old metrics
                self._cleanup_old_metrics()
                
                last_collection = current_time
                
                # Sleep until next collection
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.collector_stats['collection_errors'] += 1
                self.logger.error("Collection loop error", error=str(e))
                time.sleep(1.0)  # Error recovery delay
    
    def _update_aggregated_metrics(self, name: str, value: float, metric_type: MetricType):
        """Update aggregated metrics for a metric name"""
        if name not in self.aggregated_metrics:
            self.aggregated_metrics[name] = {
                'count': 0,
                'sum': 0.0,
                'min': float('inf'),
                'max': float('-inf'),
                'avg': 0.0
            }
        
        agg = self.aggregated_metrics[name]
        agg['count'] += 1
        agg['sum'] += value
        agg['min'] = min(agg['min'], value)
        agg['max'] = max(agg['max'], value)
        agg['avg'] = agg['sum'] / agg['count']
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics based on retention period"""
        current_time = time.time()
        cutoff_time = current_time - self.retention_period
        
        with self._lock:
            for name, metrics_deque in self.metrics.items():
                # Remove old metrics
                while metrics_deque and metrics_deque[0].timestamp < cutoff_time:
                    metrics_deque.popleft()
    
    def get_collector_stats(self) -> Dict[str, Any]:
        """Get collector statistics"""
        with self._lock:
            return {
                'collecting': self.collecting,
                'collection_interval': self.collection_interval,
                'retention_period': self.retention_period,
                'total_metric_names': len(self.metrics),
                'total_metrics_stored': sum(len(deque) for deque in self.metrics.values()),
                'system_metrics_enabled': self.system_metrics_enabled,
                'custom_metrics_enabled': self.custom_metrics_enabled,
                'stats': self.collector_stats.copy()
            }
