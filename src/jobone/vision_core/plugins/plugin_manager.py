"""
🔌 Orion Vision Core - Plugin Manager
Central plugin management and orchestration

This module provides comprehensive plugin management:
- Plugin lifecycle management (load, start, stop, unload)
- Plugin dependency resolution and validation
- Plugin communication and event routing
- Plugin performance monitoring and analytics
- Plugin security and sandboxing coordination

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import json
import os
from pathlib import Path

from .base_plugin import BasePlugin, PluginStatus, PluginType, PluginCapability, PluginEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginManager:
    """
    Central plugin manager for Orion Vision Core.

    Manages the complete plugin lifecycle:
    - Plugin discovery and registration
    - Dynamic loading and unloading
    - Dependency resolution
    - Event routing and communication
    - Performance monitoring
    - Security enforcement
    """

    def __init__(self, plugins_directory: str = "src/jobone/vision_core/plugins/installed",
                 config_file: Optional[str] = None):
        """
        Initialize the plugin manager.

        Args:
            plugins_directory: Directory containing plugin files
            config_file: Optional configuration file path
        """
        self.plugins_directory = Path(plugins_directory)
        self.config_file = config_file

        # Core components (lazy initialization to avoid circular imports)
        self.registry = None
        self.loader = None
        self.sandbox = None

        # Plugin storage
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self.active_plugins: Dict[str, BasePlugin] = {}
        self.plugin_dependencies: Dict[str, Set[str]] = {}

        # Event system
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.event_handlers: Dict[str, List[str]] = {}  # event_type -> plugin_ids

        # Performance tracking
        self.manager_metrics = {
            'total_plugins_loaded': 0,
            'total_plugins_active': 0,
            'total_events_processed': 0,
            'startup_time': 0.0,
            'last_scan_time': None
        }

        # Ensure plugins directory exists
        self.plugins_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"🔌 Plugin Manager initialized with directory: {plugins_directory}")

    async def initialize(self) -> bool:
        """
        Initialize the plugin manager and core components.

        Returns:
            True if initialization successful, False otherwise
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Initialize core components with lazy imports
            from .plugin_registry import PluginRegistry
            from .plugin_loader import PluginLoader
            from .plugin_sandbox import PluginSandbox

            self.registry = PluginRegistry()
            self.loader = PluginLoader()
            self.sandbox = PluginSandbox()

            await self.registry.initialize()
            await self.loader.initialize()
            await self.sandbox.initialize()

            # Load configuration if provided
            if self.config_file and os.path.exists(self.config_file):
                await self._load_configuration()

            # Start event processing
            asyncio.create_task(self._process_events())

            # Scan for available plugins
            await self.scan_plugins()

            self.manager_metrics['startup_time'] = asyncio.get_event_loop().time() - start_time

            logger.info("✅ Plugin Manager initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Plugin Manager initialization failed: {e}")
            return False

    async def scan_plugins(self) -> List[Any]:
        """
        Scan the plugins directory for available plugins.

        Returns:
            List of discovered plugin information
        """
        logger.info("🔍 Scanning for available plugins...")

        discovered_plugins = []

        try:
            # Scan directory for plugin files
            for plugin_path in self.plugins_directory.rglob("*.py"):
                if plugin_path.name.startswith("plugin_"):
                    plugin_info = await self._analyze_plugin_file(plugin_path)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)
                        await self.registry.register_plugin(plugin_info)

            # Scan for plugin packages
            for plugin_dir in self.plugins_directory.iterdir():
                if plugin_dir.is_dir() and not plugin_dir.name.startswith("__"):
                    plugin_info = await self._analyze_plugin_package(plugin_dir)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)
                        await self.registry.register_plugin(plugin_info)

            self.manager_metrics['last_scan_time'] = datetime.now()

            logger.info(f"📋 Discovered {len(discovered_plugins)} plugins")
            return discovered_plugins

        except Exception as e:
            logger.error(f"❌ Plugin scan failed: {e}")
            return []

    async def load_plugin(self, plugin_name: str, auto_start: bool = True) -> bool:
        """
        Load a plugin by name.

        Args:
            plugin_name: Name of the plugin to load
            auto_start: Whether to automatically start the plugin after loading

        Returns:
            True if loading successful, False otherwise
        """
        logger.info(f"📦 Loading plugin: {plugin_name}")

        try:
            # Check if plugin is already loaded
            if plugin_name in self.loaded_plugins:
                logger.warning(f"⚠️ Plugin {plugin_name} is already loaded")
                return True

            # Get plugin info from registry
            plugin_info = await self.registry.get_plugin_info(plugin_name)
            if not plugin_info:
                logger.error(f"❌ Plugin {plugin_name} not found in registry")
                return False

            # Validate dependencies
            missing_deps = await self._validate_dependencies(plugin_info)
            if missing_deps:
                logger.error(f"❌ Missing dependencies for {plugin_name}: {missing_deps}")
                return False

            # Load plugin using loader
            load_result = await self.loader.load_plugin(plugin_info)
            if not load_result.success:
                logger.error(f"❌ Failed to load {plugin_name}: {load_result.error_message}")
                return False

            plugin_instance = load_result.plugin_instance

            # Initialize plugin
            plugin_instance.set_status(PluginStatus.INITIALIZING)
            init_success = await plugin_instance.initialize()

            if not init_success:
                logger.error(f"❌ Plugin {plugin_name} initialization failed")
                return False

            # Store loaded plugin
            plugin_instance.set_status(PluginStatus.LOADED)
            self.loaded_plugins[plugin_name] = plugin_instance
            self.manager_metrics['total_plugins_loaded'] += 1

            # Auto-start if requested
            if auto_start:
                await self.start_plugin(plugin_name)

            logger.info(f"✅ Plugin {plugin_name} loaded successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")
            return False

    async def start_plugin(self, plugin_name: str) -> bool:
        """
        Start a loaded plugin.

        Args:
            plugin_name: Name of the plugin to start

        Returns:
            True if start successful, False otherwise
        """
        logger.info(f"▶️ Starting plugin: {plugin_name}")

        try:
            if plugin_name not in self.loaded_plugins:
                logger.error(f"❌ Plugin {plugin_name} is not loaded")
                return False

            plugin = self.loaded_plugins[plugin_name]

            if plugin.get_status() == PluginStatus.ACTIVE:
                logger.warning(f"⚠️ Plugin {plugin_name} is already active")
                return True

            # Start plugin
            start_success = await plugin.start()

            if start_success:
                plugin.set_status(PluginStatus.ACTIVE)
                self.active_plugins[plugin_name] = plugin
                self.manager_metrics['total_plugins_active'] += 1

                # Register event handlers
                await self._register_plugin_events(plugin)

                logger.info(f"✅ Plugin {plugin_name} started successfully")
                return True
            else:
                logger.error(f"❌ Plugin {plugin_name} start failed")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to start plugin {plugin_name}: {e}")
            return False

    async def stop_plugin(self, plugin_name: str) -> bool:
        """
        Stop an active plugin.

        Args:
            plugin_name: Name of the plugin to stop

        Returns:
            True if stop successful, False otherwise
        """
        logger.info(f"⏹️ Stopping plugin: {plugin_name}")

        try:
            if plugin_name not in self.active_plugins:
                logger.warning(f"⚠️ Plugin {plugin_name} is not active")
                return True

            plugin = self.active_plugins[plugin_name]

            # Stop plugin
            stop_success = await plugin.stop()

            if stop_success:
                plugin.set_status(PluginStatus.LOADED)
                del self.active_plugins[plugin_name]
                self.manager_metrics['total_plugins_active'] -= 1

                # Unregister event handlers
                await self._unregister_plugin_events(plugin)

                logger.info(f"✅ Plugin {plugin_name} stopped successfully")
                return True
            else:
                logger.error(f"❌ Plugin {plugin_name} stop failed")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to stop plugin {plugin_name}: {e}")
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin completely.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if unload successful, False otherwise
        """
        logger.info(f"📤 Unloading plugin: {plugin_name}")

        try:
            # Stop plugin if active
            if plugin_name in self.active_plugins:
                await self.stop_plugin(plugin_name)

            if plugin_name not in self.loaded_plugins:
                logger.warning(f"⚠️ Plugin {plugin_name} is not loaded")
                return True

            plugin = self.loaded_plugins[plugin_name]

            # Cleanup plugin
            plugin.set_status(PluginStatus.UNLOADING)
            cleanup_success = await plugin.cleanup()

            if cleanup_success:
                plugin.set_status(PluginStatus.UNLOADED)
                del self.loaded_plugins[plugin_name]
                self.manager_metrics['total_plugins_loaded'] -= 1

                logger.info(f"✅ Plugin {plugin_name} unloaded successfully")
                return True
            else:
                logger.error(f"❌ Plugin {plugin_name} cleanup failed")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to unload plugin {plugin_name}: {e}")
            return False

    async def execute_plugin(self, plugin_name: str, input_data: Any, **kwargs) -> Any:
        """
        Execute a plugin's main functionality.

        Args:
            plugin_name: Name of the plugin to execute
            input_data: Input data for processing
            **kwargs: Additional keyword arguments

        Returns:
            Plugin execution result
        """
        if plugin_name not in self.active_plugins:
            raise ValueError(f"Plugin {plugin_name} is not active")

        plugin = self.active_plugins[plugin_name]

        try:
            result = await plugin.execute(input_data, **kwargs)
            return result

        except Exception as e:
            logger.error(f"❌ Plugin execution failed for {plugin_name}: {e}")
            raise

    async def send_event(self, event: PluginEvent):
        """
        Send an event to the plugin system.

        Args:
            event: Event to send
        """
        await self.event_queue.put(event)

    async def _process_events(self):
        """Process events from the event queue"""
        while True:
            try:
                event = await self.event_queue.get()
                await self._route_event(event)
                self.manager_metrics['total_events_processed'] += 1

            except Exception as e:
                logger.error(f"❌ Event processing error: {e}")

    async def _route_event(self, event: PluginEvent):
        """Route event to appropriate plugins"""

        # Route to specific target plugin
        if event.target_plugin and event.target_plugin in self.active_plugins:
            plugin = self.active_plugins[event.target_plugin]
            await plugin.handle_event(event)

        # Route to all plugins listening for this event type
        elif event.event_type in self.event_handlers:
            for plugin_id in self.event_handlers[event.event_type]:
                if plugin_id in self.active_plugins:
                    plugin = self.active_plugins[plugin_id]
                    await plugin.handle_event(event)

    async def _register_plugin_events(self, plugin: BasePlugin):
        """Register plugin event handlers"""
        for event_type in plugin.event_handlers.keys():
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []

            if plugin.plugin_id not in self.event_handlers[event_type]:
                self.event_handlers[event_type].append(plugin.plugin_id)

    async def _unregister_plugin_events(self, plugin: BasePlugin):
        """Unregister plugin event handlers"""
        for event_type in plugin.event_handlers.keys():
            if event_type in self.event_handlers:
                if plugin.plugin_id in self.event_handlers[event_type]:
                    self.event_handlers[event_type].remove(plugin.plugin_id)

    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names"""
        return list(self.loaded_plugins.keys())

    def get_active_plugins(self) -> List[str]:
        """Get list of active plugin names"""
        return list(self.active_plugins.keys())

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a plugin"""
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name].get_info()
        return None

    def get_manager_metrics(self) -> Dict[str, Any]:
        """Get plugin manager performance metrics"""
        return {
            **self.manager_metrics,
            'loaded_plugins_count': len(self.loaded_plugins),
            'active_plugins_count': len(self.active_plugins),
            'registered_plugins_count': len(self.registry.plugins) if hasattr(self.registry, 'plugins') else 0,
            'event_queue_size': self.event_queue.qsize()
        }

    async def _analyze_plugin_file(self, plugin_path: Path) -> Optional[Any]:
        """Analyze a plugin file and extract information"""
        # Placeholder implementation - would analyze Python file for plugin metadata
        _ = plugin_path  # Suppress unused warning
        return None

    async def _analyze_plugin_package(self, plugin_dir: Path) -> Optional[Any]:
        """Analyze a plugin package and extract information"""
        # Placeholder implementation - would analyze plugin package structure
        _ = plugin_dir  # Suppress unused warning
        return None

    async def _validate_dependencies(self, plugin_info: Any) -> List[str]:
        """Validate plugin dependencies"""
        # Placeholder implementation - would check if dependencies are available
        _ = plugin_info  # Suppress unused warning
        return []

    async def _load_configuration(self):
        """Load plugin manager configuration"""
        # Placeholder implementation - would load configuration from file
        pass
