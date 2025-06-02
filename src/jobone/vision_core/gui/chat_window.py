#!/usr/bin/env python3
"""
Chat Window - Text Chat Interface
Sprint 8.1 - Atlas Prompt 8.1.2: Basic User Input (Text Chat) and AI Feedback Overlays
Orion Vision Core - Autonomous AI Operating System

This module provides the text chat interface for user-AI interaction in the
Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.1.0
Date: 30 Mayıs 2025
"""

import sys
import logging
from datetime import datetime
from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QScrollArea, QFrame, QLabel, QSplitter,
    QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor, QPixmap, QIcon

from .base_window import BaseWindow, WindowType
from ..core_ai_manager import get_core_ai_manager, MessageType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatWindow")

class MessageWidget(QFrame):
    """Individual message widget for chat display"""
    
    def __init__(self, message_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.message_data = message_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup message widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        
        # Message header
        header_layout = QHBoxLayout()
        
        # Sender info
        sender = self.message_data.get('sender', 'unknown')
        message_type = self.message_data.get('message_type', 'unknown')
        timestamp = self.message_data.get('timestamp', '')
        
        if isinstance(timestamp, str):
            try:
                timestamp_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = timestamp_obj.strftime('%H:%M:%S')
            except:
                time_str = timestamp
        else:
            time_str = timestamp.strftime('%H:%M:%S') if timestamp else ''
        
        # Sender label
        sender_label = QLabel(f"{sender.upper()}")
        sender_label.setStyleSheet(f"""
            font-weight: bold;
            color: {'#00ff88' if sender == 'ai' else '#4a9eff'};
            font-size: 11px;
        """)
        
        # Time label
        time_label = QLabel(time_str)
        time_label.setStyleSheet("""
            color: #888888;
            font-size: 10px;
        """)
        
        header_layout.addWidget(sender_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)
        
        # Message content
        content = self.message_data.get('content', '')
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Style based on message type and sender
        if sender == 'ai':
            self.setStyleSheet("""
                QFrame {
                    background-color: #2a4a3a;
                    border: 1px solid #00ff88;
                    border-radius: 8px;
                    margin: 2px;
                }
            """)
            content_label.setStyleSheet("""
                color: #ffffff;
                font-size: 13px;
                padding: 5px;
                background-color: transparent;
            """)
        elif sender == 'user':
            self.setStyleSheet("""
                QFrame {
                    background-color: #2a3a4a;
                    border: 1px solid #4a9eff;
                    border-radius: 8px;
                    margin: 2px;
                }
            """)
            content_label.setStyleSheet("""
                color: #ffffff;
                font-size: 13px;
                padding: 5px;
                background-color: transparent;
            """)
        else:  # system messages
            self.setStyleSheet("""
                QFrame {
                    background-color: #3a3a2a;
                    border: 1px solid #ffaa00;
                    border-radius: 8px;
                    margin: 2px;
                }
            """)
            content_label.setStyleSheet("""
                color: #ffaa00;
                font-size: 12px;
                font-style: italic;
                padding: 5px;
                background-color: transparent;
            """)
        
        layout.addLayout(header_layout)
        layout.addWidget(content_label)

class ChatWindow(BaseWindow):
    """
    Chat window for text-based user-AI interaction.
    
    Features:
    - Real-time chat interface
    - Message history display
    - User input handling
    - AI response integration
    - Auto-scroll functionality
    """
    
    # Signals
    message_sent = pyqtSignal(str)  # User message
    
    def __init__(self, 
                 window_id: str = "chat_window",
                 title: str = "Orion AI Chat",
                 width: int = 600,
                 height: int = 700):
        """Initialize chat window"""
        
        # Initialize AI manager connection
        self.ai_manager = get_core_ai_manager()
        
        super().__init__(
            window_id=window_id,
            window_type=WindowType.CHAT,
            title=title,
            width=width,
            height=height,
            transparent=False,
            frameless=False,
            always_on_top=False,
            resizable=True
        )
        
        # Chat state
        self.message_widgets: List[MessageWidget] = []
        self.auto_scroll = True
        
        # Connect AI manager signals
        self._connect_ai_signals()
        
        logger.info(f"💬 Chat Window initialized: {window_id}")
    
    def setup_content(self):
        """Setup chat window content"""
        # Main splitter for resizable layout
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Chat display area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Chat content widget
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setContentsMargins(5, 5, 5, 5)
        self.chat_layout.setSpacing(5)
        self.chat_layout.addStretch()  # Push messages to top
        
        self.chat_scroll.setWidget(self.chat_content)
        
        # Input area
        input_frame = QFrame()
        input_frame.setFixedHeight(100)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                border: 1px solid #606060;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #00ff88;
            }
        """)
        self.input_field.returnPressed.connect(self._send_message)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: #000000;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #00cc66;
            }
            QPushButton:pressed {
                background-color: #009944;
            }
        """)
        self.send_button.clicked.connect(self._send_message)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
            }
        """)
        self.clear_button.clicked.connect(self._clear_chat)
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.send_button)
        
        input_layout.addWidget(self.input_field)
        input_layout.addLayout(button_layout)
        
        # Add to splitter
        splitter.addWidget(self.chat_scroll)
        splitter.addWidget(input_frame)
        splitter.setSizes([600, 100])  # Chat area larger than input
        
        self.content_layout.addWidget(splitter)
        
        # Load existing conversation history
        self._load_conversation_history()
    
    def _connect_ai_signals(self):
        """Connect AI manager signals"""
        self.ai_manager.message_received.connect(self._on_message_received)
        self.ai_manager.message_sent.connect(self._on_message_sent)
    
    @pyqtSlot(dict)
    def _on_message_received(self, message_data: Dict[str, Any]):
        """Handle new message from AI manager"""
        self._add_message_widget(message_data)
    
    @pyqtSlot(dict)
    def _on_message_sent(self, message_data: Dict[str, Any]):
        """Handle message sent by AI"""
        # AI responses are already handled by message_received
        pass
    
    def _send_message(self):
        """Send user message"""
        message_text = self.input_field.text().strip()
        if not message_text:
            return
        
        # Clear input field
        self.input_field.clear()
        
        # Process message through AI manager
        try:
            # AI manager will handle adding the user message and generating response
            response = self.ai_manager.process_user_input(message_text)
            
            # Emit signal for other components
            self.message_sent.emit(message_text)
            
            logger.info(f"💬 Message sent: {message_text[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
    
    def _add_message_widget(self, message_data: Dict[str, Any]):
        """Add message widget to chat display"""
        try:
            # Create message widget
            message_widget = MessageWidget(message_data)
            
            # Insert before the stretch (second to last position)
            insert_position = self.chat_layout.count() - 1
            self.chat_layout.insertWidget(insert_position, message_widget)
            
            # Store reference
            self.message_widgets.append(message_widget)
            
            # Auto-scroll to bottom
            if self.auto_scroll:
                QTimer.singleShot(100, self._scroll_to_bottom)
            
        except Exception as e:
            logger.error(f"❌ Error adding message widget: {e}")
    
    def _scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _clear_chat(self):
        """Clear chat display"""
        # Remove all message widgets
        for widget in self.message_widgets:
            widget.deleteLater()
        
        self.message_widgets.clear()
        
        # Clear layout (except stretch)
        while self.chat_layout.count() > 1:
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        logger.info("💬 Chat cleared")
    
    def _load_conversation_history(self):
        """Load existing conversation history"""
        try:
            history = self.ai_manager.get_conversation_history()
            
            for message_data in history:
                self._add_message_widget(message_data)
            
            logger.info(f"💬 Loaded {len(history)} messages from history")
            
        except Exception as e:
            logger.error(f"❌ Error loading conversation history: {e}")
    
    def get_window_info(self) -> Dict[str, Any]:
        """Get chat window information"""
        return {
            'type': 'chat',
            'description': 'Text chat interface for user-AI interaction',
            'message_count': len(self.message_widgets),
            'auto_scroll': self.auto_scroll,
            'ai_manager_connected': self.ai_manager is not None
        }
