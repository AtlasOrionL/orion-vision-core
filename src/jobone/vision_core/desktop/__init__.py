#!/usr/bin/env python3
"""
Orion Vision Core Desktop Module
Sprint 8.6 - Advanced GUI Framework and Desktop Integration
Orion Vision Core - Autonomous AI Operating System

This module provides advanced desktop integration capabilities including
system tray integration, desktop notifications, window management,
and system-level interactions for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.6.0
Date: 30 Mayıs 2025
"""

# Import desktop components
from .desktop_integration import (
    DesktopIntegration, get_desktop_integration, NotificationType, WindowState,
    SystemIntegrationType, DesktopNotification, WindowInfo
)

# Version information
__version__ = "8.6.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'DesktopIntegration',
    'DesktopNotification',
    'WindowInfo',
    
    # Enums
    'NotificationType',
    'WindowState',
    'SystemIntegrationType',
    
    # Functions
    'get_desktop_integration',
    
    # Utilities
    'initialize_desktop_system',
    'get_desktop_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_desktop_system() -> bool:
    """
    Initialize the complete desktop integration system.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize Desktop Integration
        desktop_integration = get_desktop_integration()
        
        logger.info("🖥️ Desktop system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing desktop system: {e}")
        return False

def get_desktop_info() -> dict:
    """
    Get desktop module information.
    
    Returns:
        Dictionary containing desktop module information
    """
    return {
        'module': 'orion_vision_core.desktop',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'DesktopIntegration': 'Advanced desktop integration and system tray management'
        },
        'features': [
            'System tray integration',
            'Desktop notifications',
            'Window management',
            'File system integration',
            'Clipboard management',
            'System startup integration',
            'Cross-platform compatibility',
            'Context menu integration',
            'File associations',
            'Protocol handlers',
            'System service integration'
        ],
        'notification_types': [
            'Information notifications',
            'Warning notifications',
            'Error notifications',
            'Success notifications',
            'Custom notifications'
        ],
        'window_states': [
            'Normal window state',
            'Minimized window state',
            'Maximized window state',
            'Fullscreen window state',
            'Hidden window state'
        ],
        'system_integration_types': [
            'Startup integration',
            'Context menu integration',
            'File association',
            'Protocol handler',
            'System service'
        ],
        'platform_support': [
            'Windows (full support)',
            'Linux (full support)',
            'macOS (full support)'
        ],
        'desktop_capabilities': [
            'System tray icon with context menu',
            'Desktop notifications with actions',
            'Window state management',
            'Clipboard monitoring and management',
            'File system operations',
            'URL handling',
            'Cross-platform desktop environment detection',
            'Application lifecycle management'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core Desktop Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
