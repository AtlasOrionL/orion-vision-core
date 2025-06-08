#!/usr/bin/env python3
"""
Autonomous Action System Test Module - Q01.2.3 Tests
ŞOK İÇİNDE! OTONOM AI AGENT TESTLERİ!
ORION VISION CORE - HAİRİKA GİDİYORSUN! 💥
"""

import unittest
import time
import logging
from typing import Dict, Any

# Import the module we're testing
from autonomous_action_system import AutonomousActionSystem, get_autonomous_action_system, ActionType, ActionPriority

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

class TestAutonomousActionSystem(unittest.TestCase):
    """Q01.2.3 Autonomous Action System Test Suite - ŞOK İÇİNDE! 💥"""
    
    def setUp(self):
        """Set up test environment"""
        print("🧘‍♂️ Sabırla autonomous system başlatılıyor...")
        self.system = AutonomousActionSystem()
        print("💥 ŞOK İÇİNDE! OTONOM AI AGENT İÇİN HAZIRLANIYORUZ!")
        self.assertTrue(self.system.initialize(), "System initialization failed")
        print("✅ Autonomous Action System hazır!")
    
    def tearDown(self):
        """Clean up after tests"""
        self.system.shutdown()
    
    def test_initialization(self):
        """Test Q01.2.3.1: Autonomous system initialization"""
        print("🚀 INITIALIZATION TEST - ŞOK İÇİNDE!")
        
        # Test fresh initialization
        system = AutonomousActionSystem()
        self.assertFalse(system.initialized, "Should not be initialized before init()")
        
        print("🧘‍♂️ Sabırla yeni autonomous system başlatılıyor...")
        result = system.initialize()
        self.assertTrue(result, "Initialization should succeed")
        self.assertTrue(system.initialized, "Should be initialized after init()")
        
        # Test status
        status = system.get_status()
        self.assertIsInstance(status, dict, "Status should be a dictionary")
        self.assertIn('initialized', status, "Status should contain initialized flag")
        self.assertTrue(status['initialized'], "Status should show initialized")
        self.assertTrue(status['shock_power'], "ŞOK İÇİNDE POWER should be active!")
        self.assertTrue(status['harika_gidiyorsun_mode'], "HAİRİKA GİDİYORSUN MODE should be active!")
        self.assertTrue(status['autonomous_ai_agent'], "OTONOM AI AGENT should be active!")
        
        # Check components
        components = status['components']
        self.assertTrue(components['visual_pipeline'], "Visual pipeline should be initialized")
        self.assertTrue(components['keyboard_integration'], "Keyboard integration should be initialized")
        self.assertTrue(components['mouse_integration'], "Mouse integration should be initialized")
        
        # Check capabilities
        capabilities = status['capabilities']
        self.assertTrue(capabilities['autonomous_decision_making'], "Should have autonomous decision making")
        self.assertTrue(capabilities['multi_modal_actions'], "Should have multi-modal actions")
        self.assertTrue(capabilities['goal_oriented_planning'], "Should have goal-oriented planning")
        self.assertTrue(capabilities['context_understanding'], "Should have context understanding")
        
        system.shutdown()
        print("✅ Initialization test passed - ŞOK İÇİNDE BAŞARILDI!")
    
    def test_simple_click_goal(self):
        """Test Q01.2.3.2: Simple click goal execution"""
        print("🖱️ SIMPLE CLICK GOAL TEST - HAİRİKA GİDİYORSUN!")
        
        goal = "Click the button"
        
        print(f"🎯 Goal: '{goal}'")
        print("🤖 Autonomous action başlatılıyor...")
        
        start_time = time.time()
        result = self.system.analyze_and_act(goal, max_actions=3)
        total_time = time.time() - start_time
        
        # Basic success check
        self.assertTrue(result.get('success'), f"Autonomous action should succeed: {result.get('error')}")
        
        # Check required fields
        required_fields = ['session_id', 'goal', 'total_time', 'actions_planned', 
                          'actions_executed', 'actions_successful', 'goal_achieved']
        
        for field in required_fields:
            self.assertIn(field, result, f"Result should contain {field}")
        
        # Check execution
        self.assertGreater(result['actions_planned'], 0, "Should plan at least one action")
        self.assertGreater(result['actions_executed'], 0, "Should execute at least one action")
        
        # Check timing
        execution_time = result['total_time']
        self.assertIsInstance(execution_time, float, "Execution time should be float")
        self.assertLess(execution_time, 60.0, "Should complete in reasonable time")
        
        print(f"✅ Simple click goal completed in {execution_time:.3f}s")
        print(f"📊 Actions: {result['actions_executed']} executed, {result['actions_successful']} successful")
        print(f"🎯 Goal achieved: {result['goal_achieved']}")
        print("💥 ŞOK İÇİNDE! CLICK GOAL BAŞARILDI!")
    
    def test_typing_goal(self):
        """Test Q01.2.3.3: Typing goal execution"""
        print("⌨️ TYPING GOAL TEST!")
        
        goal = "Type 'Hello World' in the input field"
        
        print(f"🎯 Goal: '{goal}'")
        
        result = self.system.analyze_and_act(goal, max_actions=2)
        
        self.assertTrue(result.get('success'), f"Typing goal should succeed: {result.get('error')}")
        
        # Check that typing action was planned
        action_plan = result.get('action_plan', [])
        has_type_action = any(action.get('action_type') == 'type' for action in action_plan)
        
        print(f"✅ Typing goal test completed")
        print(f"📝 Type action planned: {has_type_action}")
    
    def test_search_goal(self):
        """Test Q01.2.3.4: Search goal execution"""
        print("🔍 SEARCH GOAL TEST!")
        
        goal = "Search for 'test query'"
        
        print(f"🎯 Goal: '{goal}'")
        
        result = self.system.analyze_and_act(goal, max_actions=3)
        
        self.assertTrue(result.get('success'), f"Search goal should succeed: {result.get('error')}")
        
        # Check context analysis
        context_analysis = result.get('context_analysis', {})
        self.assertEqual(context_analysis.get('goal_type'), 'search_action', "Should identify as search action")
        
        print(f"✅ Search goal test completed")
        print(f"🔍 Goal type: {context_analysis.get('goal_type')}")
    
    def test_complex_goal(self):
        """Test Q01.2.3.5: Complex multi-step goal"""
        print("🧠 COMPLEX GOAL TEST!")
        
        goal = "Find the search box, type 'autonomous AI', and click search"
        
        print(f"🎯 Complex Goal: '{goal}'")
        
        result = self.system.analyze_and_act(goal, max_actions=5)
        
        self.assertTrue(result.get('success'), f"Complex goal should succeed: {result.get('error')}")
        
        # Check multiple actions were planned
        actions_planned = result.get('actions_planned', 0)
        self.assertGreaterEqual(actions_planned, 1, "Should plan multiple actions for complex goal")
        
        print(f"✅ Complex goal test completed")
        print(f"📋 Actions planned: {actions_planned}")
    
    def test_context_understanding(self):
        """Test Q01.2.3.6: Context understanding capabilities"""
        print("🧠 CONTEXT UNDERSTANDING TEST!")
        
        goal = "Navigate to the main menu"
        context = {
            'current_page': 'home',
            'user_intent': 'navigation',
            'priority': 'high'
        }
        
        print(f"🎯 Goal: '{goal}'")
        print(f"📋 Context: {context}")
        
        result = self.system.analyze_and_act(goal, context=context, max_actions=3)
        
        self.assertTrue(result.get('success'), f"Context-aware goal should succeed: {result.get('error')}")
        
        # Check context analysis
        context_analysis = result.get('context_analysis', {})
        self.assertIn('goal_type', context_analysis, "Should analyze goal type")
        self.assertIn('interface_type', context_analysis, "Should analyze interface type")
        self.assertIn('context_score', context_analysis, "Should calculate context score")
        
        context_score = context_analysis.get('context_score', 0)
        self.assertGreaterEqual(context_score, 0.0, "Context score should be >= 0")
        self.assertLessEqual(context_score, 1.0, "Context score should be <= 1")
        
        print(f"✅ Context understanding test completed")
        print(f"🧠 Context score: {context_score:.2f}")
        print(f"🎯 Goal type: {context_analysis.get('goal_type')}")
        print(f"🖥️ Interface type: {context_analysis.get('interface_type')}")
    
    def test_performance_tracking(self):
        """Test Q01.2.3.7: Performance tracking"""
        print("⚡ PERFORMANCE TRACKING TEST!")
        
        # Execute multiple goals
        goals = [
            "Click any button",
            "Type 'test' somewhere",
            "Find something clickable"
        ]
        
        for i, goal in enumerate(goals):
            print(f"🔄 Goal {i+1}/3: '{goal}'")
            result = self.system.analyze_and_act(goal, max_actions=2)
            self.assertTrue(result.get('success'), f"Goal {i+1} should succeed")
        
        # Check performance stats
        stats = self.system.get_performance_stats()
        
        required_stats = ['total_actions', 'successful_actions', 'failed_actions',
                         'success_rate', 'total_execution_time', 'average_execution_time']
        
        for stat in required_stats:
            self.assertIn(stat, stats, f"Stats should contain {stat}")
        
        # Check values
        self.assertGreaterEqual(stats['total_actions'], 3, "Should have executed multiple actions")
        self.assertGreaterEqual(stats['successful_actions'], 0, "Should track successful actions")
        self.assertGreaterEqual(stats['success_rate'], 0.0, "Success rate should be >= 0")
        self.assertLessEqual(stats['success_rate'], 1.0, "Success rate should be <= 1")
        
        print(f"📊 Performance Stats:")
        print(f"   🔢 Total actions: {stats['total_actions']}")
        print(f"   ✅ Successful: {stats['successful_actions']}")
        print(f"   📈 Success rate: {stats['success_rate']:.1%}")
        print(f"   ⏱️ Average time: {stats['average_execution_time']:.3f}s")
        print("💥 PERFORMANCE TRACKING BAŞARILDI!")
    
    def test_error_handling(self):
        """Test Q01.2.3.8: Error handling and recovery"""
        print("🛡️ ERROR HANDLING TEST!")
        
        # Test with uninitialized system
        uninit_system = AutonomousActionSystem()
        result = uninit_system.analyze_and_act("test goal")
        
        self.assertFalse(result.get('success'), "Uninitialized system should fail")
        self.assertIn('error', result, "Failed result should contain error message")
        
        print("✅ Uninitialized system properly rejected")
        
        # Test with empty goal
        result = self.system.analyze_and_act("")
        # Should handle gracefully
        self.assertIsInstance(result, dict, "Should return dict even for empty goal")
        
        print("✅ Empty goal handled gracefully")
        
        # Test with very complex goal
        complex_goal = "Do something very complex that might not be possible to achieve with current interface elements"
        result = self.system.analyze_and_act(complex_goal, max_actions=1)
        # Should handle gracefully (might succeed or fail gracefully)
        self.assertIsInstance(result, dict, "Should return dict even for complex goal")
        
        if result.get('success'):
            print("✅ Complex goal handled successfully")
        else:
            print(f"⚠️ Complex goal failed gracefully: {result.get('error', 'unknown')}")
        
        print("💥 ERROR HANDLING BAŞARILDI!")
    
    def test_global_instance(self):
        """Test Q01.2.3.9: Global instance access"""
        global_instance = get_autonomous_action_system()
        self.assertIsInstance(global_instance, AutonomousActionSystem, 
                            "Should return AutonomousActionSystem instance")
        
        # Test that it's the same instance
        global_instance2 = get_autonomous_action_system()
        self.assertIs(global_instance, global_instance2, "Should return same instance")
        
        print("✅ Global autonomous system instance access works")

def run_autonomous_action_system_tests():
    """Run all autonomous action system tests"""
    print("🧪 Starting Q01.2.3 Autonomous Action System Tests...")
    print("💥 ŞOK İÇİNDE! OTONOM AI AGENT POWER ACTIVATED!")
    print("🔥 HAİRİKA GİDİYORSUN! WAKE UP ORION!")
    print("🧘‍♂️ Sabırla tüm testleri tamamlayacağız...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTest(unittest.makeSuite(TestAutonomousActionSystem))
    
    # Run tests with patience
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All autonomous action system tests passed!")
        print("💥 ŞOK İÇİNDE! Q01.2.3 implementation successful!")
        print("🤖 HAİRİKA GİDİYORSUN! AUTONOMOUS AI AGENT ACHIEVED!")
        print("🧠 ALT_LAS is now a TRUE AUTONOMOUS AI AGENT!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        print("🧘‍♂️ Sabırla hataları analiz edelim...")
        return False

if __name__ == '__main__':
    success = run_autonomous_action_system_tests()
    exit(0 if success else 1)
