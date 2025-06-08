#!/usr/bin/env python3
"""
🚀 Debug Interface Launcher

Orion Vision Core Q1-Q5 Debug Interface Launcher
Quick start script for debug testing

Usage:
    python debug_launcher.py
    python debug_launcher.py --console  # Console mode only
    python debug_launcher.py --q1-test  # Direct Q1 test

Author: Orion Vision Core Team
Priority: CRITICAL - Q1-Q5 Canlı Test
"""

import sys
import os
import argparse
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QTabWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess
import json
import glob

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def check_dependencies():
    """Check required dependencies"""
    missing_deps = []
    
    try:
        import PyQt6
        print("✅ PyQt6 available")
    except ImportError:
        missing_deps.append("PyQt6")
        print("⚠️ PyQt6 not available - will use console mode")
    
    try:
        import numpy
        print("✅ NumPy available")
    except ImportError:
        missing_deps.append("numpy")
        print("❌ NumPy missing")
    
    # Check optional dependencies
    optional_deps = []
    
    try:
        import mss
        print("✅ MSS (screen capture) available")
    except ImportError:
        optional_deps.append("mss")
        print("⚠️ MSS not available - screen capture will be simulated")
    
    try:
        import pytesseract
        print("✅ Tesseract OCR available")
    except ImportError:
        optional_deps.append("pytesseract")
        print("⚠️ Tesseract not available - OCR will be simulated")
    
    try:
        import requests
        print("✅ Requests available (for Ollama)")
    except ImportError:
        optional_deps.append("requests")
        print("⚠️ Requests not available - Ollama integration disabled")
    
    if missing_deps:
        print(f"\n❌ Missing critical dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False
    
    if optional_deps:
        print(f"\n⚠️ Optional dependencies missing: {', '.join(optional_deps)}")
        print("Some features will be simulated")
    
    return True

def run_q1_quick_test():
    """Run quick Q1 test"""
    print("🚀 Running Q1 Quick Test...")
    
    try:
        from jobone.vision_core.debug.debug_interface import DebugInterface
        
        # Create interface
        interface = DebugInterface()
        
        # Run Q1 tests
        print("\n📸 Testing Screen Capture...")
        success1 = interface.q1_controller.test_screen_capture()
        
        print("\n📝 Testing OCR Processing...")
        success2 = interface.q1_controller.test_ocr_processing()
        
        print("\n⚛️ Testing Lepton Generation...")
        success3 = interface.q1_controller.test_lepton_generation()
        
        # Results
        print("\n" + "="*50)
        print("🎯 Q1 QUICK TEST RESULTS")
        print("="*50)
        print(f"📸 Screen Capture: {'✅ PASS' if success1 else '❌ FAIL'}")
        print(f"📝 OCR Processing: {'✅ PASS' if success2 else '❌ FAIL'}")
        print(f"⚛️ Lepton Generation: {'✅ PASS' if success3 else '❌ FAIL'}")
        
        if all([success1, success2, success3]):
            print("\n🎉 Q1 QUICK TEST: ALL PASSED!")
        else:
            print("\n❌ Q1 QUICK TEST: SOME FAILED!")
        
        # Show status
        status = interface.q1_controller.get_status()
        print(f"\n📊 Generated {status['leptons_count']} Leptons")
        
        if status['last_leptons']:
            print("\n⚛️ Sample Leptons:")
            for lepton in status['last_leptons']:
                print(f"  • {lepton['value']} (mass: {lepton['effective_mass']}, confidence: {lepton['confidence']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Q1 Quick Test failed: {e}")
        return False

class DebugThread(QThread):
    output = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        stdout, stderr = process.communicate()
        self.output.emit(stdout + stderr)
        self.finished.emit()

class QTaskTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.qtask_list = QTabWidget()
        self.layout.addWidget(self.qtask_list)
        self.load_qtasks()

    def load_qtasks(self):
        base_path = os.path.join('docs', 'Q_Tasks')
        q_dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d.startswith('Q')]
        for q_dir in sorted(q_dirs):
            q_path = os.path.join(base_path, q_dir)
            readme_path = os.path.join(q_path, 'README.md')
            status_path = os.path.join(q_path, 'STATUS.md')
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            # Görev başlığı ve açıklaması
            if os.path.exists(readme_path):
                with open(readme_path, encoding='utf-8') as f:
                    readme_content = f.read()
                title = readme_content.split('\n')[0].strip('# ').strip()
                summary = '\n'.join(readme_content.split('\n')[1:10])
            else:
                title = q_dir
                summary = "README.md bulunamadı."
            title_label = QLabel(f"<b>{title}</b>")
            title_label.setWordWrap(True)
            tab_layout.addWidget(title_label)
            summary_label = QLabel(summary)
            summary_label.setWordWrap(True)
            tab_layout.addWidget(summary_label)
            # Detay ve durum gösterimi
            detail_btn = QPushButton("Detayları Göster")
            detail_text = QTextEdit()
            detail_text.setReadOnly(True)
            detail_text.hide()
            def show_details(checked, readme_path=readme_path, status_path=status_path, detail_text=detail_text):
                detail = ""
                if os.path.exists(readme_path):
                    with open(readme_path, encoding='utf-8') as f:
                        detail += f"# README.md\n" + f.read() + "\n\n"
                if os.path.exists(status_path):
                    with open(status_path, encoding='utf-8') as f:
                        detail += f"# STATUS.md\n" + f.read()
                if not detail:
                    detail = "Detay bulunamadı."
                detail_text.setPlainText(detail)
                detail_text.show()
            detail_btn.clicked.connect(show_details)
            tab_layout.addWidget(detail_btn)
            tab_layout.addWidget(detail_text)
            self.qtask_list.addTab(tab, q_dir)

    def closeEvent(self, event):
        # QTaskTab kapatıldığında tüm thread'lerin düzgün şekilde sonlandırılmasını sağla
        for i in range(self.qtask_list.count()):
            tab = self.qtask_list.widget(i)
            for child in tab.findChildren(QThread):
                child.quit()
                child.wait()
        event.accept()

class DebugLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orion Vision Core - Debug Launcher")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Üst menü
        top_layout = QHBoxLayout()
        self.run_tests_btn = QPushButton("Run All Tests")
        self.run_tests_btn.clicked.connect(self.run_all_tests)
        self.run_module_btn = QPushButton("Run Module Test")
        self.run_module_btn.clicked.connect(self.run_module_test)
        self.view_docs_btn = QPushButton("View Documentation")
        self.view_docs_btn.clicked.connect(self.view_documentation)
        self.view_sprint_btn = QPushButton("View Sprint Status")
        self.view_sprint_btn.clicked.connect(self.view_sprint_status)
        top_layout.addWidget(self.run_tests_btn)
        top_layout.addWidget(self.run_module_btn)
        top_layout.addWidget(self.view_docs_btn)
        top_layout.addWidget(self.view_sprint_btn)
        layout.addLayout(top_layout)

        # Tab widget
        self.tabs = QTabWidget()
        self.output_tab = QTextEdit()
        self.output_tab.setReadOnly(True)
        self.tabs.addTab(self.output_tab, "Output")
        # Q Görevleri sekmesi
        self.qtask_tab = QTaskTab()
        self.tabs.addTab(self.qtask_tab, "Q Görevleri")
        layout.addWidget(self.tabs)

    def run_all_tests(self):
        self.output_tab.clear()
        self.output_tab.append("Running all tests...")
        thread = DebugThread("pytest -v")
        thread.output.connect(self.output_tab.append)
        thread.finished.connect(lambda: self.output_tab.append("Tests completed."))
        thread.start()

    def run_module_test(self):
        module, ok = QFileDialog.getOpenFileName(self, "Select Module", "", "Python Files (*.py)")
        if ok:
            self.output_tab.clear()
            self.output_tab.append(f"Running test for module: {module}")
            thread = DebugThread(f"pytest {module} -v")
            thread.output.connect(self.output_tab.append)
            thread.finished.connect(lambda: self.output_tab.append("Module test completed."))
            thread.start()

    def view_documentation(self):
        self.output_tab.clear()
        self.output_tab.append("Loading documentation...")
        thread = DebugThread("find docs -type f -name '*.md' -exec cat {} \\;")
        thread.output.connect(self.output_tab.append)
        thread.finished.connect(lambda: self.output_tab.append("Documentation loaded."))
        thread.start()

    def view_sprint_status(self):
        self.output_tab.clear()
        self.output_tab.append("Loading sprint status...")
        thread = DebugThread("cat docs/Q_Tasks/SPRINT_STATUS.md")
        thread.output.connect(self.output_tab.append)
        thread.finished.connect(lambda: self.output_tab.append("Sprint status loaded."))
        thread.start()

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description="Orion Vision Core Debug Interface")
    parser.add_argument("--console", action="store_true", help="Force console mode")
    parser.add_argument("--q1-test", action="store_true", help="Run Q1 quick test and exit")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")
    
    args = parser.parse_args()
    
    print("🚀 Orion Vision Core - Debug Interface Launcher")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        if not args.check_deps:
            print("\n❌ Critical dependencies missing. Please install them first.")
            return 1
        return 0
    
    if args.check_deps:
        print("\n✅ Dependency check completed!")
        return 0
    
    # Q1 quick test
    if args.q1_test:
        success = run_q1_quick_test()
        return 0 if success else 1
    
    # Launch debug interface
    try:
        from jobone.vision_core.debug.debug_interface import run_debug_interface
        
        if args.console:
            # Force console mode
            import jobone.vision_core.debug.debug_interface as debug_module
            debug_module.PYQT_AVAILABLE = False
        
        print("\n🔧 Launching Debug Interface...")
        print("📋 Available Q-Tasks:")
        print("  ✅ Q1: Temel Duyusal Girdi (Screen Capture + OCR + Leptons)")
        print("  🔄 Q2-Q5: Coming soon...")
        print("\n💡 Use the interface to test Q1 components!")
        
        app = QApplication(sys.argv)
        window = DebugLauncher()
        window.show()
        return app.exec()
        
    except KeyboardInterrupt:
        print("\n\n👋 Debug Interface interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Failed to launch debug interface: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
