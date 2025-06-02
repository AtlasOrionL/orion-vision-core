"""
Plugin Manager for Orion Vision Core

This module provides comprehensive plugin lifecycle management.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.2 - Advanced Features & Enhanced Capabilities
"""

import os
import sys
import importlib
import inspect
import threading
from typing import Dict, List, Any, Optional, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import weakref

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class PluginState(Enum):
    """Plugin state enumeration"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class PluginType(Enum):
    """Plugin type enumeration"""
    CORE = "core"
    EXTENSION = "extension"
    INTEGRATION = "integration"
    UTILITY = "utility"
    CUSTOM = "custom"


@dataclass
class PluginMetadata:
    """Plugin metadata structure"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType = PluginType.EXTENSION
    dependencies: List[str] = field(default_factory=list)
    api_version: str = "1.0.0"
    entry_point: str = "main"
    config_schema: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def validate(self) -> bool:
        """Validate plugin metadata"""
        required_fields = ['name', 'version', 'description', 'author']
        return all(getattr(self, field) for field in required_fields)


@dataclass
class PluginInstance:
    """Plugin instance data structure"""
    metadata: PluginMetadata
    module: Any = None
    instance: Any = None
    state: PluginState = PluginState.UNLOADED
    load_time: float = 0.0
    error_message: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    hooks: Dict[str, List[Callable]] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """Check if plugin is active"""
        return self.state == PluginState.ACTIVE
    
    def has_error(self) -> bool:
        """Check if plugin has error"""
        return self.state == PluginState.ERROR


class PluginManager:
    """
    Comprehensive plugin lifecycle management system
    
    Provides plugin loading, initialization, dependency resolution,
    and lifecycle management with hook system support.
    """
    
    def __init__(self, plugin_directories: Optional[List[str]] = None,
                 metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize plugin manager"""
        self.logger = logger or AgentLogger("plugin_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Plugin storage
        self.plugins: Dict[str, PluginInstance] = {}
        self.plugin_directories = plugin_directories or []
        
        # Plugin discovery
        self.discovered_plugins: Dict[str, str] = {}  # name -> path
        
        # Hook system
        self.hooks: Dict[str, List[Callable]] = {}
        self.hook_priorities: Dict[str, Dict[Callable, int]] = {}
        
        # Plugin configuration
        self.auto_load_enabled = True
        self.dependency_resolution_enabled = True
        self.max_load_time = 30.0  # seconds
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.plugin_stats = {
            'total_plugins': 0,
            'active_plugins': 0,
            'failed_plugins': 0,
            'total_loads': 0,
            'total_unloads': 0,
            'hook_executions': 0,
            'discovery_runs': 0
        }
        
        self.logger.info("Plugin Manager initialized")
    
    def add_plugin_directory(self, directory: str):
        """Add plugin directory for discovery"""
        if directory not in self.plugin_directories:
            self.plugin_directories.append(directory)
            
            self.logger.info("Plugin directory added", directory=directory)
    
    def discover_plugins(self) -> Dict[str, str]:
        """Discover plugins in configured directories"""
        try:
            discovered = {}
            
            for directory in self.plugin_directories:
                if not os.path.exists(directory):
                    self.logger.warning("Plugin directory not found", directory=directory)
                    continue
                
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    
                    # Check for Python files
                    if item.endswith('.py') and not item.startswith('__'):
                        plugin_name = item[:-3]  # Remove .py extension
                        discovered[plugin_name] = item_path
                    
                    # Check for plugin directories
                    elif os.path.isdir(item_path):
                        plugin_file = os.path.join(item_path, '__init__.py')
                        if os.path.exists(plugin_file):
                            discovered[item] = item_path
            
            self.discovered_plugins.update(discovered)
            self.plugin_stats['discovery_runs'] += 1
            
            self.logger.info(
                "Plugin discovery completed",
                discovered_count=len(discovered),
                total_discovered=len(self.discovered_plugins)
            )
            
            return discovered
            
        except Exception as e:
            self.logger.error("Plugin discovery failed", error=str(e))
            return {}
    
    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Load plugin by name"""
        try:
            with self._lock:
                # Check if plugin already loaded
                if plugin_name in self.plugins:
                    if self.plugins[plugin_name].is_active():
                        self.logger.warning("Plugin already loaded", plugin_name=plugin_name)
                        return True
                
                # Find plugin path
                if plugin_name not in self.discovered_plugins:
                    self.discover_plugins()
                
                if plugin_name not in self.discovered_plugins:
                    self.logger.error("Plugin not found", plugin_name=plugin_name)
                    return False
                
                plugin_path = self.discovered_plugins[plugin_name]
                
                # Create plugin instance
                plugin_instance = PluginInstance(
                    metadata=PluginMetadata(
                        name=plugin_name,
                        version="1.0.0",
                        description=f"Plugin {plugin_name}",
                        author="Unknown"
                    ),
                    config=config or {}
                )
                
                # Update state
                plugin_instance.state = PluginState.LOADING
                self.plugins[plugin_name] = plugin_instance
                
                # Load plugin module
                import time
                start_time = time.time()
                
                try:
                    # Add plugin path to sys.path if it's a directory
                    if os.path.isdir(plugin_path):
                        if plugin_path not in sys.path:
                            sys.path.insert(0, plugin_path)
                        module = importlib.import_module(plugin_name)
                    else:
                        # Load from file
                        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                    
                    plugin_instance.module = module
                    plugin_instance.load_time = time.time() - start_time
                    
                    # Get plugin metadata if available
                    if hasattr(module, 'PLUGIN_METADATA'):
                        metadata_dict = module.PLUGIN_METADATA
                        plugin_instance.metadata = PluginMetadata(**metadata_dict)
                    
                    # Validate metadata
                    if not plugin_instance.metadata.validate():
                        raise ValueError("Invalid plugin metadata")
                    
                    # Initialize plugin
                    plugin_instance.state = PluginState.INITIALIZING
                    
                    # Look for plugin class or entry point
                    entry_point = plugin_instance.metadata.entry_point
                    if hasattr(module, entry_point):
                        plugin_class = getattr(module, entry_point)
                        if inspect.isclass(plugin_class):
                            plugin_instance.instance = plugin_class(config or {})
                        elif callable(plugin_class):
                            plugin_instance.instance = plugin_class
                    
                    # Call plugin initialization if available
                    if plugin_instance.instance and hasattr(plugin_instance.instance, 'initialize'):
                        plugin_instance.instance.initialize()
                    
                    # Register plugin hooks
                    self._register_plugin_hooks(plugin_instance)
                    
                    # Update state to active
                    plugin_instance.state = PluginState.ACTIVE
                    
                    # Update statistics
                    self.plugin_stats['total_loads'] += 1
                    self.plugin_stats['total_plugins'] = len(self.plugins)
                    self.plugin_stats['active_plugins'] = sum(
                        1 for p in self.plugins.values() if p.is_active()
                    )
                    
                    # Collect metrics
                    self.metrics_collector.collect_metric(
                        name="plugin.loaded",
                        value=plugin_instance.load_time * 1000,  # ms
                        metric_type=MetricType.TIMER,
                        tags={
                            'plugin_name': plugin_name,
                            'plugin_type': plugin_instance.metadata.plugin_type.value
                        }
                    )
                    
                    self.logger.info(
                        "Plugin loaded successfully",
                        plugin_name=plugin_name,
                        load_time_ms=f"{plugin_instance.load_time * 1000:.2f}",
                        plugin_type=plugin_instance.metadata.plugin_type.value
                    )
                    
                    return True
                    
                except Exception as e:
                    plugin_instance.state = PluginState.ERROR
                    plugin_instance.error_message = str(e)
                    self.plugin_stats['failed_plugins'] += 1
                    
                    self.logger.error(
                        "Plugin loading failed",
                        plugin_name=plugin_name,
                        error=str(e)
                    )
                    
                    return False
                
        except Exception as e:
            self.logger.error("Plugin load failed", plugin_name=plugin_name, error=str(e))
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload plugin by name"""
        try:
            with self._lock:
                if plugin_name not in self.plugins:
                    self.logger.warning("Plugin not loaded", plugin_name=plugin_name)
                    return False
                
                plugin_instance = self.plugins[plugin_name]
                
                # Update state
                plugin_instance.state = PluginState.STOPPING
                
                # Call plugin cleanup if available
                if plugin_instance.instance and hasattr(plugin_instance.instance, 'cleanup'):
                    try:
                        plugin_instance.instance.cleanup()
                    except Exception as e:
                        self.logger.warning("Plugin cleanup failed", plugin_name=plugin_name, error=str(e))
                
                # Unregister hooks
                self._unregister_plugin_hooks(plugin_instance)
                
                # Remove plugin
                del self.plugins[plugin_name]
                
                # Update statistics
                self.plugin_stats['total_unloads'] += 1
                self.plugin_stats['total_plugins'] = len(self.plugins)
                self.plugin_stats['active_plugins'] = sum(
                    1 for p in self.plugins.values() if p.is_active()
                )
                
                self.logger.info("Plugin unloaded successfully", plugin_name=plugin_name)
                return True
                
        except Exception as e:
            self.logger.error("Plugin unload failed", plugin_name=plugin_name, error=str(e))
            return False
    
    def register_hook(self, hook_name: str, callback: Callable, priority: int = 0):
        """Register hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
            self.hook_priorities[hook_name] = {}
        
        self.hooks[hook_name].append(callback)
        self.hook_priorities[hook_name][callback] = priority
        
        # Sort by priority (higher priority first)
        self.hooks[hook_name].sort(
            key=lambda cb: self.hook_priorities[hook_name].get(cb, 0),
            reverse=True
        )
        
        self.logger.debug(
            "Hook registered",
            hook_name=hook_name,
            priority=priority,
            total_callbacks=len(self.hooks[hook_name])
        )
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute hook callbacks"""
        results = []
        
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                    self.plugin_stats['hook_executions'] += 1
                except Exception as e:
                    self.logger.warning(
                        "Hook execution failed",
                        hook_name=hook_name,
                        callback=str(callback),
                        error=str(e)
                    )
        
        return results
    
    def _register_plugin_hooks(self, plugin_instance: PluginInstance):
        """Register hooks for a plugin"""
        if not plugin_instance.instance:
            return
        
        # Look for hook methods
        for attr_name in dir(plugin_instance.instance):
            if attr_name.startswith('hook_'):
                hook_name = attr_name[5:]  # Remove 'hook_' prefix
                callback = getattr(plugin_instance.instance, attr_name)
                if callable(callback):
                    self.register_hook(hook_name, callback)
                    
                    if hook_name not in plugin_instance.hooks:
                        plugin_instance.hooks[hook_name] = []
                    plugin_instance.hooks[hook_name].append(callback)
    
    def _unregister_plugin_hooks(self, plugin_instance: PluginInstance):
        """Unregister hooks for a plugin"""
        for hook_name, callbacks in plugin_instance.hooks.items():
            if hook_name in self.hooks:
                for callback in callbacks:
                    if callback in self.hooks[hook_name]:
                        self.hooks[hook_name].remove(callback)
                    if callback in self.hook_priorities.get(hook_name, {}):
                        del self.hook_priorities[hook_name][callback]
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get plugin information"""
        if plugin_name not in self.plugins:
            return None
        
        plugin = self.plugins[plugin_name]
        return {
            'name': plugin.metadata.name,
            'version': plugin.metadata.version,
            'description': plugin.metadata.description,
            'author': plugin.metadata.author,
            'type': plugin.metadata.plugin_type.value,
            'state': plugin.state.value,
            'load_time': plugin.load_time,
            'error_message': plugin.error_message,
            'dependencies': plugin.metadata.dependencies,
            'hooks': list(plugin.hooks.keys())
        }
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins"""
        return [
            self.get_plugin_info(name)
            for name in self.plugins.keys()
        ]
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get plugin manager statistics"""
        with self._lock:
            return {
                'plugin_directories': len(self.plugin_directories),
                'discovered_plugins': len(self.discovered_plugins),
                'loaded_plugins': len(self.plugins),
                'auto_load_enabled': self.auto_load_enabled,
                'dependency_resolution_enabled': self.dependency_resolution_enabled,
                'total_hooks': len(self.hooks),
                'stats': self.plugin_stats.copy()
            }
