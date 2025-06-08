#!/usr/bin/env python3
"""
Screen Capture Test Module - Q01.1.1 Tests
Ekran görüntüsü yakalama modülü testleri
"""

import unittest
import time
import logging
from typing import Dict, Any

# Import the module we're testing
from screen_capture import ScreenCapture, get_screen_capture

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

class TestScreenCapture(unittest.TestCase):
    """Q01.1.1 Screen Capture Test Suite"""
    
    def setUp(self):
        """Set up test environment"""
        self.screen_capture = ScreenCapture()
        self.assertTrue(self.screen_capture.initialize(), "Screen capture initialization failed")
    
    def tearDown(self):
        """Clean up after tests"""
        self.screen_capture.shutdown()
    
    def test_initialization(self):
        """Test Q01.1.1.1: Basic initialization"""
        # Test fresh initialization
        sc = ScreenCapture()
        self.assertFalse(sc.initialized, "Should not be initialized before init()")
        
        result = sc.initialize()
        self.assertTrue(result, "Initialization should succeed")
        self.assertTrue(sc.initialized, "Should be initialized after init()")
        
        # Test status
        status = sc.get_status()
        self.assertIsInstance(status, dict, "Status should be a dictionary")
        self.assertIn('initialized', status, "Status should contain initialized flag")
        self.assertTrue(status['initialized'], "Status should show initialized")
        
        sc.shutdown()
    
    def test_full_screen_capture(self):
        """Test Q01.1.1.2: Full screen capture"""
        result = self.screen_capture.capture_screen()
        
        # Basic success check
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertTrue(result.get('success'), f"Capture should succeed: {result.get('error')}")
        
        # Check required fields
        self.assertIn('image_size', result, "Result should contain image_size")
        self.assertIn('capture_time', result, "Result should contain capture_time")
        self.assertIn('image_data', result, "Result should contain image_data")
        
        # Check image size
        image_size = result['image_size']
        self.assertIsInstance(image_size, tuple, "Image size should be a tuple")
        self.assertEqual(len(image_size), 2, "Image size should have 2 dimensions")
        self.assertGreater(image_size[0], 0, "Width should be positive")
        self.assertGreater(image_size[1], 0, "Height should be positive")
        
        # Check capture time (should be fast)
        capture_time = result['capture_time']
        self.assertIsInstance(capture_time, float, "Capture time should be a float")
        self.assertLess(capture_time, 5.0, "Capture should be fast (< 5 seconds)")
        
        print(f"✅ Full screen capture: {image_size} in {capture_time:.3f}s")
    
    def test_region_capture(self):
        """Test Q01.1.1.3: Region capture"""
        # Test small region
        region = (0, 0, 100, 100)
        result = self.screen_capture.capture_region(*region)
        
        self.assertTrue(result.get('success'), f"Region capture should succeed: {result.get('error')}")
        
        # Check region is respected
        if not result.get('simulated'):
            image_size = result['image_size']
            self.assertEqual(image_size, (100, 100), "Region size should match request")
        
        # Check metadata
        self.assertEqual(result.get('region'), region, "Region metadata should match")
        
        print(f"✅ Region capture: {result['image_size']} for region {region}")
    
    def test_multiple_captures(self):
        """Test Q01.1.1.4: Multiple captures performance"""
        capture_times = []
        
        for i in range(3):
            start_time = time.time()
            result = self.screen_capture.capture_screen()
            end_time = time.time()
            
            self.assertTrue(result.get('success'), f"Capture {i+1} should succeed")
            capture_times.append(end_time - start_time)
        
        # Check performance consistency
        avg_time = sum(capture_times) / len(capture_times)
        self.assertLess(avg_time, 2.0, "Average capture time should be reasonable")
        
        # Check performance stats
        stats = self.screen_capture.get_performance_stats()
        self.assertGreaterEqual(stats['total_captures'], 3, "Should track capture count")
        self.assertGreater(stats['total_time'], 0, "Should track total time")
        
        print(f"✅ Multiple captures: avg {avg_time:.3f}s, total {stats['total_captures']}")
    
    def test_image_optimization(self):
        """Test Q01.1.1.5: Image optimization"""
        # First capture an image
        capture_result = self.screen_capture.capture_screen()
        self.assertTrue(capture_result.get('success'), "Initial capture should succeed")
        
        # Test optimization
        image_data = capture_result['image_data']
        opt_result = self.screen_capture.optimize_image(image_data)
        
        self.assertTrue(opt_result.get('success'), f"Optimization should succeed: {opt_result.get('error')}")
        self.assertIn('optimized_data', opt_result, "Should contain optimized data")
        
        # Check if optimization actually did something
        if not opt_result.get('simulated'):
            self.assertIn('compression_ratio', opt_result, "Should report compression ratio")
        
        print(f"✅ Image optimization: {opt_result.get('method', 'unknown')}")
    
    def test_capture_validation(self):
        """Test Q01.1.1.6: Capture validation"""
        # Test valid capture
        capture_result = self.screen_capture.capture_screen()
        validation = self.screen_capture.validate_capture(capture_result)
        
        self.assertIsInstance(validation, dict, "Validation should return dict")
        self.assertIn('valid', validation, "Validation should contain valid flag")
        self.assertIn('quality_score', validation, "Validation should contain quality score")
        
        if capture_result.get('success'):
            self.assertTrue(validation['valid'], "Valid capture should pass validation")
            self.assertGreater(validation['quality_score'], 0, "Quality score should be positive")
        
        # Test invalid capture
        invalid_capture = {'success': False, 'error': 'test error'}
        invalid_validation = self.screen_capture.validate_capture(invalid_capture)
        self.assertFalse(invalid_validation['valid'], "Invalid capture should fail validation")
        self.assertEqual(invalid_validation['quality_score'], 0.0, "Invalid capture should have 0 quality")
        
        print(f"✅ Validation: valid={validation['valid']}, score={validation['quality_score']:.2f}")
    
    def test_error_handling(self):
        """Test Q01.1.1.7: Error handling"""
        # Test capture on uninitialized instance
        uninit_sc = ScreenCapture()
        result = uninit_sc.capture_screen()
        
        self.assertFalse(result.get('success'), "Uninitialized capture should fail")
        self.assertIn('error', result, "Failed capture should contain error message")
        
        # Test invalid region
        invalid_result = self.screen_capture.capture_region(-1, -1, 0, 0)
        # Should handle gracefully (may succeed with adjusted parameters or fail gracefully)
        self.assertIsInstance(invalid_result, dict, "Should return dict even for invalid input")
        
        print("✅ Error handling tests passed")
    
    def test_performance_requirements(self):
        """Test Q01.1.1.8: Performance requirements"""
        # Test capture speed requirement (< 500ms)
        result = self.screen_capture.capture_screen()
        
        if result.get('success'):
            capture_time = result.get('capture_time', float('inf'))
            self.assertLess(capture_time, 0.5, f"Capture should be < 500ms, got {capture_time:.3f}s")
        
        # Test memory requirement (< 50MB estimated)
        estimated_memory = result.get('estimated_memory_mb', 0)
        if estimated_memory > 0:
            self.assertLess(estimated_memory, 50, f"Memory usage should be < 50MB, got {estimated_memory:.1f}MB")
        
        print(f"✅ Performance: {result.get('capture_time', 0):.3f}s, {estimated_memory:.1f}MB")
    
    def test_global_instance(self):
        """Test Q01.1.1.9: Global instance access"""
        global_instance = get_screen_capture()
        self.assertIsInstance(global_instance, ScreenCapture, "Should return ScreenCapture instance")
        
        # Test that it's the same instance
        global_instance2 = get_screen_capture()
        self.assertIs(global_instance, global_instance2, "Should return same instance")
        
        print("✅ Global instance access works")

class TestScreenCaptureIntegration(unittest.TestCase):
    """Integration tests for screen capture"""
    
    def test_real_world_scenario(self):
        """Test Q01.1.1.10: Real-world usage scenario"""
        sc = ScreenCapture()
        self.assertTrue(sc.initialize(), "Initialization should succeed")
        
        try:
            # Scenario: Capture screen, optimize, validate
            print("🎯 Testing real-world scenario...")
            
            # Step 1: Capture full screen
            capture_result = sc.capture_screen()
            self.assertTrue(capture_result.get('success'), "Screen capture should succeed")
            print(f"   📸 Captured: {capture_result['image_size']}")
            
            # Step 2: Capture a region
            region_result = sc.capture_region(100, 100, 200, 200)
            self.assertTrue(region_result.get('success'), "Region capture should succeed")
            print(f"   🎯 Region captured: {region_result['image_size']}")
            
            # Step 3: Optimize image
            opt_result = sc.optimize_image(capture_result['image_data'])
            self.assertTrue(opt_result.get('success'), "Optimization should succeed")
            print(f"   ⚡ Optimized: {opt_result.get('method', 'unknown')}")
            
            # Step 4: Validate
            validation = sc.validate_capture(capture_result)
            self.assertTrue(validation['valid'], "Capture should be valid")
            print(f"   ✅ Validation: score={validation['quality_score']:.2f}")
            
            # Step 5: Check performance
            stats = sc.get_performance_stats()
            print(f"   📊 Performance: {stats['total_captures']} captures, avg {stats['average_capture_time']:.3f}s")
            
            print("🎉 Real-world scenario completed successfully!")
            
        finally:
            sc.shutdown()

def run_tests():
    """Run all screen capture tests"""
    print("🧪 Starting Q01.1.1 Screen Capture Tests...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTest(unittest.makeSuite(TestScreenCapture))
    suite.addTest(unittest.makeSuite(TestScreenCaptureIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All tests passed! Q01.1.1 implementation successful!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
