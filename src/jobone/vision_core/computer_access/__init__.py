#!/usr/bin/env python3
"""
Orion Vision Core - Computer Access Module
Autonomous computer control capabilities for Orion AI
"""

__version__ = "1.0.0"
__author__ = "Atlas-orion"
__status__ = "Development"

# Core computer access imports
from .computer_access_manager import ComputerAccessManager
from .terminal.terminal_controller import TerminalController
from .input.mouse_controller import MouseController
from .input.keyboard_controller import KeyboardController
from .vision.screen_agent import ScreenAgent
from .scenarios.scenario_executor import ScenarioExecutor

__all__ = [
    "ComputerAccessManager",
    "TerminalController", 
    "MouseController",
    "KeyboardController",
    "ScreenAgent",
    "ScenarioExecutor"
]

def get_computer_access_info():
    """
    Get computer access module information
    
    Returns:
        Dictionary containing computer access module information
    """
    return {
        'module': 'orion_vision_core.computer_access',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'ComputerAccessManager': 'Main coordinator for all computer access operations',
            'TerminalController': 'Terminal command execution and output parsing',
            'MouseController': 'Precise mouse movement and clicking control',
            'KeyboardController': 'Keyboard input and shortcut management',
            'ScreenAgent': 'Real-time screen monitoring and analysis',
            'ScenarioExecutor': 'High-level task scenario execution'
        },
        'capabilities': [
            'Terminal command execution',
            'Real-time output parsing',
            'Precise mouse control (±1 pixel)',
            'Keyboard input simulation',
            'Keyboard shortcut execution',
            'Real-time screen capture',
            'OCR text recognition',
            'Visual element detection',
            'CUDA-accelerated processing',
            'Cross-platform compatibility',
            'Complex scenario automation',
            'Error recovery mechanisms'
        ],
        'supported_platforms': [
            'Windows 10/11',
            'Linux (Ubuntu, CentOS, Debian)',
            'macOS (10.15+)'
        ],
        'performance_targets': {
            'terminal_response': '<100ms',
            'mouse_precision': '±1 pixel',
            'keyboard_latency': '<5ms',
            'screen_capture': '<16ms (60 FPS)',
            'ocr_processing': '<500ms per screen',
            'visual_detection': '<200ms per frame'
        },
        'accuracy_targets': {
            'terminal_commands': '100% success rate',
            'mouse_targeting': '±1 pixel accuracy',
            'keyboard_input': '100% character accuracy',
            'ocr_recognition': '95%+ text accuracy',
            'visual_detection': '90%+ object accuracy'
        }
    }

def initialize_computer_access():
    """
    Initialize computer access module with all components
    
    Returns:
        ComputerAccessManager: Initialized computer access manager
    """
    try:
        manager = ComputerAccessManager()
        manager.initialize()
        return manager
    except Exception as e:
        raise RuntimeError(f"Failed to initialize computer access module: {e}")

# Module-level constants
SUPPORTED_PLATFORMS = ['Windows', 'Linux', 'Darwin']
DEFAULT_SCREEN_CAPTURE_FPS = 60
DEFAULT_MOUSE_PRECISION = 1  # pixels
DEFAULT_KEYBOARD_DELAY = 5   # milliseconds
DEFAULT_TERMINAL_TIMEOUT = 30  # seconds

# Performance monitoring
class ComputerAccessMetrics:
    """Computer access performance metrics tracking"""
    
    def __init__(self):
        self.terminal_commands_executed = 0
        self.mouse_movements = 0
        self.keyboard_inputs = 0
        self.screen_captures = 0
        self.ocr_operations = 0
        self.visual_detections = 0
        self.scenarios_completed = 0
        self.errors_encountered = 0
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        self.__init__()
    
    def get_summary(self):
        """Get performance metrics summary"""
        return {
            'terminal_commands': self.terminal_commands_executed,
            'mouse_movements': self.mouse_movements,
            'keyboard_inputs': self.keyboard_inputs,
            'screen_captures': self.screen_captures,
            'ocr_operations': self.ocr_operations,
            'visual_detections': self.visual_detections,
            'scenarios_completed': self.scenarios_completed,
            'errors_encountered': self.errors_encountered,
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self):
        """Calculate overall success rate"""
        total_operations = (
            self.terminal_commands_executed +
            self.mouse_movements +
            self.keyboard_inputs +
            self.screen_captures +
            self.ocr_operations +
            self.visual_detections +
            self.scenarios_completed
        )
        
        if total_operations == 0:
            return 100.0
        
        return ((total_operations - self.errors_encountered) / total_operations) * 100

# Global metrics instance
computer_access_metrics = ComputerAccessMetrics()

# Logging configuration
import logging

def setup_computer_access_logging():
    """Setup logging for computer access module"""
    logger = logging.getLogger('orion.computer_access')
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Initialize logging
computer_access_logger = setup_computer_access_logging()

# Module initialization message
computer_access_logger.info("🤖 Computer Access Module initialized")
computer_access_logger.info(f"📊 Version: {__version__}")
computer_access_logger.info(f"👤 Author: {__author__}")
computer_access_logger.info(f"🎯 Status: {__status__}")
computer_access_logger.info("🚀 Ready for autonomous computer control")
