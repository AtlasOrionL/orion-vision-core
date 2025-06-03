#!/usr/bin/env python3
"""
🎮 Optimized Screen Capture - Gaming AI

High-performance screen capture with multi-monitor support and memory optimization.

Sprint 1 - Task 1.3: Screen Capture Optimization
- Region-based capture for performance
- Multi-monitor support
- Memory usage optimization
- <100MB memory usage, <5ms capture time target

Author: Nexus - Quantum AI Architect
Sprint: 1.3 - Foundation & Vision System
"""

import cv2
import numpy as np
import time
import threading
import psutil
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from PIL import ImageGrab, Image
import warnings

# Platform-specific optimizations
import platform
SYSTEM = platform.system()

# Windows-specific optimizations
if SYSTEM == "Windows":
    try:
        import win32gui
        import win32ui
        import win32con
        import win32api
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
        warnings.warn("🎮 Win32 not available. Install with: pip install pywin32", ImportWarning)
else:
    WIN32_AVAILABLE = False

# Linux-specific optimizations
if SYSTEM == "Linux":
    try:
        import Xlib
        import Xlib.display
        XLIB_AVAILABLE = True
    except ImportError:
        XLIB_AVAILABLE = False
        warnings.warn("🎮 Xlib not available. Install with: pip install python-xlib", ImportWarning)
else:
    XLIB_AVAILABLE = False

@dataclass
class CaptureRegion:
    """Screen capture region definition"""
    x: int
    y: int
    width: int
    height: int
    monitor_id: int = 0
    name: str = "default"

@dataclass
class CaptureConfig:
    """Screen capture configuration"""
    target_fps: int = 60
    max_memory_mb: int = 100
    enable_compression: bool = True
    compression_quality: int = 85
    buffer_size: int = 3
    enable_threading: bool = True
    capture_method: str = "auto"  # auto, pil, win32, xlib
    
@dataclass
class CaptureMetrics:
    """Capture performance metrics"""
    capture_time_ms: float
    memory_usage_mb: float
    fps: float
    frames_captured: int
    total_time: float
    compression_ratio: float

class OptimizedScreenCapture:
    """
    Optimized Screen Capture System for Gaming AI
    
    Features:
    - Multi-monitor support
    - Region-based capture
    - Memory optimization
    - Platform-specific optimizations
    - <5ms capture time, <100MB memory target
    """
    
    def __init__(self, config: CaptureConfig = None):
        self.config = config or CaptureConfig()
        self.logger = logging.getLogger("OptimizedScreenCapture")
        
        # Performance metrics
        self.metrics = CaptureMetrics(0, 0, 0, 0, 0, 0)
        self.performance_history = []
        
        # Threading
        self.capture_lock = threading.Lock()
        self.buffer_lock = threading.Lock()
        
        # Frame buffer for smooth capture
        self.frame_buffer = []
        self.buffer_index = 0
        
        # Monitor information
        self.monitors = self._detect_monitors()
        
        # Capture method selection
        self.capture_method = self._select_optimal_capture_method()
        
        # Memory monitoring
        self.process = psutil.Process()
        
        self.logger.info(f"🎮 Optimized Screen Capture initialized with {self.capture_method} method")
        self.logger.info(f"📺 Detected {len(self.monitors)} monitors")
    
    def _detect_monitors(self) -> List[Dict[str, Any]]:
        """Detect available monitors"""
        monitors = []
        
        try:
            if SYSTEM == "Windows" and WIN32_AVAILABLE:
                monitors = self._detect_windows_monitors()
            elif SYSTEM == "Linux" and XLIB_AVAILABLE:
                monitors = self._detect_linux_monitors()
            else:
                # Fallback to PIL method
                monitors = self._detect_pil_monitors()
                
        except Exception as e:
            self.logger.error(f"🎮 Monitor detection failed: {e}")
            # Default single monitor
            monitors = [{"id": 0, "x": 0, "y": 0, "width": 1920, "height": 1080, "primary": True}]
        
        return monitors
    
    def _detect_windows_monitors(self) -> List[Dict[str, Any]]:
        """Detect monitors on Windows"""
        monitors = []
        
        def enum_callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            monitor_info = win32api.GetMonitorInfo(hMonitor)
            rect = monitor_info['Monitor']
            
            monitor = {
                "id": len(monitors),
                "x": rect[0],
                "y": rect[1], 
                "width": rect[2] - rect[0],
                "height": rect[3] - rect[1],
                "primary": monitor_info['Flags'] == win32con.MONITORINFOF_PRIMARY,
                "handle": hMonitor
            }
            monitors.append(monitor)
            return True
        
        win32api.EnumDisplayMonitors(None, None, enum_callback, 0)
        return monitors
    
    def _detect_linux_monitors(self) -> List[Dict[str, Any]]:
        """Detect monitors on Linux"""
        monitors = []
        
        try:
            display = Xlib.display.Display()
            screen = display.screen()
            
            # Get screen dimensions
            width = screen.width_in_pixels
            height = screen.height_in_pixels
            
            monitor = {
                "id": 0,
                "x": 0,
                "y": 0,
                "width": width,
                "height": height,
                "primary": True
            }
            monitors.append(monitor)
            
        except Exception as e:
            self.logger.error(f"🎮 Linux monitor detection failed: {e}")
        
        return monitors
    
    def _detect_pil_monitors(self) -> List[Dict[str, Any]]:
        """Detect monitors using PIL (fallback)"""
        try:
            # PIL doesn't provide multi-monitor info, use screen size
            screen = ImageGrab.grab()
            width, height = screen.size
            
            monitor = {
                "id": 0,
                "x": 0,
                "y": 0,
                "width": width,
                "height": height,
                "primary": True
            }
            return [monitor]
            
        except Exception as e:
            self.logger.error(f"🎮 PIL monitor detection failed: {e}")
            return [{"id": 0, "x": 0, "y": 0, "width": 1920, "height": 1080, "primary": True}]
    
    def _select_optimal_capture_method(self) -> str:
        """Select optimal capture method based on platform and availability"""
        if self.config.capture_method != "auto":
            return self.config.capture_method
        
        # Platform-specific optimization
        if SYSTEM == "Windows" and WIN32_AVAILABLE:
            return "win32"
        elif SYSTEM == "Linux" and XLIB_AVAILABLE:
            return "xlib"
        else:
            return "pil"
    
    def capture_screen_optimized(self, region: Optional[CaptureRegion] = None) -> np.ndarray:
        """Optimized screen capture with performance monitoring"""
        start_time = time.time()
        
        try:
            with self.capture_lock:
                # Select capture method
                if self.capture_method == "win32":
                    screen = self._capture_win32(region)
                elif self.capture_method == "xlib":
                    screen = self._capture_xlib(region)
                else:
                    screen = self._capture_pil(region)
                
                # Apply compression if enabled
                if self.config.enable_compression:
                    screen = self._compress_frame(screen)
                
                # Update metrics
                capture_time = (time.time() - start_time) * 1000  # Convert to ms
                self._update_metrics(capture_time, screen)
                
                return screen
                
        except Exception as e:
            self.logger.error(f"🎮 Optimized capture failed: {e}")
            return np.zeros((100, 100, 3), dtype=np.uint8)
    
    def _capture_win32(self, region: Optional[CaptureRegion] = None) -> np.ndarray:
        """Windows-optimized capture using Win32 API"""
        if not WIN32_AVAILABLE:
            return self._capture_pil(region)
        
        try:
            # Get desktop window
            hwnd = win32gui.GetDesktopWindow()
            
            # Get window DC
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Determine capture area
            if region:
                left, top, width, height = region.x, region.y, region.width, region.height
            else:
                left, top, width, height = 0, 0, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Copy screen to bitmap
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (left, top), win32con.SRCCOPY)
            
            # Convert to numpy array
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (height, width, 4)  # BGRA format
            
            # Convert BGRA to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            return img
            
        except Exception as e:
            self.logger.error(f"🎮 Win32 capture failed: {e}")
            return self._capture_pil(region)
    
    def _capture_xlib(self, region: Optional[CaptureRegion] = None) -> np.ndarray:
        """Linux-optimized capture using Xlib"""
        if not XLIB_AVAILABLE:
            return self._capture_pil(region)
        
        try:
            display = Xlib.display.Display()
            root = display.screen().root
            
            # Determine capture area
            if region:
                x, y, width, height = region.x, region.y, region.width, region.height
            else:
                geometry = root.get_geometry()
                x, y, width, height = 0, 0, geometry.width, geometry.height
            
            # Capture screen
            raw = root.get_image(x, y, width, height, Xlib.X.ZPixmap, 0xffffffff)
            
            # Convert to numpy array
            img = np.frombuffer(raw.data, dtype=np.uint8)
            img = img.reshape((height, width, 4))  # BGRA format
            
            # Convert BGRA to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            
            return img
            
        except Exception as e:
            self.logger.error(f"🎮 Xlib capture failed: {e}")
            return self._capture_pil(region)
    
    def _capture_pil(self, region: Optional[CaptureRegion] = None) -> np.ndarray:
        """PIL-based capture (cross-platform fallback)"""
        try:
            if region:
                bbox = (region.x, region.y, region.x + region.width, region.y + region.height)
                screenshot = ImageGrab.grab(bbox=bbox)
            else:
                screenshot = ImageGrab.grab()
            
            return np.array(screenshot)
            
        except Exception as e:
            self.logger.error(f"🎮 PIL capture failed: {e}")
            return np.zeros((100, 100, 3), dtype=np.uint8)
    
    def _compress_frame(self, frame: np.ndarray) -> np.ndarray:
        """Compress frame to reduce memory usage"""
        try:
            if not self.config.enable_compression:
                return frame
            
            # JPEG compression for memory optimization
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.config.compression_quality]
            _, compressed = cv2.imencode('.jpg', frame, encode_param)
            
            # Decompress back to numpy array
            decompressed = cv2.imdecode(compressed, cv2.IMREAD_COLOR)
            
            # Calculate compression ratio
            original_size = frame.nbytes
            compressed_size = compressed.nbytes
            self.metrics.compression_ratio = compressed_size / original_size
            
            return decompressed
            
        except Exception as e:
            self.logger.error(f"🎮 Frame compression failed: {e}")
            return frame
    
    def _update_metrics(self, capture_time_ms: float, frame: np.ndarray):
        """Update performance metrics"""
        try:
            # Update capture metrics
            self.metrics.capture_time_ms = capture_time_ms
            self.metrics.frames_captured += 1
            
            # Calculate memory usage
            memory_info = self.process.memory_info()
            self.metrics.memory_usage_mb = memory_info.rss / 1024 / 1024
            
            # Calculate FPS
            current_time = time.time()
            if hasattr(self, '_last_capture_time'):
                time_diff = current_time - self._last_capture_time
                self.metrics.fps = 1.0 / time_diff if time_diff > 0 else 0
            self._last_capture_time = current_time
            
            # Store performance history
            self.performance_history.append({
                'timestamp': current_time,
                'capture_time_ms': capture_time_ms,
                'memory_mb': self.metrics.memory_usage_mb,
                'fps': self.metrics.fps
            })
            
            # Keep only recent history (last 100 frames)
            if len(self.performance_history) > 100:
                self.performance_history.pop(0)
            
            # Log performance warnings
            if capture_time_ms > 5.0:  # Target: <5ms
                self.logger.warning(f"🎮 Slow capture: {capture_time_ms:.1f}ms")
            
            if self.metrics.memory_usage_mb > self.config.max_memory_mb:
                self.logger.warning(f"🎮 High memory usage: {self.metrics.memory_usage_mb:.1f}MB")
                
        except Exception as e:
            self.logger.error(f"🎮 Metrics update failed: {e}")
    
    def capture_region_async(self, region: CaptureRegion, callback=None) -> threading.Thread:
        """Asynchronous region capture"""
        def capture_worker():
            try:
                frame = self.capture_screen_optimized(region)
                if callback:
                    callback(frame, region)
            except Exception as e:
                self.logger.error(f"🎮 Async capture failed: {e}")
        
        thread = threading.Thread(target=capture_worker, daemon=True)
        thread.start()
        return thread
    
    def start_continuous_capture(self, region: Optional[CaptureRegion] = None, 
                                fps: int = None) -> threading.Thread:
        """Start continuous screen capture"""
        target_fps = fps or self.config.target_fps
        frame_time = 1.0 / target_fps
        
        def continuous_worker():
            self.logger.info(f"🎮 Starting continuous capture at {target_fps} FPS")
            
            while getattr(self, '_capture_active', True):
                try:
                    start_time = time.time()
                    
                    frame = self.capture_screen_optimized(region)
                    
                    # Add to buffer
                    with self.buffer_lock:
                        if len(self.frame_buffer) >= self.config.buffer_size:
                            self.frame_buffer.pop(0)
                        self.frame_buffer.append({
                            'frame': frame,
                            'timestamp': time.time(),
                            'region': region
                        })
                    
                    # Maintain target FPS
                    elapsed = time.time() - start_time
                    if elapsed < frame_time:
                        time.sleep(frame_time - elapsed)
                        
                except Exception as e:
                    self.logger.error(f"🎮 Continuous capture error: {e}")
                    time.sleep(0.1)
        
        self._capture_active = True
        thread = threading.Thread(target=continuous_worker, daemon=True)
        thread.start()
        return thread
    
    def stop_continuous_capture(self):
        """Stop continuous capture"""
        self._capture_active = False
        self.logger.info("🎮 Continuous capture stopped")
    
    def get_latest_frame(self) -> Optional[Dict[str, Any]]:
        """Get latest frame from buffer"""
        with self.buffer_lock:
            return self.frame_buffer[-1] if self.frame_buffer else None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            'capture_time_ms': self.metrics.capture_time_ms,
            'memory_usage_mb': self.metrics.memory_usage_mb,
            'fps': self.metrics.fps,
            'frames_captured': self.metrics.frames_captured,
            'compression_ratio': self.metrics.compression_ratio,
            'capture_method': self.capture_method,
            'monitors_detected': len(self.monitors),
            'buffer_size': len(self.frame_buffer),
            'performance_history': self.performance_history[-10:]  # Last 10 frames
        }
    
    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """Get detected monitor information"""
        return self.monitors.copy()
    
    def create_gaming_regions(self) -> Dict[str, CaptureRegion]:
        """Create common gaming capture regions"""
        if not self.monitors:
            return {}
        
        primary_monitor = next((m for m in self.monitors if m.get('primary')), self.monitors[0])
        width, height = primary_monitor['width'], primary_monitor['height']
        
        regions = {
            'full_screen': CaptureRegion(0, 0, width, height, 0, 'full_screen'),
            'top_left': CaptureRegion(0, 0, width//2, height//2, 0, 'top_left'),
            'top_right': CaptureRegion(width//2, 0, width//2, height//2, 0, 'top_right'),
            'bottom_left': CaptureRegion(0, height//2, width//2, height//2, 0, 'bottom_left'),
            'bottom_right': CaptureRegion(width//2, height//2, width//2, height//2, 0, 'bottom_right'),
            'center': CaptureRegion(width//4, height//4, width//2, height//2, 0, 'center'),
            'ui_top': CaptureRegion(0, 0, width, height//4, 0, 'ui_top'),
            'ui_bottom': CaptureRegion(0, 3*height//4, width, height//4, 0, 'ui_bottom'),
            'minimap': CaptureRegion(3*width//4, 0, width//4, height//4, 0, 'minimap'),
            'chat': CaptureRegion(0, 2*height//3, width//3, height//3, 0, 'chat')
        }
        
        return regions

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎮 Optimized Screen Capture - Sprint 1 Test")
    print("=" * 60)
    
    # Create optimized capture system
    config = CaptureConfig(
        target_fps=60,
        max_memory_mb=100,
        enable_compression=True,
        compression_quality=85,
        capture_method="auto"
    )
    
    capture_system = OptimizedScreenCapture(config)
    
    # Test monitor detection
    monitors = capture_system.get_monitor_info()
    print(f"\n📺 Monitor Detection:")
    for monitor in monitors:
        print(f"   Monitor {monitor['id']}: {monitor['width']}x{monitor['height']} "
              f"at ({monitor['x']}, {monitor['y']}) {'(Primary)' if monitor.get('primary') else ''}")
    
    # Test optimized capture
    print(f"\n📸 Testing optimized capture with {capture_system.capture_method} method...")
    
    # Capture full screen
    start_time = time.time()
    screen = capture_system.capture_screen_optimized()
    capture_time = (time.time() - start_time) * 1000
    
    print(f"✅ Full screen captured: {screen.shape} in {capture_time:.1f}ms")
    
    # Test region capture
    gaming_regions = capture_system.create_gaming_regions()
    print(f"\n🎯 Testing region capture...")
    
    for region_name, region in list(gaming_regions.items())[:3]:  # Test first 3 regions
        start_time = time.time()
        region_screen = capture_system.capture_screen_optimized(region)
        region_time = (time.time() - start_time) * 1000
        
        print(f"   {region_name}: {region_screen.shape} in {region_time:.1f}ms")
    
    # Performance metrics
    metrics = capture_system.get_performance_metrics()
    print(f"\n📊 Performance Metrics:")
    print(f"   Capture Time: {metrics['capture_time_ms']:.1f}ms (Target: <5ms)")
    print(f"   Memory Usage: {metrics['memory_usage_mb']:.1f}MB (Target: <100MB)")
    print(f"   FPS: {metrics['fps']:.1f}")
    print(f"   Compression Ratio: {metrics['compression_ratio']:.2f}")
    print(f"   Capture Method: {metrics['capture_method']}")
    
    # Test continuous capture for a few seconds
    print(f"\n🔄 Testing continuous capture for 3 seconds...")
    capture_thread = capture_system.start_continuous_capture(fps=30)
    
    time.sleep(3)
    capture_system.stop_continuous_capture()
    
    # Final metrics
    final_metrics = capture_system.get_performance_metrics()
    print(f"   Frames Captured: {final_metrics['frames_captured']}")
    print(f"   Average FPS: {final_metrics['fps']:.1f}")
    print(f"   Buffer Size: {final_metrics['buffer_size']}")
    
    print("\n🎉 Sprint 1 - Task 1.3 test completed!")
    print("🎯 Target: <100MB memory usage, <5ms capture time")
    print(f"📈 Current: {metrics['memory_usage_mb']:.1f}MB memory, {metrics['capture_time_ms']:.1f}ms capture")
