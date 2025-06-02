#!/usr/bin/env python3
"""
Desktop Integration Manager - Advanced Desktop Integration
Sprint 8.6 - Advanced GUI Framework and Desktop Integration
Orion Vision Core - Autonomous AI Operating System

This module provides advanced desktop integration capabilities including
window management, system tray integration, desktop notifications,
and system-level interactions for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.6.0
Date: 30 Mayıs 2025
"""

import logging
import os
import sys
import platform
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import (
    Qt, QObject, pyqtSignal, QTimer, QThread, QSize, QRect,
    QStandardPaths, QUrl, QProcess
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QFont, QColor, QDesktopServices,
    QScreen, QGuiApplication, QClipboard
)

from ..gui.gui_framework import get_gui_framework

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DesktopIntegration")

class NotificationType(Enum):
    """Notification type enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    CUSTOM = "custom"

class WindowState(Enum):
    """Window state enumeration"""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"
    HIDDEN = "hidden"

class SystemIntegrationType(Enum):
    """System integration type enumeration"""
    STARTUP = "startup"
    CONTEXT_MENU = "context_menu"
    FILE_ASSOCIATION = "file_association"
    PROTOCOL_HANDLER = "protocol_handler"
    SYSTEM_SERVICE = "system_service"

@dataclass
class DesktopNotification:
    """Desktop notification data"""
    notification_id: str
    title: str
    message: str
    notification_type: NotificationType
    icon_path: Optional[str]
    duration: int  # milliseconds
    actions: List[Dict[str, Any]]
    timestamp: datetime
    shown: bool = False

@dataclass
class WindowInfo:
    """Window information"""
    window_id: str
    title: str
    geometry: QRect
    state: WindowState
    visible: bool
    always_on_top: bool
    opacity: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class DesktopIntegration(QObject):
    """
    Advanced desktop integration manager.
    
    Features:
    - System tray integration
    - Desktop notifications
    - Window management
    - File system integration
    - Clipboard management
    - System startup integration
    - Cross-platform compatibility
    """
    
    # Signals
    notification_shown = pyqtSignal(str)  # notification_id
    notification_clicked = pyqtSignal(str)  # notification_id
    tray_icon_activated = pyqtSignal(str)  # activation_reason
    window_state_changed = pyqtSignal(str, str)  # window_id, new_state
    clipboard_changed = pyqtSignal(str)  # clipboard_content
    system_event = pyqtSignal(str, dict)  # event_type, event_data
    
    def __init__(self):
        """Initialize Desktop Integration"""
        super().__init__()
        
        # Component references
        self.gui_framework = get_gui_framework()
        self.app = QApplication.instance()
        
        # Desktop integration configuration
        self.app_name = "Orion Vision Core"
        self.app_version = "8.6.0"
        self.organization_name = "Orion Development Team"
        self.tray_icon_enabled = True
        self.notifications_enabled = True
        self.startup_integration = False
        
        # System information
        self.platform = platform.system()
        self.platform_version = platform.version()
        self.desktop_environment = self._detect_desktop_environment()
        
        # System tray
        self.tray_icon = None
        self.tray_menu = None
        
        # Notification management
        self.notifications: Dict[str, DesktopNotification] = {}
        self.notification_counter = 0
        
        # Window management
        self.managed_windows: Dict[str, WindowInfo] = {}
        self.window_counter = 0
        
        # Clipboard management
        self.clipboard = QGuiApplication.clipboard()
        self.clipboard_history: List[str] = []
        self.clipboard_monitor_enabled = False
        
        # File system integration
        self.file_associations: Dict[str, str] = {}
        self.protocol_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.desktop_stats = {
            'notifications_shown': 0,
            'tray_activations': 0,
            'windows_managed': 0,
            'clipboard_changes': 0,
            'file_operations': 0,
            'system_events': 0
        }
        
        # Initialize desktop integration
        self._initialize_desktop_integration()
        
        logger.info("🖥️ Desktop Integration initialized")
    
    def _initialize_desktop_integration(self):
        """Initialize desktop integration components"""
        try:
            # Set application properties
            if self.app:
                self.app.setApplicationName(self.app_name)
                self.app.setApplicationVersion(self.app_version)
                self.app.setOrganizationName(self.organization_name)
            
            # Initialize system tray
            if self.tray_icon_enabled and QSystemTrayIcon.isSystemTrayAvailable():
                self._initialize_system_tray()
            
            # Initialize clipboard monitoring
            if self.clipboard_monitor_enabled:
                self._initialize_clipboard_monitoring()
            
            # Platform-specific initialization
            self._initialize_platform_specific()
            
        except Exception as e:
            logger.error(f"❌ Error initializing desktop integration: {e}")
    
    def _initialize_system_tray(self):
        """Initialize system tray icon"""
        try:
            # Create tray icon
            self.tray_icon = QSystemTrayIcon()
            
            # Set icon
            icon_path = self._get_app_icon_path()
            if os.path.exists(icon_path):
                self.tray_icon.setIcon(QIcon(icon_path))
            else:
                # Create default icon
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor("#2196F3"))
                self.tray_icon.setIcon(QIcon(pixmap))
            
            # Set tooltip
            self.tray_icon.setToolTip(f"{self.app_name} v{self.app_version}")
            
            # Create context menu
            self._create_tray_menu()
            
            # Connect signals
            self.tray_icon.activated.connect(self._on_tray_icon_activated)
            self.tray_icon.messageClicked.connect(self._on_tray_message_clicked)
            
            # Show tray icon
            self.tray_icon.show()
            
            logger.info("🖥️ System tray icon initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing system tray: {e}")
    
    def _create_tray_menu(self):
        """Create system tray context menu"""
        try:
            # Ensure QAction is accessible in this method
            from PyQt6.QtGui import QAction
            
            self.tray_menu = QMenu()
            
            # Show/Hide action
            show_action = QAction("Show Orion", self.tray_menu)
            show_action.triggered.connect(self._show_main_window)
            self.tray_menu.addAction(show_action)
            
            hide_action = QAction("Hide Orion", self.tray_menu)
            hide_action.triggered.connect(self._hide_main_window)
            self.tray_menu.addAction(hide_action)
            
            self.tray_menu.addSeparator()
            
            # Quick actions
            status_action = QAction("System Status", self.tray_menu)
            status_action.triggered.connect(self._show_system_status)
            self.tray_menu.addAction(status_action)
            
            settings_action = QAction("Settings", self.tray_menu)
            settings_action.triggered.connect(self._show_settings)
            self.tray_menu.addAction(settings_action)
            
            self.tray_menu.addSeparator()
            
            # Exit action
            exit_action = QAction("Exit", self.tray_menu)
            exit_action.triggered.connect(self._exit_application)
            self.tray_menu.addAction(exit_action)
            
            # Set menu
            self.tray_icon.setContextMenu(self.tray_menu)
            
        except Exception as e:
            logger.error(f"❌ Error creating tray menu: {e}")
    
    def _initialize_clipboard_monitoring(self):
        """Initialize clipboard monitoring"""
        try:
            self.clipboard.dataChanged.connect(self._on_clipboard_changed)
            logger.info("🖥️ Clipboard monitoring initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing clipboard monitoring: {e}")
    
    def _initialize_platform_specific(self):
        """Initialize platform-specific features"""
        try:
            if self.platform == "Windows":
                self._initialize_windows_integration()
            elif self.platform == "Linux":
                self._initialize_linux_integration()
            elif self.platform == "Darwin":  # macOS
                self._initialize_macos_integration()
        except Exception as e:
            logger.error(f"❌ Error initializing platform-specific features: {e}")
    
    def _initialize_windows_integration(self):
        """Initialize Windows-specific integration"""
        logger.info("🖥️ Windows integration initialized")
    
    def _initialize_linux_integration(self):
        """Initialize Linux-specific integration"""
        logger.info("🖥️ Linux integration initialized")
    
    def _initialize_macos_integration(self):
        """Initialize macOS-specific integration"""
        logger.info("🖥️ macOS integration initialized")
    
    def show_notification(self, title: str, message: str, 
                         notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5000, icon_path: str = None,
                         actions: List[Dict[str, Any]] = None) -> str:
        """
        Show desktop notification.
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            duration: Duration in milliseconds
            icon_path: Path to notification icon
            actions: List of notification actions
            
        Returns:
            Notification ID
        """
        try:
            if not self.notifications_enabled:
                return None
            
            notification_id = self._generate_notification_id()
            
            # Create notification
            notification = DesktopNotification(
                notification_id=notification_id,
                title=title,
                message=message,
                notification_type=notification_type,
                icon_path=icon_path,
                duration=duration,
                actions=actions or [],
                timestamp=datetime.now()
            )
            
            # Store notification
            self.notifications[notification_id] = notification
            
            # Show notification
            if self.tray_icon and self.tray_icon.isVisible():
                # Use system tray notification
                tray_icon = self._get_notification_icon(notification_type)
                self.tray_icon.showMessage(title, message, tray_icon, duration)
            else:
                # Use alternative notification method
                self._show_alternative_notification(notification)
            
            # Mark as shown
            notification.shown = True
            
            # Update statistics
            self.desktop_stats['notifications_shown'] += 1
            
            # Emit signal
            self.notification_shown.emit(notification_id)
            
            logger.info(f"🖥️ Notification shown: {title}")
            return notification_id
            
        except Exception as e:
            logger.error(f"❌ Error showing notification: {e}")
            return None
    
    def _get_notification_icon(self, notification_type: NotificationType) -> QSystemTrayIcon.MessageIcon:
        """Get system tray icon for notification type"""
        icon_mapping = {
            NotificationType.INFO: QSystemTrayIcon.MessageIcon.Information,
            NotificationType.WARNING: QSystemTrayIcon.MessageIcon.Warning,
            NotificationType.ERROR: QSystemTrayIcon.MessageIcon.Critical,
            NotificationType.SUCCESS: QSystemTrayIcon.MessageIcon.Information,
            NotificationType.CUSTOM: QSystemTrayIcon.MessageIcon.NoIcon
        }
        return icon_mapping.get(notification_type, QSystemTrayIcon.MessageIcon.Information)
    
    def _show_alternative_notification(self, notification: DesktopNotification):
        """Show notification using alternative method"""
        try:
            # Create notification widget
            notification_widget = QWidget()
            notification_widget.setWindowFlags(
                Qt.WindowType.ToolTip | 
                Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.WindowStaysOnTopHint
            )
            notification_widget.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            
            # Set up layout
            layout = QVBoxLayout(notification_widget)
            
            # Title
            title_label = QLabel(notification.title)
            title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            layout.addWidget(title_label)
            
            # Message
            message_label = QLabel(notification.message)
            message_label.setWordWrap(True)
            layout.addWidget(message_label)
            
            # Position notification
            screen = QGuiApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            notification_widget.move(
                screen_geometry.width() - 350,
                screen_geometry.height() - 150
            )
            
            # Show notification
            notification_widget.show()
            
            # Auto-hide after duration
            QTimer.singleShot(notification.duration, notification_widget.close)
            
        except Exception as e:
            logger.error(f"❌ Error showing alternative notification: {e}")
    
    def register_window(self, window: QWidget, window_id: str = None) -> str:
        """
        Register window for management.
        
        Args:
            window: Qt widget to register
            window_id: Optional window ID
            
        Returns:
            Window ID
        """
        try:
            if window_id is None:
                window_id = self._generate_window_id()
            
            # Get window information
            window_info = WindowInfo(
                window_id=window_id,
                title=window.windowTitle(),
                geometry=window.geometry(),
                state=WindowState.NORMAL,
                visible=window.isVisible(),
                always_on_top=bool(window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint),
                opacity=window.windowOpacity()
            )
            
            # Store window
            self.managed_windows[window_id] = window_info
            
            # Update statistics
            self.desktop_stats['windows_managed'] += 1
            
            logger.info(f"🖥️ Window registered: {window_id}")
            return window_id
            
        except Exception as e:
            logger.error(f"❌ Error registering window: {e}")
            return None
    
    def set_window_state(self, window_id: str, state: WindowState) -> bool:
        """Set window state"""
        try:
            if window_id not in self.managed_windows:
                return False
            
            window_info = self.managed_windows[window_id]
            old_state = window_info.state
            window_info.state = state
            
            # Emit signal
            self.window_state_changed.emit(window_id, state.value)
            
            logger.info(f"🖥️ Window state changed: {window_id} ({old_state.value} -> {state.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting window state: {e}")
            return False
    
    def get_clipboard_content(self) -> str:
        """Get current clipboard content"""
        try:
            return self.clipboard.text()
        except Exception as e:
            logger.error(f"❌ Error getting clipboard content: {e}")
            return ""
    
    def set_clipboard_content(self, content: str) -> bool:
        """Set clipboard content"""
        try:
            self.clipboard.setText(content)
            return True
        except Exception as e:
            logger.error(f"❌ Error setting clipboard content: {e}")
            return False
    
    def open_file_location(self, file_path: str) -> bool:
        """Open file location in system file manager"""
        try:
            if os.path.exists(file_path):
                if self.platform == "Windows":
                    os.startfile(os.path.dirname(file_path))
                elif self.platform == "Darwin":  # macOS
                    os.system(f"open -R '{file_path}'")
                else:  # Linux
                    os.system(f"xdg-open '{os.path.dirname(file_path)}'")
                
                self.desktop_stats['file_operations'] += 1
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error opening file location: {e}")
            return False
    
    def open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        try:
            QDesktopServices.openUrl(QUrl(url))
            return True
        except Exception as e:
            logger.error(f"❌ Error opening URL: {e}")
            return False
    
    def _detect_desktop_environment(self) -> str:
        """Detect desktop environment"""
        try:
            if self.platform == "Linux":
                desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
                if desktop:
                    return desktop
                
                # Fallback detection
                if os.environ.get("GNOME_DESKTOP_SESSION_ID"):
                    return "gnome"
                elif os.environ.get("KDE_FULL_SESSION"):
                    return "kde"
                elif os.environ.get("XFCE_SESSION"):
                    return "xfce"
            
            return self.platform.lower()
        except Exception:
            return "unknown"
    
    def _get_app_icon_path(self) -> str:
        """Get application icon path"""
        # Try to find icon in various locations
        possible_paths = [
            "assets/icons/orion.png",
            "icons/orion.png",
            "orion.png"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return ""
    
    def _on_tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        try:
            reason_str = str(reason)
            self.tray_icon_activated.emit(reason_str)
            self.desktop_stats['tray_activations'] += 1
            
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                self._show_main_window()
                
        except Exception as e:
            logger.error(f"❌ Error handling tray icon activation: {e}")
    
    def _on_tray_message_clicked(self):
        """Handle tray message click"""
        try:
            # Find the most recent notification
            recent_notification = None
            for notification in self.notifications.values():
                if notification.shown and (recent_notification is None or 
                    notification.timestamp > recent_notification.timestamp):
                    recent_notification = notification
            
            if recent_notification:
                self.notification_clicked.emit(recent_notification.notification_id)
                
        except Exception as e:
            logger.error(f"❌ Error handling tray message click: {e}")
    
    def _on_clipboard_changed(self):
        """Handle clipboard change"""
        try:
            content = self.clipboard.text()
            if content and content not in self.clipboard_history:
                self.clipboard_history.append(content)
                if len(self.clipboard_history) > 100:  # Keep last 100 items
                    self.clipboard_history.pop(0)
                
                self.clipboard_changed.emit(content)
                self.desktop_stats['clipboard_changes'] += 1
                
        except Exception as e:
            logger.error(f"❌ Error handling clipboard change: {e}")
    
    def _show_main_window(self):
        """Show main application window"""
        try:
            # Find main window
            for window_id, window_info in self.managed_windows.items():
                if "main" in window_id.lower():
                    window = self.gui_framework.get_window(window_id)
                    if window:
                        window.show()
                        window.raise_()
                        window.activateWindow()
                        break
        except Exception as e:
            logger.error(f"❌ Error showing main window: {e}")
    
    def _hide_main_window(self):
        """Hide main application window"""
        try:
            # Find main window
            for window_id, window_info in self.managed_windows.items():
                if "main" in window_id.lower():
                    window = self.gui_framework.get_window(window_id)
                    if window:
                        window.hide()
                        break
        except Exception as e:
            logger.error(f"❌ Error hiding main window: {e}")
    
    def _show_system_status(self):
        """Show system status"""
        logger.info("🖥️ Showing system status")
    
    def _show_settings(self):
        """Show settings"""
        logger.info("🖥️ Showing settings")
    
    def _exit_application(self):
        """Exit application"""
        try:
            if self.app:
                self.app.quit()
        except Exception as e:
            logger.error(f"❌ Error exiting application: {e}")
    
    def _generate_notification_id(self) -> str:
        """Generate unique notification ID"""
        self.notification_counter += 1
        return f"notification_{self.notification_counter:06d}"
    
    def _generate_window_id(self) -> str:
        """Generate unique window ID"""
        self.window_counter += 1
        return f"window_{self.window_counter:06d}"
    
    def get_desktop_stats(self) -> Dict[str, Any]:
        """Get desktop integration statistics"""
        return self.desktop_stats.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'platform': self.platform,
            'platform_version': self.platform_version,
            'desktop_environment': self.desktop_environment,
            'app_name': self.app_name,
            'app_version': self.app_version,
            'tray_available': QSystemTrayIcon.isSystemTrayAvailable(),
            'managed_windows': len(self.managed_windows),
            'active_notifications': len([n for n in self.notifications.values() if n.shown])
        }

# Singleton instance
_desktop_integration = None

def get_desktop_integration() -> DesktopIntegration:
    """Get the singleton Desktop Integration instance"""
    global _desktop_integration
    if _desktop_integration is None:
        _desktop_integration = DesktopIntegration()
    return _desktop_integration
