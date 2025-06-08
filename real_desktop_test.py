#!/usr/bin/env python3
"""
🖥️ Real Desktop Test

Test Orion GUI on real desktop environment
with comprehensive diagnostics

Author: Orion Vision Core Team
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def check_desktop_environment():
    """Check desktop environment details"""
    print("🔍 Desktop Environment Analysis")
    print("="*50)
    
    env_vars = [
        'DISPLAY', 'XDG_SESSION_TYPE', 'XDG_CURRENT_DESKTOP', 
        'DESKTOP_SESSION', 'GDMSESSION', 'WAYLAND_DISPLAY'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")
    
    print("\n🔧 X11 Server Test:")
    try:
        result = subprocess.run(['xset', 'q'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ X11 server accessible")
        else:
            print("⚠️ X11 server access limited")
    except Exception as e:
        print(f"❌ X11 test failed: {e}")
    
    print("\n🖥️ Window Manager Test:")
    try:
        result = subprocess.run(['wmctrl', '-m'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Window manager accessible")
            print(f"WM Info: {result.stdout.strip()}")
        else:
            print("⚠️ wmctrl not available")
    except Exception as e:
        print(f"⚠️ wmctrl test failed: {e}")

def test_pyqt_availability():
    """Test PyQt6 availability and features"""
    print("\n🔧 PyQt6 Availability Test")
    print("="*50)
    
    try:
        from PyQt6.QtWidgets import QApplication, QWidget, QLabel
        from PyQt6.QtCore import Qt
        print("✅ PyQt6 widgets imported successfully")
        
        # Test QApplication creation
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            print("✅ QApplication created")
        else:
            print("✅ QApplication already exists")
        
        # Test widget creation
        widget = QWidget()
        widget.setWindowTitle("Test Widget")
        widget.resize(200, 100)
        print("✅ Test widget created")
        
        # Test platform
        platform = app.platformName()
        print(f"✅ Qt Platform: {platform}")
        
        # Test screen info
        screen = app.primaryScreen()
        if screen:
            geometry = screen.geometry()
            print(f"✅ Primary screen: {geometry.width()}x{geometry.height()}")
        
        return True
        
    except Exception as e:
        print(f"❌ PyQt6 test failed: {e}")
        return False

def test_screen_capture_integration():
    """Test screen capture integration"""
    print("\n📸 Screen Capture Integration Test")
    print("="*50)
    
    try:
        from jobone.vision_core.perception.screen_capture import ScreenCapture
        print("✅ ScreenCapture imported")
        
        # Create instance
        sc = ScreenCapture()
        print(f"✅ ScreenCapture created")
        print(f"📊 Capture method: {getattr(sc, 'capture_method', 'unknown')}")
        print(f"📊 Capture active: {sc.capture_active}")
        
        # Test capture
        print("\n📸 Testing screen capture...")
        img_array = sc.capture_full_screen_as_np_array()
        
        if img_array is not None:
            print(f"✅ Screen captured successfully!")
            print(f"📊 Image shape: {img_array.shape}")
            print(f"📊 Image size: {img_array.nbytes / (1024*1024):.2f} MB")
            
            # Try to save
            success = sc.save_capture_as_image(img_array, 'real_desktop_capture.png')
            if success:
                print("✅ Image saved as 'real_desktop_capture.png'")
            
            return True
        else:
            print("⚠️ Screen capture returned None (using simulation)")
            return False
            
    except Exception as e:
        print(f"❌ Screen capture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_creation():
    """Test GUI creation without showing"""
    print("\n🖥️ GUI Creation Test")
    print("="*50)
    
    try:
        # Import GUI class
        from orion_gui_test import OrionGUITest
        print("✅ OrionGUITest imported")
        
        # Create GUI (don't show)
        window = OrionGUITest()
        print("✅ GUI window created")
        
        # Test properties
        print(f"📊 Window title: {window.windowTitle()}")
        print(f"📊 Window size: {window.size().width()}x{window.size().height()}")
        
        # Test components
        components = [
            ('test_button', 'Test Button'),
            ('clear_button', 'Clear Button'),
            ('results_text', 'Results Text Area'),
            ('status_bar', 'Status Bar'),
            ('progress_bar', 'Progress Bar')
        ]
        
        for attr, name in components:
            if hasattr(window, attr):
                print(f"✅ {name}: Available")
            else:
                print(f"❌ {name}: Missing")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_show_briefly():
    """Test showing GUI briefly"""
    print("\n👁️ GUI Display Test (Brief)")
    print("="*50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        from orion_gui_test import OrionGUITest
        
        # Get or create application
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create window
        window = OrionGUITest()
        print("✅ GUI window created")
        
        # Show window briefly
        window.show()
        print("✅ GUI window shown")
        
        # Process events briefly
        app.processEvents()
        time.sleep(1)  # Show for 1 second
        
        # Hide window
        window.hide()
        print("✅ GUI window hidden")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI display test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Orion Vision Core - Real Desktop Test")
    print("="*60)
    print("🖥️ Testing on Unity Desktop (Pop!_OS)")
    print("="*60)
    
    # Run tests
    tests = [
        ("Desktop Environment", check_desktop_environment),
        ("PyQt6 Availability", test_pyqt_availability),
        ("Screen Capture Integration", test_screen_capture_integration),
        ("GUI Creation", test_gui_creation),
        ("GUI Display (Brief)", test_gui_show_briefly)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            if callable(test_func):
                success = test_func()
            else:
                test_func()
                success = True
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("🎯 REAL DESKTOP TEST RESULTS")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:25} : {status}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL REAL DESKTOP TESTS PASSED!")
        print("🚀 Orion GUI is ready for real desktop use!")
    elif passed >= len(results) * 0.7:
        print("\n✅ MOST TESTS PASSED!")
        print("🎯 Orion GUI is mostly functional on real desktop")
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("🔧 Desktop environment may need configuration")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
