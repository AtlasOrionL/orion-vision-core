#!/usr/bin/env python3
"""
Input Control Module - Autonomous keyboard and mouse control
"""

__version__ = "1.0.0"
__author__ = "Atlas-orion"

# Input module imports
from .mouse_controller import MouseController
from .keyboard_controller import KeyboardController
from .input_coordinator import InputCoordinator
from .gesture_engine import GestureEngine

__all__ = [
    "MouseController",
    "KeyboardController", 
    "InputCoordinator",
    "GestureEngine"
]

# Input module constants
DEFAULT_MOUSE_PRECISION = 1  # pixels
DEFAULT_KEYBOARD_DELAY = 5   # milliseconds
DEFAULT_CLICK_DURATION = 0.1 # seconds
DEFAULT_TYPING_SPEED = 50    # characters per minute

# Mouse button mappings
MOUSE_BUTTONS = {
    'left': 'left',
    'right': 'right', 
    'middle': 'middle',
    'scroll_up': 'scroll_up',
    'scroll_down': 'scroll_down'
}

# Keyboard key mappings
SPECIAL_KEYS = {
    'enter': 'enter',
    'tab': 'tab',
    'space': 'space',
    'backspace': 'backspace',
    'delete': 'delete',
    'escape': 'escape',
    'shift': 'shift',
    'ctrl': 'ctrl',
    'alt': 'alt',
    'cmd': 'cmd',
    'win': 'win',
    'up': 'up',
    'down': 'down',
    'left': 'left',
    'right': 'right',
    'home': 'home',
    'end': 'end',
    'page_up': 'page_up',
    'page_down': 'page_down',
    'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
    'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
    'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12'
}

# Common keyboard shortcuts
SHORTCUTS = {
    'copy': ['ctrl', 'c'],
    'paste': ['ctrl', 'v'],
    'cut': ['ctrl', 'x'],
    'undo': ['ctrl', 'z'],
    'redo': ['ctrl', 'y'],
    'select_all': ['ctrl', 'a'],
    'save': ['ctrl', 's'],
    'open': ['ctrl', 'o'],
    'new': ['ctrl', 'n'],
    'find': ['ctrl', 'f'],
    'replace': ['ctrl', 'h'],
    'close': ['ctrl', 'w'],
    'quit': ['ctrl', 'q'],
    'refresh': ['f5'],
    'fullscreen': ['f11'],
    'alt_tab': ['alt', 'tab'],
    'task_manager': ['ctrl', 'shift', 'escape']
}

# Platform-specific adjustments
import platform
CURRENT_PLATFORM = platform.system()

if CURRENT_PLATFORM == "Darwin":  # macOS
    SHORTCUTS.update({
        'copy': ['cmd', 'c'],
        'paste': ['cmd', 'v'],
        'cut': ['cmd', 'x'],
        'undo': ['cmd', 'z'],
        'redo': ['cmd', 'shift', 'z'],
        'select_all': ['cmd', 'a'],
        'save': ['cmd', 's'],
        'open': ['cmd', 'o'],
        'new': ['cmd', 'n'],
        'find': ['cmd', 'f'],
        'close': ['cmd', 'w'],
        'quit': ['cmd', 'q'],
        'alt_tab': ['cmd', 'tab']
    })

def get_input_info():
    """Get input module information"""
    return {
        'module': 'computer_access.input',
        'version': __version__,
        'author': __author__,
        'platform': CURRENT_PLATFORM,
        'components': {
            'MouseController': 'Precise mouse movement and clicking control',
            'KeyboardController': 'Keyboard input and shortcut management',
            'InputCoordinator': 'Coordinated input operations',
            'GestureEngine': 'Complex gesture and movement patterns'
        },
        'capabilities': [
            'Precise mouse positioning (±1 pixel)',
            'Mouse clicking and dragging',
            'Mouse scrolling and wheel control',
            'Keyboard text input',
            'Special key combinations',
            'Cross-platform shortcuts',
            'Gesture recognition',
            'Input coordination',
            'Timing control',
            'Safety mechanisms'
        ],
        'supported_platforms': ['Windows', 'Linux', 'Darwin'],
        'performance_targets': {
            'mouse_precision': '±1 pixel',
            'mouse_movement_speed': '<10ms',
            'keyboard_latency': '<5ms',
            'click_accuracy': '100%',
            'typing_speed': '50+ CPM'
        },
        'safety_features': [
            'Boundary checking',
            'Rate limiting',
            'Emergency stop',
            'Input validation',
            'Platform compatibility'
        ]
    }

def get_supported_shortcuts():
    """Get list of supported keyboard shortcuts"""
    return SHORTCUTS.copy()

def get_special_keys():
    """Get list of special keys"""
    return SPECIAL_KEYS.copy()

def validate_coordinates(x, y, screen_width=None, screen_height=None):
    """
    Validate mouse coordinates
    
    Args:
        x: X coordinate
        y: Y coordinate
        screen_width: Screen width (optional)
        screen_height: Screen height (optional)
        
    Returns:
        tuple: Validated (x, y) coordinates
    """
    # Basic validation
    x = max(0, int(x))
    y = max(0, int(y))
    
    # Screen boundary validation if provided
    if screen_width:
        x = min(x, screen_width - 1)
    if screen_height:
        y = min(y, screen_height - 1)
    
    return x, y

def normalize_key(key):
    """
    Normalize key name for cross-platform compatibility
    
    Args:
        key: Key name to normalize
        
    Returns:
        str: Normalized key name
    """
    if isinstance(key, str):
        key_lower = key.lower()
        
        # Check special keys
        if key_lower in SPECIAL_KEYS:
            return SPECIAL_KEYS[key_lower]
        
        # Platform-specific key mapping
        if CURRENT_PLATFORM == "Darwin":
            if key_lower in ['ctrl', 'control']:
                return 'cmd'
            elif key_lower in ['cmd', 'command']:
                return 'cmd'
        
        return key_lower
    
    return str(key)

def create_shortcut_sequence(shortcut_name):
    """
    Create key sequence for named shortcut
    
    Args:
        shortcut_name: Name of the shortcut
        
    Returns:
        list: Key sequence for the shortcut
    """
    if shortcut_name in SHORTCUTS:
        return SHORTCUTS[shortcut_name].copy()
    
    return []

# Input validation functions
def is_valid_mouse_button(button):
    """Check if mouse button is valid"""
    return button in MOUSE_BUTTONS

def is_valid_coordinate(x, y):
    """Check if coordinates are valid"""
    try:
        x_int = int(x)
        y_int = int(y)
        return x_int >= 0 and y_int >= 0
    except (ValueError, TypeError):
        return False

def is_valid_key(key):
    """Check if key is valid"""
    if isinstance(key, str):
        return len(key) > 0
    return False

# Performance monitoring
class InputMetrics:
    """Input performance metrics tracking"""
    
    def __init__(self):
        self.mouse_movements = 0
        self.mouse_clicks = 0
        self.keyboard_inputs = 0
        self.shortcuts_executed = 0
        self.gestures_performed = 0
        self.errors_encountered = 0
        self.total_operations = 0
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.__init__()
    
    def record_mouse_movement(self):
        """Record mouse movement"""
        self.mouse_movements += 1
        self.total_operations += 1
    
    def record_mouse_click(self):
        """Record mouse click"""
        self.mouse_clicks += 1
        self.total_operations += 1
    
    def record_keyboard_input(self):
        """Record keyboard input"""
        self.keyboard_inputs += 1
        self.total_operations += 1
    
    def record_shortcut(self):
        """Record shortcut execution"""
        self.shortcuts_executed += 1
        self.total_operations += 1
    
    def record_gesture(self):
        """Record gesture performance"""
        self.gestures_performed += 1
        self.total_operations += 1
    
    def record_error(self):
        """Record error"""
        self.errors_encountered += 1
    
    def get_summary(self):
        """Get metrics summary"""
        success_rate = 0.0
        if self.total_operations > 0:
            success_rate = ((self.total_operations - self.errors_encountered) / self.total_operations) * 100
        
        return {
            'mouse_movements': self.mouse_movements,
            'mouse_clicks': self.mouse_clicks,
            'keyboard_inputs': self.keyboard_inputs,
            'shortcuts_executed': self.shortcuts_executed,
            'gestures_performed': self.gestures_performed,
            'total_operations': self.total_operations,
            'errors_encountered': self.errors_encountered,
            'success_rate': success_rate
        }

# Global metrics instance
input_metrics = InputMetrics()

# Logging configuration
import logging

def setup_input_logging():
    """Setup logging for input module"""
    logger = logging.getLogger('orion.computer_access.input')
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
input_logger = setup_input_logging()

# Module initialization message
input_logger.info("⌨️ Input Control Module initialized")
input_logger.info(f"📊 Version: {__version__}")
input_logger.info(f"👤 Author: {__author__}")
input_logger.info(f"🖥️ Platform: {CURRENT_PLATFORM}")
input_logger.info("🎯 Ready for autonomous input control")
