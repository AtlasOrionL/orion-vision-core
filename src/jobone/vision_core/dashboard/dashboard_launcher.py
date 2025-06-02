#!/usr/bin/env python3
"""
Dashboard Launcher - System Dashboard Application Launcher
Sprint 8.7 - Comprehensive System Dashboard and Monitoring
Orion Vision Core - Autonomous AI Operating System

This script provides a standalone launcher for the Orion Vision Core
system dashboard application.

Author: Orion Development Team
Version: 8.7.0
Date: 31 Mayıs 2025
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent
sys.path.insert(0, str(src_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DashboardLauncher")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import PyQt6
        logger.info("✅ PyQt6 available")
        
        import psutil
        logger.info("✅ psutil available")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def launch_dashboard():
    """Launch the system dashboard"""
    try:
        logger.info("🚀 Launching Orion Vision Core Dashboard...")
        
        # Check dependencies
        if not check_dependencies():
            logger.error("❌ Missing required dependencies")
            return False
        
        # Import dashboard components
        from jobone.vision_core.dashboard import (
            create_dashboard_application, get_dashboard_info
        )
        
        # Get dashboard info
        info = get_dashboard_info()
        logger.info(f"📊 Dashboard Module v{info['version']}")
        logger.info(f"📋 Features: {len(info['features'])} features available")
        
        # Create and show dashboard
        app, dashboard = create_dashboard_application()
        
        if app and dashboard:
            logger.info("✅ Dashboard created successfully")
            logger.info("🖥️ Dashboard window opened")
            logger.info("📊 Real-time monitoring started")
            
            # Run application
            sys.exit(app.exec())
        else:
            logger.error("❌ Failed to create dashboard")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error launching dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main launcher function"""
    print("🚀 Orion Vision Core - System Dashboard Launcher")
    print("=" * 50)
    
    try:
        # Launch dashboard
        success = launch_dashboard()
        
        if not success:
            print("❌ Dashboard launch failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Dashboard launcher interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
