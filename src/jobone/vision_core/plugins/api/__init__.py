"""
Plugin API Module Exports

This module exports plugin API classes and utilities.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

from .plugin_api import (
    PluginInterface,
    TaskProcessingPlugin,
    DataTransformationPlugin,
    IntegrationPlugin,
    PluginContext,
    PluginResult,
    PluginCapability,
    PluginPriority,
    PluginRegistry,
    plugin_registry,
    register_plugin,
    PluginUtils
)

__all__ = [
    'PluginInterface',
    'TaskProcessingPlugin',
    'DataTransformationPlugin',
    'IntegrationPlugin',
    'PluginContext',
    'PluginResult',
    'PluginCapability',
    'PluginPriority',
    'PluginRegistry',
    'plugin_registry',
    'register_plugin',
    'PluginUtils'
]

__version__ = "9.2.0"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.2 - Advanced Features & Enhanced Capabilities"
