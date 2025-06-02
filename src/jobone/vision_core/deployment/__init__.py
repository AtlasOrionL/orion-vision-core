#!/usr/bin/env python3
"""
Orion Vision Core Deployment Module
Sprint 8.8 - Final Integration and Production Readiness
Orion Vision Core - Autonomous AI Operating System

This module provides production deployment capabilities including
installation setup, configuration management, service integration,
and system deployment for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.8.0
Date: 31 Mayıs 2025
"""

# Import deployment components
from .production_setup import (
    ProductionSetup, DeploymentConfig, DeploymentType, Platform
)

# Version information
__version__ = "8.8.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'ProductionSetup',
    'DeploymentConfig',
    
    # Enums
    'DeploymentType',
    'Platform',
    
    # Utilities
    'get_deployment_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def get_deployment_info() -> dict:
    """
    Get deployment module information.
    
    Returns:
        Dictionary containing deployment module information
    """
    return {
        'module': 'orion_vision_core.deployment',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'ProductionSetup': 'Complete production deployment setup and configuration',
            'DeploymentConfig': 'Deployment configuration data structure'
        },
        'features': [
            'Production environment setup',
            'Cross-platform deployment',
            'Service integration',
            'Desktop integration',
            'Configuration management',
            'Dependency management',
            'Directory structure creation',
            'Startup script generation',
            'Installation validation',
            'System service setup',
            'Desktop file creation',
            'Requirements management',
            'Logging configuration',
            'Platform detection',
            'Path management'
        ],
        'deployment_types': [
            'Standalone deployment',
            'System service deployment',
            'Docker deployment',
            'Systemd service deployment'
        ],
        'supported_platforms': [
            'Windows (full support)',
            'Linux (full support)',
            'macOS (full support)'
        ],
        'installation_features': [
            'Automatic directory structure creation',
            'Application file copying',
            'Configuration file generation',
            'Dependency setup',
            'Service registration',
            'Desktop integration',
            'Startup script creation',
            'Installation validation'
        ],
        'service_integration': [
            'Linux systemd service',
            'Windows service (planned)',
            'macOS launchd service (planned)',
            'Auto-start configuration',
            'Service management'
        ],
        'desktop_integration': [
            'Linux desktop files',
            'Windows shortcuts (planned)',
            'macOS app bundles (planned)',
            'Application menu integration',
            'Icon management'
        ],
        'configuration_management': [
            'JSON configuration files',
            'Logging configuration',
            'Feature toggles',
            'Path management',
            'Platform-specific settings'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core Deployment Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
