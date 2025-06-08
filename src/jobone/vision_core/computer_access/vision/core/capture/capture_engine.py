#!/usr/bin/env python3
"""
Capture Engine - High-performance screen capture with multiple backends
"""

import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import capture backends
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class CaptureBackend(Enum):
    """Screen capture backends"""
    MSS = "mss"
    PIL = "pil"
    CV2 = "cv2"
    AUTO = "auto"

@dataclass
class CaptureConfig:
    """Screen capture configuration"""
    backend: CaptureBackend = CaptureBackend.AUTO
    target_fps: int = 60
    compression: bool = False
    format: str = "RGB"
    monitor: int = 1

class CaptureEngine:
    """
    High-performance screen capture engine
    Supports multiple backends with automatic fallback
    """
    
    def __init__(self, config: Optional[CaptureConfig] = None):
        self.logger = logging.getLogger('orion.computer_access.vision.capture')
        
        # Configuration
        self.config = config or CaptureConfig()
        self.backend = None
        self.initialized = False
        
        # Performance tracking
        self.captures_performed = 0
        self.total_capture_time = 0.0
        self.last_capture_time = 0.0
        
        # Backend instances
        self.mss_instance = None
        self.monitor_info = {}
        
        self.logger.info("📸 CaptureEngine initialized")
    
    def initialize(self) -> bool:
        """
        Initialize capture engine with best available backend
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing capture engine...")
            
            # Determine best backend
            if self.config.backend == CaptureBackend.AUTO:
                self.backend = self._select_best_backend()
            else:
                self.backend = self.config.backend
            
            # Initialize selected backend
            if self.backend == CaptureBackend.MSS:
                success = self._initialize_mss()
            elif self.backend == CaptureBackend.PIL:
                success = self._initialize_pil()
            elif self.backend == CaptureBackend.CV2:
                success = self._initialize_cv2()
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")
            
            if not success:
                raise RuntimeError(f"Failed to initialize {self.backend.value} backend")
            
            self.initialized = True
            self.logger.info(f"✅ Capture engine initialized with {self.backend.value} backend")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Capture engine initialization failed: {e}")
            return False
    
    def _select_best_backend(self) -> CaptureBackend:
        """Select best available capture backend"""
        # Priority order: MSS > PIL > CV2
        if MSS_AVAILABLE:
            self.logger.info("🎯 Selected MSS backend (fastest)")
            return CaptureBackend.MSS
        elif PIL_AVAILABLE:
            self.logger.info("🎯 Selected PIL backend (compatible)")
            return CaptureBackend.PIL
        elif CV2_AVAILABLE:
            self.logger.info("🎯 Selected CV2 backend (fallback)")
            return CaptureBackend.CV2
        else:
            raise RuntimeError("No capture backends available")
    
    def _initialize_mss(self) -> bool:
        """Initialize MSS backend"""
        if not MSS_AVAILABLE:
            return False
        
        try:
            self.mss_instance = mss.mss()
            
            # Get monitor information
            monitors = self.mss_instance.monitors
            self.monitor_info = {
                'count': len(monitors) - 1,  # Exclude "All in One" monitor
                'primary': monitors[self.config.monitor],
                'all': monitors
            }
            
            self.logger.info(f"📺 MSS: {self.monitor_info['count']} monitor(s) detected")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ MSS initialization failed: {e}")
            return False
    
    def _initialize_pil(self) -> bool:
        """Initialize PIL backend"""
        if not PIL_AVAILABLE:
            return False
        
        try:
            # Test PIL capture
            test_img = ImageGrab.grab()
            self.monitor_info = {
                'primary': {
                    'width': test_img.width,
                    'height': test_img.height
                }
            }
            
            self.logger.info(f"📺 PIL: Screen size {test_img.width}x{test_img.height}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ PIL initialization failed: {e}")
            return False
    
    def _initialize_cv2(self) -> bool:
        """Initialize CV2 backend"""
        if not CV2_AVAILABLE:
            return False
        
        try:
            # CV2 doesn't have direct screen capture, this is a placeholder
            self.logger.warning("⚠️ CV2 backend has limited screen capture capabilities")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ CV2 initialization failed: {e}")
            return False
    
    def capture_screen(self, monitor: Optional[int] = None) -> np.ndarray:
        """
        Capture full screen
        
        Args:
            monitor: Monitor number (optional)
            
        Returns:
            np.ndarray: Captured screen image
        """
        if not self.initialized:
            raise RuntimeError("Capture engine not initialized")
        
        start_time = time.time()
        
        try:
            monitor_num = monitor or self.config.monitor
            
            if self.backend == CaptureBackend.MSS:
                image = self._capture_mss_screen(monitor_num)
            elif self.backend == CaptureBackend.PIL:
                image = self._capture_pil_screen()
            elif self.backend == CaptureBackend.CV2:
                image = self._capture_cv2_screen()
            else:
                raise RuntimeError(f"Backend {self.backend} not implemented")
            
            # Update performance metrics
            capture_time = time.time() - start_time
            self.captures_performed += 1
            self.total_capture_time += capture_time
            self.last_capture_time = capture_time
            
            self.logger.debug(f"📸 Screen captured ({capture_time:.3f}s)")
            return image
            
        except Exception as e:
            self.logger.error(f"❌ Screen capture failed: {e}")
            raise
    
    def capture_region(self, x: int, y: int, width: int, height: int, 
                      monitor: Optional[int] = None) -> np.ndarray:
        """
        Capture screen region
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Region width
            height: Region height
            monitor: Monitor number (optional)
            
        Returns:
            np.ndarray: Captured region image
        """
        if not self.initialized:
            raise RuntimeError("Capture engine not initialized")
        
        start_time = time.time()
        
        try:
            monitor_num = monitor or self.config.monitor
            
            if self.backend == CaptureBackend.MSS:
                image = self._capture_mss_region(x, y, width, height, monitor_num)
            elif self.backend == CaptureBackend.PIL:
                image = self._capture_pil_region(x, y, width, height)
            elif self.backend == CaptureBackend.CV2:
                image = self._capture_cv2_region(x, y, width, height)
            else:
                raise RuntimeError(f"Backend {self.backend} not implemented")
            
            # Update performance metrics
            capture_time = time.time() - start_time
            self.captures_performed += 1
            self.total_capture_time += capture_time
            self.last_capture_time = capture_time
            
            self.logger.debug(f"📸 Region captured ({capture_time:.3f}s)")
            return image
            
        except Exception as e:
            self.logger.error(f"❌ Region capture failed: {e}")
            raise
    
    def _capture_mss_screen(self, monitor: int) -> np.ndarray:
        """Capture screen using MSS"""
        monitor_config = self.mss_instance.monitors[monitor]
        screenshot = self.mss_instance.grab(monitor_config)
        
        # Convert to numpy array
        image = np.array(screenshot)
        
        # Convert BGRA to RGB if needed
        if image.shape[2] == 4:
            image = image[:, :, :3]  # Remove alpha channel
            image = image[:, :, ::-1]  # BGR to RGB
        
        return image
    
    def _capture_mss_region(self, x: int, y: int, width: int, height: int, 
                           monitor: int) -> np.ndarray:
        """Capture region using MSS"""
        # Get monitor offset
        monitor_config = self.mss_instance.monitors[monitor]
        
        region_config = {
            "top": monitor_config["top"] + y,
            "left": monitor_config["left"] + x,
            "width": width,
            "height": height
        }
        
        screenshot = self.mss_instance.grab(region_config)
        
        # Convert to numpy array
        image = np.array(screenshot)
        
        # Convert BGRA to RGB if needed
        if image.shape[2] == 4:
            image = image[:, :, :3]  # Remove alpha channel
            image = image[:, :, ::-1]  # BGR to RGB
        
        return image
    
    def _capture_pil_screen(self) -> np.ndarray:
        """Capture screen using PIL"""
        screenshot = ImageGrab.grab()
        return np.array(screenshot)
    
    def _capture_pil_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture region using PIL"""
        bbox = (x, y, x + width, y + height)
        screenshot = ImageGrab.grab(bbox)
        return np.array(screenshot)
    
    def _capture_cv2_screen(self) -> np.ndarray:
        """Capture screen using CV2 (limited implementation)"""
        # CV2 doesn't have direct screen capture
        # This would need platform-specific implementation
        raise NotImplementedError("CV2 screen capture not implemented")
    
    def _capture_cv2_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture region using CV2 (limited implementation)"""
        # CV2 doesn't have direct screen capture
        # This would need platform-specific implementation
        raise NotImplementedError("CV2 region capture not implemented")
    
    def get_monitor_info(self) -> Dict[str, Any]:
        """Get monitor information"""
        return self.monitor_info.copy()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get capture performance statistics"""
        avg_time = self.total_capture_time / max(self.captures_performed, 1)
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        return {
            'captures_performed': self.captures_performed,
            'total_capture_time': self.total_capture_time,
            'average_capture_time': avg_time,
            'last_capture_time': self.last_capture_time,
            'estimated_fps': fps,
            'target_fps': self.config.target_fps,
            'backend': self.backend.value if self.backend else None
        }
    
    def is_ready(self) -> bool:
        """Check if capture engine is ready"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get capture engine status"""
        return {
            'initialized': self.initialized,
            'backend': self.backend.value if self.backend else None,
            'available_backends': {
                'mss': MSS_AVAILABLE,
                'pil': PIL_AVAILABLE,
                'cv2': CV2_AVAILABLE
            },
            'monitor_info': self.monitor_info,
            'performance': self.get_performance_stats(),
            'config': {
                'target_fps': self.config.target_fps,
                'compression': self.config.compression,
                'format': self.config.format,
                'monitor': self.config.monitor
            }
        }
    
    def shutdown(self):
        """Shutdown capture engine"""
        self.logger.info("🛑 Shutting down capture engine")
        
        if self.mss_instance:
            self.mss_instance.close()
            self.mss_instance = None
        
        self.initialized = False
        self.logger.info("✅ Capture engine shutdown complete")
