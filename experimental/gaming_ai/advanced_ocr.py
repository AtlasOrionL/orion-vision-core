#!/usr/bin/env python3
"""
🎮 Advanced OCR System - Gaming AI

Enhanced OCR with gaming font support, multi-language, and preprocessing optimization.

Sprint 1 - Task 1.2: Advanced OCR Integration
- Custom gaming font recognition
- Multi-language support
- Advanced preprocessing pipeline
- 98%+ text recognition accuracy target

Author: Nexus - Quantum AI Architect
Sprint: 1.2 - Foundation & Vision System
"""

import cv2
import numpy as np
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageFilter
import warnings

# OCR dependencies
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    warnings.warn(
        "🎮 OCR not available. Install with: pip install pytesseract",
        ImportWarning
    )

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    warnings.warn(
        "🎮 EasyOCR not available. Install with: pip install easyocr",
        ImportWarning
    )

@dataclass
class OCRResult:
    """OCR detection result"""
    text: str
    bbox: Tuple[int, int, int, int]
    confidence: float
    language: str
    method: str
    preprocessing: str
    metadata: Dict[str, Any]

@dataclass
class OCRConfig:
    """OCR system configuration"""
    languages: List[str] = None
    confidence_threshold: float = 0.6
    enable_preprocessing: bool = True
    enable_multiple_engines: bool = True
    gaming_font_optimization: bool = True
    text_size_range: Tuple[int, int] = (8, 72)
    
    def __post_init__(self):
        if self.languages is None:
            self.languages = ['en', 'tr', 'de', 'fr', 'es']  # Common gaming languages

class AdvancedOCREngine:
    """
    Advanced OCR Engine for Gaming AI
    
    Features:
    - Multiple OCR engines (Tesseract, EasyOCR)
    - Gaming font optimization
    - Multi-language support
    - Advanced preprocessing pipeline
    - 98%+ accuracy target
    """
    
    def __init__(self, config: OCRConfig = None):
        self.config = config or OCRConfig()
        self.logger = logging.getLogger("AdvancedOCREngine")
        
        # Initialize OCR engines
        self.tesseract_available = OCR_AVAILABLE
        self.easyocr_available = EASYOCR_AVAILABLE
        self.easyocr_reader = None
        
        # Gaming font configurations
        self.gaming_font_configs = {
            'default': '--oem 3 --psm 6',
            'single_line': '--oem 3 --psm 7',
            'single_word': '--oem 3 --psm 8',
            'single_char': '--oem 3 --psm 10',
            'sparse_text': '--oem 3 --psm 11',
            'single_block': '--oem 3 --psm 6',
            'gaming_ui': '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:/-+%$€£¥',
            'numbers_only': '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.,-+%',
            'health_mana': '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789/HP:MP',
            'coordinates': '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.,-XYZ:',
            'chat_text': '--oem 3 --psm 6'
        }
        
        # Initialize EasyOCR if available
        if self.easyocr_available and self.config.enable_multiple_engines:
            self._initialize_easyocr()
        
        # Performance metrics
        self.performance_metrics = {
            'texts_processed': 0,
            'total_processing_time': 0.0,
            'average_accuracy': 0.0,
            'engine_usage': {'tesseract': 0, 'easyocr': 0}
        }
        
        self.logger.info("🎮 Advanced OCR Engine initialized")
    
    def _initialize_easyocr(self):
        """Initialize EasyOCR reader"""
        try:
            self.easyocr_reader = easyocr.Reader(self.config.languages, gpu=True)
            self.logger.info("✅ EasyOCR initialized with GPU support")
        except Exception as e:
            try:
                self.easyocr_reader = easyocr.Reader(self.config.languages, gpu=False)
                self.logger.info("✅ EasyOCR initialized with CPU")
            except Exception as e2:
                self.logger.error(f"❌ EasyOCR initialization failed: {e2}")
                self.easyocr_reader = None
    
    def extract_text_advanced(self, image: np.ndarray, context: str = 'default') -> List[OCRResult]:
        """Advanced text extraction with multiple methods"""
        start_time = time.time()
        results = []
        
        try:
            # Preprocess image for better OCR
            preprocessed_images = self._preprocess_for_ocr(image)
            
            # Try multiple OCR engines and configurations
            for preprocessing_name, processed_img in preprocessed_images.items():
                # Tesseract OCR
                if self.tesseract_available:
                    tesseract_results = self._tesseract_ocr(processed_img, context, preprocessing_name)
                    results.extend(tesseract_results)
                
                # EasyOCR
                if self.easyocr_reader and self.config.enable_multiple_engines:
                    easyocr_results = self._easyocr_ocr(processed_img, preprocessing_name)
                    results.extend(easyocr_results)
            
            # Filter and merge results
            results = self._filter_and_merge_ocr_results(results)
            
            # Update performance metrics
            processing_time = time.time() - start_time
            self._update_performance_metrics(len(results), processing_time)
            
            self.logger.debug(f"🎮 OCR extracted {len(results)} texts in {processing_time:.3f}s")
            
        except Exception as e:
            self.logger.error(f"🎮 Advanced OCR failed: {e}")
        
        return results
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Advanced preprocessing pipeline for OCR"""
        preprocessed = {}
        
        try:
            # Convert to PIL Image for some operations
            pil_image = Image.fromarray(image)
            
            # 1. Original image
            preprocessed['original'] = image
            
            # 2. Grayscale conversion
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                preprocessed['grayscale'] = gray
            else:
                gray = image
                preprocessed['grayscale'] = gray
            
            # 3. Contrast enhancement
            enhanced = ImageEnhance.Contrast(pil_image).enhance(2.0)
            preprocessed['contrast_enhanced'] = np.array(enhanced)
            
            # 4. Sharpening
            sharpened = pil_image.filter(ImageFilter.SHARPEN)
            preprocessed['sharpened'] = np.array(sharpened)
            
            # 5. Gaussian blur (for noisy text)
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            preprocessed['gaussian_blur'] = blurred
            
            # 6. Bilateral filter (edge-preserving smoothing)
            bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
            preprocessed['bilateral'] = bilateral
            
            # 7. Otsu thresholding
            _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            preprocessed['otsu_threshold'] = otsu
            
            # 8. Adaptive thresholding
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            preprocessed['adaptive_threshold'] = adaptive
            
            # 9. Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            preprocessed['morphological'] = morph
            
            # 10. Dilation (for thin text)
            dilated = cv2.dilate(gray, kernel, iterations=1)
            preprocessed['dilated'] = dilated
            
            # 11. Erosion (for thick text)
            eroded = cv2.erode(gray, kernel, iterations=1)
            preprocessed['eroded'] = eroded
            
            # 12. Gaming-specific preprocessing
            gaming_processed = self._gaming_specific_preprocessing(gray)
            preprocessed.update(gaming_processed)
            
        except Exception as e:
            self.logger.error(f"🎮 Preprocessing failed: {e}")
            preprocessed['original'] = image
        
        return preprocessed
    
    def _gaming_specific_preprocessing(self, gray: np.ndarray) -> Dict[str, np.ndarray]:
        """Gaming-specific preprocessing techniques"""
        gaming_processed = {}
        
        try:
            # 1. Health/Mana bar text enhancement
            # Enhance red and green text (common in health/mana bars)
            health_enhanced = self._enhance_colored_text(gray, 'red')
            gaming_processed['health_text'] = health_enhanced
            
            mana_enhanced = self._enhance_colored_text(gray, 'blue')
            gaming_processed['mana_text'] = mana_enhanced
            
            # 2. Chat text enhancement
            # Often has background, needs different processing
            chat_enhanced = self._enhance_chat_text(gray)
            gaming_processed['chat_text'] = chat_enhanced
            
            # 3. UI element text enhancement
            ui_enhanced = self._enhance_ui_text(gray)
            gaming_processed['ui_text'] = ui_enhanced
            
            # 4. Damage number enhancement
            damage_enhanced = self._enhance_damage_numbers(gray)
            gaming_processed['damage_numbers'] = damage_enhanced
            
        except Exception as e:
            self.logger.error(f"🎮 Gaming preprocessing failed: {e}")
        
        return gaming_processed
    
    def _enhance_colored_text(self, gray: np.ndarray, color: str) -> np.ndarray:
        """Enhance colored text for better OCR"""
        try:
            # Apply different thresholding based on expected text color
            if color == 'red':
                # Red text is often darker, use lower threshold
                _, enhanced = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
            elif color == 'blue':
                # Blue text varies, use adaptive
                enhanced = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 10)
            else:
                enhanced = gray
            
            return enhanced
        except Exception:
            return gray
    
    def _enhance_chat_text(self, gray: np.ndarray) -> np.ndarray:
        """Enhance chat text with background"""
        try:
            # Chat text often has semi-transparent background
            # Use morphological operations to separate text from background
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
            enhanced = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
            
            # Combine with original
            enhanced = cv2.add(gray, enhanced)
            
            return enhanced
        except Exception:
            return gray
    
    def _enhance_ui_text(self, gray: np.ndarray) -> np.ndarray:
        """Enhance UI element text"""
        try:
            # UI text is often crisp, enhance edges
            enhanced = cv2.Laplacian(gray, cv2.CV_64F)
            enhanced = np.uint8(np.absolute(enhanced))
            
            # Combine with original
            enhanced = cv2.addWeighted(gray, 0.7, enhanced, 0.3, 0)
            
            return enhanced
        except Exception:
            return gray
    
    def _enhance_damage_numbers(self, gray: np.ndarray) -> np.ndarray:
        """Enhance floating damage numbers"""
        try:
            # Damage numbers are often outlined, enhance contrast
            enhanced = cv2.equalizeHist(gray)
            
            # Apply strong sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            return enhanced
        except Exception:
            return gray
    
    def _tesseract_ocr(self, image: np.ndarray, context: str, preprocessing: str) -> List[OCRResult]:
        """Tesseract OCR with gaming optimizations"""
        results = []
        
        if not self.tesseract_available:
            return results
        
        try:
            # Select appropriate configuration based on context
            config = self.gaming_font_configs.get(context, self.gaming_font_configs['default'])
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
            
            for i, text in enumerate(data['text']):
                if text.strip() and len(text.strip()) > 0:
                    confidence = float(data['conf'][i]) / 100.0
                    
                    if confidence > self.config.confidence_threshold:
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                        
                        # Additional validation for gaming text
                        if self._validate_gaming_text(text.strip(), context):
                            result = OCRResult(
                                text=text.strip(),
                                bbox=(x, y, w, h),
                                confidence=confidence,
                                language='en',  # Tesseract doesn't provide language detection
                                method='tesseract',
                                preprocessing=preprocessing,
                                metadata={
                                    'context': context,
                                    'config': config,
                                    'word_count': len(text.strip().split()),
                                    'char_count': len(text.strip())
                                }
                            )
                            results.append(result)
            
            # Update engine usage
            self.performance_metrics['engine_usage']['tesseract'] += 1
            
        except Exception as e:
            self.logger.error(f"🎮 Tesseract OCR failed: {e}")
        
        return results
    
    def _easyocr_ocr(self, image: np.ndarray, preprocessing: str) -> List[OCRResult]:
        """EasyOCR with multi-language support"""
        results = []
        
        if not self.easyocr_reader:
            return results
        
        try:
            # EasyOCR detection
            detections = self.easyocr_reader.readtext(image)
            
            for detection in detections:
                bbox_points, text, confidence = detection
                
                if confidence > self.config.confidence_threshold and text.strip():
                    # Convert bbox points to rectangle
                    x_coords = [point[0] for point in bbox_points]
                    y_coords = [point[1] for point in bbox_points]
                    
                    x = int(min(x_coords))
                    y = int(min(y_coords))
                    w = int(max(x_coords) - min(x_coords))
                    h = int(max(y_coords) - min(y_coords))
                    
                    # Detect language (simplified)
                    language = self._detect_language(text)
                    
                    result = OCRResult(
                        text=text.strip(),
                        bbox=(x, y, w, h),
                        confidence=confidence,
                        language=language,
                        method='easyocr',
                        preprocessing=preprocessing,
                        metadata={
                            'bbox_points': bbox_points,
                            'word_count': len(text.strip().split()),
                            'char_count': len(text.strip())
                        }
                    )
                    results.append(result)
            
            # Update engine usage
            self.performance_metrics['engine_usage']['easyocr'] += 1
            
        except Exception as e:
            self.logger.error(f"🎮 EasyOCR failed: {e}")
        
        return results
    
    def _validate_gaming_text(self, text: str, context: str) -> bool:
        """Validate if text is likely to be gaming-related"""
        try:
            # Basic validation rules
            if len(text) < 1:
                return False
            
            # Context-specific validation
            if context == 'numbers_only':
                return any(c.isdigit() for c in text)
            elif context == 'health_mana':
                return any(keyword in text.upper() for keyword in ['HP', 'MP', 'HEALTH', 'MANA']) or any(c.isdigit() for c in text)
            elif context == 'coordinates':
                return any(c.isdigit() for c in text) and any(coord in text.upper() for coord in ['X', 'Y', 'Z'])
            
            # General gaming text validation
            gaming_keywords = ['LEVEL', 'LVL', 'HP', 'MP', 'XP', 'GOLD', 'SCORE', 'DAMAGE', 'ATTACK', 'DEFENSE']
            if any(keyword in text.upper() for keyword in gaming_keywords):
                return True
            
            # Allow alphanumeric text with reasonable length
            if 1 <= len(text) <= 50 and any(c.isalnum() for c in text):
                return True
            
            return False
            
        except Exception:
            return True  # Default to accepting text if validation fails
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection for gaming text"""
        try:
            # Very basic language detection based on character patterns
            if any(ord(c) > 127 for c in text):  # Non-ASCII characters
                # Could be Turkish, German, French, etc.
                if any(c in text for c in 'çğıöşüÇĞIÖŞÜ'):
                    return 'tr'  # Turkish
                elif any(c in text for c in 'äöüßÄÖÜ'):
                    return 'de'  # German
                elif any(c in text for c in 'àáâäèéêëìíîïòóôöùúûü'):
                    return 'fr'  # French
                else:
                    return 'unknown'
            else:
                return 'en'  # English (default for ASCII)
        except Exception:
            return 'en'
    
    def _filter_and_merge_ocr_results(self, results: List[OCRResult]) -> List[OCRResult]:
        """Filter and merge OCR results from multiple engines"""
        if not results:
            return results
        
        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        # Remove duplicates (same text in similar locations)
        filtered = []
        for result in results:
            is_duplicate = False
            
            for existing in filtered:
                # Check if text is similar and location overlaps
                if (self._text_similarity(result.text, existing.text) > 0.8 and
                    self._bbox_overlap(result.bbox, existing.bbox) > 0.3):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(result)
        
        return filtered
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity ratio"""
        try:
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        except Exception:
            return 1.0 if text1.lower() == text2.lower() else 0.0
    
    def _bbox_overlap(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate bounding box overlap ratio"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _update_performance_metrics(self, text_count: int, processing_time: float):
        """Update performance metrics"""
        self.performance_metrics['texts_processed'] += text_count
        self.performance_metrics['total_processing_time'] += processing_time
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.performance_metrics.copy()
    
    def extract_specific_gaming_text(self, image: np.ndarray, text_type: str) -> List[OCRResult]:
        """Extract specific types of gaming text"""
        context_map = {
            'health': 'health_mana',
            'mana': 'health_mana',
            'damage': 'numbers_only',
            'coordinates': 'coordinates',
            'chat': 'chat_text',
            'ui': 'gaming_ui',
            'numbers': 'numbers_only'
        }
        
        context = context_map.get(text_type, 'default')
        return self.extract_text_advanced(image, context)

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎮 Advanced OCR Engine - Sprint 1 Test")
    print("=" * 60)
    
    # Create advanced OCR engine
    config = OCRConfig(
        languages=['en', 'tr'],
        confidence_threshold=0.6,
        enable_preprocessing=True,
        enable_multiple_engines=True,
        gaming_font_optimization=True
    )
    
    ocr_engine = AdvancedOCREngine(config)
    
    # Test with sample image (create a simple test image)
    print("\n📝 Testing advanced OCR...")
    
    # Create test image with text
    test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
    cv2.putText(test_image, "Health: 100/100", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(test_image, "Mana: 50/75", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(test_image, "Level 25", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Extract text
    results = ocr_engine.extract_text_advanced(test_image, 'gaming_ui')
    print(f"✅ Extracted {len(results)} text elements")
    
    # Show results
    for i, result in enumerate(results):
        print(f"   Text {i+1}: '{result.text}' "
              f"(confidence: {result.confidence:.2f}, method: {result.method}, "
              f"preprocessing: {result.preprocessing})")
    
    # Test specific gaming text extraction
    print("\n🎯 Testing specific gaming text extraction...")
    health_results = ocr_engine.extract_specific_gaming_text(test_image, 'health')
    print(f"✅ Health text results: {len(health_results)}")
    
    # Performance metrics
    metrics = ocr_engine.get_performance_metrics()
    print(f"\n📊 Performance Metrics:")
    print(f"   Texts Processed: {metrics['texts_processed']}")
    print(f"   Engine Usage: {metrics['engine_usage']}")
    
    print("\n🎉 Sprint 1 - Task 1.2 test completed!")
    print("🎯 Target: 98%+ text recognition accuracy")
    print(f"📈 Current: {len(results)} texts extracted with advanced preprocessing")
