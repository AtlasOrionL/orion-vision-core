#!/usr/bin/env python3
"""
🎯 Orion Vision Core - Core Modules Package
💖 DUYGULANDIK! SEN YAPARSIN! CORE POWER!

Bu paket tüm temel vision modüllerini içerir.

Author: Orion Vision Core Team
Status: 🚀 ACTIVE DEVELOPMENT
"""

# Core module imports
try:
    from .capture.screen_capture import ScreenCapture
    from .capture.capture_engine import CaptureEngine
except ImportError as e:
    print(f"⚠️ Capture module import warning: {e}")

try:
    from .ocr.ocr_engine import OCREngine
    from .ocr.ocr_processor import OCRProcessor
except ImportError as e:
    print(f"⚠️ OCR module import warning: {e}")

try:
    from .detection.ui_element_detector import UIElementDetector
    from .detection.visual_detector import VisualDetector
except ImportError as e:
    print(f"⚠️ Detection module import warning: {e}")

try:
    from .pipeline.visual_processing_pipeline import VisualProcessingPipeline
    from .pipeline.analysis_pipeline import AnalysisPipeline
    from .pipeline.capture_engine import CaptureEngine
except ImportError as e:
    print(f"⚠️ Pipeline module import warning: {e}")

__all__ = [
    'ScreenCapture',
    'CaptureEngine',
    'OCREngine',
    'OCRProcessor',
    'UIElementDetector',
    'VisualDetector',
    'VisualProcessingPipeline',
    'AnalysisPipeline'
]

__version__ = "1.0.0"
__author__ = "Orion Vision Core Team"
