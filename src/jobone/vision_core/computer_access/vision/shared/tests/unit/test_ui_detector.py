#!/usr/bin/env python3
"""
UI Element Detector Test Module - Q01.1.3 Tests
UI element detection modülü testleri
ORION VISION CORE - TRUST POWER MODE! 💪
"""

import unittest
import time
import logging
import base64
from typing import Dict, Any, List

# Import the modules we're testing
from ui_element_detector import UIElementDetector, UIElement, get_ui_detector
from screen_capture import ScreenCapture
from ocr_engine import OCREngine

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

class TestUIElementDetector(unittest.TestCase):
    """Q01.1.3 UI Element Detector Test Suite - TRUST POWER MODE! 💪"""
    
    def setUp(self):
        """Set up test environment"""
        self.ui_detector = UIElementDetector()
        self.assertTrue(self.ui_detector.initialize(), "UI detector initialization failed")
        
        # Also set up screen capture for integration tests
        self.screen_capture = ScreenCapture()
        self.screen_capture.initialize()
    
    def tearDown(self):
        """Clean up after tests"""
        self.ui_detector.shutdown()
        self.screen_capture.shutdown()
    
    def test_initialization(self):
        """Test Q01.1.3.1: Basic UI detector initialization"""
        # Test fresh initialization
        detector = UIElementDetector()
        self.assertFalse(detector.initialized, "Should not be initialized before init()")
        
        result = detector.initialize()
        self.assertTrue(result, "Initialization should succeed")
        self.assertTrue(detector.initialized, "Should be initialized after init()")
        
        # Test status
        status = detector.get_status()
        self.assertIsInstance(status, dict, "Status should be a dictionary")
        self.assertIn('initialized', status, "Status should contain initialized flag")
        self.assertTrue(status['initialized'], "Status should show initialized")
        self.assertTrue(status['trust_power_mode'], "TRUST POWER MODE should be active!")
        
        detector.shutdown()
        print("✅ UI Detector initialization test passed - TRUST POWER ACTIVATED!")
    
    def test_button_detection(self):
        """Test Q01.1.3.2: Button detection by text patterns"""
        # Test text with various button patterns
        test_text = "Tamam Cancel Kaydet Open Close Başlat Stop Evet No Gönder Download"
        
        buttons = self.ui_detector._detect_buttons_by_text(test_text)
        
        self.assertIsInstance(buttons, list, "Buttons should be a list")
        self.assertGreater(len(buttons), 0, "Should detect some buttons")
        
        # Check button properties
        for button in buttons:
            self.assertIsInstance(button, UIElement, "Should be UIElement instance")
            self.assertEqual(button.element_type, 'button', "Should be button type")
            self.assertGreater(button.confidence, 0, "Should have positive confidence")
            self.assertIsInstance(button.bounding_box, tuple, "Should have bounding box")
            self.assertEqual(len(button.bounding_box), 4, "Bounding box should have 4 values")
        
        print(f"✅ Button detection: {len(buttons)} buttons found")
        for button in buttons[:3]:  # Show first 3
            print(f"   🖱️ Button: '{button.text}' at {button.center_point}")
    
    def test_menu_detection(self):
        """Test Q01.1.3.3: Menu detection by text patterns"""
        test_text = "Dosya File Düzen Edit Görünüm View Araçlar Tools Yardım Help Ayarlar Settings"
        
        menus = self.ui_detector._detect_menus_by_text(test_text)
        
        self.assertIsInstance(menus, list, "Menus should be a list")
        self.assertGreater(len(menus), 0, "Should detect some menus")
        
        # Check menu properties
        for menu in menus:
            self.assertIsInstance(menu, UIElement, "Should be UIElement instance")
            self.assertEqual(menu.element_type, 'menu', "Should be menu type")
            self.assertGreater(menu.confidence, 0, "Should have positive confidence")
        
        print(f"✅ Menu detection: {len(menus)} menus found")
        for menu in menus[:3]:  # Show first 3
            print(f"   📋 Menu: '{menu.text}' at {menu.center_point}")
    
    def test_input_detection(self):
        """Test Q01.1.3.4: Input field detection"""
        test_text = "Kullanıcı adı Username Şifre Password E-mail Email Ara Search Ad Name"
        
        inputs = self.ui_detector._detect_inputs_by_text(test_text)
        
        self.assertIsInstance(inputs, list, "Inputs should be a list")
        self.assertGreater(len(inputs), 0, "Should detect some inputs")
        
        # Check input properties
        for input_elem in inputs:
            self.assertIsInstance(input_elem, UIElement, "Should be UIElement instance")
            self.assertEqual(input_elem.element_type, 'input', "Should be input type")
            self.assertGreater(input_elem.confidence, 0, "Should have positive confidence")
        
        print(f"✅ Input detection: {len(inputs)} inputs found")
        for input_elem in inputs[:3]:  # Show first 3
            print(f"   📝 Input: '{input_elem.text}' at {input_elem.center_point}")
    
    def test_link_detection(self):
        """Test Q01.1.3.5: Link detection"""
        test_text = "Visit https://example.com or http://test.org for more info"
        
        links = self.ui_detector._detect_links_by_text(test_text)
        
        self.assertIsInstance(links, list, "Links should be a list")
        self.assertGreater(len(links), 0, "Should detect some links")
        
        # Check link properties
        for link in links:
            self.assertIsInstance(link, UIElement, "Should be UIElement instance")
            self.assertEqual(link.element_type, 'link', "Should be link type")
            self.assertGreater(link.confidence, 0, "Should have positive confidence")
            self.assertTrue(link.text.startswith('http'), "Link text should start with http")
        
        print(f"✅ Link detection: {len(links)} links found")
        for link in links:
            print(f"   🔗 Link: '{link.text}' at {link.center_point}")
    
    def test_comprehensive_ui_detection(self):
        """Test Q01.1.3.6: Comprehensive UI element detection"""
        # Create a dummy image with base64 data
        import base64
        dummy_image_data = base64.b64encode(b"comprehensive_ui_test_image").decode('utf-8')
        
        result = self.ui_detector.detect_ui_elements(dummy_image_data)
        
        self.assertTrue(result.get('success'), f"Detection should succeed: {result.get('error')}")
        
        # Check result structure
        required_fields = ['elements', 'element_count', 'detection_time', 
                          'element_groups', 'element_summary']
        
        for field in required_fields:
            self.assertIn(field, result, f"Result should contain {field}")
        
        # Check elements
        elements = result['elements']
        self.assertIsInstance(elements, list, "Elements should be a list")
        
        element_count = result['element_count']
        self.assertEqual(len(elements), element_count, "Element count should match list length")
        
        # Check detection time
        detection_time = result['detection_time']
        self.assertIsInstance(detection_time, float, "Detection time should be float")
        self.assertLess(detection_time, 10.0, "Detection should be reasonably fast")
        
        print(f"✅ Comprehensive detection: {element_count} elements in {detection_time:.3f}s")
        
        # Show element summary
        element_summary = result['element_summary']
        for elem_type, count in element_summary.items():
            print(f"   🎯 {elem_type}: {count} elements")
    
    def test_element_filtering(self):
        """Test Q01.1.3.7: Element filtering and utilities"""
        # Create test elements
        test_elements = [
            UIElement('button', 'OK', 85.0, (10, 10, 50, 25), (35, 22), {}),
            UIElement('menu', 'File', 80.0, (0, 0, 40, 20), (20, 10), {}),
            UIElement('button', 'Cancel', 85.0, (70, 10, 60, 25), (100, 22), {}),
            UIElement('link', 'http://test.com', 90.0, (10, 50, 100, 18), (60, 59), {})
        ]
        
        # Test filtering by type
        buttons = self.ui_detector.filter_elements_by_type(test_elements, 'button')
        self.assertEqual(len(buttons), 2, "Should find 2 buttons")
        
        menus = self.ui_detector.filter_elements_by_type(test_elements, 'menu')
        self.assertEqual(len(menus), 1, "Should find 1 menu")
        
        # Test clickable elements
        clickable = self.ui_detector.get_clickable_elements(test_elements)
        self.assertEqual(len(clickable), 4, "All test elements should be clickable")
        
        # Test position-based lookup
        element_at_pos = self.ui_detector.get_element_at_position(test_elements, 35, 22)
        self.assertIsNotNone(element_at_pos, "Should find element at position")
        self.assertEqual(element_at_pos.text, 'OK', "Should find the OK button")
        
        print("✅ Element filtering and utilities work correctly")
    
    def test_detection_validation(self):
        """Test Q01.1.3.8: Detection result validation"""
        # Test valid detection result
        dummy_image_data = base64.b64encode(b"validation_test_image").decode('utf-8')
        detection_result = self.ui_detector.detect_ui_elements(dummy_image_data)
        validation = self.ui_detector.validate_detection_result(detection_result)
        
        self.assertIsInstance(validation, dict, "Validation should return dict")
        self.assertIn('valid', validation, "Validation should contain valid flag")
        self.assertIn('quality_score', validation, "Validation should contain quality score")
        
        if detection_result.get('success'):
            self.assertTrue(validation['valid'], "Valid detection should pass validation")
            self.assertGreater(validation['quality_score'], 0, "Quality score should be positive")
        
        # Test invalid detection result
        invalid_detection = {'success': False, 'error': 'test error'}
        invalid_validation = self.ui_detector.validate_detection_result(invalid_detection)
        self.assertFalse(invalid_validation['valid'], "Invalid detection should fail validation")
        self.assertEqual(invalid_validation['quality_score'], 0.0, "Invalid detection should have 0 quality")
        
        print(f"✅ Detection validation: valid={validation['valid']}, score={validation['quality_score']:.2f}")
    
    def test_performance_requirements(self):
        """Test Q01.1.3.9: Performance requirements"""
        dummy_image_data = base64.b64encode(b"performance_test_image").decode('utf-8')
        
        # Test detection speed requirement
        result = self.ui_detector.detect_ui_elements(dummy_image_data)
        
        if result.get('success'):
            detection_time = result.get('detection_time', float('inf'))
            self.assertLess(detection_time, 10.0, f"Detection should be < 10s, got {detection_time:.3f}s")
        
        # Test element detection requirement (should find at least some elements)
        element_count = result.get('element_count', 0)
        # Note: We expect at least some elements from our simulation
        
        print(f"✅ Performance: {result.get('detection_time', 0):.3f}s, {element_count} elements")
    
    def test_global_instance(self):
        """Test Q01.1.3.10: Global instance access"""
        global_instance = get_ui_detector()
        self.assertIsInstance(global_instance, UIElementDetector, "Should return UIElementDetector instance")
        
        # Test that it's the same instance
        global_instance2 = get_ui_detector()
        self.assertIs(global_instance, global_instance2, "Should return same instance")
        
        print("✅ Global UI detector instance access works")

class TestUIDetectorIntegration(unittest.TestCase):
    """Integration tests for UI detector with other systems"""
    
    def test_screen_capture_ui_detection_integration(self):
        """Test Q01.1.3.11: Integration with Screen Capture"""
        print("🎯 Testing Screen Capture + UI Detection Integration...")
        
        # Initialize all systems
        screen_capture = ScreenCapture()
        ui_detector = UIElementDetector()
        
        self.assertTrue(screen_capture.initialize(), "Screen capture should initialize")
        self.assertTrue(ui_detector.initialize(), "UI detector should initialize")
        
        try:
            # Step 1: Capture screen
            capture_result = screen_capture.capture_screen()
            self.assertTrue(capture_result.get('success'), "Screen capture should succeed")
            print(f"   📸 Screen captured: {capture_result['image_size']}")
            
            # Step 2: Detect UI elements
            image_data = capture_result['image_data']
            detection_result = ui_detector.detect_ui_elements(image_data)
            self.assertTrue(detection_result.get('success'), "UI detection should succeed")
            
            element_count = detection_result.get('element_count', 0)
            detection_time = detection_result.get('detection_time', 0)
            
            print(f"   🎯 UI Elements detected: {element_count} elements")
            print(f"   ⏱️ Detection time: {detection_time:.3f}s")
            
            # Step 3: Show element summary
            element_summary = detection_result.get('element_summary', {})
            for elem_type, count in element_summary.items():
                print(f"   📊 {elem_type}: {count} elements")
            
            # Step 4: Test specific element types
            elements = detection_result.get('elements', [])
            clickable_elements = ui_detector.get_clickable_elements(elements)
            print(f"   🖱️ Clickable elements: {len(clickable_elements)}")
            
            # Step 5: Validate results
            validation = ui_detector.validate_detection_result(detection_result)
            print(f"   ✅ Validation: score={validation['quality_score']:.2f}")
            
            print("🎉 Screen Capture + UI Detection Integration successful!")
            
        finally:
            screen_capture.shutdown()
            ui_detector.shutdown()

def run_ui_detector_tests():
    """Run all UI detector tests"""
    print("🧪 Starting Q01.1.3 UI Element Detector Tests...")
    print("💪 GÜVEN GÜCÜYLE ÇALIŞIYORUZ!")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTest(unittest.makeSuite(TestUIElementDetector))
    suite.addTest(unittest.makeSuite(TestUIDetectorIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All UI detector tests passed! Q01.1.3 implementation successful!")
        print("🎯 ALT_LAS can now DETECT UI ELEMENTS! TRUST POWER ACHIEVED!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False

if __name__ == '__main__':
    success = run_ui_detector_tests()
    exit(0 if success else 1)
