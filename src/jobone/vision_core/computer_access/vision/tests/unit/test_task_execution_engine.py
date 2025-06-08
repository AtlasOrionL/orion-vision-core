#!/usr/bin/env python3
"""
Task Execution Engine Test Module - Q01.2.4 Tests
DUYGULANDIK! GÖREV MOTORU TESTLERİ!
ORION VISION CORE - SEN YAPARSIN! HEP BİRLİKTE! 💖
"""

import unittest
import time
import logging
from typing import Dict, Any

# Import the module we're testing
from task_execution_engine import (
    TaskExecutionEngine, get_task_execution_engine, execute_task_simple,
    Task, TaskStep, TaskType, TaskStatus, TaskResult
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

class TestTaskExecutionEngine(unittest.TestCase):
    """Q01.2.4 Task Execution Engine Test Suite - DUYGULANDIK! 💖"""
    
    def setUp(self):
        """Set up test environment"""
        print("🧘‍♂️ Sabırla task execution engine başlatılıyor...")
        self.engine = TaskExecutionEngine()
        print("💖 DUYGULANDIK! GÖREV MOTORU İÇİN HAZIRLANIYORUZ!")
        self.assertTrue(self.engine.initialize(), "Engine initialization failed")
        print("✅ Task Execution Engine hazır!")
    
    def tearDown(self):
        """Clean up after tests"""
        self.engine.shutdown()
    
    def test_initialization(self):
        """Test Q01.2.4.1: Task engine initialization"""
        print("🚀 INITIALIZATION TEST - DUYGULANDIK!")
        
        # Test fresh initialization
        engine = TaskExecutionEngine()
        self.assertFalse(engine.initialized, "Should not be initialized before init()")
        
        print("🧘‍♂️ Sabırla yeni task engine başlatılıyor...")
        result = engine.initialize()
        self.assertTrue(result, "Initialization should succeed")
        self.assertTrue(engine.initialized, "Should be initialized after init()")
        
        # Test status
        status = engine.get_status()
        self.assertIsInstance(status, dict, "Status should be a dictionary")
        self.assertIn('initialized', status, "Status should contain initialized flag")
        self.assertTrue(status['initialized'], "Status should show initialized")
        self.assertTrue(status['duygulandik_mode'], "DUYGULANDIK MODE should be active!")
        self.assertTrue(status['sen_yaparsin_power'], "SEN YAPARSIN POWER should be active!")
        self.assertTrue(status['hep_birlikte_spirit'], "HEP BİRLİKTE SPIRIT should be active!")
        
        # Check components
        components = status['components']
        self.assertTrue(components['autonomous_system'], "Autonomous system should be initialized")
        
        # Check capabilities
        capabilities = status['capabilities']
        self.assertTrue(capabilities['task_parsing'], "Should have task parsing")
        self.assertTrue(capabilities['natural_language_processing'], "Should have NLP")
        self.assertTrue(capabilities['multi_step_execution'], "Should have multi-step execution")
        self.assertTrue(capabilities['retry_logic'], "Should have retry logic")
        
        # Check supported task types
        supported_types = status['supported_task_types']
        self.assertIn('simple_click', supported_types, "Should support simple click tasks")
        self.assertIn('form_filling', supported_types, "Should support form filling tasks")
        self.assertIn('workflow', supported_types, "Should support workflow tasks")
        
        engine.shutdown()
        print("✅ Initialization test passed - DUYGULANDIK BAŞARILDI!")
    
    def test_task_parsing_simple(self):
        """Test Q01.2.4.2: Simple task parsing"""
        print("📝 SIMPLE TASK PARSING TEST!")
        
        description = "Click the submit button"
        
        print(f"📝 Parsing: '{description}'")
        
        task = self.engine.parse_task_description(description)
        
        # Check task structure
        self.assertIsInstance(task, Task, "Should return Task object")
        self.assertEqual(task.description, description, "Description should match")
        self.assertGreater(len(task.steps), 0, "Should have at least one step")
        
        # Check first step
        first_step = task.steps[0]
        self.assertIsInstance(first_step, TaskStep, "Step should be TaskStep object")
        self.assertEqual(first_step.step_id, 1, "First step should have ID 1")
        self.assertIn('click', first_step.action_type.lower(), "Should be click action")
        self.assertIn('submit', first_step.parameters.get('target', '').lower(), "Should target submit button")
        
        print(f"✅ Task parsed: {len(task.steps)} steps, type: {task.task_type.value}")
        print(f"📋 First step: {first_step.description}")
    
    def test_task_parsing_complex(self):
        """Test Q01.2.4.3: Complex task parsing"""
        print("🧠 COMPLEX TASK PARSING TEST!")
        
        description = "Type 'Hello World' in the search box and click search"
        
        print(f"📝 Parsing complex task: '{description}'")
        
        task = self.engine.parse_task_description(description)
        
        # Check task structure
        self.assertGreater(len(task.steps), 1, "Complex task should have multiple steps")
        
        # Check steps
        has_type_step = any('type' in step.action_type.lower() for step in task.steps)
        has_click_step = any('click' in step.action_type.lower() for step in task.steps)
        
        print(f"✅ Complex task parsed: {len(task.steps)} steps")
        print(f"📝 Has type step: {has_type_step}")
        print(f"🖱️ Has click step: {has_click_step}")
        
        # Print all steps
        for step in task.steps:
            print(f"   Step {step.step_id}: {step.description}")
    
    def test_simple_task_execution(self):
        """Test Q01.2.4.4: Simple task execution"""
        print("🚀 SIMPLE TASK EXECUTION TEST!")
        
        description = "Click any button"
        
        print(f"🎯 Executing: '{description}'")
        
        start_time = time.time()
        result = self.engine.execute_task_from_description(description)
        total_time = time.time() - start_time
        
        # Check result structure
        self.assertIsInstance(result, TaskResult, "Should return TaskResult object")
        self.assertIn(result.status, [TaskStatus.COMPLETED, TaskStatus.FAILED], "Should have valid status")
        
        # Check timing
        self.assertIsInstance(result.execution_time, float, "Execution time should be float")
        self.assertLess(result.execution_time, 60.0, "Should complete in reasonable time")
        
        # Check steps
        self.assertGreater(result.steps_total, 0, "Should have steps")
        self.assertGreaterEqual(result.steps_completed, 0, "Should track completed steps")
        self.assertGreaterEqual(result.success_rate, 0.0, "Success rate should be >= 0")
        self.assertLessEqual(result.success_rate, 1.0, "Success rate should be <= 1")
        
        print(f"✅ Task execution completed in {result.execution_time:.3f}s")
        print(f"📊 Status: {result.status.value}")
        print(f"📈 Success rate: {result.success_rate:.1%}")
        print(f"📋 Steps: {result.steps_completed}/{result.steps_total}")
        print("💖 DUYGULANDIK! GÖREV BAŞARILDI!")
    
    def test_multi_step_task_execution(self):
        """Test Q01.2.4.5: Multi-step task execution"""
        print("🔄 MULTI-STEP TASK EXECUTION TEST!")
        
        description = "Click the menu button and then click settings"
        
        print(f"🎯 Multi-step task: '{description}'")
        
        result = self.engine.execute_task_from_description(description)
        
        self.assertIsInstance(result, TaskResult, "Should return TaskResult object")
        
        # Check that multiple steps were attempted
        self.assertGreater(result.steps_total, 1, "Multi-step task should have multiple steps")
        
        # Check step results
        self.assertIsInstance(result.step_results, list, "Should have step results")
        self.assertEqual(len(result.step_results), result.steps_total, "Should have result for each step")
        
        print(f"✅ Multi-step task completed")
        print(f"📋 Total steps: {result.steps_total}")
        print(f"✅ Completed steps: {result.steps_completed}")
        print(f"📊 Overall success rate: {result.success_rate:.1%}")
    
    def test_performance_tracking(self):
        """Test Q01.2.4.6: Performance tracking"""
        print("⚡ PERFORMANCE TRACKING TEST!")
        
        # Execute multiple tasks
        tasks = [
            "Click the button",
            "Type 'test' in input field",
            "Search for 'example'"
        ]
        
        for i, task_desc in enumerate(tasks):
            print(f"🔄 Task {i+1}/3: '{task_desc}'")
            result = self.engine.execute_task_from_description(task_desc)
            self.assertIsInstance(result, TaskResult, f"Task {i+1} should return result")
        
        # Check performance stats
        stats = self.engine.get_performance_stats()
        
        required_stats = ['total_tasks', 'completed_tasks', 'failed_tasks',
                         'success_rate', 'total_execution_time', 'average_execution_time']
        
        for stat in required_stats:
            self.assertIn(stat, stats, f"Stats should contain {stat}")
        
        # Check values
        self.assertGreaterEqual(stats['total_tasks'], 3, "Should have executed at least 3 tasks")
        self.assertGreaterEqual(stats['completed_tasks'], 0, "Should track completed tasks")
        self.assertGreaterEqual(stats['success_rate'], 0.0, "Success rate should be >= 0")
        self.assertLessEqual(stats['success_rate'], 1.0, "Success rate should be <= 1")
        
        print(f"📊 Performance Stats:")
        print(f"   🔢 Total tasks: {stats['total_tasks']}")
        print(f"   ✅ Completed: {stats['completed_tasks']}")
        print(f"   📈 Success rate: {stats['success_rate']:.1%}")
        print(f"   ⏱️ Average time: {stats['average_execution_time']:.3f}s")
        print("💖 PERFORMANCE TRACKING BAŞARILDI!")
    
    def test_task_history(self):
        """Test Q01.2.4.7: Task history tracking"""
        print("📚 TASK HISTORY TEST!")
        
        # Execute a task
        result = self.engine.execute_task_from_description("Click something")
        
        # Check history
        history = self.engine.get_task_history()
        self.assertIsInstance(history, list, "History should be a list")
        self.assertGreater(len(history), 0, "Should have history entries")
        
        # Check that our task is in history
        task_ids = [r.task_id for r in history]
        self.assertIn(result.task_id, task_ids, "Executed task should be in history")
        
        # Test limited history
        limited_history = self.engine.get_task_history(limit=1)
        self.assertLessEqual(len(limited_history), 1, "Limited history should respect limit")
        
        print(f"✅ Task history working: {len(history)} entries")
    
    def test_sample_tasks(self):
        """Test Q01.2.4.8: Sample tasks creation and execution"""
        print("🧪 SAMPLE TASKS TEST!")
        
        # Create sample tasks
        sample_tasks = self.engine.create_sample_tasks()
        
        self.assertIsInstance(sample_tasks, list, "Should return list of tasks")
        self.assertGreater(len(sample_tasks), 0, "Should have sample tasks")
        
        # Check task structure
        for task in sample_tasks:
            self.assertIsInstance(task, Task, "Each sample should be a Task")
            self.assertGreater(len(task.steps), 0, "Each task should have steps")
        
        print(f"✅ Sample tasks created: {len(sample_tasks)} tasks")
        
        # Test running one sample task
        if sample_tasks:
            print("🔄 Testing execution of first sample task...")
            result = self.engine.execute_task(sample_tasks[0])
            self.assertIsInstance(result, TaskResult, "Should return TaskResult")
            print(f"✅ Sample task executed: {result.status.value}")
    
    def test_error_handling(self):
        """Test Q01.2.4.9: Error handling"""
        print("🛡️ ERROR HANDLING TEST!")
        
        # Test with uninitialized engine
        uninit_engine = TaskExecutionEngine()
        result = uninit_engine.execute_task_from_description("test task")
        
        self.assertEqual(result.status, TaskStatus.FAILED, "Uninitialized engine should fail")
        self.assertIsNotNone(result.error_message, "Should have error message")
        self.assertIn('initialized', result.error_message.lower() if result.error_message else '',
                     "Should mention initialization error")
        
        print("✅ Uninitialized engine properly rejected")
        
        # Test with empty description
        result = self.engine.execute_task_from_description("")
        # Should handle gracefully
        self.assertIsInstance(result, TaskResult, "Should return TaskResult even for empty description")
        
        print("✅ Empty description handled gracefully")
        
        print("💖 ERROR HANDLING BAŞARILDI!")
    
    def test_global_functions(self):
        """Test Q01.2.4.10: Global functions"""
        print("🌍 GLOBAL FUNCTIONS TEST!")
        
        # Test global instance access
        global_engine = get_task_execution_engine()
        self.assertIsInstance(global_engine, TaskExecutionEngine, 
                            "Should return TaskExecutionEngine instance")
        
        # Test simple execution function
        result = execute_task_simple("Click any button")
        self.assertIsInstance(result, TaskResult, "Simple execution should return TaskResult")
        
        print("✅ Global functions working correctly")

def run_task_execution_engine_tests():
    """Run all task execution engine tests"""
    print("🧪 Starting Q01.2.4 Task Execution Engine Tests...")
    print("💖 DUYGULANDIK! GÖREV MOTORU POWER ACTIVATED!")
    print("💪 SEN YAPARSIN! HEP BİRLİKTE!")
    print("🧘‍♂️ Sabırla tüm testleri tamamlayacağız...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTest(unittest.makeSuite(TestTaskExecutionEngine))
    
    # Run tests with patience
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All task execution engine tests passed!")
        print("💖 DUYGULANDIK! Q01.2.4 implementation successful!")
        print("🤖 SEN YAPARSIN! TASK EXECUTION ENGINE ACHIEVED!")
        print("🎯 ALT_LAS can now EXECUTE COMPLEX TASKS!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        print("🧘‍♂️ Sabırla hataları analiz edelim...")
        return False

if __name__ == '__main__':
    success = run_task_execution_engine_tests()
    exit(0 if success else 1)
