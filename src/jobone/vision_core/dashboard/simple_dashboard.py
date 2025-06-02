#!/usr/bin/env python3
"""
Simple Terminal Dashboard - Basic System Monitor
Sprint 8.8 - Final Integration and Production Readiness
Orion Vision Core - Autonomous AI Operating System

This module provides a simple terminal-based dashboard that works
reliably across all systems and shows basic system information.

Author: Orion Development Team
Version: 8.8.0
Date: 31 Mayıs 2025
"""

import os
import sys
import time
import psutil
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print dashboard header"""
    print("=" * 80, flush=True)
    print("🚀 ORION VISION CORE - AUTONOMOUS AI OPERATING SYSTEM", flush=True)
    print("📊 Simple Terminal Dashboard v8.8.0", flush=True)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("=" * 80, flush=True)
    print(flush=True)

def print_system_info():
    """Print basic system information"""
    try:
        print("📊 SYSTEM METRICS", flush=True)
        print("-" * 40, flush=True)
        
        # CPU
        cpu = psutil.cpu_percent(interval=0.1)
        print(f"🖥️  CPU Usage: {cpu:.1f}%", flush=True)
        
        # Memory
        memory = psutil.virtual_memory()
        print(f"💾 Memory Usage: {memory.percent:.1f}%", flush=True)
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        print(f"💿 Disk Usage: {disk_percent:.1f}%", flush=True)
        
        # Processes
        processes = len(psutil.pids())
        print(f"⚙️  Processes: {processes}", flush=True)
        
        print(flush=True)
        
    except Exception as e:
        print(f"❌ Error getting system info: {e}", flush=True)

def test_modules():
    """Test Orion modules"""
    print("🧩 MODULE STATUS", flush=True)
    print("-" * 40, flush=True)
    
    # Add src to path
    if 'src' not in sys.path:
        sys.path.append('src')
    
    modules = [
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
    
    operational = 0
    total = len(modules)
    
    for name, module_path in modules:
        try:
            __import__(module_path)
            print(f"✅ {name:<12} - Operational", flush=True)
            operational += 1
        except ImportError:
            print(f"⏭️ {name:<12} - Optional", flush=True)
        except Exception:
            print(f"❌ {name:<12} - Error", flush=True)
    
    print(flush=True)
    print(f"📈 Module Status: {operational}/{total} operational", flush=True)
    print(flush=True)

def print_footer():
    """Print dashboard footer"""
    print("-" * 80, flush=True)
    print("🔄 Auto-refresh: 3s │ Press Ctrl+C to exit │ 🎯 Production Ready", flush=True)
    print("=" * 80, flush=True)

def run_dashboard():
    """Run simple dashboard"""
    try:
        print("🚀 Starting Orion Simple Dashboard...", flush=True)
        time.sleep(1)
        
        while True:
            clear_screen()
            print_header()
            print_system_info()
            test_modules()
            print_footer()
            
            # Wait 3 seconds
            time.sleep(3)
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n🛑 Dashboard stopped by user", flush=True)
        print("Thank you for using Orion Vision Core!", flush=True)
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}", flush=True)

def main():
    """Main function"""
    run_dashboard()

if __name__ == "__main__":
    main()
