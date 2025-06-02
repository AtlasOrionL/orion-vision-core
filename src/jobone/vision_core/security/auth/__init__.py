"""
Security Authentication Module Exports

This module exports authentication classes and utilities.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

from .auth_manager import (
    AuthenticationManager,
    User,
    Session,
    AuthMethod,
    UserRole,
    SessionStatus
)

# Alias for backward compatibility
AuthManager = AuthenticationManager

__all__ = [
    'AuthenticationManager',
    'AuthManager',  # Alias
    'User',
    'Session',
    'AuthMethod',
    'UserRole',
    'SessionStatus'
]

__version__ = "9.2.0"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.2 - Advanced Features & Enhanced Capabilities"
