"""
Perception Module - Q1 Implementation

Orion Vision Core perception capabilities
"""

from .screen_capture import ScreenCapture, get_screen_capture, capture_full_screen_as_np_array
from .ocr_processor import OCRProcessor, get_ocr_processor, detect_text_regions

__all__ = [
    'ScreenCapture',
    'get_screen_capture', 
    'capture_full_screen_as_np_array',
    'OCRProcessor',
    'get_ocr_processor',
    'detect_text_regions'
]
