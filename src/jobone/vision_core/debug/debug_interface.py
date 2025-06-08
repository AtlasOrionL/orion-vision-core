"""
🔧 Debug Interface - Q1-Q5 Canlı Test Arayüzü

Orion Vision Core Q-Tasks için debug ve test arayüzü
Ollama local AI entegrasyonu ile canlı test

Author: Orion Vision Core Team
Priority: CRITICAL - Q1-Q5 Canlı Test
"""

import sys
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QPushButton, QLabel, QTabWidget, QSplitter,
        QGroupBox, QCheckBox, QSpinBox, QComboBox, QProgressBar,
        QTableWidget, QTableWidgetItem, QHeaderView
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
    from PyQt6.QtGui import QFont, QTextCursor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("⚠️ PyQt6 not available, falling back to console mode")

class DebugLogger:
    """Debug mesajları için logger"""
    
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.max_messages = 1000
    
    def log(self, level: str, component: str, message: str):
        """Debug mesajı ekle"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'component': component,
            'message': message
        }
        self.messages.append(log_entry)
        
        # Limit message count
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-500:]
        
        # Console output
        print(f"[{timestamp}] {level} {component}: {message}")
    
    def get_recent_messages(self, count: int = 50) -> List[Dict[str, Any]]:
        """Son mesajları getir"""
        return self.messages[-count:] if self.messages else []

class Q1TestController:
    """Q1 (Temel Duyusal Girdi) test kontrolcüsü"""

    def __init__(self, logger: DebugLogger):
        self.logger = logger
        self.screen_capture_active = False
        self.ocr_active = False
        self.lepton_generation_active = False

        # Test results
        self.last_screen_capture = None
        self.last_ocr_result = None
        self.last_leptons = []

        # Import real Q1 components
        try:
            from jobone.vision_core.perception.screen_capture import get_screen_capture
            from jobone.vision_core.perception.ocr_processor import get_ocr_processor
            from jobone.vision_core.quantum.planck_information_unit import create_planck_information_unit

            self.screen_capture = get_screen_capture()
            self.ocr_processor = get_ocr_processor()
            self.planck_unit = create_planck_information_unit()

            self.real_components_available = True
            self.logger.log("SUCCESS", "Q1Controller", "Real Q1 components loaded successfully")

        except Exception as e:
            self.real_components_available = False
            self.logger.log("WARNING", "Q1Controller", f"Real Q1 components not available: {e}")

        self.logger.log("INFO", "Q1Controller", "Q1 Test Controller initialized")
    
    def test_screen_capture(self) -> bool:
        """Test screen capture functionality"""
        try:
            self.logger.log("INFO", "Q1Controller", "Testing screen capture...")

            if self.real_components_available:
                # Use real screen capture
                img_array = self.screen_capture.capture_full_screen_as_np_array()

                if img_array is not None:
                    self.last_screen_capture = {
                        'timestamp': datetime.now(),
                        'resolution': f'{img_array.shape[1]}x{img_array.shape[0]}',
                        'format': 'numpy_array',
                        'size_mb': img_array.nbytes / (1024 * 1024),
                        'shape': img_array.shape,
                        'dtype': str(img_array.dtype),
                        'real_capture': True
                    }

                    # Store the actual image for OCR testing
                    self.last_captured_image = img_array

                    self.screen_capture_active = True
                    self.logger.log("SUCCESS", "Q1Controller", f"Real screen capture successful: {self.last_screen_capture['resolution']}")
                    return True
                else:
                    self.logger.log("ERROR", "Q1Controller", "Real screen capture returned None")
                    return False
            else:
                # Fallback to simulation
                import time
                time.sleep(0.1)

                self.last_screen_capture = {
                    'timestamp': datetime.now(),
                    'resolution': '1920x1080',
                    'format': 'numpy_array',
                    'size_mb': 2.3,
                    'real_capture': False
                }

                self.screen_capture_active = True
                self.logger.log("SUCCESS", "Q1Controller", "Simulated screen capture successful")
                return True

        except Exception as e:
            self.logger.log("ERROR", "Q1Controller", f"Screen capture test failed: {e}")
            return False
    
    def test_ocr_processing(self) -> bool:
        """Test OCR processing"""
        try:
            self.logger.log("INFO", "Q1Controller", "Testing OCR processing...")

            if self.real_components_available and hasattr(self, 'last_captured_image'):
                # Use real OCR on captured image
                ocr_result = self.ocr_processor.detect_text_regions(self.last_captured_image)

                self.last_ocr_result = {
                    'text_regions': ocr_result.get('text_regions', []),
                    'total_regions': ocr_result.get('total_regions', 0),
                    'processing_time': ocr_result.get('processing_time', 0.0),
                    'image_size': ocr_result.get('image_size', (0, 0)),
                    'real_ocr': True
                }

                self.ocr_active = True
                self.logger.log("SUCCESS", "Q1Controller", f"Real OCR found {self.last_ocr_result['total_regions']} text regions")

                # Log some detected text
                for i, region in enumerate(self.last_ocr_result['text_regions'][:3]):
                    self.logger.log("INFO", "Q1Controller", f"Text {i+1}: '{region['text']}' (conf: {region['confidence']:.2f})")

                return True

            elif self.real_components_available:
                # No captured image available, use OCR processor with test image
                import numpy as np
                test_img = np.ones((300, 600, 3), dtype=np.uint8) * 255  # White test image

                ocr_result = self.ocr_processor.detect_text_regions(test_img)

                self.last_ocr_result = {
                    'text_regions': ocr_result.get('text_regions', []),
                    'total_regions': ocr_result.get('total_regions', 0),
                    'processing_time': ocr_result.get('processing_time', 0.0),
                    'image_size': ocr_result.get('image_size', (600, 300)),
                    'real_ocr': True,
                    'test_image': True
                }

                self.ocr_active = True
                self.logger.log("SUCCESS", "Q1Controller", f"Real OCR test found {self.last_ocr_result['total_regions']} text regions")
                return True

            else:
                # Fallback to simulation
                time.sleep(0.2)

                self.last_ocr_result = {
                    'text_regions': [
                        {'text': 'Debug Interface', 'confidence': 0.95, 'bbox': (100, 50, 200, 80)},
                        {'text': 'Q1 Test Active', 'confidence': 0.88, 'bbox': (150, 100, 250, 130)},
                        {'text': 'Orion Vision Core', 'confidence': 0.92, 'bbox': (200, 150, 350, 180)}
                    ],
                    'total_regions': 3,
                    'processing_time': 0.2,
                    'real_ocr': False
                }

                self.ocr_active = True
                self.logger.log("SUCCESS", "Q1Controller", f"Simulated OCR found {len(self.last_ocr_result['text_regions'])} text regions")
                return True

        except Exception as e:
            self.logger.log("ERROR", "Q1Controller", f"OCR test failed: {e}")
            return False
    
    def test_lepton_generation(self) -> bool:
        """Test Lepton generation from OCR results"""
        try:
            self.logger.log("INFO", "Q1Controller", "Testing Lepton generation...")
            
            if not self.last_ocr_result:
                self.logger.log("WARNING", "Q1Controller", "No OCR results available for Lepton generation")
                return False
            
            # Generate Leptons from OCR results
            self.last_leptons = []
            for i, region in enumerate(self.last_ocr_result['text_regions']):
                lepton = {
                    'id': f"lepton_{i}",
                    'type': 'text',
                    'value': region['text'],
                    'position': region['bbox'],
                    'effective_mass': 0.1,  # Low initial mass
                    'polarization': '+' if region['confidence'] > 0.9 else '0',
                    'seed': f"q1_test_{int(time.time())}_{i}",
                    'temporal_index': i,
                    'confidence': region['confidence']
                }
                self.last_leptons.append(lepton)
            
            self.lepton_generation_active = True
            self.logger.log("SUCCESS", "Q1Controller", f"Generated {len(self.last_leptons)} Leptons")
            return True
            
        except Exception as e:
            self.logger.log("ERROR", "Q1Controller", f"Lepton generation failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get Q1 test status"""
        return {
            'screen_capture_active': self.screen_capture_active,
            'ocr_active': self.ocr_active,
            'lepton_generation_active': self.lepton_generation_active,
            'last_screen_capture': self.last_screen_capture,
            'last_ocr_result': self.last_ocr_result,
            'leptons_count': len(self.last_leptons),
            'last_leptons': self.last_leptons[-3:] if self.last_leptons else []  # Show last 3
        }

class DebugInterface(QMainWindow if PYQT_AVAILABLE else object):
    """Ana debug arayüzü"""

    def __init__(self, app=None):
        # Store QApplication reference
        self.app = app

        if PYQT_AVAILABLE and app is not None:
            super().__init__()

        # Initialize components
        self.logger = DebugLogger()
        self.q1_controller = Q1TestController(self.logger)

        # UI components
        self.log_display = None
        self.status_display = None
        self.q1_status_display = None

        # Timers
        self.update_timer = None

        if PYQT_AVAILABLE and app is not None:
            self.setup_ui()
            self.setup_timers()

        self.logger.log("INFO", "DebugInterface", "Debug Interface initialized")
    
    def setup_ui(self):
        """Setup PyQt6 UI"""
        self.setWindowTitle("🔧 Orion Vision Core - Debug Interface")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Logs and Status
        right_panel = self.create_log_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
    
    def create_control_panel(self) -> QWidget:
        """Create control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Q1 Controls
        q1_group = QGroupBox("🔍 Q1: Temel Duyusal Girdi")
        q1_layout = QVBoxLayout(q1_group)
        
        # Q1 Test buttons
        self.btn_q1_screen_capture = QPushButton("📸 Test Screen Capture")
        self.btn_q1_screen_capture.clicked.connect(self.test_q1_screen_capture)
        q1_layout.addWidget(self.btn_q1_screen_capture)
        
        self.btn_q1_ocr = QPushButton("📝 Test OCR Processing")
        self.btn_q1_ocr.clicked.connect(self.test_q1_ocr)
        q1_layout.addWidget(self.btn_q1_ocr)
        
        self.btn_q1_leptons = QPushButton("⚛️ Test Lepton Generation")
        self.btn_q1_leptons.clicked.connect(self.test_q1_leptons)
        q1_layout.addWidget(self.btn_q1_leptons)
        
        self.btn_q1_full_test = QPushButton("🚀 Q1 Full Test")
        self.btn_q1_full_test.clicked.connect(self.test_q1_full)
        q1_layout.addWidget(self.btn_q1_full_test)
        
        # Q1 Status display
        self.q1_status_display = QTextEdit()
        self.q1_status_display.setMaximumHeight(200)
        self.q1_status_display.setReadOnly(True)
        q1_layout.addWidget(self.q1_status_display)
        
        layout.addWidget(q1_group)
        
        # Placeholder for Q2-Q5
        placeholder_group = QGroupBox("🔮 Q2-Q5: Coming Soon")
        placeholder_layout = QVBoxLayout(placeholder_group)
        placeholder_label = QLabel("Q2-Q5 controls will be added after Q1 testing")
        placeholder_layout.addWidget(placeholder_label)
        layout.addWidget(placeholder_group)
        
        layout.addStretch()
        return panel
    
    def create_log_panel(self) -> QWidget:
        """Create log and status panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Status display
        status_group = QGroupBox("📊 System Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_display = QTextEdit()
        self.status_display.setMaximumHeight(150)
        self.status_display.setReadOnly(True)
        status_layout.addWidget(self.status_display)
        
        layout.addWidget(status_group)
        
        # Log display
        log_group = QGroupBox("📝 Debug Logs")
        log_layout = QVBoxLayout(log_group)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_display)
        
        layout.addWidget(log_group)
        
        return panel
    
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(1000)  # Update every second
    
    def test_q1_screen_capture(self):
        """Test Q1 screen capture"""
        self.logger.log("INFO", "UI", "User triggered Q1 screen capture test")
        success = self.q1_controller.test_screen_capture()
        if success:
            self.logger.log("SUCCESS", "UI", "Q1 screen capture test completed")
        else:
            self.logger.log("ERROR", "UI", "Q1 screen capture test failed")
    
    def test_q1_ocr(self):
        """Test Q1 OCR processing"""
        self.logger.log("INFO", "UI", "User triggered Q1 OCR test")
        success = self.q1_controller.test_ocr_processing()
        if success:
            self.logger.log("SUCCESS", "UI", "Q1 OCR test completed")
        else:
            self.logger.log("ERROR", "UI", "Q1 OCR test failed")
    
    def test_q1_leptons(self):
        """Test Q1 Lepton generation"""
        self.logger.log("INFO", "UI", "User triggered Q1 Lepton generation test")
        success = self.q1_controller.test_lepton_generation()
        if success:
            self.logger.log("SUCCESS", "UI", "Q1 Lepton generation test completed")
        else:
            self.logger.log("ERROR", "UI", "Q1 Lepton generation test failed")
    
    def test_q1_full(self):
        """Run full Q1 test sequence"""
        self.logger.log("INFO", "UI", "User triggered Q1 full test sequence")
        
        # Run tests in sequence
        tests = [
            ("Screen Capture", self.q1_controller.test_screen_capture),
            ("OCR Processing", self.q1_controller.test_ocr_processing),
            ("Lepton Generation", self.q1_controller.test_lepton_generation)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            self.logger.log("INFO", "UI", f"Running {test_name} test...")
            success = test_func()
            if not success:
                all_passed = False
                break
            time.sleep(0.5)  # Small delay between tests
        
        if all_passed:
            self.logger.log("SUCCESS", "UI", "🎉 Q1 full test sequence PASSED!")
        else:
            self.logger.log("ERROR", "UI", "❌ Q1 full test sequence FAILED!")
    
    def update_displays(self):
        """Update all displays"""
        if not PYQT_AVAILABLE:
            return
        
        # Update logs
        recent_logs = self.logger.get_recent_messages(50)
        log_text = ""
        for log in recent_logs:
            color = {
                'INFO': 'blue',
                'SUCCESS': 'green',
                'WARNING': 'orange',
                'ERROR': 'red'
            }.get(log['level'], 'black')
            
            log_text += f"<span style='color: {color}'>[{log['timestamp']}] {log['level']} {log['component']}: {log['message']}</span><br>"
        
        self.log_display.setHtml(log_text)
        
        # Scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
        
        # Update Q1 status
        q1_status = self.q1_controller.get_status()
        q1_text = f"""
<b>Q1 Status:</b><br>
📸 Screen Capture: {'✅ Active' if q1_status['screen_capture_active'] else '❌ Inactive'}<br>
📝 OCR Processing: {'✅ Active' if q1_status['ocr_active'] else '❌ Inactive'}<br>
⚛️ Lepton Generation: {'✅ Active' if q1_status['lepton_generation_active'] else '❌ Inactive'}<br>
<br>
<b>Leptons Count:</b> {q1_status['leptons_count']}<br>
"""
        
        if q1_status['last_leptons']:
            q1_text += "<b>Recent Leptons:</b><br>"
            for lepton in q1_status['last_leptons']:
                q1_text += f"• {lepton['value']} (mass: {lepton['effective_mass']})<br>"
        
        self.q1_status_display.setHtml(q1_text)
        
        # Update system status
        status_text = f"""
<b>System Status:</b><br>
🕐 Time: {datetime.now().strftime('%H:%M:%S')}<br>
📊 Total Logs: {len(self.logger.messages)}<br>
🔧 Debug Interface: Active<br>
"""
        self.status_display.setHtml(status_text)

def run_debug_interface():
    """Run debug interface"""
    if PYQT_AVAILABLE:
        app = QApplication(sys.argv)
        window = DebugInterface(app)  # Pass app to constructor
        window.show()
        return app.exec()
    else:
        # Console fallback
        print("🔧 Orion Vision Core - Debug Interface (Console Mode)")
        print("PyQt6 not available, running in console mode")

        interface = DebugInterface()  # No app needed for console mode

        while True:
            print("\n" + "="*50)
            print("🔧 DEBUG INTERFACE MENU")
            print("="*50)
            print("1. Test Q1 Screen Capture")
            print("2. Test Q1 OCR Processing")
            print("3. Test Q1 Lepton Generation")
            print("4. Run Q1 Full Test")
            print("5. Show Q1 Status")
            print("6. Show Recent Logs")
            print("0. Exit")

            choice = input("\nSelect option: ").strip()

            if choice == "1":
                interface.q1_controller.test_screen_capture()
            elif choice == "2":
                interface.q1_controller.test_ocr_processing()
            elif choice == "3":
                interface.q1_controller.test_lepton_generation()
            elif choice == "4":
                test_q1_full_console(interface)
            elif choice == "5":
                status = interface.q1_controller.get_status()
                print(f"\n📊 Q1 Status: {status}")
            elif choice == "6":
                logs = interface.logger.get_recent_messages(10)
                print("\n📝 Recent Logs:")
                for log in logs:
                    print(f"[{log['timestamp']}] {log['level']} {log['component']}: {log['message']}")
            elif choice == "0":
                break
            else:
                print("Invalid option!")

def test_q1_full_console(interface):
    """Run full Q1 test sequence for console mode"""
    print("\n🚀 Running Q1 Full Test Sequence...")
    print("="*50)

    # Run tests in sequence
    tests = [
        ("Screen Capture", interface.q1_controller.test_screen_capture),
        ("OCR Processing", interface.q1_controller.test_ocr_processing),
        ("Lepton Generation", interface.q1_controller.test_lepton_generation)
    ]

    all_passed = True
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        success = test_func()
        if success:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
            all_passed = False
        time.sleep(0.5)  # Small delay between tests

    print("\n" + "="*50)
    if all_passed:
        print("🎉 Q1 FULL TEST SEQUENCE: ALL PASSED!")
    else:
        print("❌ Q1 FULL TEST SEQUENCE: SOME FAILED!")
    print("="*50)

if __name__ == "__main__":
    run_debug_interface()
