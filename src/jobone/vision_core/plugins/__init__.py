#!/usr/bin/env python3
"""
🔌 Orion Vision Core - Plugins Module
Sprint 10.2 - Plugin Architecture and Dynamic Loading
Orion Vision Core - Autonomous AI Operating System

This module provides comprehensive plugin architecture including
dynamic plugin loading, plugin management, security validation,
and runtime plugin integration for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 10.2.0
Date: 3 Haziran 2025
"""

# Import plugin components
from .plugin_manager import (
    PluginManager, get_plugin_manager, PluginStatus, PluginType,
    SecurityLevel, Plugin, PluginMetadata, PluginExecution
)
from .plugin_loader import (
    PluginLoader, get_plugin_loader, LoaderType, ValidationResult,
    PluginInterface, PluginConfig
)

# Version information
__version__ = "10.2.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'PluginManager',
    'PluginLoader',
    'Plugin',
    'PluginMetadata',
    'PluginExecution',
    'PluginInterface',
    'PluginConfig',
    'ValidationResult',
    
    # Enums
    'PluginStatus',
    'PluginType',
    'SecurityLevel',
    'LoaderType',
    
    # Functions
    'get_plugin_manager',
    'get_plugin_loader',
    
    # Utilities
    'initialize_plugin_system',
    'get_plugin_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_plugin_system() -> bool:
    """
    Initialize the complete plugin system.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize Plugin Manager
        plugin_manager = get_plugin_manager()
        
        # Initialize Plugin Loader
        plugin_loader = get_plugin_loader()
        
        logger.info("🔌 Plugin system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing plugin system: {e}")
        return False

def get_plugin_info() -> dict:
    """
    Get plugin module information.
    
    Returns:
        Dictionary containing plugin module information
    """
    return {
        'module': 'orion_vision_core.plugins',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'PluginManager': 'Dynamic plugin management and orchestration',
            'PluginLoader': 'Secure plugin loading and validation system'
        },
        'features': [
            'Dynamic plugin loading and unloading',
            'Plugin security validation and sandboxing',
            'Plugin dependency management',
            'Runtime plugin integration',
            'Plugin lifecycle management',
            'Plugin API versioning',
            'Plugin configuration management',
            'Plugin performance monitoring',
            'Plugin error handling and recovery',
            'Plugin marketplace integration'
        ],
        'plugin_types': [
            'Core plugins (system extensions)',
            'UI plugins (interface extensions)',
            'Agent plugins (AI agent extensions)',
            'Workflow plugins (automation extensions)',
            'Integration plugins (external service connectors)',
            'Analytics plugins (data analysis extensions)'
        ],
        'security_levels': [
            'Trusted (full system access)',
            'Sandboxed (limited system access)',
            'Restricted (minimal system access)',
            'Isolated (no system access)'
        ],
        'loader_types': [
            'Python module loader',
            'JavaScript plugin loader',
            'Native library loader',
            'Container-based loader'
        ],
        'plugin_capabilities': [
            'Hot-swappable plugin loading',
            'Plugin dependency resolution',
            'Security policy enforcement',
            'Plugin API compatibility checking',
            'Plugin resource management',
            'Plugin communication framework',
            'Plugin marketplace integration',
            'Plugin development tools'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core Plugins Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
