#!/usr/bin/env python3
"""
AI Feedback Overlay - Real-time AI Status Display
Sprint 8.1 - Atlas Prompt 8.1.2: Basic User Input (Text Chat) and AI Feedback Overlays
Orion Vision Core - Autonomous AI Operating System

This module provides an always-on-top overlay window for displaying AI internal
thoughts, task status, and real-time system information.

Author: Orion Development Team
Version: 8.1.0
Date: 30 Mayıs 2025
"""

import sys
import logging
from datetime import datetime
from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QScrollArea, QProgressBar, QPushButton, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, pyqtSlot, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette

from .base_window import BaseWindow, WindowType
from ..core_ai_manager import get_core_ai_manager, AIState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIFeedbackOverlay")

class StatusIndicator(QFrame):
    """Visual status indicator widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.current_state = AIState.OFFLINE
        self.setup_ui()
    
    def setup_ui(self):
        """Setup status indicator UI"""
        self.setStyleSheet("""
            QFrame {
                border-radius: 6px;
                border: 1px solid #404040;
            }
        """)
        self.update_status(AIState.OFFLINE)
    
    def update_status(self, state: AIState):
        """Update status indicator color based on AI state"""
        self.current_state = state
        
        color_map = {
            AIState.IDLE: "#00ff88",      # Green - Ready
            AIState.THINKING: "#ffaa00",   # Orange - Processing
            AIState.PROCESSING: "#4a9eff", # Blue - Working
            AIState.RESPONDING: "#ff6b6b", # Red - Responding
            AIState.EXECUTING: "#aa00ff",  # Purple - Executing
            AIState.ERROR: "#ff0000",      # Red - Error
            AIState.OFFLINE: "#666666"     # Gray - Offline
        }
        
        color = color_map.get(state, "#666666")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 6px;
                border: 1px solid #404040;
            }}
        """)

class ThoughtWidget(QFrame):
    """Individual thought display widget"""
    
    def __init__(self, thought_text: str, parent=None):
        super().__init__(parent)
        self.thought_text = thought_text
        self.setup_ui()
    
    def setup_ui(self):
        """Setup thought widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Thought indicator
        indicator = QLabel("💭")
        indicator.setFixedSize(16, 16)
        indicator.setStyleSheet("font-size: 12px;")
        
        # Thought text
        text_label = QLabel(self.thought_text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            color: #cccccc;
            font-size: 11px;
            background-color: transparent;
        """)
        
        layout.addWidget(indicator)
        layout.addWidget(text_label)
        
        # Style the frame
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 4px;
                margin: 1px;
            }
        """)

class TaskWidget(QFrame):
    """Task status display widget"""
    
    def __init__(self, task_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup task widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Task header
        header_layout = QHBoxLayout()
        
        # Task name
        task_name = self.task_data.get('task_name', 'Unknown Task')
        name_label = QLabel(task_name)
        name_label.setStyleSheet("""
            font-weight: bold;
            font-size: 11px;
            color: #ffffff;
        """)
        
        # Task status
        task_status = self.task_data.get('task_status', 'unknown')
        status_label = QLabel(task_status.upper())
        status_label.setStyleSheet("""
            font-size: 10px;
            color: #00ff88;
            font-weight: bold;
        """)
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        
        # Progress bar
        progress = self.task_data.get('progress', 0.0)
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(progress))
        progress_bar.setFixedHeight(6)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 3px;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                border-radius: 2px;
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(progress_bar)
        
        # Style the frame
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 6px;
                margin: 2px;
            }
        """)

class AIFeedbackOverlay(BaseWindow):
    """
    Always-on-top overlay window for AI feedback and status.
    
    Features:
    - Real-time AI state indicator
    - Internal thoughts display
    - Active tasks monitoring
    - System status information
    - Minimizable/expandable interface
    """
    
    def __init__(self, 
                 window_id: str = "ai_feedback_overlay",
                 title: str = "AI Status",
                 width: int = 320,
                 height: int = 480):
        """Initialize AI feedback overlay"""
        
        # Initialize AI manager connection
        self.ai_manager = get_core_ai_manager()
        
        super().__init__(
            window_id=window_id,
            window_type=WindowType.FEEDBACK,
            title=title,
            width=width,
            height=height,
            transparent=True,
            frameless=True,
            always_on_top=True,
            resizable=False
        )
        
        # Overlay state
        self.is_minimized = False
        self.thought_widgets: List[ThoughtWidget] = []
        self.task_widgets: List[TaskWidget] = []
        self.max_thoughts_display = 5
        self.max_tasks_display = 3
        
        # Connect AI manager signals
        self._connect_ai_signals()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)  # Update every second
        
        logger.info(f"🔮 AI Feedback Overlay initialized: {window_id}")
    
    def setup_content(self):
        """Setup overlay content"""
        # Main container with rounded corners
        self.main_container = QFrame()
        self.main_container.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 240);
                border: 2px solid #00ff88;
                border-radius: 12px;
            }
        """)
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(8)
        
        # Header with status and controls
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Status indicator
        self.status_indicator = StatusIndicator()
        
        # Title
        title_label = QLabel("AI STATUS")
        title_label.setStyleSheet("""
            font-weight: bold;
            font-size: 12px;
            color: #00ff88;
        """)
        
        # Minimize button
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(20, 20)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        self.minimize_btn.clicked.connect(self._toggle_minimize)
        
        header_layout.addWidget(self.status_indicator)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.minimize_btn)
        
        # Current status text
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("""
            color: #cccccc;
            font-size: 11px;
            font-style: italic;
        """)
        self.status_label.setWordWrap(True)
        
        # Expandable content
        self.content_frame = QFrame()
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)
        
        # Thoughts section
        thoughts_label = QLabel("💭 INTERNAL THOUGHTS")
        thoughts_label.setStyleSheet("""
            font-weight: bold;
            font-size: 10px;
            color: #ffaa00;
            margin-top: 4px;
        """)
        
        self.thoughts_scroll = QScrollArea()
        self.thoughts_scroll.setFixedHeight(120)
        self.thoughts_scroll.setWidgetResizable(True)
        self.thoughts_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.thoughts_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.thoughts_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404040;
                border-radius: 6px;
                background-color: rgba(20, 20, 20, 200);
            }
        """)
        
        self.thoughts_content = QWidget()
        self.thoughts_layout = QVBoxLayout(self.thoughts_content)
        self.thoughts_layout.setContentsMargins(4, 4, 4, 4)
        self.thoughts_layout.setSpacing(2)
        self.thoughts_layout.addStretch()
        
        self.thoughts_scroll.setWidget(self.thoughts_content)
        
        # Tasks section
        tasks_label = QLabel("📋 ACTIVE TASKS")
        tasks_label.setStyleSheet("""
            font-weight: bold;
            font-size: 10px;
            color: #4a9eff;
            margin-top: 4px;
        """)
        
        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setFixedHeight(100)
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tasks_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tasks_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404040;
                border-radius: 6px;
                background-color: rgba(20, 20, 20, 200);
            }
        """)
        
        self.tasks_content = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_content)
        self.tasks_layout.setContentsMargins(4, 4, 4, 4)
        self.tasks_layout.setSpacing(2)
        self.tasks_layout.addStretch()
        
        self.tasks_scroll.setWidget(self.tasks_content)
        
        # Add to content frame
        content_layout.addWidget(thoughts_label)
        content_layout.addWidget(self.thoughts_scroll)
        content_layout.addWidget(tasks_label)
        content_layout.addWidget(self.tasks_scroll)
        
        # Add to main container
        container_layout.addWidget(header_frame)
        container_layout.addWidget(self.status_label)
        container_layout.addWidget(self.content_frame)
        
        # Add to main layout
        self.content_layout.addWidget(self.main_container)
        
        # Position overlay at top-right corner
        self._position_overlay()
    
    def _connect_ai_signals(self):
        """Connect AI manager signals"""
        self.ai_manager.state_changed.connect(self._on_state_changed)
        self.ai_manager.status_update.connect(self._on_status_update)
        self.ai_manager.internal_thought.connect(self._on_internal_thought)
        self.ai_manager.task_created.connect(self._on_task_created)
        self.ai_manager.task_updated.connect(self._on_task_updated)
    
    @pyqtSlot(str)
    def _on_state_changed(self, state_str: str):
        """Handle AI state change"""
        try:
            state = AIState(state_str)
            self.status_indicator.update_status(state)
        except ValueError:
            logger.warning(f"Unknown AI state: {state_str}")
    
    @pyqtSlot(str)
    def _on_status_update(self, status: str):
        """Handle status update"""
        self.status_label.setText(status)
    
    @pyqtSlot(str)
    def _on_internal_thought(self, thought: str):
        """Handle new internal thought"""
        self._add_thought_widget(thought)
    
    @pyqtSlot(dict)
    def _on_task_created(self, task_data: Dict[str, Any]):
        """Handle new task creation"""
        self._add_task_widget(task_data)
    
    @pyqtSlot(dict)
    def _on_task_updated(self, task_data: Dict[str, Any]):
        """Handle task update"""
        self._update_task_widget(task_data)
    
    def _add_thought_widget(self, thought: str):
        """Add new thought widget"""
        thought_widget = ThoughtWidget(thought)
        
        # Insert before stretch
        insert_position = self.thoughts_layout.count() - 1
        self.thoughts_layout.insertWidget(insert_position, thought_widget)
        
        self.thought_widgets.append(thought_widget)
        
        # Limit number of displayed thoughts
        if len(self.thought_widgets) > self.max_thoughts_display:
            old_widget = self.thought_widgets.pop(0)
            old_widget.deleteLater()
        
        # Auto-scroll to bottom
        QTimer.singleShot(50, self._scroll_thoughts_to_bottom)
    
    def _add_task_widget(self, task_data: Dict[str, Any]):
        """Add new task widget"""
        task_widget = TaskWidget(task_data)
        
        # Insert before stretch
        insert_position = self.tasks_layout.count() - 1
        self.tasks_layout.insertWidget(insert_position, task_widget)
        
        self.task_widgets.append(task_widget)
        
        # Limit number of displayed tasks
        if len(self.task_widgets) > self.max_tasks_display:
            old_widget = self.task_widgets.pop(0)
            old_widget.deleteLater()
    
    def _update_task_widget(self, task_data: Dict[str, Any]):
        """Update existing task widget"""
        # For now, just refresh all task widgets
        # In a more sophisticated implementation, we'd find and update the specific widget
        self._refresh_tasks()
    
    def _refresh_tasks(self):
        """Refresh all task widgets"""
        # Clear existing task widgets
        for widget in self.task_widgets:
            widget.deleteLater()
        self.task_widgets.clear()
        
        # Add current active tasks
        active_tasks = self.ai_manager.get_active_tasks()
        for task_data in active_tasks[-self.max_tasks_display:]:
            self._add_task_widget(task_data)
    
    def _scroll_thoughts_to_bottom(self):
        """Scroll thoughts to bottom"""
        scrollbar = self.thoughts_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _toggle_minimize(self):
        """Toggle overlay minimize state"""
        if self.is_minimized:
            self.content_frame.show()
            self.minimize_btn.setText("−")
            self.resize(320, 480)
        else:
            self.content_frame.hide()
            self.minimize_btn.setText("+")
            self.resize(320, 80)
        
        self.is_minimized = not self.is_minimized
        self._position_overlay()
    
    def _position_overlay(self):
        """Position overlay at top-right corner of screen"""
        try:
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            
            x = screen_geometry.width() - self.width() - 20
            y = 20
            
            self.move(x, y)
        except Exception as e:
            logger.warning(f"Could not position overlay: {e}")
    
    def _update_display(self):
        """Update display with current AI status"""
        # This method can be used for periodic updates
        pass
    
    def get_window_info(self) -> Dict[str, Any]:
        """Get overlay window information"""
        return {
            'type': 'ai_feedback_overlay',
            'description': 'Real-time AI status and feedback overlay',
            'is_minimized': self.is_minimized,
            'thoughts_count': len(self.thought_widgets),
            'tasks_count': len(self.task_widgets),
            'ai_manager_connected': self.ai_manager is not None
        }
