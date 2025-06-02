"""
Communication Module Exports

This module exports all communication classes and utilities.
Part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

# Core communication classes
from .core import (
    ProtocolType,
    ConnectionStatus,
    MessagePriority,
    MessageType,
    ProtocolConfig,
    CommunicationMessage,
    MessageRoute,
    ProtocolAdapter
)

# Routing classes
from .routing import (
    MessageRouter,
    RoutingStrategy
)

__all__ = [
    # Core
    'ProtocolType',
    'ConnectionStatus',
    'MessagePriority',
    'MessageType',
    'ProtocolConfig',
    'CommunicationMessage',
    'MessageRoute',
    'ProtocolAdapter',
    
    # Routing
    'MessageRouter',
    'RoutingStrategy'
]

__version__ = "9.1.1.1"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.1.1.1 - Core Framework Optimization"
