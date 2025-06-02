"""
Communication Routing Module Exports

This module exports routing classes and utilities.
Part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

from .message_router import MessageRouter, RoutingStrategy

__all__ = [
    'MessageRouter',
    'RoutingStrategy'
]

__version__ = "9.1.1.1"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.1.1.1 - Core Framework Optimization"
