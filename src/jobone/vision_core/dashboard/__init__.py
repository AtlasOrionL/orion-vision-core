#!/usr/bin/env python3
"""
Orion Vision Core Dashboard Module
Sprint 8.7 - Comprehensive System Dashboard and Monitoring
Orion Vision Core - Autonomous AI Operating System

This module provides comprehensive system dashboard and monitoring capabilities
including real-time metrics, module status tracking, alert management,
and interactive control panels for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.7.0
Date: 31 Mayıs 2025
"""

# Check PyQt6 availability first
try:
    import PyQt6
    PYQT_AVAILABLE = True

    # Import dashboard components
    from .system_dashboard import (
        SystemDashboard, get_system_dashboard, create_dashboard_application,
        DashboardMode, MetricType, AlertLevel, SystemMetric, SystemAlert,
        SystemMonitorThread
    )

except ImportError:
    PYQT_AVAILABLE = False

    # Create dummy classes for when PyQt6 is not available
    class SystemDashboard:
        def __init__(self):
            pass

        def show_dashboard(self):
            print("⚠️ Dashboard not available - PyQt6 not installed")
            return False

    def get_system_dashboard():
        return SystemDashboard()

    def create_dashboard_application():
        print("⚠️ Dashboard application not available - PyQt6 not installed")
        return None

    # Dummy enums
    class DashboardMode:
        OVERVIEW = "overview"

    class MetricType:
        CPU = "cpu"

    class AlertLevel:
        INFO = "info"

# Version information
__version__ = "8.7.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'SystemDashboard',
    'SystemMonitorThread',
    'SystemMetric',
    'SystemAlert',

    # Enums
    'DashboardMode',
    'MetricType',
    'AlertLevel',

    # Functions
    'get_system_dashboard',
    'create_dashboard_application',

    # Utilities
    'initialize_dashboard_system',
    'get_dashboard_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_dashboard_system() -> bool:
    """
    Initialize the complete dashboard system.

    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize System Dashboard
        dashboard = get_system_dashboard()

        logger.info("📊 Dashboard system initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Error initializing dashboard system: {e}")
        return False

def get_dashboard_info() -> dict:
    """
    Get dashboard module information.

    Returns:
        Dictionary containing dashboard module information
    """
    return {
        'module': 'orion_vision_core.dashboard',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'SystemDashboard': 'Comprehensive real-time system monitoring dashboard',
            'SystemMonitorThread': 'Background system metrics collection thread',
            'SystemMetric': 'System metric data structure',
            'SystemAlert': 'System alert data structure'
        },
        'features': [
            'Real-time system monitoring',
            'CPU, Memory, Disk, Network metrics',
            'Module status tracking',
            'Interactive control panels',
            'Alert management system',
            'Visual analytics and charts',
            'Performance monitoring',
            'System health tracking',
            'Customizable refresh rates',
            'Multi-tab interface',
            'Export capabilities',
            'Theme integration',
            'Background monitoring thread',
            'Automatic alert generation',
            'Status indicators',
            'Uptime tracking'
        ],
        'dashboard_modes': [
            'Overview mode',
            'Detailed mode',
            'Compact mode',
            'Fullscreen mode'
        ],
        'metric_types': [
            'CPU usage metrics',
            'Memory usage metrics',
            'Disk usage metrics',
            'Network I/O metrics',
            'Module status metrics',
            'Task count metrics',
            'Workflow status metrics',
            'AI activity metrics'
        ],
        'alert_levels': [
            'Info alerts',
            'Warning alerts',
            'Error alerts',
            'Critical alerts'
        ],
        'dashboard_tabs': [
            'Overview - System status and module overview',
            'Metrics - Detailed system metrics with controls',
            'Modules - Module status and management',
            'Alerts - Alert management and filtering',
            'Logs - System logs with filtering and export'
        ],
        'monitoring_capabilities': [
            'Real-time CPU monitoring',
            'Memory usage tracking',
            'Disk space monitoring',
            'Network I/O statistics',
            'Process count tracking',
            'Module health checking',
            'Automatic alert generation',
            'Threshold-based warnings',
            'Background data collection',
            'Historical data tracking'
        ],
        'ui_features': [
            'Modern PyQt6 interface',
            'Professional dark theme',
            'Progress bars and indicators',
            'Interactive tables',
            'Tabbed interface',
            'Status bar with uptime',
            'Refresh controls',
            'Filter capabilities',
            'Export functionality',
            'Responsive layout'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core Dashboard Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
