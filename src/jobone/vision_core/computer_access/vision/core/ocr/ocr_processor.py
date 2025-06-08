#!/usr/bin/env python3
"""
OCR Processor - Multi-engine OCR text recognition
"""

import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import OCR engines
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class OCREngine(Enum):
    """OCR engine types"""
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    AUTO = "auto"

@dataclass
class OCRResult:
    """OCR recognition result"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    engine: str

@dataclass
class OCRConfig:
    """OCR configuration"""
    engine: OCREngine = OCREngine.AUTO
    languages: List[str] = None
    confidence_threshold: float = 0.5
    gpu_enabled: bool = False
    preprocessing: bool = True

class OCRProcessor:
    """
    Multi-engine OCR processor
    Supports EasyOCR, Tesseract with automatic fallback
    """
    
    def __init__(self, config: Optional[OCRConfig] = None):
        self.logger = logging.getLogger('orion.computer_access.vision.ocr')
        
        # Configuration
        self.config = config or OCRConfig()
        if self.config.languages is None:
            self.config.languages = ['en']
        
        # Engine instances
        self.easyocr_reader = None
        self.tesseract_config = None
        self.active_engine = None
        self.initialized = False
        
        # Performance tracking
        self.ocr_operations = 0
        self.total_processing_time = 0.0
        self.last_processing_time = 0.0
        
        self.logger.info("📝 OCRProcessor initialized")
    
    def initialize(self) -> bool:
        """
        Initialize OCR processor with best available engine
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing OCR processor...")
            
            # Determine best engine
            if self.config.engine == OCREngine.AUTO:
                self.active_engine = self._select_best_engine()
            else:
                self.active_engine = self.config.engine
            
            # Initialize selected engine
            if self.active_engine == OCREngine.EASYOCR:
                success = self._initialize_easyocr()
            elif self.active_engine == OCREngine.TESSERACT:
                success = self._initialize_tesseract()
            else:
                raise ValueError(f"Unsupported OCR engine: {self.active_engine}")
            
            if not success:
                raise RuntimeError(f"Failed to initialize {self.active_engine.value} engine")
            
            self.initialized = True
            self.logger.info(f"✅ OCR processor initialized with {self.active_engine.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ OCR processor initialization failed: {e}")
            return False
    
    def _select_best_engine(self) -> OCREngine:
        """Select best available OCR engine"""
        # Priority: EasyOCR > Tesseract
        if EASYOCR_AVAILABLE:
            self.logger.info("🎯 Selected EasyOCR engine (best accuracy)")
            return OCREngine.EASYOCR
        elif TESSERACT_AVAILABLE:
            self.logger.info("🎯 Selected Tesseract engine (fallback)")
            return OCREngine.TESSERACT
        else:
            raise RuntimeError("No OCR engines available")
    
    def _initialize_easyocr(self) -> bool:
        """Initialize EasyOCR engine"""
        if not EASYOCR_AVAILABLE:
            return False
        
        try:
            self.easyocr_reader = easyocr.Reader(
                self.config.languages,
                gpu=self.config.gpu_enabled
            )
            
            self.logger.info(f"📝 EasyOCR: Languages {self.config.languages}, GPU: {self.config.gpu_enabled}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ EasyOCR initialization failed: {e}")
            return False
    
    def _initialize_tesseract(self) -> bool:
        """Initialize Tesseract engine"""
        if not TESSERACT_AVAILABLE:
            return False
        
        try:
            # Configure Tesseract
            lang_string = '+'.join(self.config.languages)
            self.tesseract_config = f'-l {lang_string} --oem 3 --psm 6'
            
            # Test Tesseract
            test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
            pytesseract.image_to_string(test_image, config=self.tesseract_config)
            
            self.logger.info(f"📝 Tesseract: Languages {self.config.languages}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Tesseract initialization failed: {e}")
            return False
    
    def process_image(self, image: np.ndarray) -> List[OCRResult]:
        """
        Process image and extract text
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of OCR results
        """
        if not self.initialized:
            raise RuntimeError("OCR processor not initialized")
        
        start_time = time.time()
        
        try:
            # Preprocess image if enabled
            if self.config.preprocessing:
                processed_image = self._preprocess_image(image)
            else:
                processed_image = image
            
            # Perform OCR based on active engine
            if self.active_engine == OCREngine.EASYOCR:
                results = self._process_easyocr(processed_image)
            elif self.active_engine == OCREngine.TESSERACT:
                results = self._process_tesseract(processed_image)
            else:
                raise RuntimeError(f"Engine {self.active_engine} not implemented")
            
            # Filter by confidence threshold
            filtered_results = [
                result for result in results 
                if result.confidence >= self.config.confidence_threshold
            ]
            
            # Update performance metrics
            processing_time = time.time() - start_time
            self.ocr_operations += 1
            self.total_processing_time += processing_time
            self.last_processing_time = processing_time
            
            self.logger.debug(f"📝 OCR completed: {len(filtered_results)} results ({processing_time:.3f}s)")
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"❌ OCR processing failed: {e}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        if not CV2_AVAILABLE:
            return image
        
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            self.logger.warning(f"⚠️ Image preprocessing failed: {e}")
            return image
    
    def _process_easyocr(self, image: np.ndarray) -> List[OCRResult]:
        """Process image using EasyOCR"""
        results = []
        
        try:
            # EasyOCR processing
            detections = self.easyocr_reader.readtext(image)
            
            for detection in detections:
                bbox_points, text, confidence = detection
                
                # Convert bbox points to x, y, width, height
                x_coords = [point[0] for point in bbox_points]
                y_coords = [point[1] for point in bbox_points]
                
                x = int(min(x_coords))
                y = int(min(y_coords))
                width = int(max(x_coords) - min(x_coords))
                height = int(max(y_coords) - min(y_coords))
                
                result = OCRResult(
                    text=text.strip(),
                    confidence=confidence,
                    bbox=(x, y, width, height),
                    engine="easyocr"
                )
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"❌ EasyOCR processing failed: {e}")
        
        return results
    
    def _process_tesseract(self, image: np.ndarray) -> List[OCRResult]:
        """Process image using Tesseract"""
        results = []
        
        try:
            # Get detailed data from Tesseract
            data = pytesseract.image_to_data(
                image, 
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Process each detected word
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                confidence = float(data['conf'][i]) / 100.0  # Convert to 0-1 range
                
                if text and confidence > 0:
                    x = data['left'][i]
                    y = data['top'][i]
                    width = data['width'][i]
                    height = data['height'][i]
                    
                    result = OCRResult(
                        text=text,
                        confidence=confidence,
                        bbox=(x, y, width, height),
                        engine="tesseract"
                    )
                    results.append(result)
                    
        except Exception as e:
            self.logger.error(f"❌ Tesseract processing failed: {e}")
        
        return results
    
    def extract_text_only(self, image: np.ndarray) -> str:
        """
        Extract only text content without bounding boxes
        
        Args:
            image: Input image
            
        Returns:
            str: Extracted text
        """
        results = self.process_image(image)
        text_parts = [result.text for result in results]
        return ' '.join(text_parts)
    
    def find_text(self, image: np.ndarray, search_text: str, 
                  case_sensitive: bool = False) -> List[OCRResult]:
        """
        Find specific text in image
        
        Args:
            image: Input image
            search_text: Text to search for
            case_sensitive: Whether search is case sensitive
            
        Returns:
            List of matching OCR results
        """
        results = self.process_image(image)
        matches = []
        
        for result in results:
            text_to_check = result.text if case_sensitive else result.text.lower()
            search_to_check = search_text if case_sensitive else search_text.lower()
            
            if search_to_check in text_to_check:
                matches.append(result)
        
        return matches
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get OCR performance statistics"""
        avg_time = self.total_processing_time / max(self.ocr_operations, 1)
        
        return {
            'ocr_operations': self.ocr_operations,
            'total_processing_time': self.total_processing_time,
            'average_processing_time': avg_time,
            'last_processing_time': self.last_processing_time,
            'engine': self.active_engine.value if self.active_engine else None
        }
    
    def is_ready(self) -> bool:
        """Check if OCR processor is ready"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get OCR processor status"""
        return {
            'initialized': self.initialized,
            'active_engine': self.active_engine.value if self.active_engine else None,
            'available_engines': {
                'easyocr': EASYOCR_AVAILABLE,
                'tesseract': TESSERACT_AVAILABLE
            },
            'config': {
                'languages': self.config.languages,
                'confidence_threshold': self.config.confidence_threshold,
                'gpu_enabled': self.config.gpu_enabled,
                'preprocessing': self.config.preprocessing
            },
            'performance': self.get_performance_stats()
        }
    
    def shutdown(self):
        """Shutdown OCR processor"""
        self.logger.info("🛑 Shutting down OCR processor")
        
        # Clean up EasyOCR reader
        if self.easyocr_reader:
            del self.easyocr_reader
            self.easyocr_reader = None
        
        self.initialized = False
        self.logger.info("✅ OCR processor shutdown complete")
