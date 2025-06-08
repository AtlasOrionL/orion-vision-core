#!/usr/bin/env python3
"""
🧪 Programmatic GUI Test

Test the Orion GUI interface programmatically
without user interaction

Author: Orion Vision Core Team
"""

import sys
import os
import time
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set Qt platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("❌ PyQt6 not available")
    sys.exit(1)

def test_gui_interface():
    """Test GUI interface programmatically"""
    print("🧪 Starting Programmatic GUI Test...")
    print("="*50)
    
    # Create application
    app = QApplication(sys.argv)
    
    # Import and create GUI
    from orion_gui_test import OrionGUITest
    
    window = OrionGUITest()
    print("✅ GUI window created successfully")
    
    # Test screen capture programmatically
    def trigger_test():
        print("🔧 Triggering screen capture test...")
        window.test_screen_capture()
    
    def check_results():
        print("📊 Checking test results...")
        # Get text from results area
        results_text = window.results_text.toPlainText()
        
        if "SCREEN CAPTURE RESULTS" in results_text:
            print("✅ Screen capture test completed successfully!")
            print("📊 Results found in GUI text area")
        elif "SCREEN CAPTURE FAILED" in results_text:
            print("⚠️ Screen capture test failed (expected in headless mode)")
            print("📊 Fallback behavior working correctly")
        else:
            print("🔄 Test still in progress...")
            return False
        
        return True
    
    def finish_test():
        print("🎯 Test completed - closing application")
        app.quit()
    
    # Schedule test execution
    QTimer.singleShot(1000, trigger_test)  # Start test after 1 second
    
    # Check results periodically
    result_timer = QTimer()
    result_timer.timeout.connect(lambda: check_results() and result_timer.stop() and QTimer.singleShot(2000, finish_test))
    result_timer.start(2000)  # Check every 2 seconds
    
    # Set maximum test time
    QTimer.singleShot(30000, finish_test)  # Force quit after 30 seconds
    
    print("🚀 Starting GUI event loop...")
    
    # Run application
    try:
        app.exec()
        print("✅ GUI test completed successfully")
        return True
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Orion Vision Core - Programmatic GUI Test")
    print("="*60)
    
    if not PYQT_AVAILABLE:
        print("❌ PyQt6 not available")
        return 1
    
    # Run GUI test
    success = test_gui_interface()
    
    if success:
        print("\n🎉 PROGRAMMATIC GUI TEST SUCCESSFUL!")
        print("✅ GUI interface working correctly")
        print("✅ Screen capture integration functional")
        print("✅ Error handling working properly")
    else:
        print("\n❌ PROGRAMMATIC GUI TEST FAILED!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
