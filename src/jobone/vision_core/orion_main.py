#!/usr/bin/env python3
"""
Orion Main Application - Complete Autonomous AI Operating System
Sprint 8.8 - Final Integration and Production Readiness
Orion Vision Core - Autonomous AI Operating System

This is the main application entry point for the Orion Vision Core autonomous
AI operating system, providing complete integration of all modules and subsystems.

Author: Orion Development Team
Version: 8.8.0
Date: 31 Mayıs 2025
"""

import sys
import os
import logging
import asyncio
import signal
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('orion.log')
    ]
)
logger = logging.getLogger("OrionMain")

class OrionMode(Enum):
    """Orion operating modes"""
    FULL = "full"                    # Full GUI mode
    HEADLESS = "headless"           # No GUI mode
    DASHBOARD_ONLY = "dashboard"    # Dashboard only mode
    CLI = "cli"                     # Command line interface mode
    SERVICE = "service"             # Background service mode

class OrionStatus(Enum):
    """Orion system status"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class OrionConfig:
    """Orion configuration"""
    mode: OrionMode = OrionMode.FULL
    enable_gui: bool = True
    enable_voice: bool = True
    enable_dashboard: bool = True
    enable_automation: bool = True
    enable_workflows: bool = True
    log_level: str = "INFO"
    config_file: Optional[str] = None
    data_dir: Optional[str] = None

class OrionApplication:
    """
    Main Orion Vision Core Application.

    This class orchestrates all Orion subsystems and provides the main
    application lifecycle management for the autonomous AI operating system.
    """

    def __init__(self, config: OrionConfig):
        """Initialize Orion Application"""
        self.config = config
        self.version = "8.8.0"
        self.status = OrionStatus.INITIALIZING
        self.start_time = datetime.now()

        # Module references
        self.modules: Dict[str, Any] = {}
        self.gui_app = None
        self.dashboard = None
        self.voice_manager = None
        self.workflow_engine = None
        self.automation_controller = None

        # System statistics
        self.stats = {
            'start_time': self.start_time,
            'modules_loaded': 0,
            'modules_active': 0,
            'tasks_completed': 0,
            'workflows_executed': 0,
            'voice_commands_processed': 0,
            'uptime': 0
        }

        # Event loop
        self.loop = None
        self.running = False

        logger.info(f"🚀 Orion Vision Core v{self.version} initializing...")

    async def initialize(self) -> bool:
        """Initialize all Orion subsystems"""
        try:
            logger.info("🔧 Initializing Orion subsystems...")

            # Initialize core modules
            await self._initialize_core_modules()

            # Initialize GUI if enabled
            if self.config.enable_gui:
                await self._initialize_gui()

            # Initialize voice if enabled
            if self.config.enable_voice:
                await self._initialize_voice()

            # Initialize dashboard if enabled
            if self.config.enable_dashboard:
                await self._initialize_dashboard()

            # Initialize automation if enabled
            if self.config.enable_automation:
                await self._initialize_automation()

            # Initialize workflows if enabled
            if self.config.enable_workflows:
                await self._initialize_workflows()

            # Setup signal handlers
            self._setup_signal_handlers()

            self.status = OrionStatus.RUNNING
            logger.info("✅ Orion Vision Core initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing Orion: {e}")
            self.status = OrionStatus.ERROR
            return False

    async def _initialize_core_modules(self):
        """Initialize core system modules"""
        try:
            logger.info("🔧 Loading core modules...")

            # System module
            from .system import get_system_manager
            self.modules['system'] = get_system_manager()
            logger.info("✅ System module loaded")

            # LLM module
            from .llm import get_llm_api_manager
            self.modules['llm'] = get_llm_api_manager()
            logger.info("✅ LLM module loaded")

            # Brain module
            from .brain import get_brain_ai_manager
            self.modules['brain'] = get_brain_ai_manager()
            logger.info("✅ Brain module loaded")

            # Tasks module
            from .tasks import get_task_framework
            self.modules['tasks'] = get_task_framework()
            logger.info("✅ Tasks module loaded")

            # NLP module
            from .nlp import get_nlp_processor
            self.modules['nlp'] = get_nlp_processor()
            logger.info("✅ NLP module loaded")

            self.stats['modules_loaded'] = len(self.modules)
            self.stats['modules_active'] = len(self.modules)

        except Exception as e:
            logger.error(f"❌ Error loading core modules: {e}")
            raise

    async def _initialize_gui(self):
        """Initialize GUI subsystem"""
        try:
            logger.info("🖥️ Initializing GUI subsystem...")

            # Check if PyQt6 is available
            try:
                from PyQt6.QtWidgets import QApplication

                # Create QApplication if not exists
                self.gui_app = QApplication.instance()
                if self.gui_app is None:
                    self.gui_app = QApplication(sys.argv)

                # Initialize GUI framework
                from .gui import get_gui_framework
                self.modules['gui'] = get_gui_framework()

                # Initialize desktop integration
                from .desktop import get_desktop_integration
                self.modules['desktop'] = get_desktop_integration()

                logger.info("✅ GUI subsystem initialized")

            except ImportError:
                logger.warning("⚠️ PyQt6 not available, GUI disabled")
                self.config.enable_gui = False

        except Exception as e:
            logger.error(f"❌ Error initializing GUI: {e}")
            self.config.enable_gui = False

    async def _initialize_voice(self):
        """Initialize voice subsystem"""
        try:
            logger.info("🎤 Initializing voice subsystem...")

            from .voice import get_voice_manager
            self.voice_manager = get_voice_manager()
            self.modules['voice'] = self.voice_manager

            logger.info("✅ Voice subsystem initialized")

        except Exception as e:
            logger.error(f"❌ Error initializing voice: {e}")
            self.config.enable_voice = False

    async def _initialize_dashboard(self):
        """Initialize dashboard subsystem"""
        try:
            logger.info("📊 Initializing dashboard subsystem...")

            if self.config.enable_gui:
                from .dashboard import get_system_dashboard
                self.dashboard = get_system_dashboard()
                self.modules['dashboard'] = self.dashboard

                logger.info("✅ Dashboard subsystem initialized")
            else:
                logger.warning("⚠️ GUI disabled, dashboard not available")
                self.config.enable_dashboard = False

        except Exception as e:
            logger.error(f"❌ Error initializing dashboard: {e}")
            self.config.enable_dashboard = False

    async def _initialize_automation(self):
        """Initialize automation subsystem"""
        try:
            logger.info("🤖 Initializing automation subsystem...")

            from .automation import get_automation_controller
            self.automation_controller = get_automation_controller()
            self.modules['automation'] = self.automation_controller

            logger.info("✅ Automation subsystem initialized")

        except Exception as e:
            logger.error(f"❌ Error initializing automation: {e}")
            self.config.enable_automation = False

    async def _initialize_workflows(self):
        """Initialize workflows subsystem"""
        try:
            logger.info("🔄 Initializing workflows subsystem...")

            from .workflows import get_workflow_engine
            self.workflow_engine = get_workflow_engine()
            self.modules['workflows'] = self.workflow_engine

            logger.info("✅ Workflows subsystem initialized")

        except Exception as e:
            logger.error(f"❌ Error initializing workflows: {e}")
            self.config.enable_workflows = False

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            logger.info("✅ Signal handlers configured")
        except Exception as e:
            logger.error(f"❌ Error setting up signal handlers: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}, initiating shutdown...")
        asyncio.create_task(self.shutdown())

    async def run(self):
        """Run the main Orion application"""
        try:
            self.running = True
            logger.info("🚀 Orion Vision Core is now running...")

            # Show dashboard if enabled
            if self.config.enable_dashboard and self.dashboard:
                self.dashboard.show_dashboard()
                logger.info("📊 Dashboard displayed")

            # Start main application loop based on mode
            if self.config.mode == OrionMode.FULL:
                await self._run_full_mode()
            elif self.config.mode == OrionMode.HEADLESS:
                await self._run_headless_mode()
            elif self.config.mode == OrionMode.DASHBOARD_ONLY:
                await self._run_dashboard_mode()
            elif self.config.mode == OrionMode.CLI:
                await self._run_cli_mode()
            elif self.config.mode == OrionMode.SERVICE:
                await self._run_service_mode()

        except Exception as e:
            logger.error(f"❌ Error running Orion: {e}")
            await self.shutdown()

    async def _run_full_mode(self):
        """Run in full GUI mode"""
        logger.info("🖥️ Running in full GUI mode")

        if self.gui_app:
            # Run Qt event loop
            self.gui_app.exec()
        else:
            # Fallback to headless mode
            await self._run_headless_mode()

    async def _run_headless_mode(self):
        """Run in headless mode"""
        logger.info("🔧 Running in headless mode")

        while self.running:
            # Update statistics
            self._update_stats()

            # Sleep for a short interval
            await asyncio.sleep(1)

    async def _run_dashboard_mode(self):
        """Run in dashboard-only mode"""
        logger.info("📊 Running in dashboard-only mode")

        if self.gui_app and self.dashboard:
            self.gui_app.exec()
        else:
            await self._run_headless_mode()

    async def _run_cli_mode(self):
        """Run in CLI mode"""
        logger.info("💻 Running in CLI mode")

        # TODO: Implement CLI interface
        print("Orion CLI mode not implemented yet")
        await self._run_headless_mode()

    async def _run_service_mode(self):
        """Run in service mode"""
        logger.info("⚙️ Running in service mode")

        # Similar to headless but optimized for background service
        await self._run_headless_mode()

    def _update_stats(self):
        """Update system statistics"""
        try:
            uptime = datetime.now() - self.start_time
            self.stats['uptime'] = uptime.total_seconds()

            # Update module statistics
            active_modules = sum(1 for module in self.modules.values() if module is not None)
            self.stats['modules_active'] = active_modules

        except Exception as e:
            logger.error(f"❌ Error updating stats: {e}")

    async def shutdown(self):
        """Shutdown Orion gracefully"""
        try:
            logger.info("⏹️ Shutting down Orion Vision Core...")
            self.status = OrionStatus.STOPPING
            self.running = False

            # Shutdown modules in reverse order
            if self.dashboard:
                logger.info("📊 Closing dashboard...")
                self.dashboard.close()

            if self.voice_manager:
                logger.info("🎤 Stopping voice manager...")
                # voice_manager.stop()

            if self.workflow_engine:
                logger.info("🔄 Stopping workflow engine...")
                # workflow_engine.stop()

            if self.automation_controller:
                logger.info("🤖 Stopping automation controller...")
                # automation_controller.stop()

            # Quit GUI application
            if self.gui_app:
                logger.info("🖥️ Closing GUI application...")
                self.gui_app.quit()

            self.status = OrionStatus.STOPPED
            logger.info("✅ Orion Vision Core shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        self._update_stats()
        return {
            'version': self.version,
            'status': self.status.value,
            'mode': self.config.mode.value,
            'uptime': self.stats['uptime'],
            'modules': {
                'loaded': self.stats['modules_loaded'],
                'active': self.stats['modules_active'],
                'list': list(self.modules.keys())
            },
            'features': {
                'gui': self.config.enable_gui,
                'voice': self.config.enable_voice,
                'dashboard': self.config.enable_dashboard,
                'automation': self.config.enable_automation,
                'workflows': self.config.enable_workflows
            },
            'statistics': self.stats
        }

def parse_arguments() -> OrionConfig:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Orion Vision Core - Autonomous AI Operating System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orion_main.py                    # Full GUI mode
  python orion_main.py --headless         # Headless mode
  python orion_main.py --dashboard-only   # Dashboard only
  python orion_main.py --cli              # CLI mode
  python orion_main.py --service          # Service mode
        """
    )

    # Mode options
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--headless', action='store_true',
        help='Run in headless mode (no GUI)'
    )
    mode_group.add_argument(
        '--dashboard-only', action='store_true',
        help='Run dashboard only'
    )
    mode_group.add_argument(
        '--cli', action='store_true',
        help='Run in CLI mode'
    )
    mode_group.add_argument(
        '--service', action='store_true',
        help='Run as background service'
    )

    # Feature toggles
    parser.add_argument(
        '--no-gui', action='store_true',
        help='Disable GUI subsystem'
    )
    parser.add_argument(
        '--no-voice', action='store_true',
        help='Disable voice subsystem'
    )
    parser.add_argument(
        '--no-dashboard', action='store_true',
        help='Disable dashboard'
    )
    parser.add_argument(
        '--no-automation', action='store_true',
        help='Disable automation subsystem'
    )
    parser.add_argument(
        '--no-workflows', action='store_true',
        help='Disable workflows subsystem'
    )

    # Configuration options
    parser.add_argument(
        '--config', type=str,
        help='Configuration file path'
    )
    parser.add_argument(
        '--data-dir', type=str,
        help='Data directory path'
    )
    parser.add_argument(
        '--log-level', type=str, default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level'
    )

    # Version
    parser.add_argument(
        '--version', action='version',
        version='Orion Vision Core v8.8.0'
    )

    args = parser.parse_args()

    # Determine mode
    mode = OrionMode.FULL
    if args.headless:
        mode = OrionMode.HEADLESS
    elif args.dashboard_only:
        mode = OrionMode.DASHBOARD_ONLY
    elif args.cli:
        mode = OrionMode.CLI
    elif args.service:
        mode = OrionMode.SERVICE

    # Create configuration
    config = OrionConfig(
        mode=mode,
        enable_gui=not args.no_gui and mode != OrionMode.HEADLESS,
        enable_voice=not args.no_voice,
        enable_dashboard=not args.no_dashboard and mode != OrionMode.HEADLESS,
        enable_automation=not args.no_automation,
        enable_workflows=not args.no_workflows,
        log_level=args.log_level,
        config_file=args.config,
        data_dir=args.data_dir
    )

    return config

def setup_logging(log_level: str):
    """Setup logging configuration"""
    try:
        # Set log level
        numeric_level = getattr(logging, log_level.upper(), None)
        if isinstance(numeric_level, int):
            logging.getLogger().setLevel(numeric_level)

        logger.info(f"📋 Logging level set to {log_level}")

    except Exception as e:
        logger.error(f"❌ Error setting up logging: {e}")

def print_banner():
    """Print Orion banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║    ██████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗                    ║
    ║   ██╔═══██╗██╔══██╗██║██╔═══██╗████╗  ██║                    ║
    ║   ██║   ██║██████╔╝██║██║   ██║██╔██╗ ██║                    ║
    ║   ██║   ██║██╔══██╗██║██║   ██║██║╚██╗██║                    ║
    ║   ╚██████╔╝██║  ██║██║╚██████╔╝██║ ╚████║                    ║
    ║    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝                    ║
    ║                                                               ║
    ║              VISION CORE v8.8.0                               ║
    ║         Autonomous AI Operating System                        ║
    ║                                                               ║
    ║              🤖 AI-Powered • 🎤 Voice-Enabled                 ║
    ║              🔄 Workflow-Driven • 📊 Real-time               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def main():
    """Main application entry point"""
    try:
        # Print banner
        print_banner()

        # Parse arguments
        config = parse_arguments()

        # Setup logging
        setup_logging(config.log_level)

        # Create and initialize Orion application
        orion = OrionApplication(config)

        # Initialize all subsystems
        success = await orion.initialize()
        if not success:
            logger.error("❌ Failed to initialize Orion")
            sys.exit(1)

        # Print status
        status = orion.get_status()
        logger.info(f"🚀 Orion v{status['version']} ready")
        logger.info(f"📋 Mode: {status['mode']}")
        logger.info(f"🧩 Modules: {status['modules']['active']}/{status['modules']['loaded']}")
        logger.info(f"✨ Features: GUI={status['features']['gui']}, Voice={status['features']['voice']}, Dashboard={status['features']['dashboard']}")

        # Run application
        await orion.run()

    except KeyboardInterrupt:
        logger.info("⏹️ Orion interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Run main application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Orion Vision Core stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
