#!/usr/bin/env python3
"""
🎮 OCR Engine Tests

Unit tests for Advanced OCR Engine.

Sprint 1 - Task 1.4: Testing Framework
"""

import unittest
import numpy as np
import cv2
import time
import logging

# Import OCR engine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from advanced_ocr import AdvancedOCREngine, OCRConfig, OCRResult
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class TestOCREngine(unittest.TestCase):
    """Test Advanced OCR Engine"""
    
    def setUp(self):
        """Set up test environment"""
        if not OCR_AVAILABLE:
            self.skipTest("OCR engine not available")
        
        self.config = OCRConfig(
            languages=['en'],
            confidence_threshold=0.6,
            enable_preprocessing=True,
            enable_multiple_engines=False  # Disable for testing
        )
        self.ocr_engine = AdvancedOCREngine(self.config)
    
    def test_initialization(self):
        """Test OCR engine initialization"""
        self.assertIsNotNone(self.ocr_engine)
        self.assertEqual(self.ocr_engine.config.languages, ['en'])
        self.assertTrue(self.ocr_engine.config.enable_preprocessing)
    
    def test_text_extraction(self):
        """Test basic text extraction"""
        # Create test image with text
        test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(test_image, "Health: 100", (10, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        results = self.ocr_engine.extract_text_advanced(test_image)
        
        # Should extract some text
        self.assertGreater(len(results), 0)
        
        # Check if "Health" or "100" is detected
        extracted_texts = [r.text for r in results]
        has_relevant_text = any('Health' in text or '100' in text 
                               for text in extracted_texts)
        self.assertTrue(has_relevant_text, f"Expected text not found in: {extracted_texts}")
    
    def test_gaming_text_validation(self):
        """Test gaming text validation"""
        # Valid gaming texts
        valid_texts = ["Health: 100", "Level 25", "HP", "MP", "XP: 1500"]
        
        for text in valid_texts:
            is_valid = self.ocr_engine._validate_gaming_text(text, 'default')
            self.assertTrue(is_valid, f"'{text}' should be valid gaming text")
        
        # Invalid texts
        invalid_texts = ["", "x", "!@#$%"]
        
        for text in invalid_texts:
            is_valid = self.ocr_engine._validate_gaming_text(text, 'default')
            self.assertFalse(is_valid, f"'{text}' should be invalid gaming text")
    
    def test_preprocessing_methods(self):
        """Test preprocessing methods"""
        test_image = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        
        preprocessed = self.ocr_engine._preprocess_for_ocr(test_image)
        
        # Should have multiple preprocessing variants
        self.assertGreater(len(preprocessed), 5)
        self.assertIn('original', preprocessed)
        self.assertIn('grayscale', preprocessed)
        self.assertIn('otsu_threshold', preprocessed)
    
    def test_specific_gaming_text(self):
        """Test specific gaming text extraction"""
        # Create health bar image
        test_image = np.ones((50, 200, 3), dtype=np.uint8) * 255
        cv2.putText(test_image, "HP: 85/100", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        health_results = self.ocr_engine.extract_specific_gaming_text(test_image, 'health')
        
        # Should extract health-related text
        self.assertGreater(len(health_results), 0)
    
    def test_language_detection(self):
        """Test simple language detection"""
        # English text
        en_lang = self.ocr_engine._detect_language("Health Points")
        self.assertEqual(en_lang, 'en')
        
        # Turkish text
        tr_lang = self.ocr_engine._detect_language("Sağlık Puanı")
        self.assertEqual(tr_lang, 'tr')
    
    def test_performance_metrics(self):
        """Test performance metrics tracking"""
        test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
        
        # Process some text
        self.ocr_engine.extract_text_advanced(test_image)
        
        metrics = self.ocr_engine.get_performance_metrics()
        
        self.assertIn('texts_processed', metrics)
        self.assertIn('engine_usage', metrics)

class TestOCRPerformance(unittest.TestCase):
    """Performance tests for OCR engine"""
    
    def setUp(self):
        """Set up performance test environment"""
        if not OCR_AVAILABLE:
            self.skipTest("OCR engine not available")
        
        self.config = OCRConfig(enable_multiple_engines=False)
        self.ocr_engine = AdvancedOCREngine(self.config)
    
    def test_extraction_speed(self):
        """Test text extraction speed"""
        test_image = np.ones((200, 400, 3), dtype=np.uint8) * 255
        cv2.putText(test_image, "Test Gaming Text", (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        start_time = time.time()
        results = self.ocr_engine.extract_text_advanced(test_image)
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time
        self.assertLess(elapsed, 2.0, f"OCR too slow: {elapsed:.3f}s")
    
    def test_accuracy_threshold(self):
        """Test accuracy meets threshold"""
        # Create clear, readable text
        test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(test_image, "LEVEL 42", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
        
        results = self.ocr_engine.extract_text_advanced(test_image)
        
        if results:
            # Check confidence levels
            high_confidence_results = [r for r in results if r.confidence > 0.8]
            self.assertGreater(len(high_confidence_results), 0, 
                             "No high-confidence results found")

if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)
