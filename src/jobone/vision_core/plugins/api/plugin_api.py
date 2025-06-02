"""
Plugin API for Orion Vision Core

This module provides plugin development framework and base classes.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.2 - Advanced Features & Enhanced Capabilities
"""

import abc
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class PluginCapability(Enum):
    """Plugin capability enumeration"""
    TASK_PROCESSING = "task_processing"
    DATA_TRANSFORMATION = "data_transformation"
    COMMUNICATION = "communication"
    MONITORING = "monitoring"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    UI_EXTENSION = "ui_extension"
    WORKFLOW = "workflow"
    CUSTOM = "custom"


class PluginPriority(Enum):
    """Plugin priority enumeration"""
    CRITICAL = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    BACKGROUND = 10


@dataclass
class PluginContext:
    """Plugin execution context"""
    plugin_name: str
    session_id: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    
    def get_execution_time(self) -> float:
        """Get execution time in seconds"""
        return time.time() - self.start_time


@dataclass
class PluginResult:
    """Plugin execution result"""
    success: bool
    data: Any = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success_result(cls, data: Any = None, metadata: Dict[str, Any] = None) -> 'PluginResult':
        """Create success result"""
        return cls(success=True, data=data, metadata=metadata or {})
    
    @classmethod
    def error_result(cls, error_message: str, metadata: Dict[str, Any] = None) -> 'PluginResult':
        """Create error result"""
        return cls(success=False, error_message=error_message, metadata=metadata or {})


class PluginInterface(abc.ABC):
    """
    Base interface for all plugins
    
    All plugins must inherit from this interface and implement required methods.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize plugin"""
        self.config = config or {}
        self.logger = AgentLogger(f"plugin.{self.get_name()}")
        self.metrics_collector = MetricsCollector(self.logger)
        self.is_initialized = False
        self.is_active = False
        
        # Plugin statistics
        self.plugin_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0,
            'last_execution_time': 0.0
        }
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """Get plugin name"""
        pass
    
    @abc.abstractmethod
    def get_version(self) -> str:
        """Get plugin version"""
        pass
    
    @abc.abstractmethod
    def get_description(self) -> str:
        """Get plugin description"""
        pass
    
    @abc.abstractmethod
    def get_capabilities(self) -> List[PluginCapability]:
        """Get plugin capabilities"""
        pass
    
    def get_priority(self) -> PluginPriority:
        """Get plugin priority (default: NORMAL)"""
        return PluginPriority.NORMAL
    
    def get_dependencies(self) -> List[str]:
        """Get plugin dependencies"""
        return []
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get plugin configuration schema"""
        return {}
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        try:
            self.is_initialized = True
            self.is_active = True
            
            self.logger.info(
                "Plugin initialized",
                plugin_name=self.get_name(),
                version=self.get_version(),
                capabilities=len(self.get_capabilities())
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Plugin initialization failed", plugin_name=self.get_name(), error=str(e))
            return False
    
    def cleanup(self):
        """Cleanup plugin resources"""
        try:
            self.is_active = False
            
            self.logger.info("Plugin cleaned up", plugin_name=self.get_name())
            
        except Exception as e:
            self.logger.error("Plugin cleanup failed", plugin_name=self.get_name(), error=str(e))
    
    def execute(self, context: PluginContext, *args, **kwargs) -> PluginResult:
        """Execute plugin with context"""
        start_time = time.time()
        
        try:
            # Check if plugin is active
            if not self.is_active:
                return PluginResult.error_result("Plugin is not active")
            
            # Update statistics
            self.plugin_stats['total_executions'] += 1
            
            # Execute plugin logic
            result = self._execute_internal(context, *args, **kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            # Update statistics
            if result.success:
                self.plugin_stats['successful_executions'] += 1
            else:
                self.plugin_stats['failed_executions'] += 1
            
            self.plugin_stats['total_execution_time'] += execution_time
            self.plugin_stats['average_execution_time'] = (
                self.plugin_stats['total_execution_time'] / self.plugin_stats['total_executions']
            )
            self.plugin_stats['last_execution_time'] = execution_time
            
            # Collect metrics
            self.metrics_collector.collect_metric(
                name="plugin.execution",
                value=execution_time * 1000,  # ms
                metric_type=MetricType.TIMER,
                tags={
                    'plugin_name': self.get_name(),
                    'success': str(result.success),
                    'capability': str(self.get_capabilities()[0].value) if self.get_capabilities() else 'unknown'
                }
            )
            
            self.logger.debug(
                "Plugin executed",
                plugin_name=self.get_name(),
                execution_time_ms=f"{execution_time * 1000:.2f}",
                success=result.success
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.plugin_stats['failed_executions'] += 1
            self.plugin_stats['total_execution_time'] += execution_time
            
            error_result = PluginResult.error_result(f"Plugin execution failed: {str(e)}")
            error_result.execution_time = execution_time
            
            self.logger.error(
                "Plugin execution failed",
                plugin_name=self.get_name(),
                execution_time_ms=f"{execution_time * 1000:.2f}",
                error=str(e)
            )
            
            return error_result
    
    @abc.abstractmethod
    def _execute_internal(self, context: PluginContext, *args, **kwargs) -> PluginResult:
        """Internal plugin execution logic (to be implemented by subclasses)"""
        pass
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get plugin statistics"""
        return {
            'name': self.get_name(),
            'version': self.get_version(),
            'description': self.get_description(),
            'capabilities': [cap.value for cap in self.get_capabilities()],
            'priority': self.get_priority().value,
            'dependencies': self.get_dependencies(),
            'is_initialized': self.is_initialized,
            'is_active': self.is_active,
            'stats': self.plugin_stats.copy()
        }


class TaskProcessingPlugin(PluginInterface):
    """Base class for task processing plugins"""
    
    def get_capabilities(self) -> List[PluginCapability]:
        """Get task processing capabilities"""
        return [PluginCapability.TASK_PROCESSING]
    
    @abc.abstractmethod
    def process_task(self, task_data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Process task data"""
        pass
    
    def _execute_internal(self, context: PluginContext, *args, **kwargs) -> PluginResult:
        """Execute task processing"""
        if 'task_data' in kwargs:
            return self.process_task(kwargs['task_data'], context)
        elif args:
            return self.process_task(args[0], context)
        else:
            return PluginResult.error_result("No task data provided")


class DataTransformationPlugin(PluginInterface):
    """Base class for data transformation plugins"""
    
    def get_capabilities(self) -> List[PluginCapability]:
        """Get data transformation capabilities"""
        return [PluginCapability.DATA_TRANSFORMATION]
    
    @abc.abstractmethod
    def transform_data(self, input_data: Any, context: PluginContext) -> PluginResult:
        """Transform input data"""
        pass
    
    def _execute_internal(self, context: PluginContext, *args, **kwargs) -> PluginResult:
        """Execute data transformation"""
        if 'input_data' in kwargs:
            return self.transform_data(kwargs['input_data'], context)
        elif args:
            return self.transform_data(args[0], context)
        else:
            return PluginResult.error_result("No input data provided")


class IntegrationPlugin(PluginInterface):
    """Base class for integration plugins"""
    
    def get_capabilities(self) -> List[PluginCapability]:
        """Get integration capabilities"""
        return [PluginCapability.INTEGRATION]
    
    @abc.abstractmethod
    def integrate(self, integration_data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Perform integration"""
        pass
    
    def _execute_internal(self, context: PluginContext, *args, **kwargs) -> PluginResult:
        """Execute integration"""
        if 'integration_data' in kwargs:
            return self.integrate(kwargs['integration_data'], context)
        elif args:
            return self.integrate(args[0], context)
        else:
            return PluginResult.error_result("No integration data provided")


class PluginRegistry:
    """
    Plugin registry for managing plugin types and factories
    """
    
    def __init__(self):
        """Initialize plugin registry"""
        self.plugin_types: Dict[str, type] = {}
        self.plugin_factories: Dict[str, Callable] = {}
        
        # Register built-in plugin types
        self.register_plugin_type('task_processing', TaskProcessingPlugin)
        self.register_plugin_type('data_transformation', DataTransformationPlugin)
        self.register_plugin_type('integration', IntegrationPlugin)
    
    def register_plugin_type(self, type_name: str, plugin_class: type):
        """Register plugin type"""
        self.plugin_types[type_name] = plugin_class
    
    def register_plugin_factory(self, plugin_name: str, factory_func: Callable):
        """Register plugin factory function"""
        self.plugin_factories[plugin_name] = factory_func
    
    def create_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> Optional[PluginInterface]:
        """Create plugin instance"""
        if plugin_name in self.plugin_factories:
            try:
                return self.plugin_factories[plugin_name](config or {})
            except Exception:
                return None
        
        return None
    
    def get_plugin_types(self) -> List[str]:
        """Get registered plugin types"""
        return list(self.plugin_types.keys())
    
    def get_registered_plugins(self) -> List[str]:
        """Get registered plugin names"""
        return list(self.plugin_factories.keys())


# Global plugin registry instance
plugin_registry = PluginRegistry()


def register_plugin(plugin_name: str):
    """Decorator for registering plugins"""
    def decorator(plugin_class):
        def factory(config):
            return plugin_class(config)
        
        plugin_registry.register_plugin_factory(plugin_name, factory)
        return plugin_class
    
    return decorator


# Plugin development utilities
class PluginUtils:
    """Utility functions for plugin development"""
    
    @staticmethod
    def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate plugin configuration against schema"""
        try:
            # Simple validation - check required fields
            required_fields = schema.get('required', [])
            for field in required_fields:
                if field not in config:
                    return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def create_context(plugin_name: str, session_id: str = None, **kwargs) -> PluginContext:
        """Create plugin context"""
        import uuid
        
        return PluginContext(
            plugin_name=plugin_name,
            session_id=session_id or str(uuid.uuid4()),
            **kwargs
        )
    
    @staticmethod
    def measure_execution_time(func: Callable) -> Callable:
        """Decorator to measure execution time"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if isinstance(result, PluginResult):
                result.execution_time = execution_time
            
            return result
        
        return wrapper
