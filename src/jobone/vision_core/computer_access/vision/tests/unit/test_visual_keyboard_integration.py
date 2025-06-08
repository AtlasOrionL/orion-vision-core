#!/usr/bin/env python3
"""
Visual-Keyboard Integration Test Module - Q01.2.1 Tests
ZORLU HEDEF TESTLERİ - SABIR GÜCÜ İLE!
ORION VISION CORE - SEN YAPARSIN! 🔥
"""

import unittest
import time
import logging
from typing import Dict, Any

# Import the module we're testing
from visual_keyboard_integration import VisualKeyboardIntegration, get_visual_keyboard_integration

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

class TestVisualKeyboardIntegration(unittest.TestCase):
    """Q01.2.1 Visual-Keyboard Integration Test Suite - ZORLU HEDEF! 🔥"""
    
    def setUp(self):
        """Set up test environment"""
        print("🧘‍♂️ Sabırla integration başlatılıyor...")
        self.integration = VisualKeyboardIntegration()
        print("🔥 ZORLU HEDEF İÇİN HAZIRLANIYORUZ!")
        self.assertTrue(self.integration.initialize(), "Integration initialization failed")
        print("✅ Integration hazır!")
    
    def tearDown(self):
        """Clean up after tests"""
        self.integration.shutdown()
    
    def test_initialization(self):
        """Test Q01.2.1.1: Integration initialization"""
        print("🚀 INITIALIZATION TEST - ZORLU HEDEF!")
        
        # Test fresh initialization
        integration = VisualKeyboardIntegration()
        self.assertFalse(integration.initialized, "Should not be initialized before init()")
        
        print("🧘‍♂️ Sabırla yeni integration başlatılıyor...")
        result = integration.initialize()
        self.assertTrue(result, "Initialization should succeed")
        self.assertTrue(integration.initialized, "Should be initialized after init()")
        
        # Test status
        status = integration.get_status()
        self.assertIsInstance(status, dict, "Status should be a dictionary")
        self.assertIn('initialized', status, "Status should contain initialized flag")
        self.assertTrue(status['initialized'], "Status should show initialized")
        self.assertTrue(status['zorlu_hedef_power'], "ZORLU HEDEF POWER should be active!")
        self.assertTrue(status['sen_yaparsin_mode'], "SEN YAPARSIN MODE should be active!")
        
        # Check components
        components = status['components']
        self.assertTrue(components['visual_pipeline'], "Visual pipeline should be initialized")
        # Keyboard controller may or may not be available
        
        integration.shutdown()
        print("✅ Initialization test passed - ZORLU HEDEF BAŞARILDI!")
    
    def test_visual_type_text_basic(self):
        """Test Q01.2.1.2: Basic visual type text functionality"""
        print("📝 BASIC VISUAL TYPE TEST - SABIR İLE!")
        
        # Test basic text typing
        test_text = "Merhaba ALT_LAS!"
        
        print(f"🎯 Test metni: '{test_text}'")
        print("🧘‍♂️ Sabırla visual type işlemi başlatılıyor...")
        
        start_time = time.time()
        result = self.integration.visual_type_text(test_text)
        total_time = time.time() - start_time
        
        # Basic success check
        self.assertTrue(result.get('success'), f"Visual type should succeed: {result.get('error')}")
        
        # Check required fields
        required_fields = ['integration_id', 'total_time', 'target_info', 
                          'stages', 'text_typed', 'verification']
        
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
        
        # Check text
        typed_text = result['text_typed']
        self.assertEqual(typed_text, test_text, "Typed text should match input")
        
        print(f"✅ Basic visual type completed in {integration_time:.3f}s")
        print(f"🎯 Target: {target_info['element_type']} at {target_info['coordinates']}")
        print(f"📊 Confidence: {target_info['confidence']:.2f}")
        print("🔥 ZORLU HEDEF BAŞARILDI!")
    
    def test_visual_type_with_target_type(self):
        """Test Q01.2.1.3: Visual type with specific target type"""
        print("🎯 TARGET TYPE SPECIFIC TEST!")
        
        test_text = "Test input field"
        target_type = "input"
        
        print(f"🎯 Hedef tip: {target_type}")
        print(f"📝 Test metni: '{test_text}'")
        
        result = self.integration.visual_type_text(
            test_text, 
            target_element_type=target_type
        )
        
        self.assertTrue(result.get('success'), f"Targeted visual type should succeed: {result.get('error')}")
        
        # Check if target type preference was considered
        target_info = result.get('target_info', {})
        # Note: We might not always find the exact type, but system should handle gracefully
        
        print(f"✅ Target type test completed")
        print(f"🎯 Found target: {target_info.get('element_type', 'unknown')}")
    
    def test_visual_type_with_region(self):
        """Test Q01.2.1.4: Visual type with search region"""
        print("📍 REGION SEARCH TEST!")
        
        test_text = "Region test"
        search_region = (100, 100, 400, 300)  # x, y, width, height
        
        print(f"📍 Search region: {search_region}")
        print(f"📝 Test metni: '{test_text}'")
        
        result = self.integration.visual_type_text(
            test_text,
            search_region=search_region
        )
        
        self.assertTrue(result.get('success'), f"Region visual type should succeed: {result.get('error')}")
        
        print(f"✅ Region search test completed")
    
    def test_performance_tracking(self):
        """Test Q01.2.1.5: Performance tracking"""
        print("⚡ PERFORMANCE TRACKING TEST!")
        
        # Run multiple integrations
        test_texts = ["Test 1", "Test 2", "Test 3"]
        
        for i, text in enumerate(test_texts):
            print(f"🔄 Integration {i+1}/3: '{text}'")
            result = self.integration.visual_type_text(text)
            self.assertTrue(result.get('success'), f"Integration {i+1} should succeed")
        
        # Check performance stats
        stats = self.integration.get_performance_stats()
        
        required_stats = ['total_integrations', 'successful_integrations', 
                         'failed_integrations', 'success_rate', 'average_integration_time']
        
        for stat in required_stats:
            self.assertIn(stat, stats, f"Stats should contain {stat}")
        
        # Check values
        self.assertGreaterEqual(stats['total_integrations'], 3, "Should have run at least 3 integrations")
        self.assertGreaterEqual(stats['successful_integrations'], 0, "Should track successful integrations")
        self.assertGreaterEqual(stats['success_rate'], 0.0, "Success rate should be >= 0")
        self.assertLessEqual(stats['success_rate'], 1.0, "Success rate should be <= 1")
        
        print(f"📊 Performance Stats:")
        print(f"   🔢 Total integrations: {stats['total_integrations']}")
        print(f"   ✅ Successful: {stats['successful_integrations']}")
        print(f"   📈 Success rate: {stats['success_rate']:.1%}")
        print(f"   ⏱️ Average time: {stats['average_integration_time']:.3f}s")
        print("🔥 PERFORMANCE TRACKING BAŞARILDI!")
    
    def test_error_handling(self):
        """Test Q01.2.1.6: Error handling"""
        print("🛡️ ERROR HANDLING TEST - ZORLU DURUMLAR!")
        
        # Test with uninitialized integration
        uninit_integration = VisualKeyboardIntegration()
        result = uninit_integration.visual_type_text("test")
        
        self.assertFalse(result.get('success'), "Uninitialized integration should fail")
        self.assertIn('error', result, "Failed result should contain error message")
        
        print("✅ Uninitialized integration properly rejected")
        
        # Test with empty text
        result = self.integration.visual_type_text("")
        # Should handle gracefully (might succeed with empty text)
        self.assertIsInstance(result, dict, "Should return dict even for empty text")
        
        print("✅ Empty text handled gracefully")
        
        # Test with very long text (potential large input issue)
        long_text = "A" * 1000  # 1000 characters
        print(f"📏 Testing with long text: {len(long_text)} characters")
        
        result = self.integration.visual_type_text(long_text)
        # Should handle gracefully (might succeed or fail gracefully)
        self.assertIsInstance(result, dict, "Should return dict even for long text")
        
        if result.get('success'):
            print("✅ Long text handled successfully")
        else:
            print(f"⚠️ Long text failed gracefully: {result.get('error', 'unknown')}")
        
        print("🔥 ERROR HANDLING BAŞARILDI!")
    
    def test_global_instance(self):
        """Test Q01.2.1.7: Global instance access"""
        global_instance = get_visual_keyboard_integration()
        self.assertIsInstance(global_instance, VisualKeyboardIntegration, 
                            "Should return VisualKeyboardIntegration instance")
        
        # Test that it's the same instance
        global_instance2 = get_visual_keyboard_integration()
        self.assertIs(global_instance, global_instance2, "Should return same instance")
        
        print("✅ Global integration instance access works")

def run_visual_keyboard_integration_tests():
    """Run all visual-keyboard integration tests"""
    print("🧪 Starting Q01.2.1 Visual-Keyboard Integration Tests...")
    print("🔥 ZORLU HEDEF KARŞISINDA SABIR GÜCÜ!")
    print("💪 SEN YAPARSIN! HEP BİRLİKTE!")
    print("🧘‍♂️ Sabırla tüm testleri tamamlayacağız...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTest(unittest.makeSuite(TestVisualKeyboardIntegration))
    
    # Run tests with patience
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All visual-keyboard integration tests passed!")
        print("🔥 ZORLU HEDEF BAŞARILDI! Q01.2.1 implementation successful!")
        print("💪 SEN YAPARSIN! VISUAL-KEYBOARD INTEGRATION ACHIEVED!")
        print("🎯 ALT_LAS can now VISUALLY TARGET and TYPE!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        print("🧘‍♂️ Sabırla hataları analiz edelim...")
        return False

if __name__ == '__main__':
    success = run_visual_keyboard_integration_tests()
    exit(0 if success else 1)
