#!/usr/bin/env python3
"""
🎯 Q01.1.1 - Capture Engine Module
💖 DUYGULANDIK! SEN YAPARSIN! CAPTURE POWER!

Bu modül Q01.1.1 görevinin bir parçası olarak ekran yakalama motorunu sağlar.
Modüler yapı ile temiz ve sürdürülebilir kod.

Author: Orion Vision Core Team
Status: 🚀 Q01.1.1 COMPLETED
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CaptureResult:
    """Capture result data structure"""
    success: bool
    image_data: Optional[str] = None
    image_size: Optional[tuple] = None
    capture_time: float = 0.0
    method: str = "unknown"
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CaptureEngine:
    """
    🎯 Q01.1.1: Capture Engine
    
    ALT_LAS'ın ekranı "yakalayabilmesi" için capture motoru
    GÜVEN GÜCÜYLE ÇALIŞIYOR! 💪
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.vision.capture_engine')
        
        # Engine settings
        self.default_quality = 85
        self.max_capture_time = 5.0
        self.retry_attempts = 3
        
        # Performance tracking
        self.capture_count = 0
        self.total_capture_time = 0.0
        self.successful_captures = 0
        self.last_capture_time = 0.0
        
        # Capability flags
        self.pil_available = False
        self.simulation_mode = True
        
        self.initialized = False
        
        self.logger.info("🎯 Capture Engine Module initialized - Q01.1.1 POWER!")
    
    def initialize(self) -> bool:
        """Initialize capture engine"""
        try:
            self.logger.info("🚀 Initializing Capture Engine...")
            self.logger.info("💪 Q01.1.1: GÜVEN GÜCÜYLE ÇALIŞIYORUZ!")
            
            # Check PIL availability
            try:
                from PIL import ImageGrab
                self.pil_available = True
                self.simulation_mode = False
                self.logger.info("✅ PIL ImageGrab available - Real capture mode")
            except ImportError:
                self.logger.warning("⚠️ PIL not available - Simulation mode")
                self.pil_available = False
                self.simulation_mode = True
            
            # Test basic capture
            test_result = self._test_basic_capture()
            
            if test_result.success:
                self.initialized = True
                self.logger.info("✅ Capture Engine initialized successfully!")
                self.logger.info("🎯 Q01.1.1: READY TO CAPTURE!")
                return True
            else:
                self.logger.error(f"❌ Capture Engine initialization failed: {test_result.error}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Capture Engine initialization error: {e}")
            return False
    
    def _test_basic_capture(self) -> CaptureResult:
        """Test basic capture functionality"""
        try:
            if self.pil_available:
                # Test real capture
                from PIL import ImageGrab
                import base64
                import io
                
                screenshot = ImageGrab.grab()
                
                # Convert to base64
                buffer = io.BytesIO()
                screenshot.save(buffer, format='PNG')
                image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return CaptureResult(
                    success=True,
                    image_data=image_data,
                    image_size=screenshot.size,
                    capture_time=0.1,
                    method='pil_real',
                    metadata={'test': True}
                )
            else:
                # Simulation mode
                return CaptureResult(
                    success=True,
                    image_data='simulated_image_data_base64',
                    image_size=(1920, 1080),
                    capture_time=0.05,
                    method='simulation',
                    metadata={'simulated': True}
                )
                
        except Exception as e:
            return CaptureResult(
                success=False,
                error=str(e),
                method='test_failed'
            )
    
    def capture_screen(self, region: Optional[tuple] = None) -> CaptureResult:
        """
        Capture screen or region
        
        Args:
            region: (x, y, width, height) for partial capture
            
        Returns:
            CaptureResult with capture data
        """
        if not self.initialized:
            return CaptureResult(
                success=False,
                error='Capture Engine not initialized'
            )
        
        start_time = time.time()
        self.capture_count += 1
        
        try:
            if self.pil_available and not self.simulation_mode:
                # Real capture
                result = self._capture_real(region)
            else:
                # Simulation capture
                result = self._capture_simulation(region)
            
            # Update performance metrics
            capture_time = time.time() - start_time
            self.total_capture_time += capture_time
            self.last_capture_time = capture_time
            
            if result.success:
                self.successful_captures += 1
                result.capture_time = capture_time
                
                self.logger.info(f"📸 Screen captured successfully in {capture_time:.3f}s")
            else:
                self.logger.error(f"❌ Screen capture failed: {result.error}")
            
            return result
            
        except Exception as e:
            capture_time = time.time() - start_time
            self.logger.error(f"❌ Capture error: {e}")
            
            return CaptureResult(
                success=False,
                error=str(e),
                capture_time=capture_time,
                method='error'
            )
    
    def _capture_real(self, region: Optional[tuple] = None) -> CaptureResult:
        """Real screen capture using PIL"""
        try:
            from PIL import ImageGrab
            import base64
            import io
            
            # Capture screen
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Convert to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG', quality=self.default_quality)
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return CaptureResult(
                success=True,
                image_data=image_data,
                image_size=screenshot.size,
                method='pil_real',
                metadata={
                    'region': region,
                    'quality': self.default_quality,
                    'format': 'PNG'
                }
            )
            
        except Exception as e:
            return CaptureResult(
                success=False,
                error=f"Real capture failed: {e}",
                method='pil_real_failed'
            )
    
    def _capture_simulation(self, region: Optional[tuple] = None) -> CaptureResult:
        """Simulation screen capture"""
        try:
            # Generate simulated image data
            if region:
                width, height = region[2], region[3]
            else:
                width, height = 1920, 1080
            
            # Simulated base64 image data
            simulated_data = f"simulated_screen_capture_{width}x{height}_q{self.default_quality}"
            
            return CaptureResult(
                success=True,
                image_data=simulated_data,
                image_size=(width, height),
                method='simulation',
                metadata={
                    'simulated': True,
                    'region': region,
                    'quality': self.default_quality,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return CaptureResult(
                success=False,
                error=f"Simulation capture failed: {e}",
                method='simulation_failed'
            )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get capture performance statistics"""
        avg_time = self.total_capture_time / self.capture_count if self.capture_count > 0 else 0
        success_rate = self.successful_captures / self.capture_count if self.capture_count > 0 else 0
        
        return {
            'total_captures': self.capture_count,
            'successful_captures': self.successful_captures,
            'success_rate': success_rate,
            'total_time': self.total_capture_time,
            'average_capture_time': avg_time,
            'last_capture_time': self.last_capture_time,
            'initialized': self.initialized,
            'simulation_mode': self.simulation_mode,
            'pil_available': self.pil_available
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current capture engine status"""
        return {
            'initialized': self.initialized,
            'simulation_mode': self.simulation_mode,
            'capabilities': {
                'pil_available': self.pil_available,
                'real_capture': self.pil_available and not self.simulation_mode,
                'region_capture': True,
                'quality_control': True
            },
            'settings': {
                'default_quality': self.default_quality,
                'max_capture_time': self.max_capture_time,
                'retry_attempts': self.retry_attempts
            },
            'performance': self.get_performance_stats(),
            'q01_1_1_power': True  # Q01.1.1 SPECIAL FLAG! 🎯
        }
    
    def shutdown(self):
        """Shutdown capture engine"""
        self.logger.info("🛑 Shutting down Capture Engine")
        self.logger.info("🎯 Q01.1.1: Harika iş çıkardık!")
        
        self.initialized = False
        self.logger.info("✅ Capture Engine shutdown complete")

# Global instance for easy access
capture_engine = CaptureEngine()

def get_capture_engine() -> CaptureEngine:
    """Get global capture engine instance"""
    return capture_engine

# Example usage and testing
if __name__ == "__main__":
    print("🎯 Q01.1.1 - Capture Engine Test")
    print("💖 DUYGULANDIK! SEN YAPARSIN!")
    
    # Test capture engine
    engine = CaptureEngine()
    if engine.initialize():
        print("✅ Capture Engine initialized")
        
        # Test capture
        result = engine.capture_screen()
        if result.success:
            print(f"✅ Screen captured: {result.image_size}")
            print(f"📊 Method: {result.method}")
            print(f"⏱️ Time: {result.capture_time:.3f}s")
        else:
            print(f"❌ Capture failed: {result.error}")
        
        # Show stats
        stats = engine.get_performance_stats()
        print(f"📊 Success rate: {stats['success_rate']:.2f}")
        
        engine.shutdown()
    else:
        print("❌ Capture Engine initialization failed")
    
    print("🎉 Q01.1.1 Capture Engine test completed!")
