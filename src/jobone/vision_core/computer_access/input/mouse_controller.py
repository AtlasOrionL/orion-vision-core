#!/usr/bin/env python3
"""
Mouse Controller - Precise mouse movement and clicking control
"""

import logging
import time
import math
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import platform-specific mouse libraries
try:
    import pyautogui
    pyautogui.FAILSAFE = False  # Disable failsafe for autonomous operation
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from pynput import mouse
    from pynput.mouse import Button, Listener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

class MouseButton(Enum):
    """Mouse button types"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"

class ClickType(Enum):
    """Mouse click types"""
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    HOLD = "hold"
    RELEASE = "release"

class MovementType(Enum):
    """Mouse movement types"""
    INSTANT = "instant"
    LINEAR = "linear"
    SMOOTH = "smooth"
    BEZIER = "bezier"

@dataclass
class MousePosition:
    """Mouse position information"""
    x: int
    y: int
    timestamp: float

@dataclass
class MouseAction:
    """Mouse action definition"""
    action_type: str
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[MouseButton] = None
    click_type: Optional[ClickType] = None
    movement_type: Optional[MovementType] = None
    duration: float = 0.1
    scroll_amount: int = 1

class MouseController:
    """
    Precise mouse controller for autonomous mouse operations
    Supports movement, clicking, dragging, and scrolling
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.computer_access.input.mouse')
        self.initialized = False
        
        # Mouse state
        self.current_position = MousePosition(0, 0, time.time())
        self.is_dragging = False
        self.drag_start_position = None
        
        # Configuration
        self.precision = 1  # pixels
        self.default_duration = 0.1  # seconds
        self.movement_speed = 1.0  # multiplier
        self.safety_enabled = True
        
        # Screen information
        self.screen_width = 1920
        self.screen_height = 1080
        
        # Performance tracking
        self.movements_performed = 0
        self.clicks_performed = 0
        self.drags_performed = 0
        self.scrolls_performed = 0
        self.errors_encountered = 0
        
        # Safety boundaries
        self.safe_zone = {
            'min_x': 0,
            'min_y': 0,
            'max_x': self.screen_width,
            'max_y': self.screen_height
        }
        
        # Thread safety
        self.action_lock = threading.Lock()
        
        self.logger.info("🖱️ MouseController initialized")
    
    def initialize(self) -> bool:
        """
        Initialize mouse controller
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing mouse controller...")
            
            # Check library availability
            if not PYAUTOGUI_AVAILABLE and not PYNPUT_AVAILABLE:
                raise RuntimeError("No mouse control libraries available (pyautogui or pynput required)")
            
            # Get screen size
            if PYAUTOGUI_AVAILABLE:
                self.screen_width, self.screen_height = pyautogui.size()
            else:
                # Default screen size if pyautogui not available
                self.screen_width, self.screen_height = 1920, 1080
            
            # Update safe zone
            self.safe_zone.update({
                'max_x': self.screen_width,
                'max_y': self.screen_height
            })
            
            # Get current mouse position
            if PYAUTOGUI_AVAILABLE:
                x, y = pyautogui.position()
                self.current_position = MousePosition(x, y, time.time())
            
            self.initialized = True
            self.logger.info("✅ Mouse controller initialized successfully")
            self.logger.info(f"🖥️ Screen size: {self.screen_width}x{self.screen_height}")
            self.logger.info(f"🖱️ Current position: ({self.current_position.x}, {self.current_position.y})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Mouse controller initialization failed: {e}")
            return False
    
    def execute_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a mouse action
        
        Args:
            parameters: Action parameters
            
        Returns:
            Dict containing action result
        """
        if not self.initialized:
            raise RuntimeError("Mouse controller not initialized")
        
        action_type = parameters.get('action_type')
        if not action_type:
            raise ValueError("Action type is required")
        
        with self.action_lock:
            try:
                if action_type == 'move':
                    return self._move_mouse(parameters)
                elif action_type == 'click':
                    return self._click_mouse(parameters)
                elif action_type == 'drag':
                    return self._drag_mouse(parameters)
                elif action_type == 'scroll':
                    return self._scroll_mouse(parameters)
                elif action_type == 'get_position':
                    return self._get_position()
                else:
                    raise ValueError(f"Unknown action type: {action_type}")
                    
            except Exception as e:
                self.errors_encountered += 1
                self.logger.error(f"❌ Mouse action failed: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'action_type': action_type
                }
    
    def _move_mouse(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Move mouse to specified position"""
        x = parameters.get('x')
        y = parameters.get('y')
        movement_type = MovementType(parameters.get('movement_type', 'linear'))
        duration = parameters.get('duration', self.default_duration)
        
        if x is None or y is None:
            raise ValueError("X and Y coordinates are required for mouse movement")
        
        # Validate and adjust coordinates
        x, y = self._validate_coordinates(x, y)
        
        start_time = time.time()
        start_x, start_y = self.current_position.x, self.current_position.y
        
        self.logger.info(f"🖱️ Moving mouse: ({start_x}, {start_y}) → ({x}, {y})")
        
        try:
            if movement_type == MovementType.INSTANT:
                self._move_instant(x, y)
            elif movement_type == MovementType.LINEAR:
                self._move_linear(x, y, duration)
            elif movement_type == MovementType.SMOOTH:
                self._move_smooth(x, y, duration)
            elif movement_type == MovementType.BEZIER:
                self._move_bezier(x, y, duration)
            
            # Update current position
            self.current_position = MousePosition(x, y, time.time())
            self.movements_performed += 1
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'action_type': 'move',
                'start_position': (start_x, start_y),
                'end_position': (x, y),
                'movement_type': movement_type.value,
                'execution_time': execution_time,
                'distance': math.sqrt((x - start_x)**2 + (y - start_y)**2)
            }
            
        except Exception as e:
            raise RuntimeError(f"Mouse movement failed: {e}")
    
    def _click_mouse(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Click mouse at specified position"""
        x = parameters.get('x', self.current_position.x)
        y = parameters.get('y', self.current_position.y)
        button = MouseButton(parameters.get('button', 'left'))
        click_type = ClickType(parameters.get('click_type', 'single'))
        
        # Validate coordinates
        x, y = self._validate_coordinates(x, y)
        
        start_time = time.time()
        
        self.logger.info(f"🖱️ Clicking {button.value} button at ({x}, {y}) - {click_type.value}")
        
        try:
            # Move to position if needed
            if x != self.current_position.x or y != self.current_position.y:
                self._move_instant(x, y)
                self.current_position = MousePosition(x, y, time.time())
            
            # Perform click
            if PYAUTOGUI_AVAILABLE:
                if click_type == ClickType.SINGLE:
                    pyautogui.click(x, y, button=button.value)
                elif click_type == ClickType.DOUBLE:
                    pyautogui.doubleClick(x, y, button=button.value)
                elif click_type == ClickType.TRIPLE:
                    pyautogui.tripleClick(x, y, button=button.value)
                elif click_type == ClickType.HOLD:
                    pyautogui.mouseDown(x, y, button=button.value)
                elif click_type == ClickType.RELEASE:
                    pyautogui.mouseUp(x, y, button=button.value)
            elif PYNPUT_AVAILABLE:
                mouse_controller = mouse.Controller()
                mouse_controller.position = (x, y)
                
                if button == MouseButton.LEFT:
                    pynput_button = Button.left
                elif button == MouseButton.RIGHT:
                    pynput_button = Button.right
                elif button == MouseButton.MIDDLE:
                    pynput_button = Button.middle
                else:
                    raise ValueError(f"Unsupported button: {button}")
                
                if click_type == ClickType.SINGLE:
                    mouse_controller.click(pynput_button)
                elif click_type == ClickType.DOUBLE:
                    mouse_controller.click(pynput_button, 2)
                elif click_type == ClickType.HOLD:
                    mouse_controller.press(pynput_button)
                elif click_type == ClickType.RELEASE:
                    mouse_controller.release(pynput_button)
            
            self.clicks_performed += 1
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'action_type': 'click',
                'position': (x, y),
                'button': button.value,
                'click_type': click_type.value,
                'execution_time': execution_time
            }
            
        except Exception as e:
            raise RuntimeError(f"Mouse click failed: {e}")
    
    def _drag_mouse(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Drag mouse from start to end position"""
        start_x = parameters.get('start_x', self.current_position.x)
        start_y = parameters.get('start_y', self.current_position.y)
        end_x = parameters.get('end_x')
        end_y = parameters.get('end_y')
        button = MouseButton(parameters.get('button', 'left'))
        duration = parameters.get('duration', self.default_duration)
        
        if end_x is None or end_y is None:
            raise ValueError("End coordinates are required for drag operation")
        
        # Validate coordinates
        start_x, start_y = self._validate_coordinates(start_x, start_y)
        end_x, end_y = self._validate_coordinates(end_x, end_y)
        
        start_time = time.time()
        
        self.logger.info(f"🖱️ Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        
        try:
            if PYAUTOGUI_AVAILABLE:
                pyautogui.drag(end_x - start_x, end_y - start_y, duration, button=button.value)
            elif PYNPUT_AVAILABLE:
                mouse_controller = mouse.Controller()
                
                # Move to start position
                mouse_controller.position = (start_x, start_y)
                
                # Press button
                if button == MouseButton.LEFT:
                    pynput_button = Button.left
                elif button == MouseButton.RIGHT:
                    pynput_button = Button.right
                else:
                    raise ValueError(f"Unsupported drag button: {button}")
                
                mouse_controller.press(pynput_button)
                
                # Drag to end position
                steps = max(10, int(duration * 100))
                for i in range(steps):
                    progress = i / steps
                    current_x = start_x + (end_x - start_x) * progress
                    current_y = start_y + (end_y - start_y) * progress
                    mouse_controller.position = (current_x, current_y)
                    time.sleep(duration / steps)
                
                # Release button
                mouse_controller.release(pynput_button)
            
            # Update position
            self.current_position = MousePosition(end_x, end_y, time.time())
            self.drags_performed += 1
            
            execution_time = time.time() - start_time
            distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
            
            return {
                'success': True,
                'action_type': 'drag',
                'start_position': (start_x, start_y),
                'end_position': (end_x, end_y),
                'button': button.value,
                'execution_time': execution_time,
                'distance': distance
            }
            
        except Exception as e:
            raise RuntimeError(f"Mouse drag failed: {e}")
    
    def _scroll_mouse(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Scroll mouse wheel"""
        x = parameters.get('x', self.current_position.x)
        y = parameters.get('y', self.current_position.y)
        scroll_amount = parameters.get('scroll_amount', 1)
        direction = parameters.get('direction', 'up')  # 'up' or 'down'
        
        # Validate coordinates
        x, y = self._validate_coordinates(x, y)
        
        start_time = time.time()
        
        self.logger.info(f"🖱️ Scrolling {direction} at ({x}, {y}) - amount: {scroll_amount}")
        
        try:
            # Move to position if needed
            if x != self.current_position.x or y != self.current_position.y:
                self._move_instant(x, y)
                self.current_position = MousePosition(x, y, time.time())
            
            # Perform scroll
            if PYAUTOGUI_AVAILABLE:
                scroll_value = scroll_amount if direction == 'up' else -scroll_amount
                pyautogui.scroll(scroll_value, x, y)
            elif PYNPUT_AVAILABLE:
                mouse_controller = mouse.Controller()
                mouse_controller.position = (x, y)
                
                scroll_value = scroll_amount if direction == 'up' else -scroll_amount
                mouse_controller.scroll(0, scroll_value)
            
            self.scrolls_performed += 1
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'action_type': 'scroll',
                'position': (x, y),
                'direction': direction,
                'scroll_amount': scroll_amount,
                'execution_time': execution_time
            }
            
        except Exception as e:
            raise RuntimeError(f"Mouse scroll failed: {e}")
    
    def _get_position(self) -> Dict[str, Any]:
        """Get current mouse position"""
        try:
            if PYAUTOGUI_AVAILABLE:
                x, y = pyautogui.position()
                self.current_position = MousePosition(x, y, time.time())
            
            return {
                'success': True,
                'action_type': 'get_position',
                'position': (self.current_position.x, self.current_position.y),
                'timestamp': self.current_position.timestamp
            }
            
        except Exception as e:
            raise RuntimeError(f"Get position failed: {e}")
    
    def _validate_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """Validate and adjust coordinates within safe boundaries"""
        x = int(x)
        y = int(y)
        
        if self.safety_enabled:
            x = max(self.safe_zone['min_x'], min(x, self.safe_zone['max_x'] - 1))
            y = max(self.safe_zone['min_y'], min(y, self.safe_zone['max_y'] - 1))
        
        return x, y
    
    def _move_instant(self, x: int, y: int):
        """Move mouse instantly to position"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.moveTo(x, y)
        elif PYNPUT_AVAILABLE:
            mouse_controller = mouse.Controller()
            mouse_controller.position = (x, y)
    
    def _move_linear(self, x: int, y: int, duration: float):
        """Move mouse linearly to position"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.moveTo(x, y, duration)
        else:
            self._move_smooth(x, y, duration)
    
    def _move_smooth(self, x: int, y: int, duration: float):
        """Move mouse smoothly to position"""
        if PYNPUT_AVAILABLE:
            mouse_controller = mouse.Controller()
            start_x, start_y = self.current_position.x, self.current_position.y
            
            steps = max(10, int(duration * 100))
            for i in range(steps):
                progress = i / steps
                # Ease-in-out function for smooth movement
                smooth_progress = 0.5 * (1 - math.cos(progress * math.pi))
                
                current_x = start_x + (x - start_x) * smooth_progress
                current_y = start_y + (y - start_y) * smooth_progress
                
                mouse_controller.position = (current_x, current_y)
                time.sleep(duration / steps)
        else:
            self._move_linear(x, y, duration)
    
    def _move_bezier(self, x: int, y: int, duration: float):
        """Move mouse using bezier curve"""
        start_x, start_y = self.current_position.x, self.current_position.y
        
        # Create control points for bezier curve
        mid_x = (start_x + x) / 2 + (y - start_y) * 0.2
        mid_y = (start_y + y) / 2 + (x - start_x) * 0.2
        
        if PYNPUT_AVAILABLE:
            mouse_controller = mouse.Controller()
            
            steps = max(20, int(duration * 100))
            for i in range(steps):
                t = i / steps
                
                # Quadratic bezier curve
                bezier_x = (1-t)**2 * start_x + 2*(1-t)*t * mid_x + t**2 * x
                bezier_y = (1-t)**2 * start_y + 2*(1-t)*t * mid_y + t**2 * y
                
                mouse_controller.position = (bezier_x, bezier_y)
                time.sleep(duration / steps)
        else:
            self._move_smooth(x, y, duration)
    
    def is_ready(self) -> bool:
        """Check if mouse controller is ready"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get mouse controller status"""
        return {
            'initialized': self.initialized,
            'current_position': (self.current_position.x, self.current_position.y),
            'screen_size': (self.screen_width, self.screen_height),
            'movements_performed': self.movements_performed,
            'clicks_performed': self.clicks_performed,
            'drags_performed': self.drags_performed,
            'scrolls_performed': self.scrolls_performed,
            'errors_encountered': self.errors_encountered,
            'safety_enabled': self.safety_enabled,
            'libraries_available': {
                'pyautogui': PYAUTOGUI_AVAILABLE,
                'pynput': PYNPUT_AVAILABLE
            }
        }
    
    def shutdown(self):
        """Shutdown mouse controller"""
        self.logger.info("🛑 Shutting down mouse controller")
        self.initialized = False
        self.logger.info("✅ Mouse controller shutdown complete")
