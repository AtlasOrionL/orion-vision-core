#!/usr/bin/env python3
"""
GUI Manager - Centralized Window Lifecycle Management
Sprint 8.1 - Atlas Prompt 8.1.1: GUI Framework and Basic Window System Setup
Orion Vision Core - Autonomous AI Operating System

This module provides centralized management for all GUI windows in the
Orion Vision Core autonomous AI operating system, implementing the singleton
pattern for window lifecycle management.

Author: Orion Development Team
Version: 8.1.0
Date: 30 Mayıs 2025
"""

import sys
import logging
import threading
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, asdict
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QIcon

from .base_window import BaseWindow, WindowType, WindowState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GUIManager")

@dataclass
class WindowRegistration:
    """Window registration information"""
    window_id: str
    window_type: WindowType
    window_class: Type[BaseWindow]
    window_instance: Optional[BaseWindow]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    is_active: bool

class GUIManager(QObject):
    """
    Centralized GUI window lifecycle manager using singleton pattern.
    
    Manages:
    - Window creation, registration, and destruction
    - Window state tracking and monitoring
    - Application lifecycle management
    - Event coordination between windows
    """
    
    # Singleton instance
    _instance = None
    _lock = threading.Lock()
    
    # Signals for GUI events
    window_registered = pyqtSignal(str)  # window_id
    window_created = pyqtSignal(str)     # window_id
    window_destroyed = pyqtSignal(str)   # window_id
    application_ready = pyqtSignal()
    application_shutdown = pyqtSignal()
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize GUI Manager (called only once due to singleton)"""
        if hasattr(self, '_initialized'):
            return
        
        super().__init__()
        
        # Application instance
        self.app: Optional[QApplication] = None
        self.app_initialized = False
        
        # Window registry
        self.window_registry: Dict[str, WindowRegistration] = {}
        self.window_classes: Dict[str, Type[BaseWindow]] = {}
        self.active_windows: Dict[str, BaseWindow] = {}
        
        # Manager state
        self.is_running = False
        self.shutdown_requested = False
        
        # Monitoring
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_windows)
        self.monitor_interval = 5000  # 5 seconds
        
        # Statistics
        self.stats = {
            'windows_created': 0,
            'windows_destroyed': 0,
            'total_access_count': 0,
            'startup_time': None,
            'uptime_seconds': 0
        }
        
        self._initialized = True
        logger.info("🎛️ GUI Manager initialized (Singleton)")
    
    def initialize_application(self, app_name: str = "Orion Vision Core") -> bool:
        """
        Initialize the Qt application.
        
        Args:
            app_name: Application name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.app is None:
                self.app = QApplication(sys.argv)
                self.app.setApplicationName(app_name)
                self.app.setApplicationVersion("8.1.0")
                self.app.setOrganizationName("Orion Development Team")
                
                # Set application icon if available
                try:
                    icon = QIcon("assets/orion_icon.png")
                    self.app.setWindowIcon(icon)
                except:
                    logger.warning("Application icon not found, using default")
                
                # Connect application signals
                self.app.aboutToQuit.connect(self._on_application_quit)
                
                self.app_initialized = True
                self.stats['startup_time'] = datetime.now()
                
                logger.info(f"🚀 Qt Application initialized: {app_name}")
                self.application_ready.emit()
                
                return True
            else:
                logger.warning("Application already initialized")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize application: {e}")
            return False
    
    def register_window_class(self, 
                            window_type: str, 
                            window_class: Type[BaseWindow]) -> bool:
        """
        Register a window class for later instantiation.
        
        Args:
            window_type: Unique window type identifier
            window_class: BaseWindow subclass
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not issubclass(window_class, BaseWindow):
                raise ValueError(f"Window class must inherit from BaseWindow")
            
            self.window_classes[window_type] = window_class
            logger.info(f"📝 Window class registered: {window_type} -> {window_class.__name__}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register window class {window_type}: {e}")
            return False
    
    def create_window(self, 
                     window_id: str,
                     window_type: str,
                     **kwargs) -> Optional[BaseWindow]:
        """
        Create and register a new window instance.
        
        Args:
            window_id: Unique window identifier
            window_type: Registered window type
            **kwargs: Additional arguments for window constructor
            
        Returns:
            Window instance if successful, None otherwise
        """
        try:
            # Check if window already exists
            if window_id in self.active_windows:
                logger.warning(f"Window {window_id} already exists")
                return self.active_windows[window_id]
            
            # Check if window class is registered
            if window_type not in self.window_classes:
                raise ValueError(f"Window type {window_type} not registered")
            
            # Create window instance
            window_class = self.window_classes[window_type]
            window = window_class(window_id=window_id, **kwargs)
            
            # Register window
            registration = WindowRegistration(
                window_id=window_id,
                window_type=window.window_type,
                window_class=window_class,
                window_instance=window,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                is_active=True
            )
            
            self.window_registry[window_id] = registration
            self.active_windows[window_id] = window
            
            # Connect window signals
            window.window_closed.connect(lambda wid: self._on_window_closed(wid))
            window.window_shown.connect(lambda wid: self._on_window_shown(wid))
            window.window_hidden.connect(lambda wid: self._on_window_hidden(wid))
            
            # Update statistics
            self.stats['windows_created'] += 1
            
            logger.info(f"🪟 Window created: {window_id} ({window_type})")
            self.window_created.emit(window_id)
            
            return window
            
        except Exception as e:
            logger.error(f"❌ Failed to create window {window_id}: {e}")
            return None
    
    def get_window(self, window_id: str) -> Optional[BaseWindow]:
        """
        Get window instance by ID.
        
        Args:
            window_id: Window identifier
            
        Returns:
            Window instance if found, None otherwise
        """
        if window_id in self.active_windows:
            # Update access statistics
            if window_id in self.window_registry:
                reg = self.window_registry[window_id]
                reg.last_accessed = datetime.now()
                reg.access_count += 1
                self.stats['total_access_count'] += 1
            
            return self.active_windows[window_id]
        
        logger.warning(f"Window not found: {window_id}")
        return None
    
    def show_window(self, window_id: str) -> bool:
        """
        Show a window by ID.
        
        Args:
            window_id: Window identifier
            
        Returns:
            True if successful, False otherwise
        """
        window = self.get_window(window_id)
        if window:
            window.show_window()
            return True
        return False
    
    def hide_window(self, window_id: str) -> bool:
        """
        Hide a window by ID.
        
        Args:
            window_id: Window identifier
            
        Returns:
            True if successful, False otherwise
        """
        window = self.get_window(window_id)
        if window:
            window.hide_window()
            return True
        return False
    
    def close_window(self, window_id: str) -> bool:
        """
        Close and destroy a window by ID.
        
        Args:
            window_id: Window identifier
            
        Returns:
            True if successful, False otherwise
        """
        window = self.get_window(window_id)
        if window:
            window.close()
            return True
        return False
    
    def list_windows(self) -> List[Dict[str, Any]]:
        """
        Get list of all registered windows.
        
        Returns:
            List of window information dictionaries
        """
        windows = []
        for window_id, registration in self.window_registry.items():
            window_info = {
                'window_id': window_id,
                'window_type': registration.window_type.value,
                'window_class': registration.window_class.__name__,
                'is_active': registration.is_active,
                'created_at': registration.created_at.isoformat(),
                'last_accessed': registration.last_accessed.isoformat(),
                'access_count': registration.access_count
            }
            
            # Add current state if window is active
            if registration.window_instance and registration.is_active:
                window_info['current_state'] = registration.window_instance.get_state()
            
            windows.append(window_info)
        
        return windows
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get GUI manager statistics.
        
        Returns:
            Statistics dictionary
        """
        current_time = datetime.now()
        if self.stats['startup_time']:
            uptime = (current_time - self.stats['startup_time']).total_seconds()
            self.stats['uptime_seconds'] = uptime
        
        return {
            **self.stats,
            'active_windows_count': len(self.active_windows),
            'registered_windows_count': len(self.window_registry),
            'registered_classes_count': len(self.window_classes),
            'app_initialized': self.app_initialized,
            'is_running': self.is_running
        }
    
    def start_monitoring(self):
        """Start window monitoring"""
        if not self.monitor_timer.isActive():
            self.monitor_timer.start(self.monitor_interval)
            logger.info("📊 Window monitoring started")
    
    def stop_monitoring(self):
        """Stop window monitoring"""
        if self.monitor_timer.isActive():
            self.monitor_timer.stop()
            logger.info("📊 Window monitoring stopped")
    
    def _monitor_windows(self):
        """Monitor window states and cleanup inactive windows"""
        inactive_windows = []
        
        for window_id, registration in self.window_registry.items():
            if registration.window_instance is None or not registration.is_active:
                inactive_windows.append(window_id)
        
        # Cleanup inactive windows
        for window_id in inactive_windows:
            self._cleanup_window(window_id)
    
    def _on_window_closed(self, window_id: str):
        """Handle window closed event"""
        logger.info(f"🪟 Window closed event: {window_id}")
        self._cleanup_window(window_id)
    
    def _on_window_shown(self, window_id: str):
        """Handle window shown event"""
        logger.debug(f"🪟 Window shown: {window_id}")
    
    def _on_window_hidden(self, window_id: str):
        """Handle window hidden event"""
        logger.debug(f"🪟 Window hidden: {window_id}")
    
    def _cleanup_window(self, window_id: str):
        """Cleanup window registration"""
        if window_id in self.active_windows:
            del self.active_windows[window_id]
        
        if window_id in self.window_registry:
            self.window_registry[window_id].is_active = False
            self.stats['windows_destroyed'] += 1
            
        logger.info(f"🧹 Window cleaned up: {window_id}")
        self.window_destroyed.emit(window_id)
    
    def _on_application_quit(self):
        """Handle application quit event"""
        logger.info("🛑 Application quit requested")
        self.shutdown_requested = True
        self.application_shutdown.emit()
        self.stop_monitoring()
    
    def run(self) -> int:
        """
        Run the GUI application event loop.
        
        Returns:
            Application exit code
        """
        if not self.app_initialized:
            logger.error("❌ Application not initialized. Call initialize_application() first.")
            return -1
        
        try:
            self.is_running = True
            self.start_monitoring()
            
            logger.info("🚀 Starting GUI application event loop")
            exit_code = self.app.exec()
            
            logger.info(f"🛑 GUI application finished with exit code: {exit_code}")
            return exit_code
            
        except Exception as e:
            logger.error(f"❌ Error in GUI application: {e}")
            return -1
        finally:
            self.is_running = False
            self.stop_monitoring()
    
    def shutdown(self):
        """Shutdown the GUI manager and close all windows"""
        logger.info("🛑 Shutting down GUI Manager")
        
        # Close all active windows
        for window_id in list(self.active_windows.keys()):
            self.close_window(window_id)
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Quit application
        if self.app:
            self.app.quit()

# Singleton instance getter
def get_gui_manager() -> GUIManager:
    """Get the singleton GUI manager instance"""
    return GUIManager()

# Example usage and testing
if __name__ == "__main__":
    from .base_window import BaseWindow, WindowType
    
    # Test window class
    class TestWindow(BaseWindow):
        def setup_content(self):
            from PyQt6.QtWidgets import QLabel
            from PyQt6.QtCore import Qt
            
            label = QLabel(f"Test Window: {self.window_id}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
        
        def get_window_info(self):
            return {
                'type': 'test',
                'description': f'Test window: {self.window_id}'
            }
    
    # Initialize GUI manager
    gui_manager = get_gui_manager()
    
    if gui_manager.initialize_application("Orion GUI Test"):
        # Register window class
        gui_manager.register_window_class("test", TestWindow)
        
        # Create test windows
        main_window = gui_manager.create_window(
            "main_test",
            "test",
            window_type=WindowType.MAIN,
            title="Main Test Window"
        )
        
        overlay_window = gui_manager.create_window(
            "overlay_test",
            "test",
            window_type=WindowType.OVERLAY,
            title="Overlay Test",
            transparent=True,
            frameless=True,
            always_on_top=True,
            width=300,
            height=200
        )
        
        # Show windows
        if main_window:
            gui_manager.show_window("main_test")
        if overlay_window:
            gui_manager.show_window("overlay_test")
        
        # Print statistics
        print("📊 GUI Manager Statistics:")
        stats = gui_manager.get_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Run application
        exit_code = gui_manager.run()
        sys.exit(exit_code)
    else:
        logger.error("Failed to initialize GUI application")
        sys.exit(-1)
