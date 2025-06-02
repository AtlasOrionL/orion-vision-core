#!/usr/bin/env python3
"""
Terminal Dashboard - Text-based System Dashboard
Sprint 8.8 - Final Integration and Production Readiness
Orion Vision Core - Autonomous AI Operating System

This module provides a terminal-based dashboard for systems without GUI support,
displaying real-time system metrics and module status in a text interface.

Author: Orion Development Team
Version: 8.8.0
Date: 31 Mayıs 2025
"""

import os
import sys
import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TerminalDashboard")

@dataclass
class SystemMetric:
    """System metric data"""
    name: str
    value: float
    unit: str
    status: str
    timestamp: datetime

class TerminalDashboard:
    """
    Terminal-based system dashboard for Orion Vision Core.

    This class provides a text-based interface for monitoring system
    metrics and module status when GUI is not available.
    """

    def __init__(self):
        """Initialize terminal dashboard"""
        self.version = "8.8.0"
        self.start_time = datetime.now()
        self.refresh_rate = 2.0  # seconds
        self.running = False

        # System metrics
        self.metrics: List[SystemMetric] = []

        # Module status
        self.modules = {}

        logger.info(f"📊 Terminal Dashboard v{self.version} initialized")

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_system_metrics(self) -> List[SystemMetric]:
        """Get current system metrics"""
        metrics = []
        now = datetime.now()

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_status = "🟢 Normal" if cpu_percent < 80 else "🟡 High" if cpu_percent < 95 else "🔴 Critical"
            metrics.append(SystemMetric("CPU Usage", cpu_percent, "%", cpu_status, now))

            # Memory metrics
            memory = psutil.virtual_memory()
            mem_status = "🟢 Normal" if memory.percent < 80 else "🟡 High" if memory.percent < 95 else "🔴 Critical"
            metrics.append(SystemMetric("Memory Usage", memory.percent, "%", mem_status, now))

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_status = "🟢 Normal" if disk_percent < 80 else "🟡 High" if disk_percent < 95 else "🔴 Critical"
            metrics.append(SystemMetric("Disk Usage", disk_percent, "%", disk_status, now))

            # Network metrics
            network = psutil.net_io_counters()
            net_mb_sent = network.bytes_sent / (1024 * 1024)
            net_mb_recv = network.bytes_recv / (1024 * 1024)
            metrics.append(SystemMetric("Network Sent", net_mb_sent, "MB", "🟢 Active", now))
            metrics.append(SystemMetric("Network Received", net_mb_recv, "MB", "🟢 Active", now))

            # Process count
            process_count = len(psutil.pids())
            proc_status = "🟢 Normal" if process_count < 200 else "🟡 High" if process_count < 300 else "🔴 Critical"
            metrics.append(SystemMetric("Processes", process_count, "count", proc_status, now))

        except Exception as e:
            logger.error(f"❌ Error getting system metrics: {e}")

        return metrics

    def get_module_status(self) -> Dict[str, Any]:
        """Get module status information"""
        modules = {}

        # Test core modules
        module_list = [
            ('System', 'jobone.vision_core.system'),
            ('LLM', 'jobone.vision_core.llm'),
            ('Brain', 'jobone.vision_core.brain'),
            ('Tasks', 'jobone.vision_core.tasks'),
            ('Workflows', 'jobone.vision_core.workflows'),
            ('Voice', 'jobone.vision_core.voice'),
            ('NLP', 'jobone.vision_core.nlp'),
            ('Automation', 'jobone.vision_core.automation'),
            ('GUI', 'jobone.vision_core.gui'),
            ('Desktop', 'jobone.vision_core.desktop'),
            ('Dashboard', 'jobone.vision_core.dashboard')
        ]

        for name, module_path in module_list:
            try:
                # Add src to path if not already there
                if 'src' not in sys.path:
                    sys.path.append('src')

                module = __import__(module_path, fromlist=['get_' + name.lower() + '_info'])

                # Check if module has info function
                info_func_name = 'get_' + name.lower() + '_info'
                if hasattr(module, info_func_name):
                    info_func = getattr(module, info_func_name)
                    info = info_func()
                    modules[name] = {
                        'status': '🟢 Operational',
                        'version': info.get('version', 'Unknown'),
                        'features': len(info.get('features', []))
                    }
                else:
                    modules[name] = {
                        'status': '🟢 Loaded',
                        'version': 'Unknown',
                        'features': 0
                    }

            except ImportError:
                modules[name] = {
                    'status': '🟡 Optional',
                    'version': 'N/A',
                    'features': 0
                }
            except Exception as e:
                modules[name] = {
                    'status': '🔴 Error',
                    'version': 'N/A',
                    'features': 0
                }

        return modules

    def render_header(self):
        """Render dashboard header"""
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds

        print("╔" + "═" * 78 + "╗", flush=True)
        print("║" + " " * 78 + "║", flush=True)
        print("║" + "🚀 ORION VISION CORE - AUTONOMOUS AI OPERATING SYSTEM".center(78) + "║", flush=True)
        print("║" + f"📊 Terminal Dashboard v{self.version}".center(78) + "║", flush=True)
        print("║" + " " * 78 + "║", flush=True)
        print("║" + f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(39) +
              f"⏱️ Uptime: {uptime_str}".center(39) + "║", flush=True)
        print("║" + " " * 78 + "║", flush=True)
        print("╚" + "═" * 78 + "╝", flush=True)
        print(flush=True)

    def render_system_metrics(self):
        """Render system metrics section"""
        print("📊 SYSTEM METRICS", flush=True)
        print("─" * 80, flush=True)

        metrics = self.get_system_metrics()

        for metric in metrics:
            value_str = f"{metric.value:.1f} {metric.unit}"
            print(f"  {metric.name:<20} │ {value_str:<15} │ {metric.status}", flush=True)

        print(flush=True)

    def render_module_status(self):
        """Render module status section"""
        print("🧩 MODULE STATUS", flush=True)
        print("─" * 80, flush=True)

        modules = self.get_module_status()

        for name, info in modules.items():
            version_str = f"v{info['version']}"
            features_str = f"{info['features']} features"
            print(f"  {name:<12} │ {version_str:<10} │ {features_str:<15} │ {info['status']}", flush=True)

        print(flush=True)

    def render_footer(self):
        """Render dashboard footer"""
        print("─" * 80, flush=True)
        print(f"🔄 Auto-refresh: {self.refresh_rate}s │ Press Ctrl+C to exit │ 🎯 Production Ready", flush=True)
        print("=" * 80, flush=True)

    def render_dashboard(self):
        """Render complete dashboard"""
        self.clear_screen()
        self.render_header()
        self.render_system_metrics()
        self.render_module_status()
        self.render_footer()

    def run(self):
        """Run terminal dashboard"""
        try:
            self.running = True

            # Force output to be visible
            print("🚀 Orion Vision Core - Terminal Dashboard", flush=True)
            print("=" * 50, flush=True)
            print("Loading...", flush=True)

            # Initial render
            self.render_dashboard()

            # Main loop
            while self.running:
                time.sleep(self.refresh_rate)
                self.render_dashboard()

        except KeyboardInterrupt:
            self.running = False
            self.clear_screen()
            print("\n🛑 Terminal Dashboard stopped by user", flush=True)
            print("Thank you for using Orion Vision Core!", flush=True)

        except Exception as e:
            self.running = False
            print(f"\n❌ Dashboard error: {e}", flush=True)
            import traceback
            traceback.print_exc()

    def stop(self):
        """Stop terminal dashboard"""
        self.running = False

def main():
    """Main function"""
    try:
        dashboard = TerminalDashboard()
        dashboard.run()
    except Exception as e:
        print(f"❌ Error starting terminal dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
