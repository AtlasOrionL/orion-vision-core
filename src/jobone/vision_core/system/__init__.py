#!/usr/bin/env python3
"""
Orion Vision Core System Module
Sprint 8.3 - Basic Computer Management and First Autonomous Task
Orion Vision Core - Autonomous AI Operating System

This module provides system management capabilities including terminal
command execution, file system operations, and safety mechanisms for the
Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.3.0
Date: 30 Mayıs 2025
"""

# Import system components
from .terminal_manager import (
    TerminalManager, get_terminal_manager, CommandSafety, ExecutionStatus,
    CommandResult, CommandExecutor
)
from .file_system_manager import (
    FileSystemManager, get_file_system_manager, OperationType, PermissionLevel,
    FileOperation
)
from .system_manager import SystemManager, get_system_manager

# Version information
__version__ = "8.3.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'TerminalManager',
    'FileSystemManager',
    'SystemManager',
    'CommandResult',
    'CommandExecutor',
    'FileOperation',

    # Enums
    'CommandSafety',
    'ExecutionStatus',
    'OperationType',
    'PermissionLevel',

    # Functions
    'get_terminal_manager',
    'get_file_system_manager',
    'get_system_manager',

    # Utilities
    'initialize_system_management',
    'get_system_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_system_management() -> bool:
    """
    Initialize the complete system management system.

    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize Terminal Manager
        terminal_manager = get_terminal_manager()

        # Initialize File System Manager
        file_manager = get_file_system_manager()

        logger.info("🖥️ System management initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Error initializing system management: {e}")
        return False

def get_system_info() -> dict:
    """
    Get system module information.

    Returns:
        Dictionary containing system module information
    """
    return {
        'module': 'orion_vision_core.system',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'TerminalManager': 'Safe terminal command execution with sandboxing',
            'FileSystemManager': 'Secure file system operations with permissions'
        },
        'features': [
            'Safe command execution',
            'Command safety classification',
            'Sandboxed execution environment',
            'Permission-based file access',
            'Comprehensive logging',
            'Background execution',
            'Timeout management',
            'Error handling and recovery',
            'Usage statistics',
            'File integrity checking'
        ],
        'safety_levels': [
            'Safe commands (read-only operations)',
            'Moderate commands (limited modifications)',
            'Dangerous commands (system modifications)',
            'Forbidden commands (blocked entirely)'
        ],
        'supported_operations': {
            'terminal': [
                'System information commands',
                'File listing and viewing',
                'Text processing',
                'Development tools',
                'Network diagnostics'
            ],
            'file_system': [
                'File reading and writing',
                'Directory operations',
                'File copying and moving',
                'Permission management',
                'Integrity verification'
            ]
        }
    }

# Module initialization
logger.info(f"📦 Orion Vision Core System Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
