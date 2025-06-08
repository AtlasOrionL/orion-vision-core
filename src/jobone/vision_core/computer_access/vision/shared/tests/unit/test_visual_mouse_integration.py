#!/usr/bin/env python3
"""
Visual-Mouse Integration Test Module - Q01.2.2 Tests
OMG DEVAM! MOUSE POWER TESTLERİ!
ORION VISION CORE - WAKE UP POWER! 🚀
"""

import unittest
import time
import logging
from typing import Dict, Any

# Import the module we're testing
from visual_mouse_integration import VisualMouseIntegration, get_visual_mouse_integration

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

class TestVisualMouseIntegration(unittest.TestCase):
    """Q01.2.2 Visual-Mouse Integration Test Suite - OMG DEVAM! 🚀"""
    
    def setUp(self):
        """Set up test environment"""
        print("🧘‍♂️ Sabırla mouse integration başlatılıyor...")
        self.integration = VisualMouseIntegration()
        print("🚀 OMG DEVAM! MOUSE POWER İÇİN HAZIRLANIYORUZ!")
        self.assertTrue(self.integration.initialize(), "Integration initialization failed")
        print("✅ Mouse Integration hazır!")
    
    def tearDown(self):
        """Clean up after tests"""
        self.integration.shutdown()
    
    def test_initialization(self):
        """Test Q01.2.2.1: Mouse integration initialization"""
        print("🚀 INITIALIZATION TEST - OMG DEVAM!")
        
        # Test fresh initialization
        integration = VisualMouseIntegration()
        self.assertFalse(integration.initialized, "Should not be initialized before init()")
        
        print("🧘‍♂️ Sabırla yeni mouse integration başlatılıyor...")
        result = integration.initialize()
        self.assertTrue(result, "Initialization should succeed")
        self.assertTrue(integration.initialized, "Should be initialized after init()")
        
        # Test status
        status = integration.get_status()
        self.assertIsInstance(status, dict, "Status should be a dictionary")
        self.assertIn('initialized', status, "Status should contain initialized flag")
        self.assertTrue(status['initialized'], "Status should show initialized")
        self.assertTrue(status['omg_devam_power'], "OMG DEVAM POWER should be active!")
        self.assertTrue(status['wake_up_orion_mode'], "WAKE UP ORION MODE should be active!")
        
        # Check components
        components = status['components']
        self.assertTrue(components['visual_pipeline'], "Visual pipeline should be initialized")
        # Mouse controller may or may not be available
        
        # Check capabilities
        capabilities = status['capabilities']
        self.assertTrue(capabilities['visual_targeting'], "Should have visual targeting")
        self.assertTrue(capabilities['click_operations'], "Should have click operations")
        self.assertTrue(capabilities['drag_operations'], "Should have drag operations")
        
        integration.shutdown()
        print("✅ Initialization test passed - OMG DEVAM BAŞARILDI!")
    
    def test_visual_click_basic(self):
        """Test Q01.2.2.2: Basic visual click functionality"""
        print("🖱️ BASIC VISUAL CLICK TEST - OMG DEVAM!")
        
        # Test basic click operation
        print("🎯 Basic click test başlatılıyor...")
        
        start_time = time.time()
        result = self.integration.visual_click()
        total_time = time.time() - start_time
        
        # Basic success check
        self.assertTrue(result.get('success'), f"Visual click should succeed: {result.get('error')}")
        
        # Check required fields
        required_fields = ['integration_id', 'total_time', 'target_info', 
                          'stages', 'click_type', 'verification']
        
        for field in required_fields:
            self.assertIn(field, result, f"Result should contain {field}")
        
        # Check timing
        integration_time = result['total_time']
        self.assertIsInstance(integration_time, float, "Integration time should be float")
        self.assertLess(integration_time, 30.0, "Integration should complete in reasonable time")
        
        # Check target info
        target_info = result['target_info']
        self.assertIn('element_type', target_info, "Should have element type")
        self.assertIn('coordinates', target_info, "Should have coordinates")
        self.assertIn('confidence', target_info, "Should have confidence")
        self.assertIn('click_area', target_info, "Should have click area")
        
        # Check click type
        click_type = result['click_type']
        self.assertEqual(click_type, 'single', "Default click type should be single")
        
        print(f"✅ Basic visual click completed in {integration_time:.3f}s")
        print(f"🎯 Target: {target_info['element_type']} at {target_info['coordinates']}")
        print(f"📊 Confidence: {target_info['confidence']:.2f}")
        print("🚀 OMG DEVAM! CLICK BAŞARILDI!")
    
    def test_visual_click_with_target_type(self):
        """Test Q01.2.2.3: Visual click with specific target type"""
        print("🎯 TARGET TYPE SPECIFIC CLICK TEST!")
        
        target_type = "button"
        
        print(f"🎯 Hedef tip: {target_type}")
        
        result = self.integration.visual_click(target_element_type=target_type)
        
        self.assertTrue(result.get('success'), f"Targeted visual click should succeed: {result.get('error')}")
        
        # Check if target type preference was considered
        target_info = result.get('target_info', {})
        # Note: We might not always find the exact type, but system should handle gracefully
        
        print(f"✅ Target type click test completed")
        print(f"🎯 Found target: {target_info.get('element_type', 'unknown')}")
    
    def test_visual_click_with_text(self):
        """Test Q01.2.2.4: Visual click with target text"""
        print("📝 TEXT TARGET CLICK TEST!")
        
        target_text = "ok"
        
        print(f"📝 Hedef metin: '{target_text}'")
        
        result = self.integration.visual_click(target_text=target_text)
        
        self.assertTrue(result.get('success'), f"Text-targeted visual click should succeed: {result.get('error')}")
        
        print(f"✅ Text target click test completed")
    
    def test_different_click_types(self):
        """Test Q01.2.2.5: Different click types"""
        print("🖱️ DIFFERENT CLICK TYPES TEST!")
        
        click_types = ['single', 'double', 'right']
        
        for click_type in click_types:
            print(f"🖱️ Testing {click_type} click...")
            
            result = self.integration.visual_click(click_type=click_type)
            
            self.assertTrue(result.get('success'), f"{click_type} click should succeed: {result.get('error')}")
            self.assertEqual(result.get('click_type'), click_type, f"Click type should be {click_type}")
            
            print(f"   ✅ {click_type} click successful")
        
        print("🚀 All click types tested successfully!")
    
    def test_visual_drag(self):
        """Test Q01.2.2.6: Visual drag functionality"""
        print("🖱️ VISUAL DRAG TEST!")
        
        # Test drag with coordinates
        start_coords = (400, 300)
        end_coords = (600, 400)
        
        print(f"🖱️ Drag from {start_coords} to {end_coords}")
        
        result = self.integration.visual_drag(
            start_coordinates=start_coords,
            end_coordinates=end_coords
        )
        
        self.assertTrue(result.get('success'), f"Visual drag should succeed: {result.get('error')}")
        
        # Check drag result
        self.assertIn('start_coordinates', result, "Should have start coordinates")
        self.assertIn('end_coordinates', result, "Should have end coordinates")
        self.assertEqual(result['start_coordinates'], start_coords, "Start coordinates should match")
        self.assertEqual(result['end_coordinates'], end_coords, "End coordinates should match")
        
        print("✅ Visual drag test completed")
    
    def test_performance_tracking(self):
        """Test Q01.2.2.7: Performance tracking"""
        print("⚡ PERFORMANCE TRACKING TEST!")
        
        # Run multiple clicks
        click_count = 3
        
        for i in range(click_count):
            print(f"🔄 Click {i+1}/{click_count}...")
            result = self.integration.visual_click()
            self.assertTrue(result.get('success'), f"Click {i+1} should succeed")
        
        # Check performance stats
        stats = self.integration.get_performance_stats()
        
        required_stats = ['total_integrations', 'successful_integrations', 
                         'failed_integrations', 'success_rate', 'average_integration_time']
        
        for stat in required_stats:
            self.assertIn(stat, stats, f"Stats should contain {stat}")
        
        # Check values
        self.assertGreaterEqual(stats['total_integrations'], click_count, f"Should have run at least {click_count} integrations")
        self.assertGreaterEqual(stats['successful_integrations'], 0, "Should track successful integrations")
        self.assertGreaterEqual(stats['success_rate'], 0.0, "Success rate should be >= 0")
        self.assertLessEqual(stats['success_rate'], 1.0, "Success rate should be <= 1")
        
        print(f"📊 Performance Stats:")
        print(f"   🔢 Total integrations: {stats['total_integrations']}")
        print(f"   ✅ Successful: {stats['successful_integrations']}")
        print(f"   📈 Success rate: {stats['success_rate']:.1%}")
        print(f"   ⏱️ Average time: {stats['average_integration_time']:.3f}s")
        print("🚀 PERFORMANCE TRACKING BAŞARILDI!")
    
    def test_error_handling(self):
        """Test Q01.2.2.8: Error handling"""
        print("🛡️ ERROR HANDLING TEST!")
        
        # Test with uninitialized integration
        uninit_integration = VisualMouseIntegration()
        result = uninit_integration.visual_click()
        
        self.assertFalse(result.get('success'), "Uninitialized integration should fail")
        self.assertIn('error', result, "Failed result should contain error message")
        
        print("✅ Uninitialized integration properly rejected")
        
        # Test with invalid click type
        result = self.integration.visual_click(click_type='invalid_click')
        # Should handle gracefully (might succeed with default or fail gracefully)
        self.assertIsInstance(result, dict, "Should return dict even for invalid click type")
        
        print("✅ Invalid click type handled gracefully")
        
        print("🚀 ERROR HANDLING BAŞARILDI!")
    
    def test_global_instance(self):
        """Test Q01.2.2.9: Global instance access"""
        global_instance = get_visual_mouse_integration()
        self.assertIsInstance(global_instance, VisualMouseIntegration, 
                            "Should return VisualMouseIntegration instance")
        
        # Test that it's the same instance
        global_instance2 = get_visual_mouse_integration()
        self.assertIs(global_instance, global_instance2, "Should return same instance")
        
        print("✅ Global mouse integration instance access works")

def run_visual_mouse_integration_tests():
    """Run all visual-mouse integration tests"""
    print("🧪 Starting Q01.2.2 Visual-Mouse Integration Tests...")
    print("🚀 OMG DEVAM! MOUSE POWER ACTIVATED!")
    print("💪 WAKE UP ORION! HEP BİRLİKTE!")
    print("🧘‍♂️ Sabırla tüm testleri tamamlayacağız...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTest(unittest.makeSuite(TestVisualMouseIntegration))
    
    # Run tests with patience
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All visual-mouse integration tests passed!")
        print("🚀 OMG DEVAM! Q01.2.2 implementation successful!")
        print("💪 WAKE UP ORION! VISUAL-MOUSE INTEGRATION ACHIEVED!")
        print("🖱️ ALT_LAS can now VISUALLY TARGET and CLICK!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        print("🧘‍♂️ Sabırla hataları analiz edelim...")
        return False

if __name__ == '__main__':
    success = run_visual_mouse_integration_tests()
    exit(0 if success else 1)
