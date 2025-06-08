"""
🛡️ Graceful Degradation System - PHASE 1 CONSOLIDATION

Error handling, fallback mechanisms, system resilience.
Ensures system continues operating even when components fail.

Author: Orion Vision Core Team
Phase: PHASE 1 - CONSOLIDATION
Priority: HIGH
"""

import logging
import threading
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union
import json

# Error Severity Levels
class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"                                     # Low impact
    MEDIUM = "medium"                               # Medium impact
    HIGH = "high"                                   # High impact
    CRITICAL = "critical"                           # Critical impact

# Degradation Levels
class DegradationLevel(Enum):
    """System degradation levels"""
    FULL_OPERATION = "full_operation"               # Full functionality
    REDUCED_FUNCTIONALITY = "reduced_functionality" # Some features disabled
    MINIMAL_OPERATION = "minimal_operation"         # Basic functionality only
    EMERGENCY_MODE = "emergency_mode"               # Emergency operations only
    SYSTEM_FAILURE = "system_failure"               # System failure

# Recovery Strategies
class RecoveryStrategy(Enum):
    """Recovery strategies"""
    RETRY = "retry"                                 # Retry operation
    FALLBACK = "fallback"                           # Use fallback method
    SKIP = "skip"                                   # Skip operation
    RESTART_COMPONENT = "restart_component"         # Restart component
    SYSTEM_RESTART = "system_restart"               # Restart system

@dataclass
class ErrorEvent:
    """Error event information"""
    
    error_id: str = ""
    component: str = ""
    error_type: str = ""
    error_message: str = ""
    severity: ErrorSeverity = ErrorSeverity.LOW
    
    # Error context
    stack_trace: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Recovery
    recovery_attempted: bool = False
    recovery_strategy: Optional[RecoveryStrategy] = None
    recovery_successful: bool = False

@dataclass
class ComponentHealth:
    """Component health status"""
    
    component_name: str = ""
    is_healthy: bool = True
    last_error: Optional[ErrorEvent] = None
    
    # Health metrics
    error_count: int = 0
    success_count: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    # Performance
    average_response_time: float = 0.0
    max_response_time: float = 0.0
    
    # Status
    degradation_level: DegradationLevel = DegradationLevel.FULL_OPERATION
    
    def get_success_rate(self) -> float:
        """Get success rate percentage"""
        total = self.error_count + self.success_count
        if total == 0:
            return 100.0
        return (self.success_count / total) * 100.0

class GracefulDegradationSystem:
    """
    Graceful Degradation System
    
    PHASE 1 CONSOLIDATION'ın üçüncü bileşeni.
    Error handling, fallback mechanisms, system resilience.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Component health tracking
        self.component_health: Dict[str, ComponentHealth] = {}
        
        # Error tracking
        self.error_history: List[ErrorEvent] = []
        self.error_patterns: Dict[str, int] = {}
        
        # System status
        self.system_degradation_level = DegradationLevel.FULL_OPERATION
        self.emergency_mode = False
        
        # Recovery mechanisms
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        
        # Configuration
        self.max_error_history = 1000
        self.error_threshold_critical = 10          # Errors before critical
        self.error_threshold_emergency = 20         # Errors before emergency
        self.recovery_timeout = 30.0                # Recovery timeout
        
        # Threading
        self._lock = threading.Lock()
        
        self.logger.info("🛡️ GracefulDegradationSystem initialized - PHASE 1 CONSOLIDATION")
    
    def register_component(self, component_name: str) -> bool:
        """Register component for health monitoring"""
        try:
            with self._lock:
                if component_name not in self.component_health:
                    self.component_health[component_name] = ComponentHealth(
                        component_name=component_name
                    )
                    self.logger.info(f"✅ Component registered: {component_name}")
                    return True
                else:
                    self.logger.warning(f"⚠️ Component already registered: {component_name}")
                    return False
        except Exception as e:
            self.logger.error(f"❌ Component registration failed: {e}")
            return False
    
    def register_fallback_handler(self, component_name: str, handler: Callable) -> bool:
        """Register fallback handler for component"""
        try:
            self.fallback_handlers[component_name] = handler
            self.logger.info(f"✅ Fallback handler registered: {component_name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Fallback handler registration failed: {e}")
            return False
    
    def report_error(self, component: str, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Report error and trigger recovery if needed"""
        try:
            # Create error event
            error_event = ErrorEvent(
                error_id=f"err_{int(time.time())}_{hash(str(error)) % 10000}",
                component=component,
                error_type=type(error).__name__,
                error_message=str(error),
                severity=self._determine_error_severity(error),
                stack_trace=traceback.format_exc(),
                context_data=context or {}
            )
            
            # Update component health
            with self._lock:
                if component in self.component_health:
                    health = self.component_health[component]
                    health.error_count += 1
                    health.last_error = error_event
                    health.last_failure = datetime.now()
                    health.is_healthy = health.get_success_rate() > 50.0
                    
                    # Update degradation level
                    self._update_component_degradation(component)
                else:
                    # Auto-register component
                    self.register_component(component)
                    return self.report_error(component, error, context)
                
                # Add to error history
                self.error_history.append(error_event)
                if len(self.error_history) > self.max_error_history:
                    self.error_history = self.error_history[-self.max_error_history//2:]
                
                # Track error patterns
                error_pattern = f"{component}:{error_event.error_type}"
                self.error_patterns[error_pattern] = self.error_patterns.get(error_pattern, 0) + 1
            
            # Log error
            self.logger.error(f"❌ Error reported: {component} - {error_event.error_message}")
            
            # Trigger recovery if needed
            self._trigger_recovery(error_event)
            
            # Update system degradation level
            self._update_system_degradation()
            
            return error_event.error_id
            
        except Exception as e:
            self.logger.error(f"❌ Error reporting failed: {e}")
            return ""
    
    def report_success(self, component: str, response_time: float = 0.0) -> bool:
        """Report successful operation"""
        try:
            with self._lock:
                if component in self.component_health:
                    health = self.component_health[component]
                    health.success_count += 1
                    health.last_success = datetime.now()
                    health.is_healthy = True
                    
                    # Update response time metrics
                    if response_time > 0:
                        current_avg = health.average_response_time
                        total = health.success_count
                        health.average_response_time = (current_avg * (total - 1) + response_time) / total
                        health.max_response_time = max(health.max_response_time, response_time)
                    
                    # Update degradation level
                    self._update_component_degradation(component)
                    
                    return True
                else:
                    # Auto-register component
                    self.register_component(component)
                    return self.report_success(component, response_time)
                    
        except Exception as e:
            self.logger.error(f"❌ Success reporting failed: {e}")
            return False
    
    def _determine_error_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Critical errors
        if any(keyword in error_message for keyword in ['critical', 'fatal', 'system', 'memory']):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if any(keyword in error_message for keyword in ['connection', 'timeout', 'permission']):
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if any(keyword in error_message for keyword in ['warning', 'deprecated', 'retry']):
            return ErrorSeverity.MEDIUM
        
        # Default to low
        return ErrorSeverity.LOW
    
    def _update_component_degradation(self, component: str):
        """Update component degradation level"""
        if component not in self.component_health:
            return
        
        health = self.component_health[component]
        success_rate = health.get_success_rate()
        
        if success_rate >= 90:
            health.degradation_level = DegradationLevel.FULL_OPERATION
        elif success_rate >= 70:
            health.degradation_level = DegradationLevel.REDUCED_FUNCTIONALITY
        elif success_rate >= 50:
            health.degradation_level = DegradationLevel.MINIMAL_OPERATION
        elif success_rate >= 20:
            health.degradation_level = DegradationLevel.EMERGENCY_MODE
        else:
            health.degradation_level = DegradationLevel.SYSTEM_FAILURE
    
    def _update_system_degradation(self):
        """Update system-wide degradation level"""
        if not self.component_health:
            return
        
        # Calculate overall system health
        total_components = len(self.component_health)
        healthy_components = sum(1 for h in self.component_health.values() if h.is_healthy)
        system_health_rate = (healthy_components / total_components) * 100
        
        # Determine system degradation level
        if system_health_rate >= 90:
            self.system_degradation_level = DegradationLevel.FULL_OPERATION
        elif system_health_rate >= 70:
            self.system_degradation_level = DegradationLevel.REDUCED_FUNCTIONALITY
        elif system_health_rate >= 50:
            self.system_degradation_level = DegradationLevel.MINIMAL_OPERATION
        elif system_health_rate >= 20:
            self.system_degradation_level = DegradationLevel.EMERGENCY_MODE
        else:
            self.system_degradation_level = DegradationLevel.SYSTEM_FAILURE
        
        # Check for emergency mode
        critical_errors = sum(1 for h in self.component_health.values() 
                            if h.error_count >= self.error_threshold_emergency)
        
        if critical_errors > 0:
            self.emergency_mode = True
            self.system_degradation_level = DegradationLevel.EMERGENCY_MODE
            self.logger.warning("⚠️ System entered emergency mode")
    
    def _trigger_recovery(self, error_event: ErrorEvent):
        """Trigger recovery mechanism"""
        try:
            component = error_event.component
            
            # Determine recovery strategy
            if error_event.severity == ErrorSeverity.CRITICAL:
                strategy = RecoveryStrategy.RESTART_COMPONENT
            elif error_event.severity == ErrorSeverity.HIGH:
                strategy = RecoveryStrategy.FALLBACK
            elif error_event.severity == ErrorSeverity.MEDIUM:
                strategy = RecoveryStrategy.RETRY
            else:
                strategy = RecoveryStrategy.SKIP
            
            error_event.recovery_strategy = strategy
            error_event.recovery_attempted = True
            
            # Execute recovery
            if strategy == RecoveryStrategy.FALLBACK and component in self.fallback_handlers:
                try:
                    self.fallback_handlers[component]()
                    error_event.recovery_successful = True
                    self.logger.info(f"✅ Fallback recovery successful: {component}")
                except Exception as e:
                    self.logger.error(f"❌ Fallback recovery failed: {e}")
            
            elif strategy == RecoveryStrategy.RETRY:
                # Mark for retry (handled by calling code)
                error_event.recovery_successful = True
                self.logger.info(f"🔄 Retry recovery triggered: {component}")
            
            elif strategy == RecoveryStrategy.RESTART_COMPONENT:
                # Mark for component restart (handled by calling code)
                self.logger.warning(f"🔄 Component restart triggered: {component}")
            
        except Exception as e:
            self.logger.error(f"❌ Recovery trigger failed: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        with self._lock:
            return {
                'system_degradation_level': self.system_degradation_level.value,
                'emergency_mode': self.emergency_mode,
                'total_components': len(self.component_health),
                'healthy_components': sum(1 for h in self.component_health.values() if h.is_healthy),
                'total_errors': len(self.error_history),
                'error_patterns': len(self.error_patterns),
                'component_health': {
                    name: {
                        'is_healthy': health.is_healthy,
                        'success_rate': health.get_success_rate(),
                        'error_count': health.error_count,
                        'success_count': health.success_count,
                        'degradation_level': health.degradation_level.value,
                        'average_response_time': health.average_response_time
                    }
                    for name, health in self.component_health.items()
                }
            }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        with self._lock:
            recent_errors = [e for e in self.error_history 
                           if e.timestamp > datetime.now() - timedelta(hours=1)]
            
            return {
                'total_errors': len(self.error_history),
                'recent_errors': len(recent_errors),
                'error_patterns': dict(sorted(self.error_patterns.items(), 
                                            key=lambda x: x[1], reverse=True)[:10]),
                'severity_distribution': {
                    severity.value: sum(1 for e in self.error_history if e.severity == severity)
                    for severity in ErrorSeverity
                }
            }

# Utility functions
def create_graceful_degradation_system() -> GracefulDegradationSystem:
    """Create graceful degradation system"""
    return GracefulDegradationSystem()

def test_graceful_degradation_system():
    """Test graceful degradation system"""
    print("🛡️ Testing Graceful Degradation System...")
    
    # Create system
    gds = create_graceful_degradation_system()
    print("✅ Graceful degradation system created")
    
    # Register components
    gds.register_component("test_component")
    print("✅ Test component registered")
    
    # Report success
    gds.report_success("test_component", 0.1)
    print("✅ Success reported")
    
    # Report error
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_id = gds.report_error("test_component", e)
        print(f"✅ Error reported: {error_id}")
    
    # Get status
    status = gds.get_system_status()
    print(f"✅ System status: {status['system_degradation_level']}")
    
    print("🚀 Graceful Degradation System test completed!")

if __name__ == "__main__":
    test_graceful_degradation_system()
