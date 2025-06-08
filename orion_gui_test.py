#!/usr/bin/env python3
"""
🚀 Orion Vision Core - GUI Test Interface

PyQt6 GUI application for testing screen capture functionality
with Xvfb + MSS integration

Author: Orion Vision Core Team
Priority: CRITICAL - GUI Testing Interface
"""

import sys
import os
import traceback
from datetime import datetime
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QStatusBar, QMessageBox,
        QProgressBar, QFrame, QSplitter
    )
    from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QTextCursor, QPixmap
    PYQT_AVAILABLE = True
except ImportError as e:
    print(f"❌ PyQt6 not available: {e}")
    PYQT_AVAILABLE = False
    sys.exit(1)

class ScreenCaptureWorker(QThread):
    """Worker thread for screen capture operations"""
    
    # Signals
    capture_started = pyqtSignal()
    capture_progress = pyqtSignal(str)  # Progress message
    capture_completed = pyqtSignal(dict)  # Results dictionary
    capture_failed = pyqtSignal(str)  # Error message
    
    def __init__(self):
        super().__init__()
        self.screen_capture = None
    
    def run(self):
        """Run screen capture in background thread"""
        try:
            self.capture_started.emit()
            
            # Import ScreenCapture
            self.capture_progress.emit("📦 Importing ScreenCapture module...")
            from jobone.vision_core.perception.screen_capture import ScreenCapture
            
            # Create ScreenCapture instance
            self.capture_progress.emit("🔧 Initializing ScreenCapture...")
            self.screen_capture = ScreenCapture()
            
            # Get capture method info
            capture_method = getattr(self.screen_capture, 'capture_method', 'unknown')
            self.capture_progress.emit(f"📊 Capture method: {capture_method}")
            
            # Perform capture
            self.capture_progress.emit("📸 Capturing screen...")
            img_array = self.screen_capture.capture_full_screen_as_np_array()
            
            if img_array is not None:
                # Get statistics
                stats = self.screen_capture.get_capture_statistics()
                
                # Prepare results
                results = {
                    'success': True,
                    'shape': img_array.shape,
                    'size_mb': img_array.nbytes / (1024 * 1024),
                    'dtype': str(img_array.dtype),
                    'capture_method': capture_method,
                    'statistics': stats,
                    'image_array': img_array
                }
                
                self.capture_progress.emit("✅ Screen capture successful!")
                self.capture_completed.emit(results)
            else:
                self.capture_failed.emit("❌ Screen capture returned None")
                
        except Exception as e:
            error_msg = f"❌ Screen capture failed: {str(e)}"
            self.capture_failed.emit(error_msg)

class OrionGUITest(QMainWindow):
    """Main GUI Test Application"""
    
    def __init__(self):
        super().__init__()
        
        # Window properties
        self.setWindowTitle("Orion Vision Core - Debug Interface")
        self.setGeometry(100, 100, 800, 600)
        self.center_window()
        
        # Worker thread
        self.capture_worker = None
        
        # Setup UI
        self.setup_ui()
        self.setup_status_bar()
        
        # Initial status
        self.update_status("Ready - Orion Vision Core GUI Test Interface")
        
        print("🚀 Orion GUI Test Interface initialized")
    
    def center_window(self):
        """Center window on screen"""
        try:
            # Get screen geometry
            screen = QApplication.primaryScreen().geometry()
            
            # Calculate center position
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            
            # Move window to center
            self.move(x, y)
        except Exception as e:
            print(f"⚠️ Could not center window: {e}")
    
    def setup_ui(self):
        """Setup user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        self.setup_header(main_layout)
        
        # Control panel
        self.setup_controls(main_layout)
        
        # Results area
        self.setup_results_area(main_layout)
    
    def setup_header(self, layout):
        """Setup header section"""
        # Header frame
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.Box)
        header_frame.setStyleSheet("QFrame { background-color: #f0f0f0; border: 1px solid #ccc; }")
        
        header_layout = QVBoxLayout(header_frame)
        
        # Title label
        title_label = QLabel("🚀 Orion Vision Core - Q1 Screen Capture Test")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("QLabel { color: #2c3e50; padding: 10px; }")
        
        # Subtitle
        subtitle_label = QLabel("Enhanced ScreenCapture with Xvfb + MSS Support")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("QLabel { color: #7f8c8d; font-style: italic; }")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
    
    def setup_controls(self, layout):
        """Setup control panel"""
        # Controls frame
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        
        # Test button
        self.test_button = QPushButton("📸 Test Screen Capture")
        self.test_button.setMinimumHeight(40)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.test_button.clicked.connect(self.test_screen_capture)
        
        # Clear button
        self.clear_button = QPushButton("🗑️ Clear Results")
        self.clear_button.setMinimumHeight(40)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_button.clicked.connect(self.clear_results)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 5px;
            }
        """)
        
        controls_layout.addWidget(self.test_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.progress_bar)
        
        layout.addWidget(controls_frame)
    
    def setup_results_area(self, layout):
        """Setup results display area"""
        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setMinimumHeight(300)
        self.results_text.setFont(QFont("Consolas", 10))
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # Initial message
        self.results_text.append("🔧 Orion Vision Core - Debug Interface Ready")
        self.results_text.append("="*60)
        self.results_text.append("📋 Available Features:")
        self.results_text.append("  ✅ Enhanced ScreenCapture with Xvfb support")
        self.results_text.append("  ✅ MSS + Virtual Display integration")
        self.results_text.append("  ✅ Fallback to simulation mode")
        self.results_text.append("  ✅ Real-time progress monitoring")
        self.results_text.append("")
        self.results_text.append("💡 Click 'Test Screen Capture' to begin testing!")
        self.results_text.append("")
        
        layout.addWidget(self.results_text)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Permanent widgets
        self.status_bar.addPermanentWidget(QLabel("Orion Vision Core v1.0"))
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.setText(message)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        cursor = self.results_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.results_text.setTextCursor(cursor)
    
    def test_screen_capture(self):
        """Test screen capture functionality"""
        try:
            # Disable button during test
            self.test_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            self.update_status("🚀 Starting screen capture test...")
            
            # Create and start worker thread
            self.capture_worker = ScreenCaptureWorker()
            self.capture_worker.capture_started.connect(self.on_capture_started)
            self.capture_worker.capture_progress.connect(self.on_capture_progress)
            self.capture_worker.capture_completed.connect(self.on_capture_completed)
            self.capture_worker.capture_failed.connect(self.on_capture_failed)
            self.capture_worker.finished.connect(self.on_capture_finished)
            
            self.capture_worker.start()
            
        except Exception as e:
            self.on_capture_failed(f"❌ Failed to start capture test: {e}")
    
    def on_capture_started(self):
        """Handle capture started"""
        self.update_status("📸 Screen capture test started...")
    
    def on_capture_progress(self, message):
        """Handle capture progress"""
        self.update_status(message)
    
    def on_capture_completed(self, results):
        """Handle successful capture"""
        self.update_status("✅ Screen capture completed successfully!")
        
        # Display results
        self.results_text.append("")
        self.results_text.append("🎯 SCREEN CAPTURE RESULTS")
        self.results_text.append("="*60)
        self.results_text.append(f"📊 Image Shape: {results['shape']}")
        self.results_text.append(f"📊 Image Size: {results['size_mb']:.2f} MB")
        self.results_text.append(f"📊 Data Type: {results['dtype']}")
        self.results_text.append(f"📊 Capture Method: {results['capture_method']}")
        
        # Statistics
        stats = results['statistics']
        self.results_text.append("")
        self.results_text.append("📈 PERFORMANCE STATISTICS")
        self.results_text.append("-"*30)
        self.results_text.append(f"Total Captures: {stats['total_captures']}")
        self.results_text.append(f"Average Time: {stats['average_capture_time']:.3f}s")
        self.results_text.append(f"Last Capture Time: {stats['last_capture_time']:.3f}s")
        self.results_text.append(f"Captures/Second: {stats['captures_per_second']:.1f}")
        self.results_text.append(f"MSS Available: {stats['mss_available']}")
        self.results_text.append(f"PIL Available: {stats['pil_available']}")
        
        self.results_text.append("")
        self.results_text.append("🎉 SCREEN CAPTURE TEST SUCCESSFUL!")
        
        # Try to save image
        try:
            if 'image_array' in results:
                from jobone.vision_core.perception.screen_capture import get_screen_capture
                sc = get_screen_capture()
                success = sc.save_capture_as_image(results['image_array'], 'gui_test_capture.png')
                if success:
                    self.results_text.append("💾 Image saved as 'gui_test_capture.png'")
        except Exception as e:
            self.results_text.append(f"⚠️ Could not save image: {e}")
    
    def on_capture_failed(self, error_message):
        """Handle capture failure"""
        self.update_status("❌ Screen capture test failed")
        self.results_text.append("")
        self.results_text.append("❌ SCREEN CAPTURE FAILED")
        self.results_text.append("="*60)
        self.results_text.append(error_message)
        self.results_text.append("")
        self.results_text.append("💡 This may be normal in headless environments.")
        self.results_text.append("💡 The system should fallback to simulation mode.")
    
    def on_capture_finished(self):
        """Handle capture thread finished"""
        # Re-enable button
        self.test_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Cleanup worker
        if self.capture_worker:
            self.capture_worker.deleteLater()
            self.capture_worker = None
    
    def clear_results(self):
        """Clear results text area"""
        self.results_text.clear()
        self.results_text.append("🔧 Results cleared - Ready for new test")
        self.update_status("Results cleared")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop any running worker
        if self.capture_worker and self.capture_worker.isRunning():
            self.capture_worker.terminate()
            self.capture_worker.wait()
        
        event.accept()

def main():
    """Main application entry point"""
    if not PYQT_AVAILABLE:
        print("❌ PyQt6 is required to run this application")
        print("Install with: pip install PyQt6")
        return 1
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Orion Vision Core")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = OrionGUITest()
    window.show()
    
    print("🚀 Orion GUI Test Interface started")
    print("📋 Window opened - ready for testing!")
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
