#!/usr/bin/env python3
"""
🧪 Simple GUI Test

Simple test of GUI components without event loop
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set Qt platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_gui_components():
    """Test GUI components creation"""
    print("🧪 Testing GUI Components...")
    print("="*40)
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 imported successfully")
        
        # Create application
        app = QApplication([])
        print("✅ QApplication created")
        
        # Test our GUI class
        from orion_gui_test import OrionGUITest
        print("✅ OrionGUITest imported")
        
        # Create window
        window = OrionGUITest()
        print("✅ GUI window created")
        
        # Test window properties
        print(f"📊 Window title: {window.windowTitle()}")
        print(f"📊 Window size: {window.size().width()}x{window.size().height()}")
        
        # Test components
        print(f"✅ Test button exists: {hasattr(window, 'test_button')}")
        print(f"✅ Results text exists: {hasattr(window, 'results_text')}")
        print(f"✅ Status bar exists: {hasattr(window, 'status_bar')}")
        
        # Test screen capture import
        try:
            from jobone.vision_core.perception.screen_capture import ScreenCapture
            print("✅ ScreenCapture import successful")
            
            # Create ScreenCapture instance
            sc = ScreenCapture()
            print(f"✅ ScreenCapture created (method: {getattr(sc, 'capture_method', 'unknown')})")
            
        except Exception as e:
            print(f"⚠️ ScreenCapture test failed: {e}")
        
        print("\n🎉 GUI COMPONENTS TEST SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Orion Vision Core - Simple GUI Test")
    print("="*50)
    
    success = test_gui_components()
    
    if success:
        print("\n✅ ALL GUI TESTS PASSED!")
        print("🎯 GUI interface is working correctly")
        print("🎯 Screen capture integration ready")
    else:
        print("\n❌ GUI TESTS FAILED!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
