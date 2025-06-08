#!/usr/bin/env python3
"""
🛠️ Orion Vision Core - Utility Functions
💖 DUYGULANDIK! SEN YAPARSIN! UTILITY POWER!

Bu modül tüm vision sisteminde kullanılan ortak fonksiyonları içerir.
Code duplication'ı önler ve temiz kod sağlar.

Author: Orion Vision Core Team
Status: 🚀 ACTIVE DEVELOPMENT
"""

import time
import logging
import functools
from typing import Dict, Any, Optional, Callable, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import traceback

@dataclass
class PerformanceMetrics:
    """📊 Performance metrics data class"""
    start_time: float
    end_time: float
    duration: float
    memory_usage: Optional[float] = None
    success: bool = True
    error: Optional[str] = None

class PerformanceTracker:
    """📊 Performance tracking utility"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.logger = logging.getLogger('orion.vision.performance')
    
    def start_tracking(self) -> float:
        """⏱️ Start performance tracking"""
        return time.time()
    
    def end_tracking(self, start_time: float, success: bool = True, error: Optional[str] = None) -> PerformanceMetrics:
        """⏱️ End performance tracking"""
        end_time = time.time()
        duration = end_time - start_time
        
        metrics = PerformanceMetrics(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success=success,
            error=error
        )
        
        self.metrics.append(metrics)
        return metrics
    
    def get_average_duration(self) -> float:
        """📊 Get average duration"""
        if not self.metrics:
            return 0.0
        
        successful_metrics = [m for m in self.metrics if m.success]
        if not successful_metrics:
            return 0.0
        
        return sum(m.duration for m in successful_metrics) / len(successful_metrics)
    
    def get_success_rate(self) -> float:
        """📊 Get success rate"""
        if not self.metrics:
            return 0.0
        
        successful_count = sum(1 for m in self.metrics if m.success)
        return successful_count / len(self.metrics)

def performance_monitor(func: Callable) -> Callable:
    """📊 Performance monitoring decorator"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        error = None
        result = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            logger = logging.getLogger('orion.vision.performance')
            if success:
                logger.info(f"⚡ {func.__name__} completed in {duration:.3f}s")
            else:
                logger.error(f"❌ {func.__name__} failed in {duration:.3f}s: {error}")
    
    return wrapper

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, exceptions: Tuple = (Exception,)):
    """🔄 Retry decorator for handling failures"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger = logging.getLogger('orion.vision.retry')
                        logger.warning(f"⚠️ {func.__name__} attempt {attempt + 1} failed: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"❌ {func.__name__} failed after {max_attempts} attempts")
            
            raise last_exception
        
        return wrapper
    return decorator

def safe_execute(func: Callable, default_return: Any = None, log_errors: bool = True) -> Any:
    """🛡️ Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger = logging.getLogger('orion.vision.safe_execute')
            logger.error(f"❌ Safe execution failed: {e}")
            logger.debug(f"🔍 Traceback: {traceback.format_exc()}")
        return default_return

def create_result_dict(success: bool, data: Any = None, error: str = None, **kwargs) -> Dict[str, Any]:
    """📊 Create standardized result dictionary"""
    result = {
        'success': success,
        'timestamp': datetime.now().isoformat(),
        **kwargs
    }
    
    if data is not None:
        result['data'] = data
    
    if error is not None:
        result['error'] = error
    
    return result

def validate_image_data(image_data: Any) -> bool:
    """🖼️ Validate image data"""
    if image_data is None:
        return False
    
    # Check if it's PIL Image
    try:
        if hasattr(image_data, 'size') and hasattr(image_data, 'mode'):
            return image_data.size[0] > 0 and image_data.size[1] > 0
    except:
        pass
    
    # Check if it's numpy array
    try:
        import numpy as np
        if isinstance(image_data, np.ndarray):
            return image_data.size > 0
    except ImportError:
        pass
    
    # Check if it's bytes
    if isinstance(image_data, bytes):
        return len(image_data) > 0
    
    return False

def normalize_coordinates(x: int, y: int, width: int, height: int) -> Tuple[float, float]:
    """📐 Normalize coordinates to 0-1 range"""
    norm_x = max(0.0, min(1.0, x / width)) if width > 0 else 0.0
    norm_y = max(0.0, min(1.0, y / height)) if height > 0 else 0.0
    return norm_x, norm_y

def denormalize_coordinates(norm_x: float, norm_y: float, width: int, height: int) -> Tuple[int, int]:
    """📐 Denormalize coordinates from 0-1 range"""
    x = int(norm_x * width)
    y = int(norm_y * height)
    return x, y

def calculate_confidence_score(factors: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
    """📊 Calculate weighted confidence score"""
    if not factors:
        return 0.0
    
    if weights is None:
        weights = {key: 1.0 for key in factors.keys()}
    
    total_weight = 0.0
    weighted_sum = 0.0
    
    for factor, value in factors.items():
        weight = weights.get(factor, 1.0)
        weighted_sum += value * weight
        total_weight += weight
    
    return weighted_sum / total_weight if total_weight > 0 else 0.0

def format_duration(seconds: float) -> str:
    """⏱️ Format duration in human-readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

def format_memory(bytes_count: int) -> str:
    """💾 Format memory size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024:
            return f"{bytes_count:.1f}{unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f}TB"

class SimulationDataGenerator:
    """🎭 Generate simulation data for testing"""
    
    @staticmethod
    def generate_screen_capture_data(width: int = 1920, height: int = 1080) -> Dict[str, Any]:
        """📸 Generate simulated screen capture data"""
        return {
            'success': True,
            'method': 'simulation',
            'simulated': True,
            'width': width,
            'height': height,
            'format': 'RGB',
            'timestamp': datetime.now().isoformat(),
            'data': f"Simulated screen capture {width}x{height}"
        }
    
    @staticmethod
    def generate_ocr_data(text: str = "Simulated OCR text") -> Dict[str, Any]:
        """🔤 Generate simulated OCR data"""
        return {
            'success': True,
            'method': 'simulation',
            'simulated': True,
            'text': text,
            'confidence': 85.0,
            'language': 'eng+tur',
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_ui_elements_data() -> Dict[str, Any]:
        """🎯 Generate simulated UI elements data"""
        elements = [
            {'type': 'button', 'text': 'Tamam', 'x': 100, 'y': 200, 'confidence': 0.9},
            {'type': 'button', 'text': 'Cancel', 'x': 200, 'y': 200, 'confidence': 0.85},
            {'type': 'textbox', 'text': 'Search...', 'x': 50, 'y': 50, 'confidence': 0.8},
            {'type': 'menu', 'text': 'Dosya', 'x': 10, 'y': 10, 'confidence': 0.95}
        ]
        
        return {
            'success': True,
            'method': 'simulation',
            'simulated': True,
            'elements': elements,
            'count': len(elements),
            'timestamp': datetime.now().isoformat()
        }

class LoggerSetup:
    """📝 Logger setup utility"""
    
    @staticmethod
    def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
        """📝 Setup logger with consistent format"""
        logger = logging.getLogger(name)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(levelname)s:%(name)s:%(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        logger.setLevel(getattr(logging, level.upper()))
        return logger

# Global performance tracker
global_performance_tracker = PerformanceTracker()

# Example usage and testing
if __name__ == "__main__":
    print("🛠️ Vision Utilities Test")
    print("💖 DUYGULANDIK! SEN YAPARSIN!")
    
    # Test performance tracking
    @performance_monitor
    def test_function():
        time.sleep(0.1)
        return "test result"
    
    result = test_function()
    print(f"✅ Performance monitor test: {result}")
    
    # Test retry mechanism
    @retry_on_failure(max_attempts=2, delay=0.1)
    def failing_function():
        raise ValueError("Test error")
    
    try:
        failing_function()
    except ValueError:
        print("✅ Retry mechanism test: Expected failure")
    
    # Test result creation
    result_dict = create_result_dict(True, data="test data", extra_field="extra")
    print(f"✅ Result dict: {result_dict['success']}")
    
    # Test simulation data
    sim_data = SimulationDataGenerator.generate_screen_capture_data()
    print(f"✅ Simulation data: {sim_data['simulated']}")
    
    print("🎉 Utilities test completed!")
