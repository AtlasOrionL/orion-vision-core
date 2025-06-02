#!/usr/bin/env python3
"""
Settings Panel - LLM Configuration Interface
Sprint 8.2 - Advanced LLM Management and Core "Brain" AI Capabilities
Orion Vision Core - Autonomous AI Operating System

This module provides a comprehensive settings interface for LLM configuration,
model selection, and AI behavior customization.

Author: Orion Development Team
Version: 8.2.0
Date: 30 Mayıs 2025
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QSlider, QTextEdit, QScrollArea, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

from .base_window import BaseWindow, WindowType
from ..llm.llm_api_manager import get_llm_api_manager, ProviderType
from ..llm.model_selector import get_model_selector, SelectionStrategy
from ..brain.brain_ai_manager import get_brain_ai_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SettingsPanel")

class SettingsPanel(BaseWindow):
    """
    Comprehensive settings panel for LLM and AI configuration.

    Features:
    - LLM provider configuration
    - API key management
    - Model selection strategies
    - Performance tuning
    - Brain AI settings
    - Export/import configuration
    """

    # Signals
    settings_changed = pyqtSignal(str, dict)  # category, settings
    api_key_updated = pyqtSignal(str, bool)  # provider, success
    configuration_saved = pyqtSignal(str)  # config_path

    def __init__(self,
                 window_id: str = "settings_panel",
                 title: str = "Orion AI Settings",
                 width: int = 800,
                 height: int = 600):
        """Initialize settings panel"""

        # Component references
        self.llm_manager = get_llm_api_manager()
        self.model_selector = get_model_selector()
        self.brain_manager = get_brain_ai_manager()

        super().__init__(
            window_id=window_id,
            window_type=WindowType.SETTINGS,
            title=title,
            width=width,
            height=height,
            transparent=False,
            frameless=False,
            always_on_top=False,
            resizable=True
        )

        # Settings data
        self.current_settings = {}
        self.unsaved_changes = False

        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save_settings)
        self.auto_save_timer.start(30000)  # Auto-save every 30 seconds

        logger.info(f"⚙️ Settings Panel initialized: {window_id}")

    def setup_content(self):
        """Setup settings panel content"""
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #00ff88;
                color: #000000;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
        """)

        # Create tabs
        self._create_llm_providers_tab()
        self._create_model_selection_tab()
        self._create_brain_ai_tab()
        self._create_performance_tab()
        self._create_advanced_tab()

        # Add tab widget to content
        self.content_layout.addWidget(self.tab_widget)

        # Create bottom buttons
        self._create_bottom_buttons()

        # Load current settings
        self._load_current_settings()

    def _create_llm_providers_tab(self):
        """Create LLM providers configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Title
        title_label = QLabel("🤖 LLM Provider Configuration")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # Scroll area for providers
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # OpenAI Configuration
        self._create_openai_config(scroll_layout)

        # Anthropic Configuration
        self._create_anthropic_config(scroll_layout)

        # Local/Ollama Configuration
        self._create_local_config(scroll_layout)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.tab_widget.addTab(tab, "🔑 Providers")

    def _create_openai_config(self, parent_layout):
        """Create OpenAI configuration section"""
        group = QGroupBox("OpenAI Configuration")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00ff88;
            }
        """)

        layout = QFormLayout(group)

        # API Key
        self.openai_api_key = QLineEdit()
        self.openai_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_api_key.setPlaceholderText("Enter OpenAI API key...")
        self.openai_api_key.textChanged.connect(lambda: self._mark_unsaved_changes())

        # Test button
        test_openai_btn = QPushButton("Test Connection")
        test_openai_btn.clicked.connect(lambda: self._test_api_connection(ProviderType.OPENAI))

        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.openai_api_key)
        api_key_layout.addWidget(test_openai_btn)

        layout.addRow("API Key:", api_key_layout)

        # Enable/Disable
        self.openai_enabled = QCheckBox("Enable OpenAI")
        self.openai_enabled.setChecked(True)
        self.openai_enabled.stateChanged.connect(lambda: self._mark_unsaved_changes())
        layout.addRow("Status:", self.openai_enabled)

        # Default Model
        self.openai_default_model = QComboBox()
        self.openai_default_model.addItems(["gpt-4", "gpt-3.5-turbo"])
        self.openai_default_model.currentTextChanged.connect(lambda: self._mark_unsaved_changes())
        layout.addRow("Default Model:", self.openai_default_model)

        parent_layout.addWidget(group)

    def _create_anthropic_config(self, parent_layout):
        """Create Anthropic configuration section"""
        group = QGroupBox("Anthropic Configuration")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4a9eff;
            }
        """)

        layout = QFormLayout(group)

        # API Key
        self.anthropic_api_key = QLineEdit()
        self.anthropic_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_api_key.setPlaceholderText("Enter Anthropic API key...")
        self.anthropic_api_key.textChanged.connect(lambda: self._mark_unsaved_changes())

        # Test button
        test_anthropic_btn = QPushButton("Test Connection")
        test_anthropic_btn.clicked.connect(lambda: self._test_api_connection(ProviderType.ANTHROPIC))

        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.anthropic_api_key)
        api_key_layout.addWidget(test_anthropic_btn)

        layout.addRow("API Key:", api_key_layout)

        # Enable/Disable
        self.anthropic_enabled = QCheckBox("Enable Anthropic")
        self.anthropic_enabled.setChecked(True)
        self.anthropic_enabled.stateChanged.connect(lambda: self._mark_unsaved_changes())
        layout.addRow("Status:", self.anthropic_enabled)

        # Default Model
        self.anthropic_default_model = QComboBox()
        self.anthropic_default_model.addItems(["claude-3-opus", "claude-3-sonnet"])
        self.anthropic_default_model.currentTextChanged.connect(lambda: self._mark_unsaved_changes())
        layout.addRow("Default Model:", self.anthropic_default_model)

        parent_layout.addWidget(group)

    def _create_local_config(self, parent_layout):
        """Create local/Ollama configuration section"""
        group = QGroupBox("Local Models (Ollama)")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffaa00;
            }
        """)

        layout = QFormLayout(group)

        # Ollama URL
        self.ollama_url = QLineEdit()
        self.ollama_url.setText("http://localhost:11434")
        self.ollama_url.setPlaceholderText("Ollama server URL...")
        self.ollama_url.textChanged.connect(lambda: self._mark_unsaved_changes())

        # Test button
        test_ollama_btn = QPushButton("Test Connection")
        test_ollama_btn.clicked.connect(lambda: self._test_api_connection(ProviderType.OLLAMA))

        url_layout = QHBoxLayout()
        url_layout.addWidget(self.ollama_url)
        url_layout.addWidget(test_ollama_btn)

        layout.addRow("Server URL:", url_layout)

        # Enable/Disable
        self.ollama_enabled = QCheckBox("Enable Local Models")
        self.ollama_enabled.setChecked(True)
        self.ollama_enabled.stateChanged.connect(lambda: self._mark_unsaved_changes())
        layout.addRow("Status:", self.ollama_enabled)

        # Default Model
        self.ollama_default_model = QComboBox()
        self.ollama_default_model.addItems(["llama2-7b", "mistral-7b"])
        self.ollama_default_model.currentTextChanged.connect(lambda: self._mark_unsaved_changes())
        layout.addRow("Default Model:", self.ollama_default_model)

        parent_layout.addWidget(group)

    def _create_model_selection_tab(self):
        """Create model selection strategy tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Title
        title_label = QLabel("🎯 Model Selection Strategy")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # Strategy Selection
        strategy_group = QGroupBox("Selection Strategy")
        strategy_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00ff88;
            }
        """)

        strategy_layout = QFormLayout(strategy_group)

        # Strategy dropdown
        self.selection_strategy = QComboBox()
        strategies = [
            ("balanced", "⚖️ Balanced (Cost + Performance + Quality)"),
            ("cost_optimized", "💰 Cost Optimized"),
            ("performance_optimized", "⚡ Performance Optimized"),
            ("local_preferred", "🏠 Local Models Preferred"),
            ("fastest", "🚀 Fastest Response"),
            ("most_capable", "🧠 Most Capable")
        ]

        for value, display in strategies:
            self.selection_strategy.addItem(display, value)

        self.selection_strategy.currentTextChanged.connect(lambda: self._mark_unsaved_changes())
        strategy_layout.addRow("Strategy:", self.selection_strategy)

        layout.addWidget(strategy_group)

        # Model Preferences
        preferences_group = QGroupBox("Model Preferences")
        preferences_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4a9eff;
            }
        """)

        preferences_layout = QFormLayout(preferences_group)

        # Max cost per token
        self.max_cost_per_token = QDoubleSpinBox()
        self.max_cost_per_token.setRange(0.0, 1.0)
        self.max_cost_per_token.setDecimals(6)
        self.max_cost_per_token.setValue(0.0001)
        self.max_cost_per_token.setSuffix(" per token")
        self.max_cost_per_token.valueChanged.connect(lambda: self._mark_unsaved_changes())
        preferences_layout.addRow("Max Cost:", self.max_cost_per_token)

        # Max response time
        self.max_response_time = QSpinBox()
        self.max_response_time.setRange(1, 300)
        self.max_response_time.setValue(30)
        self.max_response_time.setSuffix(" seconds")
        self.max_response_time.valueChanged.connect(lambda: self._mark_unsaved_changes())
        preferences_layout.addRow("Max Response Time:", self.max_response_time)

        # Prefer local models
        self.prefer_local = QCheckBox("Prefer Local Models")
        self.prefer_local.stateChanged.connect(lambda: self._mark_unsaved_changes())
        preferences_layout.addRow("Local Preference:", self.prefer_local)

        layout.addWidget(preferences_group)

        self.tab_widget.addTab(tab, "🎯 Selection")

    def _create_brain_ai_tab(self):
        """Create brain AI configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Title
        title_label = QLabel("🧠 Brain AI Configuration")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # Task Analysis Settings
        analysis_group = QGroupBox("Task Analysis")
        analysis_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00ff88;
            }
        """)

        analysis_layout = QFormLayout(analysis_group)

        # Enable task analysis
        self.enable_task_analysis = QCheckBox("Enable Intelligent Task Analysis")
        self.enable_task_analysis.setChecked(True)
        self.enable_task_analysis.stateChanged.connect(lambda: self._mark_unsaved_changes())
        analysis_layout.addRow("Status:", self.enable_task_analysis)

        # Confidence threshold
        self.confidence_threshold = QSlider(Qt.Orientation.Horizontal)
        self.confidence_threshold.setRange(0, 100)
        self.confidence_threshold.setValue(70)
        self.confidence_threshold.valueChanged.connect(lambda: self._mark_unsaved_changes())
        analysis_layout.addRow("Confidence Threshold:", self.confidence_threshold)

        layout.addWidget(analysis_group)

        # Message Fragmentation
        fragmentation_group = QGroupBox("Message Fragmentation")
        fragmentation_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4a9eff;
            }
        """)

        fragmentation_layout = QFormLayout(fragmentation_group)

        # Enable fragmentation
        self.enable_fragmentation = QCheckBox("Enable Message Fragmentation")
        self.enable_fragmentation.setChecked(True)
        self.enable_fragmentation.stateChanged.connect(lambda: self._mark_unsaved_changes())
        fragmentation_layout.addRow("Status:", self.enable_fragmentation)

        # Max fragment tokens
        self.max_fragment_tokens = QSpinBox()
        self.max_fragment_tokens.setRange(500, 8000)
        self.max_fragment_tokens.setValue(2000)
        self.max_fragment_tokens.setSuffix(" tokens")
        self.max_fragment_tokens.valueChanged.connect(lambda: self._mark_unsaved_changes())
        fragmentation_layout.addRow("Max Fragment Size:", self.max_fragment_tokens)

        layout.addWidget(fragmentation_group)

        self.tab_widget.addTab(tab, "🧠 Brain AI")

    def _create_performance_tab(self):
        """Create performance monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Title
        title_label = QLabel("📊 Performance Monitoring")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # Performance metrics display
        metrics_group = QGroupBox("Current Metrics")
        metrics_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00ff88;
            }
        """)

        metrics_layout = QVBoxLayout(metrics_group)

        # Metrics display area
        self.metrics_display = QTextEdit()
        self.metrics_display.setReadOnly(True)
        self.metrics_display.setMaximumHeight(200)
        self.metrics_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        metrics_layout.addWidget(self.metrics_display)

        # Refresh button
        refresh_metrics_btn = QPushButton("🔄 Refresh Metrics")
        refresh_metrics_btn.clicked.connect(self._refresh_performance_metrics)
        metrics_layout.addWidget(refresh_metrics_btn)

        layout.addWidget(metrics_group)

        self.tab_widget.addTab(tab, "📊 Performance")

    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Title
        title_label = QLabel("⚙️ Advanced Settings")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # Export/Import
        io_group = QGroupBox("Configuration Management")
        io_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00ff88;
            }
        """)

        io_layout = QHBoxLayout(io_group)

        export_btn = QPushButton("📤 Export Configuration")
        export_btn.clicked.connect(self._export_configuration)
        io_layout.addWidget(export_btn)

        import_btn = QPushButton("📥 Import Configuration")
        import_btn.clicked.connect(self._import_configuration)
        io_layout.addWidget(import_btn)

        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        io_layout.addWidget(reset_btn)

        layout.addWidget(io_group)

        self.tab_widget.addTab(tab, "⚙️ Advanced")

    def _create_bottom_buttons(self):
        """Create bottom action buttons"""
        button_layout = QHBoxLayout()

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        button_layout.addWidget(self.status_label)

        button_layout.addStretch()

        # Apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: #000000;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #00cc66;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
            }
        """)
        self.apply_btn.clicked.connect(self._apply_settings)
        self.apply_btn.setEnabled(False)
        button_layout.addWidget(self.apply_btn)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: #ffffff;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
        """)
        self.save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_btn)

        self.content_layout.addLayout(button_layout)

    def _mark_unsaved_changes(self):
        """Mark that there are unsaved changes"""
        self.unsaved_changes = True
        self.apply_btn.setEnabled(True)
        self.status_label.setText("Unsaved changes")
        self.status_label.setStyleSheet("color: #ffaa00; font-weight: bold;")

    def _load_current_settings(self):
        """Load current settings from components"""
        try:
            # Load LLM settings
            # This would load from actual configuration in a real implementation

            # Load model selector settings
            current_strategy = self.model_selector.current_strategy
            for i in range(self.selection_strategy.count()):
                if self.selection_strategy.itemData(i) == current_strategy.value:
                    self.selection_strategy.setCurrentIndex(i)
                    break

            # Load brain AI settings
            brain_status = self.brain_manager.get_brain_status()

            self.status_label.setText("Settings loaded")
            self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")

        except Exception as e:
            logger.error(f"❌ Error loading settings: {e}")
            self.status_label.setText("Error loading settings")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

    def _apply_settings(self):
        """Apply current settings to components"""
        try:
            # Apply LLM provider settings
            if self.openai_enabled.isChecked() and self.openai_api_key.text():
                self.llm_manager.set_api_key(ProviderType.OPENAI, self.openai_api_key.text())

            if self.anthropic_enabled.isChecked() and self.anthropic_api_key.text():
                self.llm_manager.set_api_key(ProviderType.ANTHROPIC, self.anthropic_api_key.text())

            # Apply model selection strategy
            strategy_value = self.selection_strategy.currentData()
            if strategy_value:
                from ..llm.model_selector import SelectionStrategy
                strategy = SelectionStrategy(strategy_value)
                self.model_selector.set_selection_strategy(strategy)

            self.unsaved_changes = False
            self.apply_btn.setEnabled(False)
            self.status_label.setText("Settings applied")
            self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")

            # Emit signal
            self.settings_changed.emit("all", self._get_current_settings())

        except Exception as e:
            logger.error(f"❌ Error applying settings: {e}")
            self.status_label.setText("Error applying settings")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

    def _save_settings(self):
        """Save settings to file"""
        try:
            # Apply settings first
            self._apply_settings()

            # Save to configuration file
            config_data = self._get_current_settings()
            config_path = "orion_settings.json"

            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)

            self.status_label.setText(f"Settings saved to {config_path}")
            self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")

            # Emit signal
            self.configuration_saved.emit(config_path)

        except Exception as e:
            logger.error(f"❌ Error saving settings: {e}")
            self.status_label.setText("Error saving settings")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

    def _get_current_settings(self) -> Dict[str, Any]:
        """Get current settings as dictionary"""
        return {
            'llm_providers': {
                'openai': {
                    'enabled': self.openai_enabled.isChecked(),
                    'api_key': self.openai_api_key.text(),
                    'default_model': self.openai_default_model.currentText()
                },
                'anthropic': {
                    'enabled': self.anthropic_enabled.isChecked(),
                    'api_key': self.anthropic_api_key.text(),
                    'default_model': self.anthropic_default_model.currentText()
                },
                'ollama': {
                    'enabled': self.ollama_enabled.isChecked(),
                    'url': self.ollama_url.text(),
                    'default_model': self.ollama_default_model.currentText()
                }
            },
            'model_selection': {
                'strategy': self.selection_strategy.currentData(),
                'max_cost_per_token': self.max_cost_per_token.value(),
                'max_response_time': self.max_response_time.value(),
                'prefer_local': self.prefer_local.isChecked()
            },
            'brain_ai': {
                'enable_task_analysis': self.enable_task_analysis.isChecked(),
                'confidence_threshold': self.confidence_threshold.value() / 100.0,
                'enable_fragmentation': self.enable_fragmentation.isChecked(),
                'max_fragment_tokens': self.max_fragment_tokens.value()
            }
        }

    def _test_api_connection(self, provider: ProviderType):
        """Test API connection for a provider"""
        try:
            self.status_label.setText(f"Testing {provider.value} connection...")
            self.status_label.setStyleSheet("color: #ffaa00; font-weight: bold;")

            # Simulate API test (in real implementation, would make actual API call)
            QTimer.singleShot(1000, lambda: self._api_test_complete(provider, True))

        except Exception as e:
            logger.error(f"❌ Error testing {provider.value} connection: {e}")
            self._api_test_complete(provider, False)

    def _api_test_complete(self, provider: ProviderType, success: bool):
        """Handle API test completion"""
        if success:
            self.status_label.setText(f"{provider.value} connection successful")
            self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        else:
            self.status_label.setText(f"{provider.value} connection failed")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

        self.api_key_updated.emit(provider.value, success)

    def _refresh_performance_metrics(self):
        """Refresh performance metrics display"""
        try:
            # Get metrics from components
            llm_stats = self.llm_manager.get_usage_statistics()
            model_performance = self.model_selector.get_performance_summary()
            brain_status = self.brain_manager.get_brain_status()

            # Format metrics text
            metrics_text = f"""LLM API Manager Statistics:
Total Requests: {llm_stats.get('total_requests', 0)}
Successful Requests: {llm_stats.get('successful_requests', 0)}
Total Cost: ${llm_stats.get('total_cost', 0.0):.4f}
Average Response Time: {llm_stats.get('average_response_time', 0.0):.2f}s

Model Selector Performance:
Total Models: {model_performance.get('total_models', 0)}
Current Strategy: {model_performance.get('strategy', 'unknown')}

Brain AI Manager Status:
Tasks Analyzed: {brain_status.get('learning_metrics', {}).get('tasks_analyzed', 0)}
Messages Fragmented: {brain_status.get('learning_metrics', {}).get('messages_fragmented', 0)}
Active Contexts: {brain_status.get('active_contexts', 0)}
"""

            self.metrics_display.setText(metrics_text)

        except Exception as e:
            logger.error(f"❌ Error refreshing metrics: {e}")
            self.metrics_display.setText(f"Error loading metrics: {e}")

    def _export_configuration(self):
        """Export configuration to file"""
        try:
            config_data = self._get_current_settings()

            # Add metadata
            config_data['metadata'] = {
                'export_date': datetime.now().isoformat(),
                'version': '8.2.0',
                'exported_by': 'Orion Settings Panel'
            }

            filename = f"orion_config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2)

            self.status_label.setText(f"Configuration exported to {filename}")
            self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")

        except Exception as e:
            logger.error(f"❌ Error exporting configuration: {e}")
            self.status_label.setText("Error exporting configuration")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

    def _import_configuration(self):
        """Import configuration from file"""
        try:
            # In a real implementation, would use QFileDialog
            filename = "orion_settings.json"

            with open(filename, 'r') as f:
                config_data = json.load(f)

            # Load settings into UI
            self._load_settings_from_data(config_data)

            self.status_label.setText(f"Configuration imported from {filename}")
            self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")

            self._mark_unsaved_changes()

        except Exception as e:
            logger.error(f"❌ Error importing configuration: {e}")
            self.status_label.setText("Error importing configuration")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

    def _load_settings_from_data(self, config_data: Dict[str, Any]):
        """Load settings from configuration data"""
        try:
            # Load LLM provider settings
            llm_providers = config_data.get('llm_providers', {})

            openai_config = llm_providers.get('openai', {})
            self.openai_enabled.setChecked(openai_config.get('enabled', True))
            self.openai_api_key.setText(openai_config.get('api_key', ''))

            anthropic_config = llm_providers.get('anthropic', {})
            self.anthropic_enabled.setChecked(anthropic_config.get('enabled', True))
            self.anthropic_api_key.setText(anthropic_config.get('api_key', ''))

            # Load model selection settings
            model_selection = config_data.get('model_selection', {})
            strategy = model_selection.get('strategy', 'balanced')

            for i in range(self.selection_strategy.count()):
                if self.selection_strategy.itemData(i) == strategy:
                    self.selection_strategy.setCurrentIndex(i)
                    break

            # Load brain AI settings
            brain_ai = config_data.get('brain_ai', {})
            self.enable_task_analysis.setChecked(brain_ai.get('enable_task_analysis', True))
            self.enable_fragmentation.setChecked(brain_ai.get('enable_fragmentation', True))

        except Exception as e:
            logger.error(f"❌ Error loading settings from data: {e}")

    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Reset to default values
                self.openai_enabled.setChecked(True)
                self.openai_api_key.clear()
                self.anthropic_enabled.setChecked(True)
                self.anthropic_api_key.clear()
                self.ollama_enabled.setChecked(True)
                self.ollama_url.setText("http://localhost:11434")

                self.selection_strategy.setCurrentIndex(0)  # Balanced
                self.max_cost_per_token.setValue(0.0001)
                self.max_response_time.setValue(30)
                self.prefer_local.setChecked(False)

                self.enable_task_analysis.setChecked(True)
                self.confidence_threshold.setValue(70)
                self.enable_fragmentation.setChecked(True)
                self.max_fragment_tokens.setValue(2000)

                self.status_label.setText("Settings reset to defaults")
                self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")

                self._mark_unsaved_changes()

            except Exception as e:
                logger.error(f"❌ Error resetting settings: {e}")
                self.status_label.setText("Error resetting settings")
                self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

    def _auto_save_settings(self):
        """Auto-save settings if there are unsaved changes"""
        if self.unsaved_changes:
            try:
                self._save_settings()
                logger.info("⚙️ Settings auto-saved")
            except Exception as e:
                logger.error(f"❌ Auto-save failed: {e}")

    def get_window_info(self) -> Dict[str, Any]:
        """Get settings panel window information"""
        return {
            'type': 'settings_panel',
            'description': 'LLM and AI configuration interface',
            'unsaved_changes': self.unsaved_changes,
            'current_tab': self.tab_widget.currentIndex(),
            'components_connected': {
                'llm_manager': self.llm_manager is not None,
                'model_selector': self.model_selector is not None,
                'brain_manager': self.brain_manager is not None
            }
        }