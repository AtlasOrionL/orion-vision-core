#!/usr/bin/env python3
"""
Input Module Test Suite - Comprehensive testing for input functionality
"""

import unittest
import time
import platform
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

# Import input modules
from .mouse_controller import MouseController, MouseButton, ClickType, MovementType
from .keyboard_controller import KeyboardController, InputType, KeyState
from .input_coordinator import InputCoordinator, CoordinatedAction, CoordinatedTask
from .gesture_engine import GestureEngine, GestureType, GestureDirection

class TestMouseController(unittest.TestCase):
    """Test cases for MouseController"""
    
    def setUp(self):
        """Set up test environment"""
        self.controller = MouseController()
        # Mock the libraries to avoid actual mouse movement during tests
        self.controller.initialized = True
        self.controller.screen_width = 1920
        self.controller.screen_height = 1080
    
    def test_initialization(self):
        """Test mouse controller initialization"""
        self.assertTrue(self.controller.initialized)
        self.assertTrue(self.controller.is_ready())
        self.assertEqual(self.controller.screen_width, 1920)
        self.assertEqual(self.controller.screen_height, 1080)
    
    def test_coordinate_validation(self):
        """Test coordinate validation"""
        # Valid coordinates
        x, y = self.controller._validate_coordinates(100, 200)
        self.assertEqual(x, 100)
        self.assertEqual(y, 200)
        
        # Negative coordinates (should be adjusted)
        x, y = self.controller._validate_coordinates(-10, -20)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        
        # Coordinates beyond screen (should be adjusted)
        x, y = self.controller._validate_coordinates(2000, 1200)
        self.assertEqual(x, 1919)  # screen_width - 1
        self.assertEqual(y, 1079)  # screen_height - 1
    
    @patch('src.jobone.vision_core.computer_access.input.mouse_controller.pyautogui')
    def test_mouse_movement(self, mock_pyautogui):
        """Test mouse movement functionality"""
        mock_pyautogui.moveTo = MagicMock()
        
        result = self.controller.execute_action({
            'action_type': 'move',
            'x': 500,
            'y': 300,
            'movement_type': 'instant'
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['end_position'], (500, 300))
        self.assertEqual(result['movement_type'], 'instant')
    
    @patch('src.jobone.vision_core.computer_access.input.mouse_controller.pyautogui')
    def test_mouse_clicking(self, mock_pyautogui):
        """Test mouse clicking functionality"""
        mock_pyautogui.click = MagicMock()
        
        result = self.controller.execute_action({
            'action_type': 'click',
            'x': 400,
            'y': 250,
            'button': 'left',
            'click_type': 'single'
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['position'], (400, 250))
        self.assertEqual(result['button'], 'left')
        self.assertEqual(result['click_type'], 'single')
    
    def test_get_status(self):
        """Test status reporting"""
        status = self.controller.get_status()
        
        self.assertIn('initialized', status)
        self.assertIn('current_position', status)
        self.assertIn('screen_size', status)
        self.assertIn('movements_performed', status)
        self.assertIn('clicks_performed', status)

class TestKeyboardController(unittest.TestCase):
    """Test cases for KeyboardController"""
    
    def setUp(self):
        """Set up test environment"""
        self.controller = KeyboardController()
        # Mock initialization
        self.controller.initialized = True
    
    def test_initialization(self):
        """Test keyboard controller initialization"""
        self.assertTrue(self.controller.initialized)
        self.assertTrue(self.controller.is_ready())
        self.assertIsNotNone(self.controller.key_mappings)
    
    def test_key_normalization(self):
        """Test key name normalization"""
        # Test special keys
        self.assertEqual(self.controller._normalize_key('Enter'), 'enter')
        self.assertEqual(self.controller._normalize_key('SPACE'), 'space')
        self.assertEqual(self.controller._normalize_key('ctrl'), 'ctrl')
        
        # Test regular characters
        self.assertEqual(self.controller._normalize_key('a'), 'a')
        self.assertEqual(self.controller._normalize_key('A'), 'a')
    
    @patch('src.jobone.vision_core.computer_access.input.keyboard_controller.pyautogui')
    def test_text_typing(self, mock_pyautogui):
        """Test text typing functionality"""
        mock_pyautogui.typewrite = MagicMock()
        
        result = self.controller.execute_action({
            'action_type': 'type_text',
            'text': 'Hello World',
            'typing_speed': 60
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['text_length'], 11)
        self.assertEqual(result['typing_speed'], 60)
    
    @patch('src.jobone.vision_core.computer_access.input.keyboard_controller.pyautogui')
    def test_key_pressing(self, mock_pyautogui):
        """Test key pressing functionality"""
        mock_pyautogui.press = MagicMock()
        
        result = self.controller.execute_action({
            'action_type': 'press_key',
            'key': 'enter'
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['key'], 'enter')
        self.assertEqual(result['normalized_key'], 'enter')
    
    @patch('src.jobone.vision_core.computer_access.input.keyboard_controller.pyautogui')
    def test_key_combinations(self, mock_pyautogui):
        """Test key combination functionality"""
        mock_pyautogui.hotkey = MagicMock()
        
        result = self.controller.execute_action({
            'action_type': 'key_combination',
            'keys': ['ctrl', 'c']
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['keys'], ['ctrl', 'c'])
    
    def test_get_status(self):
        """Test status reporting"""
        status = self.controller.get_status()
        
        self.assertIn('initialized', status)
        self.assertIn('platform', status)
        self.assertIn('characters_typed', status)
        self.assertIn('keys_pressed', status)
        self.assertIn('shortcuts_executed', status)

class TestInputCoordinator(unittest.TestCase):
    """Test cases for InputCoordinator"""
    
    def setUp(self):
        """Set up test environment"""
        # Create mock controllers
        self.mock_mouse = Mock()
        self.mock_mouse.is_ready.return_value = True
        self.mock_mouse.execute_action.return_value = {'success': True}
        
        self.mock_keyboard = Mock()
        self.mock_keyboard.is_ready.return_value = True
        self.mock_keyboard.execute_action.return_value = {'success': True}
        
        self.coordinator = InputCoordinator()
        self.coordinator.initialize(self.mock_mouse, self.mock_keyboard)
    
    def test_initialization(self):
        """Test input coordinator initialization"""
        self.assertTrue(self.coordinator.initialized)
        self.assertTrue(self.coordinator.is_ready())
        self.assertEqual(self.coordinator.mouse, self.mock_mouse)
        self.assertEqual(self.coordinator.keyboard, self.mock_keyboard)
    
    def test_click_and_type(self):
        """Test click and type coordinated action"""
        task = CoordinatedTask(
            task_id="test_1",
            action_type=CoordinatedAction.CLICK_AND_TYPE,
            parameters={
                'x': 100,
                'y': 200,
                'text': 'Test Text',
                'clear_existing': True
            }
        )
        
        result = self.coordinator.execute_coordinated_action(task)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['task_id'], 'test_1')
        self.assertIn('actions_performed', result)
    
    def test_drag_and_drop(self):
        """Test drag and drop coordinated action"""
        task = CoordinatedTask(
            task_id="test_2",
            action_type=CoordinatedAction.DRAG_AND_DROP,
            parameters={
                'start_x': 100,
                'start_y': 100,
                'end_x': 200,
                'end_y': 200
            }
        )
        
        result = self.coordinator.execute_coordinated_action(task)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['task_id'], 'test_2')
        self.assertIn('start_position', result)
        self.assertIn('end_position', result)
    
    def test_get_status(self):
        """Test status reporting"""
        status = self.coordinator.get_status()
        
        self.assertIn('initialized', status)
        self.assertIn('coordinated_actions', status)
        self.assertIn('successful_actions', status)
        self.assertIn('controllers_ready', status)

class TestGestureEngine(unittest.TestCase):
    """Test cases for GestureEngine"""
    
    def setUp(self):
        """Set up test environment"""
        # Create mock mouse controller
        self.mock_mouse = Mock()
        self.mock_mouse.is_ready.return_value = True
        self.mock_mouse.execute_action.return_value = {'success': True}
        
        self.engine = GestureEngine()
        self.engine.initialize(self.mock_mouse)
    
    def test_initialization(self):
        """Test gesture engine initialization"""
        self.assertTrue(self.engine.initialized)
        self.assertTrue(self.engine.is_ready())
        self.assertIsNotNone(self.engine.gesture_library)
    
    def test_gesture_library(self):
        """Test built-in gesture library"""
        gestures = self.engine.get_available_gestures()
        
        self.assertIn('built_in', gestures)
        self.assertIn('custom', gestures)
        self.assertGreater(len(gestures['built_in']), 0)
        
        # Check for specific gestures
        built_in = gestures['built_in']
        self.assertIn('swipe_up', built_in)
        self.assertIn('circle_clockwise', built_in)
        self.assertIn('spiral_in', built_in)
    
    def test_swipe_gesture_creation(self):
        """Test swipe gesture creation"""
        pattern = self.engine._create_swipe_gesture('right')
        
        self.assertEqual(pattern.gesture_type, GestureType.SWIPE)
        self.assertEqual(len(pattern.points), 2)
        self.assertEqual(pattern.parameters['direction'], 'right')
    
    def test_circle_gesture_creation(self):
        """Test circle gesture creation"""
        pattern = self.engine._create_circle_gesture('clockwise')
        
        self.assertEqual(pattern.gesture_type, GestureType.CIRCLE)
        self.assertGreater(len(pattern.points), 10)  # Should have many points for smooth circle
        self.assertEqual(pattern.parameters['direction'], 'clockwise')
    
    def test_custom_gesture_registration(self):
        """Test custom gesture registration"""
        # Create a simple custom pattern
        from .gesture_engine import GesturePoint, GesturePattern
        
        points = [
            GesturePoint(0, 0, 0),
            GesturePoint(50, 50, 0.5),
            GesturePoint(100, 0, 1.0)
        ]
        
        pattern = GesturePattern(
            gesture_type=GestureType.CUSTOM_PATH,
            points=points,
            duration=1.0,
            parameters={}
        )
        
        success = self.engine.register_custom_gesture('test_gesture', pattern)
        self.assertTrue(success)
        
        # Check if gesture is available
        gestures = self.engine.get_available_gestures()
        self.assertIn('test_gesture', gestures['custom'])
    
    def test_gesture_execution(self):
        """Test gesture execution"""
        result = self.engine.execute_gesture({
            'gesture_name': 'swipe_right',
            'start_x': 100,
            'start_y': 100,
            'scale': 1.0,
            'speed': 1.0
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['gesture_name'], 'swipe_right')
    
    def test_get_status(self):
        """Test status reporting"""
        status = self.engine.get_status()
        
        self.assertIn('initialized', status)
        self.assertIn('gestures_executed', status)
        self.assertIn('successful_gestures', status)
        self.assertIn('available_gestures', status)

class TestInputIntegration(unittest.TestCase):
    """Integration tests for input module"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Create controllers with mocked libraries
        self.mouse = MouseController()
        self.mouse.initialized = True
        
        self.keyboard = KeyboardController()
        self.keyboard.initialized = True
        
        self.coordinator = InputCoordinator()
        self.coordinator.initialize(self.mouse, self.keyboard)
        
        self.gesture_engine = GestureEngine()
        self.gesture_engine.initialize(self.mouse)
    
    def test_full_integration(self):
        """Test full integration of all input components"""
        # Test that all components are ready
        self.assertTrue(self.mouse.is_ready())
        self.assertTrue(self.keyboard.is_ready())
        self.assertTrue(self.coordinator.is_ready())
        self.assertTrue(self.gesture_engine.is_ready())
    
    def test_coordinated_workflow(self):
        """Test a complete coordinated workflow"""
        # This would test a real workflow in a production environment
        # For now, just verify components can work together
        
        mouse_status = self.mouse.get_status()
        keyboard_status = self.keyboard.get_status()
        coordinator_status = self.coordinator.get_status()
        gesture_status = self.gesture_engine.get_status()
        
        self.assertTrue(mouse_status['initialized'])
        self.assertTrue(keyboard_status['initialized'])
        self.assertTrue(coordinator_status['initialized'])
        self.assertTrue(gesture_status['initialized'])
    
    def test_error_handling(self):
        """Test error handling across components"""
        # Test invalid parameters
        with self.assertRaises(ValueError):
            self.mouse.execute_action({'action_type': 'invalid_action'})
        
        with self.assertRaises(ValueError):
            self.keyboard.execute_action({'action_type': 'invalid_action'})
    
    def test_performance_tracking(self):
        """Test performance tracking across components"""
        # Get initial metrics
        mouse_status = self.mouse.get_status()
        keyboard_status = self.keyboard.get_status()
        
        # Verify metrics are being tracked
        self.assertIn('movements_performed', mouse_status)
        self.assertIn('clicks_performed', mouse_status)
        self.assertIn('characters_typed', keyboard_status)
        self.assertIn('keys_pressed', keyboard_status)

def run_input_tests():
    """Run all input module tests"""
    print("🧪 Running Input Module Test Suite...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestMouseController))
    test_suite.addTest(unittest.makeSuite(TestKeyboardController))
    test_suite.addTest(unittest.makeSuite(TestInputCoordinator))
    test_suite.addTest(unittest.makeSuite(TestGestureEngine))
    test_suite.addTest(unittest.makeSuite(TestInputIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_input_tests()
    exit(0 if success else 1)
