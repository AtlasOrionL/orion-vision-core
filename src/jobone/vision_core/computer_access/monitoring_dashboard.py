#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard - Live system monitoring with AI insights
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    response_time: float
    success_rate: float
    active_tasks: int
    total_operations: int
    errors_count: int

@dataclass
class ComponentStatus:
    """Individual component status"""
    name: str
    status: str  # 'online', 'offline', 'degraded'
    response_time: float
    last_activity: float
    error_count: int
    health_score: float

class MetricsCollector:
    """Collects system metrics in real-time"""
    
    def __init__(self):
        self.metrics_history = []
        self.collection_interval = 5.0  # seconds
        self.max_history = 100  # Keep last 100 metrics
        self.collecting = False
        self.collection_thread = None
        
        logger.info("📊 Metrics Collector initialized")
    
    def start_collection(self, computer_access_manager):
        """Start metrics collection"""
        if self.collecting:
            return
        
        self.collecting = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            args=(computer_access_manager,),
            daemon=True
        )
        self.collection_thread.start()
        
        logger.info("📈 Metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=2.0)
        
        logger.info("📉 Metrics collection stopped")
    
    def _collection_loop(self, computer_access_manager):
        """Main collection loop"""
        while self.collecting:
            try:
                metrics = self._collect_metrics(computer_access_manager)
                self.metrics_history.append(metrics)
                
                # Keep only recent metrics
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                time.sleep(1.0)
    
    def _collect_metrics(self, manager) -> SystemMetrics:
        """Collect current system metrics"""
        status = manager.get_status()
        
        # Simulate some metrics (in production, these would be real)
        import random
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_usage=random.uniform(10, 40),
            memory_usage=random.uniform(20, 60),
            response_time=random.uniform(0.01, 0.5),
            success_rate=status.get('success_rate', 100),
            active_tasks=status.get('active_tasks', 0),
            total_operations=status.get('total_tasks', 0),
            errors_count=status.get('failed_tasks', 0)
        )
    
    def get_latest_metrics(self) -> Optional[SystemMetrics]:
        """Get latest metrics"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self, count: int = 20) -> List[SystemMetrics]:
        """Get recent metrics history"""
        return self.metrics_history[-count:] if self.metrics_history else []

class ComponentMonitor:
    """Monitors individual component health"""
    
    def __init__(self):
        self.component_status = {}
        self.monitoring = False
        self.monitor_thread = None
        
        logger.info("🔍 Component Monitor initialized")
    
    def start_monitoring(self, computer_access_manager):
        """Start component monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(computer_access_manager,),
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info("🔍 Component monitoring started")
    
    def stop_monitoring(self):
        """Stop component monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        logger.info("🔍 Component monitoring stopped")
    
    def _monitoring_loop(self, computer_access_manager):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._check_components(computer_access_manager)
                time.sleep(3.0)  # Check every 3 seconds
                
            except Exception as e:
                logger.error(f"Component monitoring error: {e}")
                time.sleep(1.0)
    
    def _check_components(self, manager):
        """Check all component statuses"""
        components = ['terminal', 'mouse', 'keyboard', 'screen', 'scenarios']
        
        for comp_name in components:
            try:
                component = getattr(manager, comp_name, None)
                if component:
                    status = self._check_component_health(component)
                    self.component_status[comp_name] = ComponentStatus(
                        name=comp_name,
                        status=status['status'],
                        response_time=status['response_time'],
                        last_activity=time.time(),
                        error_count=status['error_count'],
                        health_score=status['health_score']
                    )
                else:
                    self.component_status[comp_name] = ComponentStatus(
                        name=comp_name,
                        status='offline',
                        response_time=0.0,
                        last_activity=0.0,
                        error_count=0,
                        health_score=0.0
                    )
                    
            except Exception as e:
                logger.error(f"Error checking component {comp_name}: {e}")
    
    def _check_component_health(self, component) -> Dict[str, Any]:
        """Check individual component health"""
        start_time = time.time()
        
        try:
            # Check if component is ready
            is_ready = component.is_ready() if hasattr(component, 'is_ready') else True
            response_time = time.time() - start_time
            
            # Get component status if available
            status_info = component.get_status() if hasattr(component, 'get_status') else {}
            
            return {
                'status': 'online' if is_ready else 'degraded',
                'response_time': response_time,
                'error_count': status_info.get('failed_operations', 0),
                'health_score': 100.0 if is_ready else 50.0
            }
            
        except Exception as e:
            return {
                'status': 'offline',
                'response_time': time.time() - start_time,
                'error_count': 1,
                'health_score': 0.0
            }
    
    def get_component_status(self) -> Dict[str, ComponentStatus]:
        """Get all component statuses"""
        return self.component_status.copy()

class AlertManager:
    """Manages system alerts and notifications"""
    
    def __init__(self):
        self.alerts = []
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'response_time': 2.0,
            'success_rate': 90.0,
            'error_rate': 10.0
        }
        
        logger.info("🚨 Alert Manager initialized")
    
    def check_alerts(self, metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        new_alerts = []
        
        # CPU usage alert
        if metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            new_alerts.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f'High CPU usage: {metrics.cpu_usage:.1f}%',
                'timestamp': metrics.timestamp
            })
        
        # Memory usage alert
        if metrics.memory_usage > self.alert_thresholds['memory_usage']:
            new_alerts.append({
                'type': 'memory_high',
                'severity': 'warning',
                'message': f'High memory usage: {metrics.memory_usage:.1f}%',
                'timestamp': metrics.timestamp
            })
        
        # Response time alert
        if metrics.response_time > self.alert_thresholds['response_time']:
            new_alerts.append({
                'type': 'response_slow',
                'severity': 'warning',
                'message': f'Slow response time: {metrics.response_time:.3f}s',
                'timestamp': metrics.timestamp
            })
        
        # Success rate alert
        if metrics.success_rate < self.alert_thresholds['success_rate']:
            new_alerts.append({
                'type': 'success_low',
                'severity': 'critical',
                'message': f'Low success rate: {metrics.success_rate:.1f}%',
                'timestamp': metrics.timestamp
            })
        
        # Add new alerts
        self.alerts.extend(new_alerts)
        
        # Keep only recent alerts (last 50)
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]
        
        return new_alerts
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        # Return alerts from last 5 minutes
        current_time = time.time()
        return [
            alert for alert in self.alerts
            if current_time - alert['timestamp'] < 300
        ]

class MonitoringDashboard:
    """Real-time monitoring dashboard"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.component_monitor = ComponentMonitor()
        self.alert_manager = AlertManager()
        
        self.dashboard_active = False
        self.computer_access_manager = None
        
        logger.info("📊 Monitoring Dashboard initialized")
    
    def start_monitoring(self, computer_access_manager):
        """Start all monitoring components"""
        self.computer_access_manager = computer_access_manager
        self.dashboard_active = True
        
        self.metrics_collector.start_collection(computer_access_manager)
        self.component_monitor.start_monitoring(computer_access_manager)
        
        logger.info("🚀 Monitoring Dashboard started")
    
    def stop_monitoring(self):
        """Stop all monitoring components"""
        self.dashboard_active = False
        
        self.metrics_collector.stop_collection()
        self.component_monitor.stop_monitoring()
        
        logger.info("🛑 Monitoring Dashboard stopped")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        latest_metrics = self.metrics_collector.get_latest_metrics()
        metrics_history = self.metrics_collector.get_metrics_history()
        component_status = self.component_monitor.get_component_status()
        
        # Check for alerts
        alerts = []
        if latest_metrics:
            alerts = self.alert_manager.check_alerts(latest_metrics)
        
        active_alerts = self.alert_manager.get_active_alerts()
        
        return {
            'timestamp': time.time(),
            'dashboard_active': self.dashboard_active,
            'latest_metrics': asdict(latest_metrics) if latest_metrics else None,
            'metrics_history': [asdict(m) for m in metrics_history],
            'component_status': {name: asdict(status) for name, status in component_status.items()},
            'new_alerts': alerts,
            'active_alerts': active_alerts,
            'system_health': self._calculate_system_health(latest_metrics, component_status)
        }
    
    def _calculate_system_health(self, metrics: Optional[SystemMetrics], 
                                components: Dict[str, ComponentStatus]) -> Dict[str, Any]:
        """Calculate overall system health"""
        if not metrics:
            return {'score': 0, 'status': 'unknown'}
        
        # Base health score from metrics
        health_score = 100.0
        
        # Deduct for high resource usage
        if metrics.cpu_usage > 70:
            health_score -= (metrics.cpu_usage - 70) * 0.5
        
        if metrics.memory_usage > 80:
            health_score -= (metrics.memory_usage - 80) * 0.3
        
        # Deduct for slow response
        if metrics.response_time > 1.0:
            health_score -= min(20, metrics.response_time * 10)
        
        # Deduct for low success rate
        if metrics.success_rate < 95:
            health_score -= (95 - metrics.success_rate) * 0.5
        
        # Factor in component health
        if components:
            component_scores = [comp.health_score for comp in components.values()]
            avg_component_health = sum(component_scores) / len(component_scores)
            health_score = (health_score + avg_component_health) / 2
        
        # Determine status
        if health_score >= 90:
            status = 'excellent'
        elif health_score >= 75:
            status = 'good'
        elif health_score >= 50:
            status = 'degraded'
        else:
            status = 'critical'
        
        return {
            'score': max(0, min(100, health_score)),
            'status': status
        }
    
    def print_dashboard(self):
        """Print dashboard to console"""
        data = self.get_dashboard_data()
        
        print("\n" + "="*70)
        print("📊 ORION VISION CORE - REAL-TIME MONITORING DASHBOARD")
        print("="*70)
        
        # System Health
        health = data['system_health']
        health_emoji = {
            'excellent': '🟢',
            'good': '🟡',
            'degraded': '🟠',
            'critical': '🔴'
        }.get(health['status'], '⚪')
        
        print(f"{health_emoji} System Health: {health['status'].upper()} ({health['score']:.1f}/100)")
        
        # Latest Metrics
        if data['latest_metrics']:
            metrics = data['latest_metrics']
            print(f"\n📈 Current Metrics:")
            print(f"   💻 CPU: {metrics['cpu_usage']:.1f}%")
            print(f"   🧠 Memory: {metrics['memory_usage']:.1f}%")
            print(f"   ⚡ Response: {metrics['response_time']:.3f}s")
            print(f"   ✅ Success Rate: {metrics['success_rate']:.1f}%")
            print(f"   🎯 Active Tasks: {metrics['active_tasks']}")
        
        # Component Status
        if data['component_status']:
            print(f"\n🔧 Component Status:")
            for name, status in data['component_status'].items():
                status_emoji = {
                    'online': '🟢',
                    'degraded': '🟡',
                    'offline': '🔴'
                }.get(status['status'], '⚪')
                
                print(f"   {status_emoji} {name.capitalize()}: {status['status']} ({status['health_score']:.0f}%)")
        
        # Active Alerts
        if data['active_alerts']:
            print(f"\n🚨 Active Alerts:")
            for alert in data['active_alerts'][-5:]:  # Show last 5 alerts
                severity_emoji = {
                    'critical': '🔴',
                    'warning': '🟡',
                    'info': '🔵'
                }.get(alert['severity'], '⚪')
                
                print(f"   {severity_emoji} {alert['message']}")
        else:
            print(f"\n✅ No Active Alerts")
        
        print("\n" + "="*70)

# Global dashboard instance
dashboard = MonitoringDashboard()

def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get global monitoring dashboard"""
    return dashboard
