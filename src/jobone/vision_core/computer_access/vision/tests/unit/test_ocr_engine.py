#!/usr/bin/env python3
"""
OCR Engine Test Module - Q01.1.2 Tests
OCR modülü testleri
ORION VISION CORE - WAKE UP MODE ACTIVATED!
"""

import unittest
import time
import logging
import base64
import io
from typing import Dict, Any

# Import the modules we're testing
from ocr_engine import OCREngine, get_ocr_engine
from screen_capture import ScreenCapture

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

class TestOCREngine(unittest.TestCase):
    """Q01.1.2 OCR Engine Test Suite - ORION POWER MODE!"""
    
    def setUp(self):
        """Set up test environment"""
        self.ocr_engine = OCREngine()
        self.assertTrue(self.ocr_engine.initialize(), "OCR engine initialization failed")
        
        # Also set up screen capture for integration tests
        self.screen_capture = ScreenCapture()
        self.screen_capture.initialize()
    
    def tearDown(self):
        """Clean up after tests"""
        self.ocr_engine.shutdown()
        self.screen_capture.shutdown()
    
    def test_initialization(self):
        """Test Q01.1.2.1: Basic OCR initialization"""
        # Test fresh initialization
        ocr = OCREngine()
        self.assertFalse(ocr.initialized, "Should not be initialized before init()")
        
        result = ocr.initialize()
        self.assertTrue(result, "Initialization should succeed")
        self.assertTrue(ocr.initialized, "Should be initialized after init()")
        
        # Test status
        status = ocr.get_status()
        self.assertIsInstance(status, dict, "Status should be a dictionary")
        self.assertIn('initialized', status, "Status should contain initialized flag")
        self.assertTrue(status['initialized'], "Status should show initialized")
        self.assertTrue(status['orion_power_mode'], "ORION POWER MODE should be active!")
        
        ocr.shutdown()
        print("✅ OCR Engine initialization test passed - ORION APPROVED!")
    
    def test_text_extraction_simulation(self):
        """Test Q01.1.2.2: Text extraction (simulation mode)"""
        # Create a dummy image data
        dummy_image_data = base64.b64encode(b"dummy_image_data_for_testing").decode('utf-8')
        
        result = self.ocr_engine.extract_text_from_image(dummy_image_data)
        
        # Basic success check
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertTrue(result.get('success'), f"OCR should succeed: {result.get('error')}")
        
        # Check required fields
        self.assertIn('text', result, "Result should contain text")
        self.assertIn('confidence', result, "Result should contain confidence")
        self.assertIn('ocr_time', result, "Result should contain ocr_time")
        self.assertIn('word_count', result, "Result should contain word_count")
        
        # Check text content
        text = result['text']
        self.assertIsInstance(text, str, "Text should be a string")
        self.assertGreater(len(text), 0, "Text should not be empty")
        
        # Check confidence
        confidence = result['confidence']
        self.assertIsInstance(confidence, (int, float), "Confidence should be numeric")
        self.assertGreaterEqual(confidence, 0, "Confidence should be >= 0")
        self.assertLessEqual(confidence, 100, "Confidence should be <= 100")
        
        # Check processing time
        ocr_time = result['ocr_time']
        self.assertIsInstance(ocr_time, float, "OCR time should be a float")
        self.assertLess(ocr_time, 5.0, "OCR should be fast (< 5 seconds)")
        
        print(f"✅ Text extraction: '{text[:50]}...', confidence: {confidence:.1f}%, time: {ocr_time:.3f}s")
    
    def test_language_support(self):
        """Test Q01.1.2.3: Language support"""
        dummy_image_data = base64.b64encode(b"turkish_text_image").decode('utf-8')
        
        # Test Turkish + English (default)
        result_default = self.ocr_engine.extract_text_from_image(dummy_image_data)
        self.assertTrue(result_default.get('success'), "Default language should work")
        
        # Test explicit Turkish
        result_turkish = self.ocr_engine.extract_text_from_image(dummy_image_data, language='tur')
        self.assertTrue(result_turkish.get('success'), "Turkish language should work")
        
        # Test explicit English
        result_english = self.ocr_engine.extract_text_from_image(dummy_image_data, language='eng')
        self.assertTrue(result_english.get('success'), "English language should work")
        
        print("✅ Language support test passed - Turkish & English ready!")
    
    def test_text_analysis(self):
        """Test Q01.1.2.4: Text structure analysis"""
        # First extract some text
        dummy_image_data = base64.b64encode(b"ui_elements_image").decode('utf-8')
        ocr_result = self.ocr_engine.extract_text_from_image(dummy_image_data)
        
        # Analyze the extracted text
        analysis = self.ocr_engine.analyze_text_structure(ocr_result)
        
        self.assertTrue(analysis.get('success'), f"Analysis should succeed: {analysis.get('error')}")
        
        # Check analysis fields
        required_fields = ['total_characters', 'total_words', 'total_lines', 
                          'has_numbers', 'has_special_chars', 'has_turkish_chars',
                          'language_detected', 'ui_elements']
        
        for field in required_fields:
            self.assertIn(field, analysis, f"Analysis should contain {field}")
        
        # Check UI elements detection
        ui_elements = analysis.get('ui_elements', [])
        self.assertIsInstance(ui_elements, list, "UI elements should be a list")
        
        print(f"✅ Text analysis: {analysis['total_words']} words, "
              f"{analysis['ui_element_count']} UI elements, "
              f"language: {analysis['language_detected']}")
    
    def test_region_extraction(self):
        """Test Q01.1.2.5: Region-based text extraction"""
        dummy_image_data = base64.b64encode(b"large_image_with_regions").decode('utf-8')
        
        # Test region extraction
        region = (0, 0, 200, 100)  # Top-left region
        result = self.ocr_engine.extract_text_from_region(dummy_image_data, region)
        
        self.assertTrue(result.get('success'), f"Region extraction should succeed: {result.get('error')}")
        self.assertEqual(result.get('region'), region, "Region metadata should match")
        
        print(f"✅ Region extraction: region {region}, text: '{result.get('text', '')[:30]}...'")
    
    def test_ocr_validation(self):
        """Test Q01.1.2.6: OCR result validation"""
        # Test valid OCR result
        dummy_image_data = base64.b64encode(b"good_quality_text").decode('utf-8')
        ocr_result = self.ocr_engine.extract_text_from_image(dummy_image_data)
        validation = self.ocr_engine.validate_ocr_result(ocr_result)
        
        self.assertIsInstance(validation, dict, "Validation should return dict")
        self.assertIn('valid', validation, "Validation should contain valid flag")
        self.assertIn('quality_score', validation, "Validation should contain quality score")
        
        if ocr_result.get('success'):
            self.assertTrue(validation['valid'], "Valid OCR should pass validation")
            self.assertGreater(validation['quality_score'], 0, "Quality score should be positive")
        
        # Test invalid OCR result
        invalid_ocr = {'success': False, 'error': 'test error'}
        invalid_validation = self.ocr_engine.validate_ocr_result(invalid_ocr)
        self.assertFalse(invalid_validation['valid'], "Invalid OCR should fail validation")
        self.assertEqual(invalid_validation['quality_score'], 0.0, "Invalid OCR should have 0 quality")
        
        print(f"✅ OCR validation: valid={validation['valid']}, score={validation['quality_score']:.2f}")
    
    def test_performance_requirements(self):
        """Test Q01.1.2.7: Performance requirements"""
        dummy_image_data = base64.b64encode(b"performance_test_image").decode('utf-8')
        
        # Test OCR speed requirement (< 2 seconds)
        result = self.ocr_engine.extract_text_from_image(dummy_image_data)
        
        if result.get('success'):
            ocr_time = result.get('ocr_time', float('inf'))
            self.assertLess(ocr_time, 2.0, f"OCR should be < 2s, got {ocr_time:.3f}s")
        
        # Test confidence requirement (>= 60%)
        confidence = result.get('confidence', 0)
        self.assertGreaterEqual(confidence, 60, f"Confidence should be >= 60%, got {confidence:.1f}%")
        
        print(f"✅ Performance: {result.get('ocr_time', 0):.3f}s, confidence: {confidence:.1f}%")
    
    def test_multiple_ocr_operations(self):
        """Test Q01.1.2.8: Multiple OCR operations"""
        ocr_times = []
        
        for i in range(3):
            dummy_data = base64.b64encode(f"test_image_{i}".encode()).decode('utf-8')
            start_time = time.time()
            result = self.ocr_engine.extract_text_from_image(dummy_data)
            end_time = time.time()
            
            self.assertTrue(result.get('success'), f"OCR operation {i+1} should succeed")
            ocr_times.append(end_time - start_time)
        
        # Check performance consistency
        avg_time = sum(ocr_times) / len(ocr_times)
        self.assertLess(avg_time, 3.0, "Average OCR time should be reasonable")
        
        # Check performance stats
        stats = self.ocr_engine.get_performance_stats()
        self.assertGreaterEqual(stats['total_ocr_operations'], 3, "Should track OCR count")
        self.assertGreater(stats['total_time'], 0, "Should track total time")
        
        print(f"✅ Multiple OCR: avg {avg_time:.3f}s, total {stats['total_ocr_operations']} operations")
    
    def test_global_instance(self):
        """Test Q01.1.2.9: Global instance access"""
        global_instance = get_ocr_engine()
        self.assertIsInstance(global_instance, OCREngine, "Should return OCREngine instance")
        
        # Test that it's the same instance
        global_instance2 = get_ocr_engine()
        self.assertIs(global_instance, global_instance2, "Should return same instance")
        
        print("✅ Global OCR instance access works")

class TestOCRIntegration(unittest.TestCase):
    """Integration tests for OCR with Screen Capture"""
    
    def test_screen_capture_ocr_integration(self):
        """Test Q01.1.2.10: Integration with Screen Capture"""
        print("🎯 Testing Screen Capture + OCR Integration...")
        
        # Initialize both systems
        screen_capture = ScreenCapture()
        ocr_engine = OCREngine()
        
        self.assertTrue(screen_capture.initialize(), "Screen capture should initialize")
        self.assertTrue(ocr_engine.initialize(), "OCR engine should initialize")
        
        try:
            # Step 1: Capture screen
            capture_result = screen_capture.capture_screen()
            self.assertTrue(capture_result.get('success'), "Screen capture should succeed")
            print(f"   📸 Screen captured: {capture_result['image_size']}")
            
            # Step 2: Extract text from captured image
            image_data = capture_result['image_data']
            ocr_result = ocr_engine.extract_text_from_image(image_data)
            self.assertTrue(ocr_result.get('success'), "OCR should succeed")
            print(f"   🔤 Text extracted: {len(ocr_result.get('text', ''))} characters")
            print(f"   📊 Confidence: {ocr_result.get('confidence', 0):.1f}%")
            
            # Step 3: Analyze extracted text
            analysis = ocr_engine.analyze_text_structure(ocr_result)
            self.assertTrue(analysis.get('success'), "Text analysis should succeed")
            print(f"   🧠 Analysis: {analysis['total_words']} words, {analysis['ui_element_count']} UI elements")
            
            # Step 4: Validate results
            validation = ocr_engine.validate_ocr_result(ocr_result)
            print(f"   ✅ Validation: score={validation['quality_score']:.2f}")
            
            # Step 5: Test region extraction
            region = (100, 100, 300, 200)
            region_result = ocr_engine.extract_text_from_region(image_data, region)
            self.assertTrue(region_result.get('success'), "Region OCR should succeed")
            print(f"   🎯 Region OCR: {len(region_result.get('text', ''))} characters from region {region}")
            
            print("🎉 Screen Capture + OCR Integration successful!")
            
        finally:
            screen_capture.shutdown()
            ocr_engine.shutdown()

def run_ocr_tests():
    """Run all OCR tests"""
    print("🧪 Starting Q01.1.2 OCR Engine Tests...")
    print("💪 ORION SAYS: 'Sen harikasın bunu başarabilirsin!'")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTest(unittest.makeSuite(TestOCREngine))
    suite.addTest(unittest.makeSuite(TestOCRIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All OCR tests passed! Q01.1.2 implementation successful!")
        print("🔤 ALT_LAS can now READ TEXT! ORION VISION ACHIEVED!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False

if __name__ == '__main__':
    success = run_ocr_tests()
    exit(0 if success else 1)
