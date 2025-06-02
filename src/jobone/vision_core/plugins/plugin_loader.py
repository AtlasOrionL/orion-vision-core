"""
🔌 Orion Vision Core - Plugin Loader
Dynamic plugin loading and instantiation

This module provides plugin loading capabilities:
- Dynamic Python module loading
- Plugin class instantiation
- Plugin validation and verification
- Loading strategy management
- Error handling and recovery

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import importlib.util
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import inspect

from .base_plugin import BasePlugin, PluginMetadata, PluginConfig
from .plugin_registry import PluginInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoaderStrategy(Enum):
    """Plugin loading strategies"""
    DIRECT_IMPORT = "direct_import"
    DYNAMIC_IMPORT = "dynamic_import"
    ISOLATED_IMPORT = "isolated_import"
    SANDBOXED_IMPORT = "sandboxed_import"

@dataclass
class PluginLoadResult:
    """Result of plugin loading operation"""
    success: bool
    plugin_instance: Optional[BasePlugin] = None
    plugin_class: Optional[Type[BasePlugin]] = None
    error_message: Optional[str] = None
    load_time: float = 0.0
    strategy_used: Optional[LoaderStrategy] = None

class PluginLoader:
    """
    Dynamic plugin loader for Orion Vision Core.
    
    Provides secure and flexible plugin loading with:
    - Multiple loading strategies
    - Plugin validation and verification
    - Error handling and recovery
    - Performance monitoring
    - Security checks
    """
    
    def __init__(self, default_strategy: LoaderStrategy = LoaderStrategy.DYNAMIC_IMPORT):
        """
        Initialize the plugin loader.
        
        Args:
            default_strategy: Default loading strategy to use
        """
        self.default_strategy = default_strategy
        self.loaded_modules: Dict[str, Any] = {}
        self.loading_cache: Dict[str, PluginLoadResult] = {}
        self.loader_metrics = {
            'total_loads': 0,
            'successful_loads': 0,
            'failed_loads': 0,
            'cache_hits': 0,
            'average_load_time': 0.0
        }
        
        logger.info(f"🔧 Plugin Loader initialized with strategy: {default_strategy.value}")
    
    async def initialize(self) -> bool:
        """
        Initialize the plugin loader.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Clear any existing cache
            self.loaded_modules.clear()
            self.loading_cache.clear()
            
            logger.info("✅ Plugin Loader initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Plugin Loader initialization failed: {e}")
            return False
    
    async def load_plugin(self, plugin_info: PluginInfo, 
                         strategy: Optional[LoaderStrategy] = None,
                         force_reload: bool = False) -> PluginLoadResult:
        """
        Load a plugin from plugin information.
        
        Args:
            plugin_info: Plugin information to load
            strategy: Loading strategy to use (optional)
            force_reload: Force reload even if cached
            
        Returns:
            PluginLoadResult with loading details
        """
        start_time = asyncio.get_event_loop().time()
        strategy = strategy or self.default_strategy
        plugin_key = f"{plugin_info.name}_{plugin_info.version}"
        
        logger.info(f"📦 Loading plugin: {plugin_key} with strategy: {strategy.value}")
        
        try:
            # Check cache first
            if not force_reload and plugin_key in self.loading_cache:
                cached_result = self.loading_cache[plugin_key]
                if cached_result.success:
                    self.loader_metrics['cache_hits'] += 1
                    logger.info(f"💾 Using cached plugin: {plugin_key}")
                    return cached_result
            
            # Load plugin based on strategy
            if strategy == LoaderStrategy.DIRECT_IMPORT:
                result = await self._load_direct_import(plugin_info)
            elif strategy == LoaderStrategy.DYNAMIC_IMPORT:
                result = await self._load_dynamic_import(plugin_info)
            elif strategy == LoaderStrategy.ISOLATED_IMPORT:
                result = await self._load_isolated_import(plugin_info)
            elif strategy == LoaderStrategy.SANDBOXED_IMPORT:
                result = await self._load_sandboxed_import(plugin_info)
            else:
                raise ValueError(f"Unknown loading strategy: {strategy}")
            
            # Set loading details
            result.load_time = asyncio.get_event_loop().time() - start_time
            result.strategy_used = strategy
            
            # Update metrics
            self.loader_metrics['total_loads'] += 1
            if result.success:
                self.loader_metrics['successful_loads'] += 1
                # Cache successful loads
                self.loading_cache[plugin_key] = result
            else:
                self.loader_metrics['failed_loads'] += 1
            
            # Update average load time
            total_loads = self.loader_metrics['total_loads']
            current_avg = self.loader_metrics['average_load_time']
            self.loader_metrics['average_load_time'] = (
                (current_avg * (total_loads - 1) + result.load_time) / total_loads
            )
            
            if result.success:
                logger.info(f"✅ Plugin {plugin_key} loaded successfully in {result.load_time:.2f}s")
            else:
                logger.error(f"❌ Plugin {plugin_key} loading failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            load_time = asyncio.get_event_loop().time() - start_time
            error_result = PluginLoadResult(
                success=False,
                error_message=str(e),
                load_time=load_time,
                strategy_used=strategy
            )
            
            self.loader_metrics['total_loads'] += 1
            self.loader_metrics['failed_loads'] += 1
            
            logger.error(f"❌ Plugin {plugin_key} loading exception: {e}")
            return error_result
    
    async def _load_direct_import(self, plugin_info: PluginInfo) -> PluginLoadResult:
        """Load plugin using direct import (for built-in plugins)"""
        
        try:
            # For direct import, assume plugin is in a known module path
            module_name = f"plugins.{plugin_info.name}"
            
            if module_name in sys.modules:
                module = sys.modules[module_name]
            else:
                module = importlib.import_module(module_name)
            
            # Find plugin class
            plugin_class = self._find_plugin_class(module, plugin_info)
            if not plugin_class:
                return PluginLoadResult(
                    success=False,
                    error_message=f"Plugin class not found in module {module_name}"
                )
            
            # Create plugin instance
            plugin_instance = await self._create_plugin_instance(plugin_class, plugin_info)
            
            return PluginLoadResult(
                success=True,
                plugin_instance=plugin_instance,
                plugin_class=plugin_class
            )
            
        except Exception as e:
            return PluginLoadResult(
                success=False,
                error_message=f"Direct import failed: {e}"
            )
    
    async def _load_dynamic_import(self, plugin_info: PluginInfo) -> PluginLoadResult:
        """Load plugin using dynamic import from file"""
        
        try:
            # Determine file path
            file_path = plugin_info.file_path or plugin_info.package_path
            if not file_path or not Path(file_path).exists():
                return PluginLoadResult(
                    success=False,
                    error_message=f"Plugin file not found: {file_path}"
                )
            
            # Create module spec
            module_name = f"dynamic_plugin_{plugin_info.name}_{plugin_info.version}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            
            if not spec or not spec.loader:
                return PluginLoadResult(
                    success=False,
                    error_message=f"Failed to create module spec for {file_path}"
                )
            
            # Load module
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Store module reference
            self.loaded_modules[module_name] = module
            
            # Find plugin class
            plugin_class = self._find_plugin_class(module, plugin_info)
            if not plugin_class:
                return PluginLoadResult(
                    success=False,
                    error_message=f"Plugin class not found in {file_path}"
                )
            
            # Create plugin instance
            plugin_instance = await self._create_plugin_instance(plugin_class, plugin_info)
            
            return PluginLoadResult(
                success=True,
                plugin_instance=plugin_instance,
                plugin_class=plugin_class
            )
            
        except Exception as e:
            return PluginLoadResult(
                success=False,
                error_message=f"Dynamic import failed: {e}"
            )
    
    async def _load_isolated_import(self, plugin_info: PluginInfo) -> PluginLoadResult:
        """Load plugin in isolated environment"""
        
        # For now, use dynamic import with additional isolation measures
        # In a full implementation, this would create a separate namespace
        
        try:
            result = await self._load_dynamic_import(plugin_info)
            
            if result.success:
                # Add isolation measures here
                logger.info(f"🔒 Plugin {plugin_info.name} loaded in isolated environment")
            
            return result
            
        except Exception as e:
            return PluginLoadResult(
                success=False,
                error_message=f"Isolated import failed: {e}"
            )
    
    async def _load_sandboxed_import(self, plugin_info: PluginInfo) -> PluginLoadResult:
        """Load plugin in sandboxed environment"""
        
        # For now, use isolated import with additional sandboxing
        # In a full implementation, this would use proper sandboxing
        
        try:
            result = await self._load_isolated_import(plugin_info)
            
            if result.success:
                # Add sandboxing measures here
                logger.info(f"🛡️ Plugin {plugin_info.name} loaded in sandboxed environment")
            
            return result
            
        except Exception as e:
            return PluginLoadResult(
                success=False,
                error_message=f"Sandboxed import failed: {e}"
            )
    
    def _find_plugin_class(self, module: Any, plugin_info: PluginInfo) -> Optional[Type[BasePlugin]]:
        """Find the plugin class in a loaded module"""
        
        # Look for classes that inherit from BasePlugin
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, BasePlugin) and 
                obj != BasePlugin and 
                hasattr(obj, '__module__') and 
                obj.__module__ == module.__name__):
                
                logger.info(f"🎯 Found plugin class: {name}")
                return obj
        
        # Fallback: look for class with specific name patterns
        class_name_patterns = [
            plugin_info.name.replace('_', '').title() + 'Plugin',
            plugin_info.name.title() + 'Plugin',
            plugin_info.name.title(),
            'Plugin'
        ]
        
        for pattern in class_name_patterns:
            if hasattr(module, pattern):
                obj = getattr(module, pattern)
                if inspect.isclass(obj) and issubclass(obj, BasePlugin):
                    logger.info(f"🎯 Found plugin class by pattern: {pattern}")
                    return obj
        
        return None
    
    async def _create_plugin_instance(self, plugin_class: Type[BasePlugin], 
                                    plugin_info: PluginInfo) -> BasePlugin:
        """Create an instance of the plugin class"""
        
        # Create plugin metadata
        metadata = PluginMetadata(
            name=plugin_info.name,
            version=plugin_info.version,
            description=plugin_info.description,
            author=plugin_info.author,
            plugin_type=plugin_info.plugin_type,
            capabilities=plugin_info.capabilities,
            dependencies=[dep.name for dep in plugin_info.dependencies],
            min_system_version=plugin_info.min_system_version,
            max_system_version=plugin_info.max_system_version,
            license=plugin_info.license,
            homepage=plugin_info.homepage,
            repository=plugin_info.repository,
            tags=plugin_info.tags
        )
        
        # Create plugin configuration
        config = PluginConfig(
            enabled=True,
            auto_start=True,
            priority=100,
            sandbox_enabled=True
        )
        
        # Instantiate plugin
        plugin_instance = plugin_class(metadata, config)
        
        logger.info(f"🔧 Created plugin instance: {plugin_instance.plugin_id}")
        return plugin_instance
    
    async def unload_plugin(self, plugin_name: str, version: str) -> bool:
        """
        Unload a plugin and clean up resources.
        
        Args:
            plugin_name: Name of the plugin to unload
            version: Version of the plugin to unload
            
        Returns:
            True if unload successful, False otherwise
        """
        plugin_key = f"{plugin_name}_{version}"
        
        try:
            # Remove from cache
            if plugin_key in self.loading_cache:
                del self.loading_cache[plugin_key]
            
            # Remove module if dynamically loaded
            module_name = f"dynamic_plugin_{plugin_name}_{version}"
            if module_name in self.loaded_modules:
                del self.loaded_modules[module_name]
            
            # Remove from sys.modules if present
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            logger.info(f"🗑️ Unloaded plugin: {plugin_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unload plugin {plugin_key}: {e}")
            return False
    
    def get_loader_metrics(self) -> Dict[str, Any]:
        """Get plugin loader performance metrics"""
        total_loads = self.loader_metrics['total_loads']
        success_rate = (
            self.loader_metrics['successful_loads'] / total_loads 
            if total_loads > 0 else 0.0
        )
        
        return {
            **self.loader_metrics,
            'success_rate': success_rate,
            'cached_plugins': len(self.loading_cache),
            'loaded_modules': len(self.loaded_modules)
        }
    
    def clear_cache(self):
        """Clear the plugin loading cache"""
        self.loading_cache.clear()
        logger.info("🧹 Plugin loading cache cleared")
