"""
📊 Monitoring & Observability - Q6.3 Implementation

Production monitoring, metrics collection, alerting, and observability
for Orion Vision Core systems

Author: Orion Vision Core Team
Based on: Q1-Q5 Foundation + Vision Integration + Q6.1-Q6.2 Production
Priority: HIGH - Production Monitoring
"""

import logging
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Callable
import threading
from collections import deque

# Metric Types
class MetricType(Enum):
    """Metrik türleri"""
    COUNTER = "counter"                             # Sayaç metrik
    GAUGE = "gauge"                                 # Anlık değer metrik
    HISTOGRAM = "histogram"                         # Histogram metrik
    SUMMARY = "summary"                             # Özet metrik

# Alert Severity Levels
class AlertSeverity(Enum):
    """Alert önem seviyeleri"""
    CRITICAL = "critical"                           # Kritik
    HIGH = "high"                                   # Yüksek
    MEDIUM = "medium"                               # Orta
    LOW = "low"                                     # Düşük
    INFO = "info"                                   # Bilgi

# System Components
class SystemComponent(Enum):
    """Sistem bileşenleri"""
    QUANTUM_CORE = "quantum_core"                   # Q1-Q5 Quantum systems
    VISION_PROCESSOR = "vision_processor"           # Vision computer access
    API_GATEWAY = "api_gateway"                     # API gateway
    DATABASE = "database"                           # Database systems
    CONTAINER_ORCHESTRATOR = "container_orchestrator" # K8s orchestrator
    CICD_PIPELINE = "cicd_pipeline"                 # CI/CD pipeline

@dataclass
class Metric:
    """
    Metric
    
    Sistem metriği tanımı ve değeri.
    """
    
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: MetricType = MetricType.GAUGE
    
    # Metric properties
    name: str = ""
    component: SystemComponent = SystemComponent.QUANTUM_CORE
    value: float = 0.0
    unit: str = ""
    
    # Labels and tags
    labels: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Temporal properties
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Metadata
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_prometheus_format(self) -> str:
        """Convert to Prometheus format"""
        labels_str = ""
        if self.labels:
            labels_list = [f'{k}="{v}"' for k, v in self.labels.items()]
            labels_str = "{" + ",".join(labels_list) + "}"
        
        return f"{self.name}{labels_str} {self.value} {int(self.timestamp.timestamp() * 1000)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'metric_id': self.metric_id,
            'metric_type': self.metric_type.value,
            'name': self.name,
            'component': self.component.value,
            'value': self.value,
            'unit': self.unit,
            'labels': self.labels,
            'tags': self.tags,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'metadata': self.metadata
        }

@dataclass
class Alert:
    """
    Alert
    
    Sistem uyarısı tanımı.
    """
    
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    severity: AlertSeverity = AlertSeverity.MEDIUM
    
    # Alert properties
    title: str = ""
    message: str = ""
    component: SystemComponent = SystemComponent.QUANTUM_CORE
    
    # Alert conditions
    metric_name: str = ""
    threshold_value: float = 0.0
    current_value: float = 0.0
    condition: str = ">"                            # >, <, ==, !=
    
    # Alert state
    active: bool = True
    acknowledged: bool = False
    resolved: bool = False
    
    # Temporal properties
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Notification
    notification_sent: bool = False
    notification_channels: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def acknowledge(self, user: str = "system"):
        """Acknowledge alert"""
        self.acknowledged = True
        self.acknowledged_at = datetime.now()
        self.metadata['acknowledged_by'] = user
    
    def resolve(self, user: str = "system"):
        """Resolve alert"""
        self.resolved = True
        self.resolved_at = datetime.now()
        self.active = False
        self.metadata['resolved_by'] = user
    
    def get_duration(self) -> float:
        """Get alert duration in seconds"""
        end_time = self.resolved_at or datetime.now()
        return (end_time - self.triggered_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'component': self.component.value,
            'metric_name': self.metric_name,
            'threshold_value': self.threshold_value,
            'current_value': self.current_value,
            'condition': self.condition,
            'active': self.active,
            'acknowledged': self.acknowledged,
            'resolved': self.resolved,
            'triggered_at': self.triggered_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'duration_seconds': self.get_duration(),
            'notification_sent': self.notification_sent,
            'notification_channels': self.notification_channels,
            'metadata': self.metadata
        }

@dataclass
class HealthCheck:
    """
    Health Check
    
    Sistem sağlık kontrolü.
    """
    
    check_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    component: SystemComponent = SystemComponent.QUANTUM_CORE
    
    # Health check properties
    name: str = ""
    endpoint: str = ""
    
    # Health status
    healthy: bool = True
    status_code: int = 200
    response_time: float = 0.0                      # Response time in seconds
    
    # Check configuration
    timeout: float = 5.0                            # Timeout in seconds
    interval: float = 30.0                          # Check interval in seconds
    
    # Temporal properties
    last_check: datetime = field(default_factory=datetime.now)
    next_check: datetime = field(default_factory=datetime.now)
    
    # Error information
    error_message: str = ""
    consecutive_failures: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_next_check(self):
        """Update next check time"""
        self.next_check = datetime.now() + timedelta(seconds=self.interval)
    
    def record_success(self, response_time: float):
        """Record successful health check"""
        self.healthy = True
        self.status_code = 200
        self.response_time = response_time
        self.error_message = ""
        self.consecutive_failures = 0
        self.last_check = datetime.now()
        self.update_next_check()
    
    def record_failure(self, error_message: str, status_code: int = 500):
        """Record failed health check"""
        self.healthy = False
        self.status_code = status_code
        self.error_message = error_message
        self.consecutive_failures += 1
        self.last_check = datetime.now()
        self.update_next_check()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'check_id': self.check_id,
            'component': self.component.value,
            'name': self.name,
            'endpoint': self.endpoint,
            'healthy': self.healthy,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'timeout': self.timeout,
            'interval': self.interval,
            'last_check': self.last_check.isoformat(),
            'next_check': self.next_check.isoformat(),
            'error_message': self.error_message,
            'consecutive_failures': self.consecutive_failures,
            'metadata': self.metadata
        }

class MonitoringSystem:
    """
    Monitoring System
    
    Production monitoring ve observability sistemi.
    """
    
    def __init__(self, 
                 system_name: str = "orion-vision-core",
                 metrics_retention_hours: int = 24):
        self.logger = logging.getLogger(__name__)
        self.system_name = system_name
        self.metrics_retention_hours = metrics_retention_hours
        
        # Metrics storage
        self.metrics: Dict[str, deque] = {}          # metric_name -> deque of metrics
        self.current_metrics: Dict[str, Metric] = {} # metric_name -> latest metric
        
        # Alerts
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: List[str] = []
        
        # Health checks
        self.health_checks: Dict[str, HealthCheck] = {}
        
        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.total_metrics_collected = 0
        self.total_alerts_triggered = 0
        self.total_health_checks = 0
        
        # Initialize default alert rules
        self._initialize_default_alert_rules()
        
        self.logger.info(f"📊 MonitoringSystem initialized - Q6.3 Implementation "
                        f"(system: {system_name}, retention: {metrics_retention_hours}h)")
    
    def _initialize_default_alert_rules(self):
        """Initialize default alert rules"""
        self.alert_rules = {
            'quantum_core_cpu_high': {
                'metric_name': 'quantum_core_cpu_usage',
                'condition': '>',
                'threshold': 80.0,
                'severity': AlertSeverity.HIGH,
                'title': 'Quantum Core High CPU Usage',
                'message': 'Quantum Core CPU usage is above 80%'
            },
            'vision_processor_memory_high': {
                'metric_name': 'vision_processor_memory_usage',
                'condition': '>',
                'threshold': 85.0,
                'severity': AlertSeverity.HIGH,
                'title': 'Vision Processor High Memory Usage',
                'message': 'Vision Processor memory usage is above 85%'
            },
            'api_gateway_response_time_high': {
                'metric_name': 'api_gateway_response_time',
                'condition': '>',
                'threshold': 2.0,
                'severity': AlertSeverity.MEDIUM,
                'title': 'API Gateway Slow Response',
                'message': 'API Gateway response time is above 2 seconds'
            },
            'health_check_failure': {
                'metric_name': 'health_check_failures',
                'condition': '>',
                'threshold': 3.0,
                'severity': AlertSeverity.CRITICAL,
                'title': 'Health Check Failures',
                'message': 'Multiple consecutive health check failures detected'
            }
        }
    
    def collect_metric(self, metric: Metric):
        """Collect system metric"""
        try:
            # Store metric
            if metric.name not in self.metrics:
                self.metrics[metric.name] = deque(maxlen=1000)  # Keep last 1000 metrics
            
            self.metrics[metric.name].append(metric)
            self.current_metrics[metric.name] = metric
            self.total_metrics_collected += 1
            
            # Check alert rules
            self._check_alert_rules(metric)
            
            # Clean old metrics
            self._cleanup_old_metrics()
            
            self.logger.debug(f"📊 Collected metric: {metric.name} = {metric.value} {metric.unit}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to collect metric: {e}")
    
    def _check_alert_rules(self, metric: Metric):
        """Check alert rules against metric"""
        for rule_name, rule in self.alert_rules.items():
            if rule['metric_name'] == metric.name:
                condition = rule['condition']
                threshold = rule['threshold']
                
                # Evaluate condition
                triggered = False
                if condition == '>' and metric.value > threshold:
                    triggered = True
                elif condition == '<' and metric.value < threshold:
                    triggered = True
                elif condition == '==' and metric.value == threshold:
                    triggered = True
                elif condition == '!=' and metric.value != threshold:
                    triggered = True
                
                if triggered:
                    self._trigger_alert(rule_name, rule, metric)
    
    def _trigger_alert(self, rule_name: str, rule: Dict[str, Any], metric: Metric):
        """Trigger alert based on rule"""
        try:
            # Check if alert already exists and is active
            existing_alert_id = None
            for alert_id, alert in self.alerts.items():
                if (alert.metric_name == rule['metric_name'] and 
                    alert.active and not alert.resolved):
                    existing_alert_id = alert_id
                    break
            
            if existing_alert_id:
                # Update existing alert
                alert = self.alerts[existing_alert_id]
                alert.current_value = metric.value
                return
            
            # Create new alert
            alert = Alert(
                severity=rule['severity'],
                title=rule['title'],
                message=rule['message'],
                component=metric.component,
                metric_name=rule['metric_name'],
                threshold_value=rule['threshold'],
                current_value=metric.value,
                condition=rule['condition']
            )
            
            self.alerts[alert.alert_id] = alert
            self.active_alerts.append(alert.alert_id)
            self.total_alerts_triggered += 1
            
            self.logger.warning(f"📊 Alert triggered: {alert.title} "
                              f"(value: {metric.value}, threshold: {rule['threshold']})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to trigger alert: {e}")
    
    def add_health_check(self, health_check: HealthCheck):
        """Add health check"""
        self.health_checks[health_check.check_id] = health_check
        self.logger.info(f"📊 Added health check: {health_check.name} "
                        f"({health_check.component.value})")
    
    def perform_health_checks(self):
        """Perform all health checks"""
        for check_id, health_check in self.health_checks.items():
            if datetime.now() >= health_check.next_check:
                self._perform_single_health_check(health_check)
    
    def _perform_single_health_check(self, health_check: HealthCheck):
        """Perform single health check"""
        try:
            start_time = time.time()
            
            # Mock health check (in real implementation, this would make HTTP request)
            if health_check.component == SystemComponent.QUANTUM_CORE:
                # Simulate quantum core health check
                healthy = True
                response_time = 0.1
            elif health_check.component == SystemComponent.VISION_PROCESSOR:
                # Simulate vision processor health check
                healthy = True
                response_time = 0.2
            else:
                # Default health check
                healthy = True
                response_time = 0.05
            
            if healthy:
                health_check.record_success(response_time)
            else:
                health_check.record_failure("Service unavailable", 503)
            
            self.total_health_checks += 1
            
            # Collect health check metric
            health_metric = Metric(
                metric_type=MetricType.GAUGE,
                name=f"{health_check.component.value}_health_status",
                component=health_check.component,
                value=1.0 if healthy else 0.0,
                unit="boolean",
                labels={
                    'check_name': health_check.name,
                    'endpoint': health_check.endpoint
                }
            )
            
            self.collect_metric(health_metric)
            
        except Exception as e:
            health_check.record_failure(str(e))
            self.logger.error(f"❌ Health check failed: {health_check.name} - {e}")
    
    def start_monitoring(self):
        """Start monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("📊 Monitoring system started")
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        
        self.logger.info("📊 Monitoring system stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform health checks
                self.perform_health_checks()
                
                # Generate system metrics
                self._generate_system_metrics()
                
                # Sleep for monitoring interval
                time.sleep(10)  # 10 second monitoring interval
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(5)
    
    def _generate_system_metrics(self):
        """Generate system metrics"""
        try:
            # Generate mock system metrics
            import random
            
            # Quantum Core metrics
            quantum_cpu = Metric(
                metric_type=MetricType.GAUGE,
                name="quantum_core_cpu_usage",
                component=SystemComponent.QUANTUM_CORE,
                value=random.uniform(20, 90),
                unit="percent"
            )
            self.collect_metric(quantum_cpu)
            
            # Vision Processor metrics
            vision_memory = Metric(
                metric_type=MetricType.GAUGE,
                name="vision_processor_memory_usage",
                component=SystemComponent.VISION_PROCESSOR,
                value=random.uniform(30, 95),
                unit="percent"
            )
            self.collect_metric(vision_memory)
            
            # API Gateway metrics
            api_response_time = Metric(
                metric_type=MetricType.HISTOGRAM,
                name="api_gateway_response_time",
                component=SystemComponent.API_GATEWAY,
                value=random.uniform(0.1, 3.0),
                unit="seconds"
            )
            self.collect_metric(api_response_time)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate system metrics: {e}")
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics based on retention policy"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
            
            for metric_name, metric_deque in self.metrics.items():
                # Remove old metrics
                while metric_deque and metric_deque[0].timestamp < cutoff_time:
                    metric_deque.popleft()
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup old metrics: {e}")
    
    def get_metrics_summary(self, component: Optional[SystemComponent] = None) -> Dict[str, Any]:
        """Get metrics summary"""
        summary = {
            'total_metrics': len(self.current_metrics),
            'metrics_by_component': {},
            'latest_values': {}
        }
        
        # Group metrics by component
        for metric_name, metric in self.current_metrics.items():
            if component and metric.component != component:
                continue
                
            comp_name = metric.component.value
            if comp_name not in summary['metrics_by_component']:
                summary['metrics_by_component'][comp_name] = []
            
            summary['metrics_by_component'][comp_name].append({
                'name': metric.name,
                'value': metric.value,
                'unit': metric.unit,
                'timestamp': metric.timestamp.isoformat()
            })
            
            summary['latest_values'][metric_name] = metric.value
        
        return summary
    
    def get_alerts_summary(self) -> Dict[str, Any]:
        """Get alerts summary"""
        active_alerts = [alert for alert in self.alerts.values() if alert.active]
        resolved_alerts = [alert for alert in self.alerts.values() if alert.resolved]
        
        # Group by severity
        alerts_by_severity = {}
        for alert in active_alerts:
            severity = alert.severity.value
            if severity not in alerts_by_severity:
                alerts_by_severity[severity] = 0
            alerts_by_severity[severity] += 1
        
        return {
            'total_alerts': len(self.alerts),
            'active_alerts': len(active_alerts),
            'resolved_alerts': len(resolved_alerts),
            'alerts_by_severity': alerts_by_severity,
            'recent_alerts': [alert.to_dict() for alert in list(self.alerts.values())[-5:]]
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health checks summary"""
        healthy_checks = [check for check in self.health_checks.values() if check.healthy]
        unhealthy_checks = [check for check in self.health_checks.values() if not check.healthy]
        
        # Average response time
        total_response_time = sum(check.response_time for check in self.health_checks.values())
        avg_response_time = total_response_time / len(self.health_checks) if self.health_checks else 0.0
        
        return {
            'total_health_checks': len(self.health_checks),
            'healthy_checks': len(healthy_checks),
            'unhealthy_checks': len(unhealthy_checks),
            'average_response_time': avg_response_time,
            'health_status': 'healthy' if len(unhealthy_checks) == 0 else 'degraded'
        }
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get monitoring system statistics"""
        return {
            'system_name': self.system_name,
            'monitoring_active': self.monitoring_active,
            'total_metrics_collected': self.total_metrics_collected,
            'total_alerts_triggered': self.total_alerts_triggered,
            'total_health_checks': self.total_health_checks,
            'metrics_retention_hours': self.metrics_retention_hours,
            'current_metrics_count': len(self.current_metrics),
            'active_alerts_count': len(self.active_alerts),
            'health_checks_count': len(self.health_checks),
            'alert_rules_count': len(self.alert_rules)
        }

# Utility functions
def create_monitoring_system(system_name: str = "orion-vision-core",
                            retention_hours: int = 24) -> MonitoringSystem:
    """Create Monitoring System"""
    return MonitoringSystem(system_name, retention_hours)

def test_monitoring_observability():
    """Test Monitoring & Observability system"""
    print("📊 Testing Monitoring & Observability...")
    
    # Create monitoring system
    monitoring = create_monitoring_system()
    print("✅ Monitoring System created")
    
    # Add health checks
    quantum_health = HealthCheck(
        component=SystemComponent.QUANTUM_CORE,
        name="quantum_core_health",
        endpoint="/health",
        interval=30.0
    )
    
    vision_health = HealthCheck(
        component=SystemComponent.VISION_PROCESSOR,
        name="vision_processor_health",
        endpoint="/health",
        interval=30.0
    )
    
    monitoring.add_health_check(quantum_health)
    monitoring.add_health_check(vision_health)
    print("✅ Health checks added")
    
    # Collect some metrics
    test_metrics = [
        Metric(
            metric_type=MetricType.GAUGE,
            name="quantum_core_cpu_usage",
            component=SystemComponent.QUANTUM_CORE,
            value=75.5,
            unit="percent"
        ),
        Metric(
            metric_type=MetricType.GAUGE,
            name="vision_processor_memory_usage",
            component=SystemComponent.VISION_PROCESSOR,
            value=82.3,
            unit="percent"
        ),
        Metric(
            metric_type=MetricType.HISTOGRAM,
            name="api_gateway_response_time",
            component=SystemComponent.API_GATEWAY,
            value=1.2,
            unit="seconds"
        )
    ]
    
    for metric in test_metrics:
        monitoring.collect_metric(metric)
    
    print(f"✅ Collected {len(test_metrics)} metrics")
    
    # Perform health checks
    monitoring.perform_health_checks()
    print("✅ Health checks performed")
    
    # Start monitoring for a short time
    monitoring.start_monitoring()
    time.sleep(2)  # Let it run for 2 seconds
    monitoring.stop_monitoring()
    print("✅ Monitoring system tested")
    
    # Get summaries
    metrics_summary = monitoring.get_metrics_summary()
    alerts_summary = monitoring.get_alerts_summary()
    health_summary = monitoring.get_health_summary()
    stats = monitoring.get_monitoring_statistics()
    
    print(f"✅ Monitoring statistics:")
    print(f"    - Total metrics collected: {stats['total_metrics_collected']}")
    print(f"    - Current metrics: {stats['current_metrics_count']}")
    print(f"    - Active alerts: {stats['active_alerts_count']}")
    print(f"    - Health checks: {stats['health_checks_count']}")
    print(f"    - Health status: {health_summary['health_status']}")
    print(f"    - Average response time: {health_summary['average_response_time']:.3f}s")
    
    print("🚀 Monitoring & Observability test completed!")

if __name__ == "__main__":
    test_monitoring_observability()
