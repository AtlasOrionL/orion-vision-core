#!/usr/bin/env python3
"""
Orion Vision Core GUI Module
Sprint 8.6 - Advanced GUI Framework and Desktop Integration
Orion Vision Core - Autonomous AI Operating System

This module provides advanced PyQt6 GUI framework capabilities including
modern design systems, visual workflow designer, component management,
and desktop integration for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.6.0
Date: 30 Mayıs 2025
"""

# Check PyQt6 availability first
try:
    import PyQt6
    PYQT_AVAILABLE = True

    # Legacy imports (Sprint 8.1)
    from .base_window import BaseWindow, WindowType, WindowState
    from .gui_manager import GUIManager, get_gui_manager, WindowRegistration
    from .chat_window import ChatWindow
    from .ai_feedback_overlay import AIFeedbackOverlay

    # New imports (Sprint 8.6)
    from .gui_framework import (
        GUIFramework, get_gui_framework, ThemeType, ComponentType, AnimationType,
        GUITheme, GUIComponent
    )
    from .visual_workflow_designer import (
        VisualWorkflowDesigner, get_visual_workflow_designer, NodeType, ConnectionType,
        NodeState, WorkflowNode, WorkflowConnection
    )

except ImportError:
    PYQT_AVAILABLE = False

    # Create dummy classes for when PyQt6 is not available
    class BaseWindow:
        def __init__(self, *args, **kwargs):
            pass

    class GUIManager:
        def __init__(self):
            pass

        def initialize_application(self, app_name):
            return False

    def get_gui_manager():
        return GUIManager()

    def get_gui_framework():
        return None

    def get_visual_workflow_designer():
        return None

    # Dummy enums
    class WindowType:
        MAIN = "main"

    class WindowState:
        NORMAL = "normal"

# Version information
__version__ = "8.6.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Legacy classes (Sprint 8.1)
    'BaseWindow',
    'GUIManager',
    'WindowRegistration',
    'ChatWindow',
    'AIFeedbackOverlay',

    # New classes (Sprint 8.6)
    'GUIFramework',
    'VisualWorkflowDesigner',
    'GUITheme',
    'GUIComponent',
    'WorkflowNode',
    'WorkflowConnection',

    # Legacy enums (Sprint 8.1)
    'WindowType',
    'WindowState',

    # New enums (Sprint 8.6)
    'ThemeType',
    'ComponentType',
    'AnimationType',
    'NodeType',
    'ConnectionType',
    'NodeState',

    # Functions
    'get_gui_manager',
    'get_gui_framework',
    'get_visual_workflow_designer',

    # Utilities
    'initialize_gui_system',
    'create_test_window',
    'get_gui_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_gui_system(app_name: str = "Orion Vision Core") -> bool:
    """
    Initialize the complete GUI system.

    Args:
        app_name: Application name

    Returns:
        True if successful, False otherwise
    """
    try:
        gui_manager = get_gui_manager()
        success = gui_manager.initialize_application(app_name)

        if success:
            logger.info(f"🚀 GUI System initialized: {app_name}")
            return True
        else:
            logger.error("❌ Failed to initialize GUI system")
            return False

    except Exception as e:
        logger.error(f"❌ Error initializing GUI system: {e}")
        return False

def create_test_window(window_id: str = "test_window") -> BaseWindow:
    """
    Create a test window for development and testing.

    Args:
        window_id: Unique window identifier

    Returns:
        Test window instance
    """
    if not PYQT_AVAILABLE:
        logger.warning("⚠️ PyQt6 not available - cannot create test window")
        return BaseWindow()

    from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout
    from PyQt6.QtCore import Qt

    class TestWindow(BaseWindow):
        def setup_content(self):
            # Title
            title_label = QLabel("🚀 Orion Vision Core")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #00ff88;
                margin: 20px;
            """)

            # Subtitle
            subtitle_label = QLabel("Autonomous AI Operating System")
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle_label.setStyleSheet("""
                font-size: 16px;
                color: #cccccc;
                margin-bottom: 20px;
            """)

            # Version info
            version_label = QLabel(f"GUI Framework v{__version__}")
            version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            version_label.setStyleSheet("""
                font-size: 12px;
                color: #888888;
                margin-bottom: 30px;
            """)

            # Test button
            test_button = QPushButton("🧪 Test GUI System")
            test_button.setStyleSheet("""
                QPushButton {
                    background-color: #00ff88;
                    color: #000000;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #00cc66;
                }
                QPushButton:pressed {
                    background-color: #009944;
                }
            """)
            test_button.clicked.connect(self._on_test_clicked)

            # Add widgets to layout
            self.content_layout.addWidget(title_label)
            self.content_layout.addWidget(subtitle_label)
            self.content_layout.addWidget(version_label)
            self.content_layout.addWidget(test_button)
            self.content_layout.addStretch()

        def _on_test_clicked(self):
            """Handle test button click"""
            logger.info("🧪 GUI Test button clicked")

            # Show GUI manager statistics
            gui_manager = get_gui_manager()
            stats = gui_manager.get_statistics()

            print("\n📊 GUI Manager Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")

            print("\n🪟 Active Windows:")
            windows = gui_manager.list_windows()
            for window in windows:
                print(f"   - {window['window_id']} ({window['window_type']})")

        def get_window_info(self):
            return {
                'type': 'test',
                'description': 'Test window for GUI framework',
                'version': __version__
            }

    return TestWindow(
        window_id=window_id,
        window_type=WindowType.MAIN,
        title="Orion Vision Core - GUI Test",
        width=500,
        height=400
    )

def get_gui_info() -> dict:
    """
    Get GUI module information.

    Returns:
        Dictionary containing GUI module information
    """
    return {
        'module': 'orion_vision_core.gui',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'BaseWindow': 'Abstract base class for all GUI windows',
            'GUIManager': 'Centralized window lifecycle management',
            'WindowType': 'Window type enumeration',
            'WindowState': 'Window state enumeration'
        },
        'features': [
            'Transparency support',
            'Frameless windows',
            'Window lifecycle management',
            'Modular window system',
            'Animation support',
            'Modern dark theme',
            'Singleton GUI manager',
            'Window monitoring',
            'Event coordination'
        ],
        'dependencies': [
            'PyQt6',
            'Python 3.8+'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core GUI Module v{__version__} loaded")

# Check PyQt6 availability
try:
    import PyQt6
    logger.info("✅ PyQt6 dependency available")
except ImportError:
    logger.warning("⚠️ PyQt6 not available - GUI functionality will be limited")

# Export version for external access
VERSION = __version__
