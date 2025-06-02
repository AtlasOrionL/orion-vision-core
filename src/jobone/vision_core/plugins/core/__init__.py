"""
Plugin Core Module Exports

This module exports plugin core classes and utilities.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

from .plugin_manager import (
    PluginManager,
    PluginInstance,
    PluginMetadata,
    PluginState,
    PluginType
)

__all__ = [
    'PluginManager',
    'PluginInstance',
    'PluginMetadata',
    'PluginState',
    'PluginType'
]

__version__ = "9.2.0"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.2 - Advanced Features & Enhanced Capabilities"
