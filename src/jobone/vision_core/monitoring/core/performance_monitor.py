"""
Performance Monitor for Orion Vision Core

This module provides comprehensive performance tracking and analysis.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.2 - Advanced Features & Enhanced Capabilities
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
from contextlib import contextmanager

from ...agent.core.agent_logger import AgentLogger
from .metrics_collector import MetricsCollector, MetricType, MetricLevel


class PerformanceLevel(Enum):
    """Performance level enumeration"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    baseline: float
    threshold_warning: float
    threshold_critical: float
    unit: str = "ms"
    timestamp: float = field(default_factory=time.time)
    
    def get_performance_level(self) -> PerformanceLevel:
        """Determine performance level based on thresholds"""
        if self.value <= self.baseline * 0.8:
            return PerformanceLevel.EXCELLENT
        elif self.value <= self.baseline:
            return PerformanceLevel.GOOD
        elif self.value <= self.threshold_warning:
            return PerformanceLevel.AVERAGE
        elif self.value <= self.threshold_critical:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL
    
    def get_performance_score(self) -> float:
        """Calculate performance score (0-100)"""
        if self.value <= self.baseline:
            return 100.0
        elif self.value <= self.threshold_warning:
            return 80.0 - ((self.value - self.baseline) / (self.threshold_warning - self.baseline)) * 30.0
        elif self.value <= self.threshold_critical:
            return 50.0 - ((self.value - self.threshold_warning) / (self.threshold_critical - self.threshold_warning)) * 30.0
        else:
            return max(0.0, 20.0 - ((self.value - self.threshold_critical) / self.threshold_critical) * 20.0)


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system
    
    Tracks performance metrics, analyzes trends, and provides optimization insights.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None, 
                 logger: Optional[AgentLogger] = None):
        """Initialize performance monitor"""
        self.logger = logger or AgentLogger("performance_monitor")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Performance tracking
        self.performance_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.baselines: Dict[str, float] = {}
        self.thresholds: Dict[str, Dict[str, float]] = {}
        
        # Timing contexts
        self.active_timers: Dict[str, float] = {}
        
        # Performance analysis
        self.performance_trends: Dict[str, List[float]] = defaultdict(list)
        self.performance_alerts: List[Dict[str, Any]] = []
        
        # Configuration
        self.monitoring_enabled = True
        self.trend_analysis_window = 100  # Number of samples for trend analysis
        self.alert_cooldown = 300.0  # 5 minutes cooldown between same alerts
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.monitor_stats = {
            'total_measurements': 0,
            'performance_alerts_generated': 0,
            'average_performance_score': 0.0,
            'monitored_operations': 0,
            'last_analysis_time': None
        }
        
        # Default performance baselines (in milliseconds)
        self._setup_default_baselines()
        
        self.logger.info("Performance Monitor initialized")
    
    def _setup_default_baselines(self):
        """Setup default performance baselines"""
        default_baselines = {
            'agent.startup_time': 500.0,  # 500ms
            'agent.shutdown_time': 200.0,  # 200ms
            'task.execution_time': 1000.0,  # 1 second
            'task.scheduling_time': 10.0,  # 10ms
            'communication.message_send_time': 50.0,  # 50ms
            'communication.message_receive_time': 30.0,  # 30ms
            'workflow.step_execution_time': 2000.0,  # 2 seconds
            'database.query_time': 100.0,  # 100ms
            'api.response_time': 200.0,  # 200ms
            'system.memory_allocation_time': 5.0,  # 5ms
        }
        
        for operation, baseline in default_baselines.items():
            self.set_baseline(operation, baseline)
    
    def set_baseline(self, operation: str, baseline: float, 
                    warning_multiplier: float = 2.0, critical_multiplier: float = 5.0):
        """Set performance baseline for an operation"""
        with self._lock:
            self.baselines[operation] = baseline
            self.thresholds[operation] = {
                'warning': baseline * warning_multiplier,
                'critical': baseline * critical_multiplier
            }
        
        self.logger.info(
            "Performance baseline set",
            operation=operation,
            baseline=baseline,
            warning_threshold=baseline * warning_multiplier,
            critical_threshold=baseline * critical_multiplier
        )
    
    @contextmanager
    def measure_performance(self, operation: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for measuring operation performance"""
        start_time = time.time()
        
        try:
            yield
        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000.0
            
            self.record_performance(operation, duration_ms, tags)
    
    def record_performance(self, operation: str, duration_ms: float, 
                          tags: Optional[Dict[str, str]] = None):
        """Record performance measurement"""
        try:
            with self._lock:
                # Get baseline and thresholds
                baseline = self.baselines.get(operation, duration_ms)
                thresholds = self.thresholds.get(operation, {
                    'warning': baseline * 2.0,
                    'critical': baseline * 5.0
                })
                
                # Create performance metric
                perf_metric = PerformanceMetric(
                    name=operation,
                    value=duration_ms,
                    baseline=baseline,
                    threshold_warning=thresholds['warning'],
                    threshold_critical=thresholds['critical']
                )
                
                # Store performance metric
                self.performance_metrics[operation].append(perf_metric)
                
                # Update statistics
                self.monitor_stats['total_measurements'] += 1
                self.monitor_stats['monitored_operations'] = len(self.performance_metrics)
                
                # Collect metric for metrics collector
                self.metrics_collector.collect_metric(
                    name=f"performance.{operation}",
                    value=duration_ms,
                    metric_type=MetricType.TIMER,
                    level=self._get_metric_level(perf_metric.get_performance_level()),
                    tags=tags or {},
                    metadata={
                        'baseline': baseline,
                        'performance_level': perf_metric.get_performance_level().value,
                        'performance_score': perf_metric.get_performance_score()
                    }
                )
                
                # Update trend analysis
                self._update_trend_analysis(operation, duration_ms)
                
                # Check for performance alerts
                self._check_performance_alerts(perf_metric, tags)
                
                # Update average performance score
                self._update_average_performance_score()
                
                self.logger.debug(
                    "Performance recorded",
                    operation=operation,
                    duration_ms=f"{duration_ms:.2f}",
                    performance_level=perf_metric.get_performance_level().value,
                    performance_score=f"{perf_metric.get_performance_score():.1f}"
                )
                
        except Exception as e:
            self.logger.error("Failed to record performance", operation=operation, error=str(e))
    
    def start_timer(self, operation: str) -> str:
        """Start a named timer"""
        timer_id = f"{operation}_{int(time.time() * 1000000)}"
        self.active_timers[timer_id] = time.time()
        
        self.logger.debug("Timer started", operation=operation, timer_id=timer_id)
        return timer_id
    
    def stop_timer(self, timer_id: str, tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Stop a named timer and record performance"""
        if timer_id not in self.active_timers:
            self.logger.warning("Timer not found", timer_id=timer_id)
            return None
        
        start_time = self.active_timers.pop(timer_id)
        duration_ms = (time.time() - start_time) * 1000.0
        
        # Extract operation name from timer_id
        operation = timer_id.rsplit('_', 1)[0]
        self.record_performance(operation, duration_ms, tags)
        
        self.logger.debug("Timer stopped", timer_id=timer_id, duration_ms=f"{duration_ms:.2f}")
        return duration_ms
    
    def get_performance_summary(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary for operation(s)"""
        with self._lock:
            if operation:
                # Get summary for specific operation
                if operation not in self.performance_metrics:
                    return {}
                
                metrics = list(self.performance_metrics[operation])
                return self._calculate_operation_summary(operation, metrics)
            
            else:
                # Get summary for all operations
                summary = {}
                for op_name, metrics_deque in self.performance_metrics.items():
                    metrics = list(metrics_deque)
                    summary[op_name] = self._calculate_operation_summary(op_name, metrics)
                
                return summary
    
    def get_performance_trends(self, operation: str, window_size: Optional[int] = None) -> Dict[str, Any]:
        """Get performance trends for an operation"""
        window_size = window_size or self.trend_analysis_window
        
        with self._lock:
            if operation not in self.performance_trends:
                return {}
            
            trends = self.performance_trends[operation][-window_size:]
            
            if len(trends) < 2:
                return {'trend': 'insufficient_data', 'samples': len(trends)}
            
            # Calculate trend direction
            recent_avg = sum(trends[-10:]) / min(10, len(trends))
            older_avg = sum(trends[:10]) / min(10, len(trends))
            
            if recent_avg < older_avg * 0.9:
                trend_direction = 'improving'
            elif recent_avg > older_avg * 1.1:
                trend_direction = 'degrading'
            else:
                trend_direction = 'stable'
            
            return {
                'trend': trend_direction,
                'recent_average': recent_avg,
                'older_average': older_avg,
                'change_percent': ((recent_avg - older_avg) / older_avg) * 100,
                'samples': len(trends),
                'min_value': min(trends),
                'max_value': max(trends)
            }
    
    def get_performance_alerts(self, since: Optional[float] = None) -> List[Dict[str, Any]]:
        """Get performance alerts"""
        with self._lock:
            if since:
                return [alert for alert in self.performance_alerts if alert['timestamp'] >= since]
            else:
                return list(self.performance_alerts)
    
    def _calculate_operation_summary(self, operation: str, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate summary statistics for an operation"""
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        scores = [m.get_performance_score() for m in metrics]
        levels = [m.get_performance_level().value for m in metrics]
        
        return {
            'operation': operation,
            'sample_count': len(metrics),
            'average_duration': sum(values) / len(values),
            'min_duration': min(values),
            'max_duration': max(values),
            'average_score': sum(scores) / len(scores),
            'baseline': metrics[0].baseline,
            'warning_threshold': metrics[0].threshold_warning,
            'critical_threshold': metrics[0].threshold_critical,
            'performance_distribution': {
                level: levels.count(level) for level in set(levels)
            },
            'last_measurement': metrics[-1].timestamp
        }
    
    def _update_trend_analysis(self, operation: str, duration_ms: float):
        """Update trend analysis for an operation"""
        trends = self.performance_trends[operation]
        trends.append(duration_ms)
        
        # Keep only recent samples
        if len(trends) > self.trend_analysis_window:
            trends.pop(0)
    
    def _check_performance_alerts(self, metric: PerformanceMetric, tags: Optional[Dict[str, str]]):
        """Check if performance alert should be generated"""
        level = metric.get_performance_level()
        
        if level in [PerformanceLevel.POOR, PerformanceLevel.CRITICAL]:
            # Check cooldown
            current_time = time.time()
            recent_alerts = [
                alert for alert in self.performance_alerts
                if alert['operation'] == metric.name and 
                   current_time - alert['timestamp'] < self.alert_cooldown
            ]
            
            if not recent_alerts:
                alert = {
                    'operation': metric.name,
                    'level': level.value,
                    'duration_ms': metric.value,
                    'baseline': metric.baseline,
                    'performance_score': metric.get_performance_score(),
                    'timestamp': current_time,
                    'tags': tags or {}
                }
                
                self.performance_alerts.append(alert)
                self.monitor_stats['performance_alerts_generated'] += 1
                
                self.logger.warning(
                    "Performance alert generated",
                    operation=metric.name,
                    level=level.value,
                    duration_ms=f"{metric.value:.2f}",
                    baseline=f"{metric.baseline:.2f}",
                    performance_score=f"{metric.get_performance_score():.1f}"
                )
    
    def _update_average_performance_score(self):
        """Update average performance score across all operations"""
        with self._lock:
            total_score = 0.0
            total_count = 0
            
            for metrics_deque in self.performance_metrics.values():
                if metrics_deque:
                    latest_metric = metrics_deque[-1]
                    total_score += latest_metric.get_performance_score()
                    total_count += 1
            
            if total_count > 0:
                self.monitor_stats['average_performance_score'] = total_score / total_count
                self.monitor_stats['last_analysis_time'] = time.time()
    
    def _get_metric_level(self, performance_level: PerformanceLevel) -> MetricLevel:
        """Convert performance level to metric level"""
        mapping = {
            PerformanceLevel.EXCELLENT: MetricLevel.DEBUG,
            PerformanceLevel.GOOD: MetricLevel.INFO,
            PerformanceLevel.AVERAGE: MetricLevel.INFO,
            PerformanceLevel.POOR: MetricLevel.WARNING,
            PerformanceLevel.CRITICAL: MetricLevel.ERROR
        }
        return mapping.get(performance_level, MetricLevel.INFO)
    
    def get_monitor_stats(self) -> Dict[str, Any]:
        """Get performance monitor statistics"""
        with self._lock:
            return {
                'monitoring_enabled': self.monitoring_enabled,
                'active_timers': len(self.active_timers),
                'total_operations_monitored': len(self.performance_metrics),
                'total_performance_alerts': len(self.performance_alerts),
                'trend_analysis_window': self.trend_analysis_window,
                'alert_cooldown': self.alert_cooldown,
                'stats': self.monitor_stats.copy()
            }
