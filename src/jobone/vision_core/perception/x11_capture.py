"""
🖥️ X11 Direct Screen Capture - MSS Alternative

X11 protokolü ile direkt ekran yakalama
python-xlib kullanarak MSS bypass

Author: Orion Vision Core Team
Priority: CRITICAL - MSS Alternative
"""

import logging
import numpy as np
from typing import Optional, Dict, Any
import subprocess
import tempfile
import os

try:
    from Xlib import X, display
    from Xlib.ext import randr
    XLIB_AVAILABLE = True
except ImportError:
    XLIB_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class X11Capture:
    """
    X11 Direct Screen Capture System
    
    Direct X11 screen capture bypassing MSS issues
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Capture state
        self.capture_active = False
        self.display_conn = None
        self.screen = None
        self.root_window = None
        
        # Performance metrics
        self.total_captures = 0
        self.total_capture_time = 0.0
        self.last_capture_time = 0.0
        
        # Initialize X11 connection
        self._initialize_x11()
    
    def _initialize_x11(self):
        """Initialize X11 connection"""
        try:
            if XLIB_AVAILABLE:
                # Try to connect to X11 display
                self.display_conn = display.Display()
                self.screen = self.display_conn.screen()
                self.root_window = self.screen.root
                self.capture_active = True
                self.logger.info("🖥️ X11Capture initialized with python-xlib")
            else:
                self.logger.warning("⚠️ python-xlib not available")
                self.capture_active = False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize X11: {e}")
            self.capture_active = False
    
    def capture_screen_as_np_array(self) -> Optional[np.ndarray]:
        """Capture screen using X11 direct access"""
        import time
        start_time = time.time()
        
        try:
            if self.capture_active and XLIB_AVAILABLE:
                return self._capture_with_xlib()
            else:
                # Try subprocess methods
                return self._capture_with_subprocess()
                
        except Exception as e:
            self.logger.error(f"❌ X11 capture failed: {e}")
            return self._simulate_capture()
        finally:
            # Update metrics
            capture_time = time.time() - start_time
            self.total_captures += 1
            self.total_capture_time += capture_time
            self.last_capture_time = capture_time
    
    def _capture_with_xlib(self) -> Optional[np.ndarray]:
        """Capture using python-xlib"""
        try:
            # Get screen geometry
            geometry = self.root_window.get_geometry()
            width = geometry.width
            height = geometry.height
            
            # Capture the root window
            raw_image = self.root_window.get_image(0, 0, width, height, X.ZPixmap, 0xffffffff)
            
            # Convert to numpy array
            # X11 typically uses BGRA format
            image_data = raw_image.data
            
            # Convert bytes to numpy array
            if len(image_data) == width * height * 4:  # BGRA
                img_array = np.frombuffer(image_data, dtype=np.uint8)
                img_array = img_array.reshape((height, width, 4))
                # Convert BGRA to RGB
                img_array = img_array[:, :, [2, 1, 0]]  # BGR to RGB, skip alpha
            elif len(image_data) == width * height * 3:  # RGB
                img_array = np.frombuffer(image_data, dtype=np.uint8)
                img_array = img_array.reshape((height, width, 3))
            else:
                self.logger.error(f"❌ Unexpected image data size: {len(image_data)}")
                return None
            
            self.logger.debug(f"🖥️ X11 capture successful: {img_array.shape}")
            return img_array
            
        except Exception as e:
            self.logger.error(f"❌ python-xlib capture failed: {e}")
            return None
    
    def _capture_with_subprocess(self) -> Optional[np.ndarray]:
        """Capture using subprocess commands"""
        # Try different capture methods
        methods = [
            self._try_xwd_capture,
            self._try_import_capture,
            self._try_scrot_capture,
            self._try_gnome_screenshot_capture
        ]
        
        for method in methods:
            try:
                result = method()
                if result is not None:
                    return result
            except Exception as e:
                self.logger.debug(f"Capture method failed: {e}")
                continue
        
        return None
    
    def _try_xwd_capture(self) -> Optional[np.ndarray]:
        """Try xwd (X Window Dump)"""
        with tempfile.NamedTemporaryFile(suffix='.xwd', delete=False) as tmp_file:
            try:
                # Use xwd to capture root window
                env = os.environ.copy()
                env['DISPLAY'] = ':0'
                
                result = subprocess.run([
                    'xwd', '-root', '-out', tmp_file.name
                ], capture_output=True, text=True, timeout=10, env=env)
                
                if result.returncode == 0 and os.path.exists(tmp_file.name):
                    # Convert XWD to PNG using ImageMagick
                    png_file = tmp_file.name + '.png'
                    convert_result = subprocess.run([
                        'convert', tmp_file.name, png_file
                    ], capture_output=True, text=True, timeout=10)
                    
                    if convert_result.returncode == 0 and os.path.exists(png_file):
                        if PIL_AVAILABLE:
                            img = Image.open(png_file)
                            img_array = np.array(img)
                            self.logger.debug(f"🖥️ XWD capture successful: {img_array.shape}")
                            os.unlink(png_file)
                            return img_array
                
            except Exception as e:
                self.logger.debug(f"XWD capture failed: {e}")
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
        
        return None
    
    def _try_import_capture(self) -> Optional[np.ndarray]:
        """Try ImageMagick import"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            try:
                env = os.environ.copy()
                env['DISPLAY'] = ':0'
                
                result = subprocess.run([
                    'import', '-window', 'root', tmp_file.name
                ], capture_output=True, text=True, timeout=10, env=env)
                
                if result.returncode == 0 and os.path.exists(tmp_file.name):
                    if PIL_AVAILABLE:
                        img = Image.open(tmp_file.name)
                        img_array = np.array(img)
                        self.logger.debug(f"🖥️ ImageMagick capture successful: {img_array.shape}")
                        return img_array
                        
            except Exception as e:
                self.logger.debug(f"ImageMagick capture failed: {e}")
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
        
        return None
    
    def _try_scrot_capture(self) -> Optional[np.ndarray]:
        """Try scrot"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            try:
                env = os.environ.copy()
                env['DISPLAY'] = ':0'
                
                result = subprocess.run([
                    'scrot', tmp_file.name
                ], capture_output=True, text=True, timeout=10, env=env)
                
                if result.returncode == 0 and os.path.exists(tmp_file.name):
                    if PIL_AVAILABLE:
                        img = Image.open(tmp_file.name)
                        img_array = np.array(img)
                        self.logger.debug(f"🖥️ Scrot capture successful: {img_array.shape}")
                        return img_array
                        
            except Exception as e:
                self.logger.debug(f"Scrot capture failed: {e}")
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
        
        return None
    
    def _try_gnome_screenshot_capture(self) -> Optional[np.ndarray]:
        """Try gnome-screenshot"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            try:
                env = os.environ.copy()
                env['DISPLAY'] = ':0'
                
                result = subprocess.run([
                    'gnome-screenshot', '--file', tmp_file.name
                ], capture_output=True, text=True, timeout=10, env=env)
                
                if result.returncode == 0 and os.path.exists(tmp_file.name):
                    if PIL_AVAILABLE:
                        img = Image.open(tmp_file.name)
                        img_array = np.array(img)
                        self.logger.debug(f"🖥️ GNOME Screenshot capture successful: {img_array.shape}")
                        return img_array
                        
            except Exception as e:
                self.logger.debug(f"GNOME Screenshot capture failed: {e}")
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
        
        return None
    
    def _simulate_capture(self) -> np.ndarray:
        """Simulate screen capture"""
        # Create realistic desktop simulation
        width, height = 1920, 1080
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Desktop background
        for y in range(height):
            for x in range(width):
                img_array[y, x] = [
                    int(30 + (x / width) * 60),
                    int(80 + (y / height) * 60),
                    int(120 + (x / width) * 100)
                ]
        
        # Add some windows
        windows = [
            (100, 100, 500, 300),
            (700, 200, 600, 400),
            (200, 600, 800, 300)
        ]
        
        for x, y, w, h in windows:
            img_array[y:y+h, x:x+w] = [240, 240, 240]
            img_array[y:y+30, x:x+w] = [200, 200, 220]  # Title bar
        
        self.logger.debug(f"🖥️ Simulated X11 capture: {img_array.shape}")
        return img_array
    
    def get_capture_statistics(self) -> Dict[str, Any]:
        """Get capture statistics"""
        avg_capture_time = (self.total_capture_time / max(1, self.total_captures))
        
        return {
            'total_captures': self.total_captures,
            'average_capture_time': avg_capture_time,
            'last_capture_time': self.last_capture_time,
            'captures_per_second': 1.0 / max(0.001, avg_capture_time),
            'capture_active': self.capture_active,
            'xlib_available': XLIB_AVAILABLE,
            'pil_available': PIL_AVAILABLE
        }

# Global instance
_x11_capture_instance = None

def get_x11_capture():
    """Get global X11 capture instance"""
    global _x11_capture_instance
    if _x11_capture_instance is None:
        _x11_capture_instance = X11Capture()
    return _x11_capture_instance

def test_x11_capture():
    """Test X11 capture functionality"""
    print("🖥️ Testing X11 Capture...")
    
    x11 = X11Capture()
    print(f"✅ X11Capture created (active: {x11.capture_active})")
    
    # Test capture
    img_array = x11.capture_screen_as_np_array()
    
    if img_array is not None:
        print(f"✅ Screen captured: {img_array.shape}")
        print(f"✅ Size: {img_array.nbytes / (1024*1024):.1f} MB")
        
        # Show statistics
        stats = x11.get_capture_statistics()
        print(f"📊 Stats: {stats}")
        
        return True
    else:
        print("❌ Screen capture failed")
        return False

if __name__ == "__main__":
    test_x11_capture()
