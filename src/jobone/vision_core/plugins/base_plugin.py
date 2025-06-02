"""
🔌 Orion Vision Core - Base Plugin Class
Abstract base class for all plugins

This module provides the foundation for all plugins:
- Plugin interface definition and contracts
- Plugin lifecycle management hooks
- Plugin metadata and configuration
- Plugin capability declarations
- Plugin communication protocols

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginType(Enum):
    """Types of plugins supported by the system"""
    AI_ENHANCEMENT = "ai_enhancement"
    DATA_PROCESSING = "data_processing"
    UI_EXTENSION = "ui_extension"
    INTEGRATION = "integration"
    UTILITY = "utility"
    WORKFLOW = "workflow"
    SECURITY = "security"
    MONITORING = "monitoring"

class PluginCapability(Enum):
    """Capabilities that plugins can provide"""
    TEXT_PROCESSING = "text_processing"
    IMAGE_PROCESSING = "image_processing"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_PROCESSING = "video_processing"
    DATA_ANALYSIS = "data_analysis"
    MACHINE_LEARNING = "machine_learning"
    NATURAL_LANGUAGE = "natural_language"
    COMPUTER_VISION = "computer_vision"
    API_INTEGRATION = "api_integration"
    DATABASE_ACCESS = "database_access"
    FILE_MANAGEMENT = "file_management"
    NETWORK_COMMUNICATION = "network_communication"
    USER_INTERFACE = "user_interface"
    SYSTEM_MONITORING = "system_monitoring"
    SECURITY_SCANNING = "security_scanning"

class PluginStatus(Enum):
    """Plugin lifecycle status"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    UNLOADING = "unloading"

@dataclass
class PluginMetadata:
    """Metadata for plugin description and management"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    capabilities: List[PluginCapability]
    dependencies: List[str] = field(default_factory=list)
    min_system_version: str = "9.1.0"
    max_system_version: Optional[str] = None
    license: str = "MIT"
    homepage: Optional[str] = None
    repository: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class PluginConfig:
    """Configuration for plugin behavior"""
    enabled: bool = True
    auto_start: bool = True
    priority: int = 100  # Higher number = higher priority
    max_memory_mb: int = 512
    max_cpu_percent: float = 10.0
    timeout_seconds: float = 30.0
    sandbox_enabled: bool = True
    network_access: bool = False
    file_system_access: bool = False
    custom_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PluginEvent:
    """Event data for plugin communication"""
    event_type: str
    source_plugin: str
    target_plugin: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = ""

class BasePlugin(ABC):
    """
    Abstract base class for all Orion Vision Core plugins.
    
    All plugins must inherit from this class and implement the required methods.
    This ensures consistent behavior and proper integration with the plugin system.
    """
    
    def __init__(self, metadata: PluginMetadata, config: PluginConfig):
        """
        Initialize the plugin with metadata and configuration.
        
        Args:
            metadata: Plugin metadata and description
            config: Plugin configuration and settings
        """
        self.metadata = metadata
        self.config = config
        self.status = PluginStatus.UNLOADED
        self.plugin_id = f"{metadata.name}_{metadata.version}"
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.performance_metrics = {
            'initialization_time': 0.0,
            'total_executions': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0,
            'error_count': 0,
            'last_execution': None
        }
        
        logger.info(f"🔌 Initialized plugin: {self.plugin_id}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        This method is called when the plugin is first loaded.
        Perform any necessary setup, resource allocation, or configuration here.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def start(self) -> bool:
        """
        Start the plugin.
        
        This method is called to activate the plugin after initialization.
        Begin any background tasks, event listeners, or active processing here.
        
        Returns:
            True if start successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """
        Stop the plugin.
        
        This method is called to deactivate the plugin.
        Stop any background tasks, close connections, or pause processing here.
        
        Returns:
            True if stop successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """
        Clean up plugin resources.
        
        This method is called when the plugin is being unloaded.
        Release resources, close files, cleanup temporary data here.
        
        Returns:
            True if cleanup successful, False otherwise
        """
        pass
    
    async def execute(self, input_data: Any, **kwargs) -> Any:
        """
        Execute the main plugin functionality.
        
        This is the primary method for plugin execution.
        Override this method to implement your plugin's core functionality.
        
        Args:
            input_data: Input data for processing
            **kwargs: Additional keyword arguments
            
        Returns:
            Processed output data
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Update metrics
            self.performance_metrics['total_executions'] += 1
            self.performance_metrics['last_execution'] = datetime.now()
            
            # Default implementation - override in subclasses
            result = await self._process_data(input_data, **kwargs)
            
            # Update execution time metrics
            execution_time = asyncio.get_event_loop().time() - start_time
            self.performance_metrics['total_execution_time'] += execution_time
            self.performance_metrics['average_execution_time'] = (
                self.performance_metrics['total_execution_time'] / 
                self.performance_metrics['total_executions']
            )
            
            return result
            
        except Exception as e:
            self.performance_metrics['error_count'] += 1
            logger.error(f"❌ Plugin execution error in {self.plugin_id}: {e}")
            raise
    
    async def _process_data(self, input_data: Any, **kwargs) -> Any:
        """
        Process input data - override in subclasses.
        
        Args:
            input_data: Input data for processing
            **kwargs: Additional keyword arguments
            
        Returns:
            Processed output data
        """
        # Default implementation returns input unchanged
        return input_data
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        Register an event handler for specific event types.
        
        Args:
            event_type: Type of event to handle
            handler: Callback function to handle the event
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"📡 Registered event handler for {event_type} in {self.plugin_id}")
    
    async def handle_event(self, event: PluginEvent):
        """
        Handle incoming plugin events.
        
        Args:
            event: Plugin event to handle
        """
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"❌ Event handler error in {self.plugin_id}: {e}")
    
    def get_capabilities(self) -> List[PluginCapability]:
        """Get plugin capabilities"""
        return self.metadata.capabilities
    
    def has_capability(self, capability: PluginCapability) -> bool:
        """Check if plugin has specific capability"""
        return capability in self.metadata.capabilities
    
    def get_status(self) -> PluginStatus:
        """Get current plugin status"""
        return self.status
    
    def set_status(self, status: PluginStatus):
        """Set plugin status"""
        old_status = self.status
        self.status = status
        logger.info(f"🔄 Plugin {self.plugin_id} status: {old_status.value} → {status.value}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get plugin performance metrics"""
        return {
            **self.performance_metrics,
            'plugin_id': self.plugin_id,
            'status': self.status.value,
            'uptime_seconds': (
                (datetime.now() - self.performance_metrics.get('start_time', datetime.now())).total_seconds()
                if 'start_time' in self.performance_metrics else 0
            )
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get comprehensive plugin information"""
        return {
            'plugin_id': self.plugin_id,
            'metadata': {
                'name': self.metadata.name,
                'version': self.metadata.version,
                'description': self.metadata.description,
                'author': self.metadata.author,
                'type': self.metadata.plugin_type.value,
                'capabilities': [cap.value for cap in self.metadata.capabilities],
                'dependencies': self.metadata.dependencies,
                'license': self.metadata.license,
                'tags': self.metadata.tags
            },
            'config': {
                'enabled': self.config.enabled,
                'auto_start': self.config.auto_start,
                'priority': self.config.priority,
                'sandbox_enabled': self.config.sandbox_enabled,
                'network_access': self.config.network_access,
                'file_system_access': self.config.file_system_access
            },
            'status': self.status.value,
            'performance': self.get_performance_metrics(),
            'event_handlers': list(self.event_handlers.keys())
        }
    
    def validate_dependencies(self, available_plugins: List[str]) -> List[str]:
        """
        Validate plugin dependencies.
        
        Args:
            available_plugins: List of available plugin names
            
        Returns:
            List of missing dependencies
        """
        missing_deps = []
        
        for dependency in self.metadata.dependencies:
            if dependency not in available_plugins:
                missing_deps.append(dependency)
        
        return missing_deps
    
    def is_compatible_with_system(self, system_version: str) -> bool:
        """
        Check if plugin is compatible with system version.
        
        Args:
            system_version: Current system version
            
        Returns:
            True if compatible, False otherwise
        """
        # Simple version comparison (in real implementation, use proper version parsing)
        min_version = self.metadata.min_system_version
        max_version = self.metadata.max_system_version
        
        # For now, assume compatibility if min version requirement is met
        return system_version >= min_version
    
    async def configure(self, new_config: Dict[str, Any]) -> bool:
        """
        Update plugin configuration.
        
        Args:
            new_config: New configuration settings
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            # Update custom settings
            self.config.custom_settings.update(new_config)
            
            # Apply configuration changes
            await self._apply_configuration()
            
            logger.info(f"⚙️ Updated configuration for {self.plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration update failed for {self.plugin_id}: {e}")
            return False
    
    async def _apply_configuration(self):
        """Apply configuration changes - override in subclasses if needed"""
        pass
    
    def __str__(self) -> str:
        """String representation of the plugin"""
        return f"Plugin({self.metadata.name} v{self.metadata.version} - {self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the plugin"""
        return (f"Plugin(id={self.plugin_id}, type={self.metadata.plugin_type.value}, "
                f"status={self.status.value}, capabilities={len(self.metadata.capabilities)})")
