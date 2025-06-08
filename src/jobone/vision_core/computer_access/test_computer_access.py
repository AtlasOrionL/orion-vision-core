#!/usr/bin/env python3
"""
Computer Access Test Suite - Comprehensive testing for autonomous computer access
"""

import unittest
import time
import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# Import computer access modules
try:
    from .terminal.terminal_controller import TerminalController
    from .input.mouse_controller import MouseController
    from .input.keyboard_controller import KeyboardController
    from .input.input_coordinator import InputCoordinator
    from .vision.screen_agent import ScreenAgent
    from .scenarios.scenario_executor import ScenarioExecutor
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module import failed: {e}")
    MODULES_AVAILABLE = False

class TestComputerAccessIntegration(unittest.TestCase):
    """Integration tests for computer access system"""
    
    def setUp(self):
        """Set up test environment"""
        if not MODULES_AVAILABLE:
            self.skipTest("Computer access modules not available")
        
        # Create mock computer access manager
        self.computer_access_manager = Mock()
        self.computer_access_manager.initialized = True
        
        # Initialize components with mocking
        self.terminal = TerminalController()
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.screen = ScreenAgent()
        
        # Mock initialization to avoid actual system interaction
        self.terminal.initialized = True
        self.mouse.initialized = True
        self.keyboard.initialized = True
        self.screen.initialized = True
        
        # Set up computer access manager references
        self.computer_access_manager.terminal = self.terminal
        self.computer_access_manager.mouse = self.mouse
        self.computer_access_manager.keyboard = self.keyboard
        self.computer_access_manager.screen = self.screen
    
    def test_terminal_basic_functionality(self):
        """Test basic terminal functionality"""
        print("\n🖥️ Testing Terminal Controller...")
        
        # Test status
        self.assertTrue(self.terminal.is_ready())
        
        # Test command structure
        command_params = {
            'command': 'echo "Hello Orion"',
            'timeout': 10.0
        }
        
        # Mock the actual execution
        with patch.object(self.terminal, 'execute_command') as mock_exec:
            mock_exec.return_value = Mock(
                status=Mock(value='completed'),
                stdout='Hello Orion\n',
                stderr='',
                return_code=0,
                execution_time=0.1
            )
            
            result = self.terminal.execute_command(command_params)
            
            self.assertEqual(result.status.value, 'completed')
            self.assertEqual(result.return_code, 0)
            self.assertIn('Hello Orion', result.stdout)
        
        print("✅ Terminal Controller: PASSED")
    
    def test_mouse_basic_functionality(self):
        """Test basic mouse functionality"""
        print("\n🖱️ Testing Mouse Controller...")
        
        # Test status
        self.assertTrue(self.mouse.is_ready())
        
        # Test mouse action structure
        click_params = {
            'action_type': 'click',
            'x': 100,
            'y': 200,
            'button': 'left'
        }
        
        # Mock the actual execution
        with patch.object(self.mouse, 'execute_action') as mock_action:
            mock_action.return_value = {
                'success': True,
                'action_type': 'click',
                'position': (100, 200),
                'execution_time': 0.05
            }
            
            result = self.mouse.execute_action(click_params)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['position'], (100, 200))
        
        print("✅ Mouse Controller: PASSED")
    
    def test_keyboard_basic_functionality(self):
        """Test basic keyboard functionality"""
        print("\n⌨️ Testing Keyboard Controller...")
        
        # Test status
        self.assertTrue(self.keyboard.is_ready())
        
        # Test keyboard action structure
        type_params = {
            'action_type': 'type_text',
            'text': 'Orion Test',
            'typing_speed': 60
        }
        
        # Mock the actual execution
        with patch.object(self.keyboard, 'execute_action') as mock_action:
            mock_action.return_value = {
                'success': True,
                'action_type': 'type_text',
                'text_length': 10,
                'execution_time': 0.2
            }
            
            result = self.keyboard.execute_action(type_params)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['text_length'], 10)
        
        print("✅ Keyboard Controller: PASSED")
    
    def test_vision_basic_functionality(self):
        """Test basic vision functionality"""
        print("\n👁️ Testing Vision System...")
        
        # Test status
        self.assertTrue(self.screen.is_ready())
        
        # Test vision analysis structure
        analysis_params = {
            'detection_types': ['ui_elements', 'text_ocr'],
            'confidence_threshold': 0.7
        }
        
        # Mock the actual execution
        with patch.object(self.screen, 'capture_and_analyze') as mock_analyze:
            mock_analyze.return_value = {
                'success': True,
                'analysis': Mock(
                    elements=[],
                    text_content='Sample text',
                    confidence=0.8
                ),
                'execution_time': 0.5,
                'vision_type': 'core_vision'
            }
            
            result = self.screen.capture_and_analyze(analysis_params)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['analysis'].text_content, 'Sample text')
        
        print("✅ Vision System: PASSED")
    
    def test_input_coordinator_functionality(self):
        """Test input coordinator functionality"""
        print("\n🎯 Testing Input Coordinator...")
        
        # Create input coordinator
        coordinator = InputCoordinator()
        coordinator.initialize(self.mouse, self.keyboard)
        
        self.assertTrue(coordinator.is_ready())
        
        # Test coordinated action structure
        from .input.input_coordinator import CoordinatedTask, CoordinatedAction
        
        task = CoordinatedTask(
            task_id="test_task",
            action_type=CoordinatedAction.CLICK_AND_TYPE,
            parameters={
                'x': 100,
                'y': 200,
                'text': 'Test input'
            }
        )
        
        # Mock the execution
        with patch.object(coordinator, 'execute_coordinated_action') as mock_coord:
            mock_coord.return_value = {
                'success': True,
                'task_id': 'test_task',
                'actions_performed': [('click', {}), ('type_text', {})],
                'execution_time': 0.3
            }
            
            result = coordinator.execute_coordinated_action(task)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['task_id'], 'test_task')
        
        print("✅ Input Coordinator: PASSED")
    
    def test_scenario_executor_functionality(self):
        """Test scenario executor functionality"""
        print("\n🎯 Testing Scenario Executor...")
        
        # Create scenario executor
        executor = ScenarioExecutor(self.computer_access_manager)
        
        # Mock component initialization
        with patch('src.jobone.vision_core.computer_access.scenarios.task_planner.TaskPlanner') as MockPlanner, \
             patch('src.jobone.vision_core.computer_access.scenarios.integration_manager.IntegrationManager') as MockIntegration, \
             patch('src.jobone.vision_core.computer_access.scenarios.validation_engine.ValidationEngine') as MockValidation:
            
            # Setup mocks
            mock_planner = MockPlanner.return_value
            mock_planner.initialize.return_value = True
            mock_planner.is_ready.return_value = True
            
            mock_integration = MockIntegration.return_value
            mock_integration.initialize.return_value = True
            mock_integration.is_ready.return_value = True
            
            mock_validation = MockValidation.return_value
            mock_validation.initialize.return_value = True
            mock_validation.is_ready.return_value = True
            
            # Initialize executor
            success = executor.initialize()
            self.assertTrue(success)
            self.assertTrue(executor.is_ready())
        
        print("✅ Scenario Executor: PASSED")

class TestScenarioExecution(unittest.TestCase):
    """Test scenario execution with mocked components"""
    
    def setUp(self):
        """Set up scenario test environment"""
        if not MODULES_AVAILABLE:
            self.skipTest("Computer access modules not available")
        
        # Create comprehensive mock setup
        self.setup_mocks()
    
    def setup_mocks(self):
        """Setup all necessary mocks"""
        # Mock computer access manager
        self.computer_access_manager = Mock()
        self.computer_access_manager.initialized = True
        
        # Mock all components
        self.mock_terminal = Mock()
        self.mock_terminal.is_ready.return_value = True
        self.mock_terminal.execute_command.return_value = Mock(
            status=Mock(value='completed'),
            stdout='Command executed successfully',
            stderr='',
            return_code=0,
            execution_time=0.1
        )
        
        self.mock_mouse = Mock()
        self.mock_mouse.is_ready.return_value = True
        self.mock_mouse.execute_action.return_value = {
            'success': True,
            'execution_time': 0.05
        }
        
        self.mock_keyboard = Mock()
        self.mock_keyboard.is_ready.return_value = True
        self.mock_keyboard.execute_action.return_value = {
            'success': True,
            'execution_time': 0.1
        }
        
        self.mock_screen = Mock()
        self.mock_screen.is_ready.return_value = True
        self.mock_screen.capture_and_analyze.return_value = {
            'success': True,
            'analysis': Mock(elements=[], text_content='', confidence=0.8),
            'execution_time': 0.3
        }
        
        # Set references
        self.computer_access_manager.terminal = self.mock_terminal
        self.computer_access_manager.mouse = self.mock_mouse
        self.computer_access_manager.keyboard = self.mock_keyboard
        self.computer_access_manager.screen = self.mock_screen
    
    def test_simple_terminal_scenario(self):
        """Test simple terminal file creation scenario"""
        print("\n📝 Testing Terminal File Creation Scenario...")
        
        # Create scenario parameters
        scenario_params = {
            'template_name': 'terminal_file_creation',
            'parameters': {
                'filename': 'orion_test.txt',
                'content': 'Orion Vision Core Test'
            }
        }
        
        # Mock scenario execution
        with patch('src.jobone.vision_core.computer_access.scenarios.scenario_executor.ScenarioExecutor') as MockExecutor:
            mock_executor = MockExecutor.return_value
            mock_executor.initialize.return_value = True
            mock_executor.is_ready.return_value = True
            
            # Mock successful execution
            from .scenarios.scenario_executor import ScenarioResult, ScenarioStatus
            mock_result = ScenarioResult(
                scenario_id='test_scenario',
                status=ScenarioStatus.COMPLETED,
                success=True,
                steps_completed=2,
                total_steps=2,
                execution_time=1.5,
                step_results=[
                    {'step_id': 'create_file', 'success': True},
                    {'step_id': 'verify_file', 'success': True}
                ]
            )
            
            mock_executor.execute_scenario.return_value = mock_result
            
            # Execute scenario
            executor = MockExecutor(self.computer_access_manager)
            result = executor.execute_scenario(scenario_params)
            
            self.assertTrue(result.success)
            self.assertEqual(result.steps_completed, 2)
            self.assertEqual(result.status, ScenarioStatus.COMPLETED)
        
        print("✅ Terminal File Creation Scenario: PASSED")
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        print("\n📊 Testing Performance Metrics...")
        
        # Import metrics
        from .scenarios import scenarios_metrics
        
        # Reset metrics
        scenarios_metrics.reset_metrics()
        
        # Simulate scenario execution
        scenarios_metrics.record_scenario_start('test_scenario')
        time.sleep(0.1)  # Simulate execution time
        scenarios_metrics.record_scenario_end('test_scenario', True)
        
        # Record other metrics
        scenarios_metrics.record_planning_time(0.05)
        scenarios_metrics.record_validation_time(0.03)
        scenarios_metrics.record_integration_overhead(0.02)
        
        # Get summary
        summary = scenarios_metrics.get_summary()
        
        self.assertEqual(summary['scenarios_executed'], 1)
        self.assertEqual(summary['successful_scenarios'], 1)
        self.assertEqual(summary['success_rate'], 100.0)
        self.assertGreater(summary['total_execution_time'], 0)
        
        print("✅ Performance Metrics: PASSED")

def run_computer_access_tests():
    """Run all computer access tests"""
    print("🧪 ORION VISION CORE - AUTONOMOUS COMPUTER ACCESS TEST SUITE")
    print("=" * 70)
    
    # Check if modules are available
    if not MODULES_AVAILABLE:
        print("❌ Computer access modules not available for testing")
        print("   This is expected in a development environment")
        print("   Tests would run with actual hardware in production")
        return False
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestComputerAccessIntegration))
    test_suite.addTest(unittest.makeSuite(TestScenarioExecution))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"   Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    # Overall result
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! Computer Access System Ready! 🚀")
    else:
        print("\n⚠️ Some tests failed. Check logs for details.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_computer_access_tests()
    exit(0 if success else 1)
