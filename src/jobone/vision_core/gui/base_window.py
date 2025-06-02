#!/usr/bin/env python3
"""
BaseWindow Abstract Class
Sprint 8.1 - Atlas Prompt 8.1.1: GUI Framework and Basic Window System Setup
Orion Vision Core - Autonomous AI Operating System

This module provides the abstract base class for all GUI windows in the
Orion Vision Core autonomous AI operating system, supporting transparency,
frameless windows, and modular window management.

Author: Orion Development Team
Version: 8.1.0
Date: 30 Mayıs 2025
"""

import sys
import logging
from abc import ABC, ABCMeta, abstractmethod
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QApplication
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect,
    pyqtSignal, QPoint, QSize
)
from PyQt6.QtGui import (
    QPalette, QColor, QFont, QPainter, QPaintEvent, QMouseEvent,
    QMoveEvent, QResizeEvent
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BaseWindow")

class WindowType(Enum):
    """Window type enumeration for different window behaviors"""
    MAIN = "main"
    OVERLAY = "overlay"
    DIALOG = "dialog"
    CHAT = "chat"
    FEEDBACK = "feedback"
    SETTINGS = "settings"

class WindowState(Enum):
    """Window state enumeration"""
    HIDDEN = "hidden"
    VISIBLE = "visible"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"

# Create a metaclass that resolves the conflict between QWidget and ABC
class MetaQWidgetABC(type(QWidget), ABCMeta):
    """Metaclass that combines QWidget's metaclass with ABCMeta"""
    pass

class BaseWindow(QWidget, metaclass=MetaQWidgetABC):
    """
    Abstract base class for all Orion Vision Core GUI windows.
    
    Provides common functionality for:
    - Transparency and frameless window capabilities
    - Window lifecycle management
    - Modular window system integration
    - Event handling and state management
    """
    
    # Signals for window lifecycle events
    window_created = pyqtSignal(str)  # window_id
    window_shown = pyqtSignal(str)    # window_id
    window_hidden = pyqtSignal(str)   # window_id
    window_closed = pyqtSignal(str)   # window_id
    window_moved = pyqtSignal(str, QPoint)  # window_id, position
    window_resized = pyqtSignal(str, QSize)  # window_id, size
    
    def __init__(self, 
                 window_id: str,
                 window_type: WindowType = WindowType.MAIN,
                 title: str = "Orion Vision Core",
                 width: int = 800,
                 height: int = 600,
                 transparent: bool = False,
                 frameless: bool = False,
                 always_on_top: bool = False,
                 resizable: bool = True):
        """
        Initialize the base window.
        
        Args:
            window_id: Unique identifier for this window
            window_type: Type of window (main, overlay, dialog, etc.)
            title: Window title
            width: Initial window width
            height: Initial window height
            transparent: Enable window transparency
            frameless: Remove window frame/decorations
            always_on_top: Keep window always on top
            resizable: Allow window resizing
        """
        super().__init__()
        
        # Window properties
        self.window_id = window_id
        self.window_type = window_type
        self.window_state = WindowState.HIDDEN
        self.title = title
        self.transparent = transparent
        self.frameless = frameless
        self.always_on_top = always_on_top
        self.resizable = resizable
        
        # Window geometry
        self.initial_width = width
        self.initial_height = height
        
        # Drag functionality for frameless windows
        self.dragging = False
        self.drag_position = QPoint()
        
        # Animation support
        self.fade_animation = None
        self.move_animation = None
        
        # Initialize window
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        
        logger.info(f"🪟 BaseWindow created: {self.window_id} ({self.window_type.value})")
        self.window_created.emit(self.window_id)
    
    def _setup_window(self):
        """Setup window properties and flags"""
        # Set window title
        self.setWindowTitle(self.title)
        
        # Set initial size
        self.resize(self.initial_width, self.initial_height)
        
        # Configure window flags
        flags = Qt.WindowType.Window
        
        if self.frameless:
            flags |= Qt.WindowType.FramelessWindowHint
        
        if self.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        
        if not self.resizable:
            flags |= Qt.WindowType.MSWindowsFixedSizeDialogHint
        
        self.setWindowFlags(flags)
        
        # Configure transparency
        if self.transparent:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setWindowOpacity(0.95)
        
        # Set window properties
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Apply modern styling
        self._apply_modern_styling()
    
    def _apply_modern_styling(self):
        """Apply modern dark theme styling"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            
            QFrame {
                border: 1px solid #404040;
                border-radius: 8px;
                background-color: #2b2b2b;
            }
            
            QPushButton {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #505050;
                border-color: #707070;
            }
            
            QPushButton:pressed {
                background-color: #353535;
            }
            
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
        """)
        
        # Add drop shadow effect for non-transparent windows
        if not self.transparent:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 5)
            self.setGraphicsEffect(shadow)
    
    def _setup_ui(self):
        """Setup the user interface - to be implemented by subclasses"""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Create title bar for frameless windows
        if self.frameless:
            self._create_title_bar()
        
        # Create content area
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        
        self.main_layout.addWidget(self.content_frame)
        
        # Call abstract method for subclass UI setup
        self.setup_content()
    
    def _create_title_bar(self):
        """Create custom title bar for frameless windows"""
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setStyleSheet("""
            #titleBar {
                background-color: #1e1e1e;
                border: none;
                border-bottom: 1px solid #404040;
            }
        """)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # Window title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Window controls
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.clicked.connect(self.showMinimized)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(self.minimize_btn)
        title_layout.addWidget(self.close_btn)
        
        self.main_layout.addWidget(self.title_bar)
        
        # Enable dragging
        self.title_bar.mousePressEvent = self._title_bar_mouse_press
        self.title_bar.mouseMoveEvent = self._title_bar_mouse_move
    
    def _connect_signals(self):
        """Connect internal signals"""
        pass
    
    @abstractmethod
    def setup_content(self):
        """
        Setup the main content of the window.
        Must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def get_window_info(self) -> Dict[str, Any]:
        """
        Get window information for the GUI manager.
        Must be implemented by subclasses.
        
        Returns:
            Dictionary containing window information
        """
        pass
    
    def show_window(self):
        """Show the window with fade-in animation"""
        self.window_state = WindowState.VISIBLE
        
        if self.transparent:
            self.setWindowOpacity(0.0)
            self.show()
            self._fade_in()
        else:
            self.show()
        
        logger.info(f"🪟 Window shown: {self.window_id}")
        self.window_shown.emit(self.window_id)
    
    def hide_window(self):
        """Hide the window with fade-out animation"""
        self.window_state = WindowState.HIDDEN
        
        if self.transparent:
            self._fade_out()
        else:
            self.hide()
        
        logger.info(f"🪟 Window hidden: {self.window_id}")
        self.window_hidden.emit(self.window_id)
    
    def _fade_in(self):
        """Fade in animation for transparent windows"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(0.95)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.start()
    
    def _fade_out(self):
        """Fade out animation for transparent windows"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.95)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
    
    def _title_bar_mouse_press(self, event: QMouseEvent):
        """Handle title bar mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def _title_bar_mouse_move(self, event: QMouseEvent):
        """Handle title bar mouse move for dragging"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release to stop dragging"""
        self.dragging = False
        super().mouseReleaseEvent(event)
    
    def moveEvent(self, event: QMoveEvent):
        """Handle window move events"""
        super().moveEvent(event)
        self.window_moved.emit(self.window_id, self.pos())
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.window_resized.emit(self.window_id, self.size())
    
    def closeEvent(self, event):
        """Handle window close events"""
        logger.info(f"🪟 Window closing: {self.window_id}")
        self.window_closed.emit(self.window_id)
        super().closeEvent(event)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current window state"""
        return {
            'window_id': self.window_id,
            'window_type': self.window_type.value,
            'window_state': self.window_state.value,
            'title': self.title,
            'geometry': {
                'x': self.x(),
                'y': self.y(),
                'width': self.width(),
                'height': self.height()
            },
            'properties': {
                'transparent': self.transparent,
                'frameless': self.frameless,
                'always_on_top': self.always_on_top,
                'resizable': self.resizable
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # This is for testing the BaseWindow class
    class TestWindow(BaseWindow):
        def setup_content(self):
            label = QLabel("Test Window Content")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
        
        def get_window_info(self):
            return {
                'type': 'test',
                'description': 'Test window for BaseWindow class'
            }
    
    app = QApplication(sys.argv)
    
    # Test different window types
    main_window = TestWindow(
        window_id="test_main",
        window_type=WindowType.MAIN,
        title="Test Main Window",
        width=600,
        height=400
    )
    
    overlay_window = TestWindow(
        window_id="test_overlay",
        window_type=WindowType.OVERLAY,
        title="Test Overlay",
        width=300,
        height=200,
        transparent=True,
        frameless=True,
        always_on_top=True
    )
    
    main_window.show_window()
    overlay_window.show_window()
    
    sys.exit(app.exec())
