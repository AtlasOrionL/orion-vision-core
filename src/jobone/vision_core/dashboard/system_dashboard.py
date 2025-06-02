#!/usr/bin/env python3
"""
System Dashboard - Comprehensive System Monitoring Dashboard
Sprint 8.7 - Comprehensive System Dashboard and Monitoring
Orion Vision Core - Autonomous AI Operating System

This module provides a comprehensive real-time system dashboard with monitoring,
analytics, and control capabilities for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.7.0
Date: 31 Mayıs 2025
"""

import logging
import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QTabWidget,
    QGroupBox, QFrame, QScrollArea, QSplitter, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QSpinBox, QCheckBox
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QSize, QRect
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QBrush
)

from ..gui.gui_framework import get_gui_framework
try:
    from ..system.system_manager import get_system_manager
except ImportError:
    # Fallback if system_manager not available
    def get_system_manager():
        return None
from ..brain.brain_ai_manager import get_brain_ai_manager
from ..workflows.workflow_engine import get_workflow_engine
from ..voice.voice_manager import get_voice_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemDashboard")

class DashboardMode(Enum):
    """Dashboard display mode"""
    OVERVIEW = "overview"
    DETAILED = "detailed"
    COMPACT = "compact"
    FULLSCREEN = "fullscreen"

class MetricType(Enum):
    """System metric types"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    MODULE_STATUS = "module_status"
    TASK_COUNT = "task_count"
    WORKFLOW_STATUS = "workflow_status"
    AI_ACTIVITY = "ai_activity"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SystemMetric:
    """System metric data"""
    metric_id: str
    metric_type: MetricType
    name: str
    value: float
    unit: str
    timestamp: datetime
    threshold_warning: float = 80.0
    threshold_critical: float = 95.0
    history: List[float] = field(default_factory=list)

@dataclass
class SystemAlert:
    """System alert data"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    source_module: str
    acknowledged: bool = False
    resolved: bool = False

class SystemMonitorThread(QThread):
    """Background thread for system monitoring"""

    metrics_updated = pyqtSignal(dict)  # metrics_data
    alert_generated = pyqtSignal(dict)  # alert_data

    def __init__(self):
        super().__init__()
        self.running = False
        self.update_interval = 1.0  # seconds

    def run(self):
        """Main monitoring loop"""
        self.running = True
        while self.running:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                self.metrics_updated.emit(metrics)

                # Check for alerts
                alerts = self._check_alerts(metrics)
                for alert in alerts:
                    self.alert_generated.emit(alert)

                time.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"❌ Error in monitoring thread: {e}")
                time.sleep(5)  # Wait before retry

    def stop(self):
        """Stop monitoring thread"""
        self.running = False
        self.wait()

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            metrics = {}

            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics['cpu_usage'] = {
                'value': cpu_percent,
                'unit': '%',
                'timestamp': datetime.now()
            }

            # Memory metrics
            memory = psutil.virtual_memory()
            metrics['memory_usage'] = {
                'value': memory.percent,
                'unit': '%',
                'total': memory.total,
                'available': memory.available,
                'timestamp': datetime.now()
            }

            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics['disk_usage'] = {
                'value': (disk.used / disk.total) * 100,
                'unit': '%',
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'timestamp': datetime.now()
            }

            # Network metrics
            network = psutil.net_io_counters()
            metrics['network_io'] = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv,
                'timestamp': datetime.now()
            }

            # Process count
            metrics['process_count'] = {
                'value': len(psutil.pids()),
                'unit': 'processes',
                'timestamp': datetime.now()
            }

            return metrics

        except Exception as e:
            logger.error(f"❌ Error collecting metrics: {e}")
            return {}

    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics for alert conditions"""
        alerts = []

        try:
            # CPU usage alert
            cpu_usage = metrics.get('cpu_usage', {}).get('value', 0)
            if cpu_usage > 90:
                alerts.append({
                    'level': AlertLevel.CRITICAL,
                    'title': 'High CPU Usage',
                    'message': f'CPU usage is {cpu_usage:.1f}%',
                    'source': 'system_monitor'
                })
            elif cpu_usage > 80:
                alerts.append({
                    'level': AlertLevel.WARNING,
                    'title': 'Elevated CPU Usage',
                    'message': f'CPU usage is {cpu_usage:.1f}%',
                    'source': 'system_monitor'
                })

            # Memory usage alert
            memory_usage = metrics.get('memory_usage', {}).get('value', 0)
            if memory_usage > 95:
                alerts.append({
                    'level': AlertLevel.CRITICAL,
                    'title': 'Critical Memory Usage',
                    'message': f'Memory usage is {memory_usage:.1f}%',
                    'source': 'system_monitor'
                })
            elif memory_usage > 85:
                alerts.append({
                    'level': AlertLevel.WARNING,
                    'title': 'High Memory Usage',
                    'message': f'Memory usage is {memory_usage:.1f}%',
                    'source': 'system_monitor'
                })

            # Disk usage alert
            disk_usage = metrics.get('disk_usage', {}).get('value', 0)
            if disk_usage > 95:
                alerts.append({
                    'level': AlertLevel.CRITICAL,
                    'title': 'Critical Disk Space',
                    'message': f'Disk usage is {disk_usage:.1f}%',
                    'source': 'system_monitor'
                })
            elif disk_usage > 85:
                alerts.append({
                    'level': AlertLevel.WARNING,
                    'title': 'Low Disk Space',
                    'message': f'Disk usage is {disk_usage:.1f}%',
                    'source': 'system_monitor'
                })

        except Exception as e:
            logger.error(f"❌ Error checking alerts: {e}")

        return alerts

class SystemDashboard(QMainWindow):
    """
    Comprehensive system dashboard for Orion Vision Core.

    Features:
    - Real-time system monitoring
    - Module status tracking
    - Performance analytics
    - Interactive controls
    - Alert management
    - Visual metrics display
    """

    def __init__(self):
        """Initialize System Dashboard"""
        super().__init__()

        # Dashboard configuration
        self.dashboard_title = "Orion Vision Core - System Dashboard"
        self.version = "8.7.0"
        self.mode = DashboardMode.OVERVIEW
        self.auto_refresh = True
        self.refresh_interval = 1000  # milliseconds

        # Component references
        self.gui_framework = get_gui_framework()

        # Data storage
        self.current_metrics: Dict[str, SystemMetric] = {}
        self.metric_history: Dict[str, List[float]] = {}
        self.active_alerts: Dict[str, SystemAlert] = {}
        self.module_status: Dict[str, Dict[str, Any]] = {}

        # UI components
        self.central_widget = None
        self.main_layout = None
        self.tab_widget = None
        self.status_bar = None

        # Monitoring
        self.monitor_thread = SystemMonitorThread()
        self.refresh_timer = QTimer()

        # Statistics
        self.dashboard_stats = {
            'uptime_start': datetime.now(),
            'total_alerts': 0,
            'metrics_collected': 0,
            'refresh_count': 0,
            'last_update': None
        }

        # Initialize dashboard
        self._initialize_dashboard()

        logger.info("📊 System Dashboard initialized")

    def _initialize_dashboard(self):
        """Initialize dashboard UI and monitoring"""
        try:
            # Set window properties
            self.setWindowTitle(self.dashboard_title)
            self.setMinimumSize(1400, 900)
            self.resize(1600, 1000)

            # Create UI
            self._create_ui()

            # Apply theme
            self._apply_dashboard_theme()

            # Start monitoring
            self._start_monitoring()

            # Connect signals
            self._connect_signals()

        except Exception as e:
            logger.error(f"❌ Error initializing dashboard: {e}")

    def _create_ui(self):
        """Create dashboard user interface"""
        try:
            # Central widget
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)

            # Main layout
            self.main_layout = QVBoxLayout(self.central_widget)
            self.main_layout.setContentsMargins(10, 10, 10, 10)
            self.main_layout.setSpacing(10)

            # Create header
            self._create_header()

            # Create tab widget
            self._create_tab_widget()

            # Create status bar
            self._create_status_bar()

        except Exception as e:
            logger.error(f"❌ Error creating UI: {e}")

    def _create_header(self):
        """Create dashboard header"""
        try:
            header_frame = QFrame()
            header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
            header_frame.setMaximumHeight(80)

            header_layout = QHBoxLayout(header_frame)

            # Title
            title_label = QLabel("🚀 Orion Vision Core")
            title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #00ff88; margin: 10px;")

            # Subtitle
            subtitle_label = QLabel("System Dashboard v8.7.0")
            subtitle_label.setFont(QFont("Arial", 12))
            subtitle_label.setStyleSheet("color: #cccccc; margin: 5px;")

            # Status indicator
            self.status_indicator = QLabel("🟢 OPERATIONAL")
            self.status_indicator.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.status_indicator.setStyleSheet("color: #00ff88; margin: 10px;")

            # Control buttons
            refresh_btn = QPushButton("🔄 Refresh")
            refresh_btn.clicked.connect(self._manual_refresh)

            settings_btn = QPushButton("⚙️ Settings")
            settings_btn.clicked.connect(self._show_settings)

            # Layout
            title_layout = QVBoxLayout()
            title_layout.addWidget(title_label)
            title_layout.addWidget(subtitle_label)

            header_layout.addLayout(title_layout)
            header_layout.addStretch()
            header_layout.addWidget(self.status_indicator)
            header_layout.addWidget(refresh_btn)
            header_layout.addWidget(settings_btn)

            self.main_layout.addWidget(header_frame)

        except Exception as e:
            logger.error(f"❌ Error creating header: {e}")

    def _create_tab_widget(self):
        """Create main tab widget"""
        try:
            self.tab_widget = QTabWidget()

            # Overview tab
            self._create_overview_tab()

            # System Metrics tab
            self._create_metrics_tab()

            # Module Status tab
            self._create_modules_tab()

            # Alerts tab
            self._create_alerts_tab()

            # Logs tab
            self._create_logs_tab()

            self.main_layout.addWidget(self.tab_widget)

        except Exception as e:
            logger.error(f"❌ Error creating tab widget: {e}")

    def _create_overview_tab(self):
        """Create overview tab"""
        try:
            overview_widget = QWidget()
            overview_layout = QGridLayout(overview_widget)

            # System Status Group
            status_group = QGroupBox("🖥️ System Status")
            status_layout = QGridLayout(status_group)

            # CPU Usage
            self.cpu_progress = QProgressBar()
            self.cpu_progress.setMaximum(100)
            self.cpu_label = QLabel("CPU: 0%")
            status_layout.addWidget(QLabel("CPU Usage:"), 0, 0)
            status_layout.addWidget(self.cpu_progress, 0, 1)
            status_layout.addWidget(self.cpu_label, 0, 2)

            # Memory Usage
            self.memory_progress = QProgressBar()
            self.memory_progress.setMaximum(100)
            self.memory_label = QLabel("Memory: 0%")
            status_layout.addWidget(QLabel("Memory Usage:"), 1, 0)
            status_layout.addWidget(self.memory_progress, 1, 1)
            status_layout.addWidget(self.memory_label, 1, 2)

            # Disk Usage
            self.disk_progress = QProgressBar()
            self.disk_progress.setMaximum(100)
            self.disk_label = QLabel("Disk: 0%")
            status_layout.addWidget(QLabel("Disk Usage:"), 2, 0)
            status_layout.addWidget(self.disk_progress, 2, 1)
            status_layout.addWidget(self.disk_label, 2, 2)

            overview_layout.addWidget(status_group, 0, 0)

            # Module Status Group
            modules_group = QGroupBox("🧩 Module Status")
            modules_layout = QVBoxLayout(modules_group)

            self.module_status_table = QTableWidget()
            self.module_status_table.setColumnCount(3)
            self.module_status_table.setHorizontalHeaderLabels(["Module", "Status", "Version"])
            self.module_status_table.horizontalHeader().setStretchLastSection(True)
            modules_layout.addWidget(self.module_status_table)

            overview_layout.addWidget(modules_group, 0, 1)

            # Recent Alerts Group
            alerts_group = QGroupBox("🚨 Recent Alerts")
            alerts_layout = QVBoxLayout(alerts_group)

            self.recent_alerts_list = QTextEdit()
            self.recent_alerts_list.setMaximumHeight(150)
            self.recent_alerts_list.setReadOnly(True)
            alerts_layout.addWidget(self.recent_alerts_list)

            overview_layout.addWidget(alerts_group, 1, 0, 1, 2)

            self.tab_widget.addTab(overview_widget, "📊 Overview")

        except Exception as e:
            logger.error(f"❌ Error creating overview tab: {e}")

    def _create_metrics_tab(self):
        """Create system metrics tab"""
        try:
            metrics_widget = QWidget()
            metrics_layout = QVBoxLayout(metrics_widget)

            # Metrics controls
            controls_frame = QFrame()
            controls_layout = QHBoxLayout(controls_frame)

            controls_layout.addWidget(QLabel("Refresh Rate:"))

            refresh_combo = QComboBox()
            refresh_combo.addItems(["1 sec", "2 sec", "5 sec", "10 sec"])
            refresh_combo.currentTextChanged.connect(self._update_refresh_rate)
            controls_layout.addWidget(refresh_combo)

            controls_layout.addStretch()

            auto_refresh_check = QCheckBox("Auto Refresh")
            auto_refresh_check.setChecked(True)
            auto_refresh_check.toggled.connect(self._toggle_auto_refresh)
            controls_layout.addWidget(auto_refresh_check)

            metrics_layout.addWidget(controls_frame)

            # Metrics display
            metrics_scroll = QScrollArea()
            metrics_content = QWidget()
            self.metrics_layout = QGridLayout(metrics_content)

            # Create metric widgets
            self._create_metric_widgets()

            metrics_scroll.setWidget(metrics_content)
            metrics_scroll.setWidgetResizable(True)
            metrics_layout.addWidget(metrics_scroll)

            self.tab_widget.addTab(metrics_widget, "📈 Metrics")

        except Exception as e:
            logger.error(f"❌ Error creating metrics tab: {e}")

    def _create_modules_tab(self):
        """Create modules status tab"""
        try:
            modules_widget = QWidget()
            modules_layout = QVBoxLayout(modules_widget)

            # Module controls
            controls_frame = QFrame()
            controls_layout = QHBoxLayout(controls_frame)

            refresh_modules_btn = QPushButton("🔄 Refresh Modules")
            refresh_modules_btn.clicked.connect(self._refresh_module_status)
            controls_layout.addWidget(refresh_modules_btn)

            restart_module_btn = QPushButton("🔄 Restart Module")
            restart_module_btn.clicked.connect(self._restart_selected_module)
            controls_layout.addWidget(restart_module_btn)

            controls_layout.addStretch()

            modules_layout.addWidget(controls_frame)

            # Modules table
            self.modules_table = QTableWidget()
            self.modules_table.setColumnCount(5)
            self.modules_table.setHorizontalHeaderLabels([
                "Module", "Status", "Version", "Uptime", "Actions"
            ])
            self.modules_table.horizontalHeader().setStretchLastSection(True)
            modules_layout.addWidget(self.modules_table)

            self.tab_widget.addTab(modules_widget, "🧩 Modules")

        except Exception as e:
            logger.error(f"❌ Error creating modules tab: {e}")

    def _create_alerts_tab(self):
        """Create alerts management tab"""
        try:
            alerts_widget = QWidget()
            alerts_layout = QVBoxLayout(alerts_widget)

            # Alert controls
            controls_frame = QFrame()
            controls_layout = QHBoxLayout(controls_frame)

            clear_alerts_btn = QPushButton("🗑️ Clear All")
            clear_alerts_btn.clicked.connect(self._clear_all_alerts)
            controls_layout.addWidget(clear_alerts_btn)

            acknowledge_btn = QPushButton("✅ Acknowledge")
            acknowledge_btn.clicked.connect(self._acknowledge_selected_alert)
            controls_layout.addWidget(acknowledge_btn)

            controls_layout.addStretch()

            alert_level_combo = QComboBox()
            alert_level_combo.addItems(["All", "Critical", "Warning", "Info"])
            alert_level_combo.currentTextChanged.connect(self._filter_alerts)
            controls_layout.addWidget(QLabel("Filter:"))
            controls_layout.addWidget(alert_level_combo)

            alerts_layout.addWidget(controls_frame)

            # Alerts table
            self.alerts_table = QTableWidget()
            self.alerts_table.setColumnCount(5)
            self.alerts_table.setHorizontalHeaderLabels([
                "Time", "Level", "Source", "Message", "Status"
            ])
            self.alerts_table.horizontalHeader().setStretchLastSection(True)
            alerts_layout.addWidget(self.alerts_table)

            self.tab_widget.addTab(alerts_widget, "🚨 Alerts")

        except Exception as e:
            logger.error(f"❌ Error creating alerts tab: {e}")

    def _create_logs_tab(self):
        """Create system logs tab"""
        try:
            logs_widget = QWidget()
            logs_layout = QVBoxLayout(logs_widget)

            # Log controls
            controls_frame = QFrame()
            controls_layout = QHBoxLayout(controls_frame)

            clear_logs_btn = QPushButton("🗑️ Clear Logs")
            clear_logs_btn.clicked.connect(self._clear_logs)
            controls_layout.addWidget(clear_logs_btn)

            export_logs_btn = QPushButton("💾 Export Logs")
            export_logs_btn.clicked.connect(self._export_logs)
            controls_layout.addWidget(export_logs_btn)

            controls_layout.addStretch()

            log_level_combo = QComboBox()
            log_level_combo.addItems(["All", "ERROR", "WARNING", "INFO", "DEBUG"])
            log_level_combo.currentTextChanged.connect(self._filter_logs)
            controls_layout.addWidget(QLabel("Level:"))
            controls_layout.addWidget(log_level_combo)

            logs_layout.addWidget(controls_frame)

            # Logs display
            self.logs_display = QTextEdit()
            self.logs_display.setReadOnly(True)
            self.logs_display.setFont(QFont("Consolas", 10))
            logs_layout.addWidget(self.logs_display)

            self.tab_widget.addTab(logs_widget, "📋 Logs")

        except Exception as e:
            logger.error(f"❌ Error creating logs tab: {e}")

    def _create_status_bar(self):
        """Create status bar"""
        try:
            self.status_bar = self.statusBar()

            # Status messages
            self.status_bar.showMessage("Dashboard initialized")

            # Uptime display
            self.uptime_label = QLabel("Uptime: 0s")
            self.status_bar.addPermanentWidget(self.uptime_label)

            # Last update time
            self.last_update_label = QLabel("Last Update: Never")
            self.status_bar.addPermanentWidget(self.last_update_label)

        except Exception as e:
            logger.error(f"❌ Error creating status bar: {e}")

    def _create_metric_widgets(self):
        """Create metric display widgets"""
        try:
            # CPU metrics
            cpu_group = QGroupBox("🖥️ CPU Metrics")
            cpu_layout = QVBoxLayout(cpu_group)

            self.cpu_usage_bar = QProgressBar()
            self.cpu_usage_bar.setMaximum(100)
            cpu_layout.addWidget(QLabel("Usage:"))
            cpu_layout.addWidget(self.cpu_usage_bar)

            self.cpu_cores_label = QLabel(f"Cores: {psutil.cpu_count()}")
            cpu_layout.addWidget(self.cpu_cores_label)

            self.metrics_layout.addWidget(cpu_group, 0, 0)

            # Memory metrics
            memory_group = QGroupBox("💾 Memory Metrics")
            memory_layout = QVBoxLayout(memory_group)

            self.memory_usage_bar = QProgressBar()
            self.memory_usage_bar.setMaximum(100)
            memory_layout.addWidget(QLabel("Usage:"))
            memory_layout.addWidget(self.memory_usage_bar)

            memory_info = psutil.virtual_memory()
            self.memory_total_label = QLabel(f"Total: {memory_info.total / (1024**3):.1f} GB")
            memory_layout.addWidget(self.memory_total_label)

            self.metrics_layout.addWidget(memory_group, 0, 1)

            # Disk metrics
            disk_group = QGroupBox("💿 Disk Metrics")
            disk_layout = QVBoxLayout(disk_group)

            self.disk_usage_bar = QProgressBar()
            self.disk_usage_bar.setMaximum(100)
            disk_layout.addWidget(QLabel("Usage:"))
            disk_layout.addWidget(self.disk_usage_bar)

            disk_info = psutil.disk_usage('/')
            self.disk_total_label = QLabel(f"Total: {disk_info.total / (1024**3):.1f} GB")
            disk_layout.addWidget(self.disk_total_label)

            self.metrics_layout.addWidget(disk_group, 1, 0)

            # Network metrics
            network_group = QGroupBox("🌐 Network Metrics")
            network_layout = QVBoxLayout(network_group)

            self.network_sent_label = QLabel("Sent: 0 MB")
            self.network_recv_label = QLabel("Received: 0 MB")
            network_layout.addWidget(self.network_sent_label)
            network_layout.addWidget(self.network_recv_label)

            self.metrics_layout.addWidget(network_group, 1, 1)

        except Exception as e:
            logger.error(f"❌ Error creating metric widgets: {e}")

    def _apply_dashboard_theme(self):
        """Apply dashboard theme"""
        try:
            # Apply GUI framework theme
            if self.gui_framework and self.gui_framework.current_theme:
                theme = self.gui_framework.current_theme

                # Custom dashboard styling
                dashboard_style = f"""
                QMainWindow {{
                    background-color: {theme.background_color};
                    color: {theme.text_color};
                }}

                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {theme.border_color};
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                }}

                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: {theme.primary_color};
                }}

                QProgressBar {{
                    border: 2px solid {theme.border_color};
                    border-radius: 5px;
                    text-align: center;
                    font-weight: bold;
                }}

                QProgressBar::chunk {{
                    background-color: {theme.primary_color};
                    border-radius: 3px;
                }}

                QTabWidget::pane {{
                    border: 1px solid {theme.border_color};
                    background-color: {theme.surface_color};
                }}

                QTabBar::tab {{
                    background-color: {theme.background_color};
                    color: {theme.text_color};
                    border: 1px solid {theme.border_color};
                    padding: 8px 16px;
                    margin-right: 2px;
                }}

                QTabBar::tab:selected {{
                    background-color: {theme.primary_color};
                    color: white;
                }}

                QTableWidget {{
                    gridline-color: {theme.border_color};
                    background-color: {theme.surface_color};
                    alternate-background-color: {theme.background_color};
                }}

                QHeaderView::section {{
                    background-color: {theme.primary_color};
                    color: white;
                    padding: 8px;
                    border: none;
                    font-weight: bold;
                }}
                """

                self.setStyleSheet(dashboard_style)

        except Exception as e:
            logger.error(f"❌ Error applying dashboard theme: {e}")

    def _start_monitoring(self):
        """Start system monitoring"""
        try:
            # Connect monitor thread signals
            self.monitor_thread.metrics_updated.connect(self._update_metrics)
            self.monitor_thread.alert_generated.connect(self._handle_alert)

            # Start monitor thread
            self.monitor_thread.start()

            # Start refresh timer
            self.refresh_timer.timeout.connect(self._update_display)
            self.refresh_timer.start(self.refresh_interval)

            logger.info("📊 System monitoring started")

        except Exception as e:
            logger.error(f"❌ Error starting monitoring: {e}")

    def _connect_signals(self):
        """Connect UI signals"""
        try:
            # Window close event
            pass  # Will be handled in closeEvent

        except Exception as e:
            logger.error(f"❌ Error connecting signals: {e}")

    def _update_metrics(self, metrics_data: Dict[str, Any]):
        """Update metrics from monitoring thread"""
        try:
            # Update CPU
            if 'cpu_usage' in metrics_data:
                cpu_value = metrics_data['cpu_usage']['value']
                self.cpu_progress.setValue(int(cpu_value))
                self.cpu_label.setText(f"CPU: {cpu_value:.1f}%")
                self.cpu_usage_bar.setValue(int(cpu_value))

            # Update Memory
            if 'memory_usage' in metrics_data:
                memory_value = metrics_data['memory_usage']['value']
                self.memory_progress.setValue(int(memory_value))
                self.memory_label.setText(f"Memory: {memory_value:.1f}%")
                self.memory_usage_bar.setValue(int(memory_value))

            # Update Disk
            if 'disk_usage' in metrics_data:
                disk_value = metrics_data['disk_usage']['value']
                self.disk_progress.setValue(int(disk_value))
                self.disk_label.setText(f"Disk: {disk_value:.1f}%")
                self.disk_usage_bar.setValue(int(disk_value))

            # Update Network
            if 'network_io' in metrics_data:
                network_data = metrics_data['network_io']
                sent_mb = network_data['bytes_sent'] / (1024 * 1024)
                recv_mb = network_data['bytes_recv'] / (1024 * 1024)
                self.network_sent_label.setText(f"Sent: {sent_mb:.1f} MB")
                self.network_recv_label.setText(f"Received: {recv_mb:.1f} MB")

            # Update statistics
            self.dashboard_stats['metrics_collected'] += 1
            self.dashboard_stats['last_update'] = datetime.now()

        except Exception as e:
            logger.error(f"❌ Error updating metrics: {e}")

    def _handle_alert(self, alert_data: Dict[str, Any]):
        """Handle new alert"""
        try:
            alert_id = f"alert_{len(self.active_alerts)}"

            alert = SystemAlert(
                alert_id=alert_id,
                level=alert_data['level'],
                title=alert_data['title'],
                message=alert_data['message'],
                timestamp=datetime.now(),
                source_module=alert_data['source']
            )

            self.active_alerts[alert_id] = alert
            self.dashboard_stats['total_alerts'] += 1

            # Update recent alerts display
            alert_text = f"[{alert.timestamp.strftime('%H:%M:%S')}] {alert.level.value.upper()}: {alert.message}"
            self.recent_alerts_list.append(alert_text)

            # Update status indicator based on alert level
            if alert.level == AlertLevel.CRITICAL:
                self.status_indicator.setText("🔴 CRITICAL")
                self.status_indicator.setStyleSheet("color: #ff4444; margin: 10px;")
            elif alert.level == AlertLevel.WARNING:
                self.status_indicator.setText("🟡 WARNING")
                self.status_indicator.setStyleSheet("color: #ffaa00; margin: 10px;")

            logger.warning(f"🚨 Alert generated: {alert.title}")

        except Exception as e:
            logger.error(f"❌ Error handling alert: {e}")

    def _update_display(self):
        """Update display elements"""
        try:
            # Update uptime
            uptime = datetime.now() - self.dashboard_stats['uptime_start']
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            self.uptime_label.setText(f"Uptime: {uptime_str}")

            # Update last update time
            if self.dashboard_stats['last_update']:
                last_update = self.dashboard_stats['last_update'].strftime('%H:%M:%S')
                self.last_update_label.setText(f"Last Update: {last_update}")

            # Update refresh count
            self.dashboard_stats['refresh_count'] += 1

            # Update module status
            self._update_module_status()

        except Exception as e:
            logger.error(f"❌ Error updating display: {e}")

    def _update_module_status(self):
        """Update module status display"""
        try:
            modules = [
                ("System", "jobone.vision_core.system"),
                ("LLM", "jobone.vision_core.llm"),
                ("Brain", "jobone.vision_core.brain"),
                ("Tasks", "jobone.vision_core.tasks"),
                ("Workflows", "jobone.vision_core.workflows"),
                ("Voice", "jobone.vision_core.voice"),
                ("NLP", "jobone.vision_core.nlp"),
                ("Automation", "jobone.vision_core.automation"),
                ("GUI", "jobone.vision_core.gui"),
                ("Desktop", "jobone.vision_core.desktop")
            ]

            self.module_status_table.setRowCount(len(modules))

            for i, (name, module_path) in enumerate(modules):
                try:
                    # Try to import module
                    module = __import__(module_path, fromlist=['get_' + name.lower() + '_info'])
                    info_func = getattr(module, 'get_' + name.lower() + '_info')
                    info = info_func()

                    # Module name
                    self.module_status_table.setItem(i, 0, QTableWidgetItem(name))

                    # Status
                    status_item = QTableWidgetItem("✅ ACTIVE")
                    status_item.setForeground(QColor("#00ff88"))
                    self.module_status_table.setItem(i, 1, status_item)

                    # Version
                    self.module_status_table.setItem(i, 2, QTableWidgetItem(info['version']))

                except Exception:
                    # Module name
                    self.module_status_table.setItem(i, 0, QTableWidgetItem(name))

                    # Status
                    status_item = QTableWidgetItem("❌ ERROR")
                    status_item.setForeground(QColor("#ff4444"))
                    self.module_status_table.setItem(i, 1, status_item)

                    # Version
                    self.module_status_table.setItem(i, 2, QTableWidgetItem("N/A"))

        except Exception as e:
            logger.error(f"❌ Error updating module status: {e}")

    # Event handlers
    def _manual_refresh(self):
        """Manual refresh button clicked"""
        try:
            self._update_display()
            self.status_bar.showMessage("Manual refresh completed", 2000)
        except Exception as e:
            logger.error(f"❌ Error in manual refresh: {e}")

    def _show_settings(self):
        """Show settings dialog"""
        try:
            # TODO: Implement settings dialog
            self.status_bar.showMessage("Settings dialog not implemented yet", 3000)
        except Exception as e:
            logger.error(f"❌ Error showing settings: {e}")

    def _update_refresh_rate(self, rate_text: str):
        """Update refresh rate"""
        try:
            rate_map = {
                "1 sec": 1000,
                "2 sec": 2000,
                "5 sec": 5000,
                "10 sec": 10000
            }

            if rate_text in rate_map:
                self.refresh_interval = rate_map[rate_text]
                self.refresh_timer.setInterval(self.refresh_interval)
                self.status_bar.showMessage(f"Refresh rate updated to {rate_text}", 2000)

        except Exception as e:
            logger.error(f"❌ Error updating refresh rate: {e}")

    def _toggle_auto_refresh(self, enabled: bool):
        """Toggle auto refresh"""
        try:
            self.auto_refresh = enabled
            if enabled:
                self.refresh_timer.start()
                self.status_bar.showMessage("Auto refresh enabled", 2000)
            else:
                self.refresh_timer.stop()
                self.status_bar.showMessage("Auto refresh disabled", 2000)

        except Exception as e:
            logger.error(f"❌ Error toggling auto refresh: {e}")

    def _refresh_module_status(self):
        """Refresh module status"""
        try:
            self._update_module_status()
            self.status_bar.showMessage("Module status refreshed", 2000)
        except Exception as e:
            logger.error(f"❌ Error refreshing module status: {e}")

    def _restart_selected_module(self):
        """Restart selected module"""
        try:
            # TODO: Implement module restart functionality
            self.status_bar.showMessage("Module restart not implemented yet", 3000)
        except Exception as e:
            logger.error(f"❌ Error restarting module: {e}")

    def _clear_all_alerts(self):
        """Clear all alerts"""
        try:
            self.active_alerts.clear()
            self.recent_alerts_list.clear()
            self.alerts_table.setRowCount(0)
            self.status_indicator.setText("🟢 OPERATIONAL")
            self.status_indicator.setStyleSheet("color: #00ff88; margin: 10px;")
            self.status_bar.showMessage("All alerts cleared", 2000)
        except Exception as e:
            logger.error(f"❌ Error clearing alerts: {e}")

    def _acknowledge_selected_alert(self):
        """Acknowledge selected alert"""
        try:
            # TODO: Implement alert acknowledgment
            self.status_bar.showMessage("Alert acknowledgment not implemented yet", 3000)
        except Exception as e:
            logger.error(f"❌ Error acknowledging alert: {e}")

    def _filter_alerts(self, level: str):
        """Filter alerts by level"""
        try:
            # TODO: Implement alert filtering
            self.status_bar.showMessage(f"Alert filtering by {level} not implemented yet", 3000)
        except Exception as e:
            logger.error(f"❌ Error filtering alerts: {e}")

    def _clear_logs(self):
        """Clear logs display"""
        try:
            self.logs_display.clear()
            self.status_bar.showMessage("Logs cleared", 2000)
        except Exception as e:
            logger.error(f"❌ Error clearing logs: {e}")

    def _export_logs(self):
        """Export logs to file"""
        try:
            # TODO: Implement log export
            self.status_bar.showMessage("Log export not implemented yet", 3000)
        except Exception as e:
            logger.error(f"❌ Error exporting logs: {e}")

    def _filter_logs(self, level: str):
        """Filter logs by level"""
        try:
            # TODO: Implement log filtering
            self.status_bar.showMessage(f"Log filtering by {level} not implemented yet", 3000)
        except Exception as e:
            logger.error(f"❌ Error filtering logs: {e}")

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Stop monitoring thread
            self.monitor_thread.stop()

            # Stop refresh timer
            self.refresh_timer.stop()

            logger.info("📊 System Dashboard closed")
            event.accept()

        except Exception as e:
            logger.error(f"❌ Error closing dashboard: {e}")
            event.accept()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        return self.dashboard_stats.copy()

    def show_dashboard(self):
        """Show dashboard window"""
        try:
            self.show()
            self.raise_()
            self.activateWindow()
        except Exception as e:
            logger.error(f"❌ Error showing dashboard: {e}")

# Singleton instance
_system_dashboard = None

def get_system_dashboard() -> SystemDashboard:
    """Get the singleton System Dashboard instance"""
    global _system_dashboard
    if _system_dashboard is None:
        _system_dashboard = SystemDashboard()
    return _system_dashboard

def create_dashboard_application():
    """Create and show dashboard application"""
    try:
        from PyQt6.QtWidgets import QApplication
        import sys

        # Create application if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create and show dashboard
        dashboard = get_system_dashboard()
        dashboard.show_dashboard()

        return app, dashboard

    except Exception as e:
        logger.error(f"❌ Error creating dashboard application: {e}")
        return None, None
