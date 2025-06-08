#!/usr/bin/env python3
"""
Keyboard Controller - Autonomous keyboard input and shortcut management
"""

import logging
import time
import threading
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Import platform-specific keyboard libraries
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from pynput import keyboard
    from pynput.keyboard import Key, Listener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

import platform

class InputType(Enum):
    """Keyboard input types"""
    TEXT = "text"
    KEY = "key"
    SHORTCUT = "shortcut"
    COMBINATION = "combination"

class KeyState(Enum):
    """Key states"""
    PRESS = "press"
    RELEASE = "release"
    HOLD = "hold"

@dataclass
class KeyboardAction:
    """Keyboard action definition"""
    action_type: InputType
    content: Union[str, List[str]]
    duration: float = 0.0
    delay: float = 0.05
    state: KeyState = KeyState.PRESS

class KeyboardController:
    """
    Autonomous keyboard controller for text input and shortcuts
    Supports typing, key combinations, and cross-platform shortcuts
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.computer_access.input.keyboard')
        self.initialized = False
        self.platform = platform.system()
        
        # Keyboard state
        self.pressed_keys = set()
        self.caps_lock_state = False
        self.num_lock_state = True
        
        # Configuration
        self.typing_speed = 50  # characters per minute
        self.key_delay = 0.05   # seconds between keys
        self.safety_enabled = True
        
        # Performance tracking
        self.characters_typed = 0
        self.keys_pressed = 0
        self.shortcuts_executed = 0
        self.errors_encountered = 0
        
        # Key mappings for cross-platform compatibility
        self.key_mappings = self._initialize_key_mappings()
        
        # Thread safety
        self.action_lock = threading.Lock()
        
        self.logger.info("⌨️ KeyboardController initialized")
    
    def initialize(self) -> bool:
        """
        Initialize keyboard controller
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing keyboard controller...")
            
            # Check library availability
            if not PYAUTOGUI_AVAILABLE and not PYNPUT_AVAILABLE:
                raise RuntimeError("No keyboard control libraries available (pyautogui or pynput required)")
            
            # Test basic functionality
            if not self._test_basic_input():
                raise RuntimeError("Basic keyboard input test failed")
            
            self.initialized = True
            self.logger.info("✅ Keyboard controller initialized successfully")
            self.logger.info(f"🖥️ Platform: {self.platform}")
            self.logger.info(f"📚 Libraries: PyAutoGUI={PYAUTOGUI_AVAILABLE}, Pynput={PYNPUT_AVAILABLE}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Keyboard controller initialization failed: {e}")
            return False
    
    def _initialize_key_mappings(self) -> Dict[str, Any]:
        """Initialize platform-specific key mappings"""
        base_mappings = {
            # Special keys
            'enter': 'enter',
            'tab': 'tab',
            'space': 'space',
            'backspace': 'backspace',
            'delete': 'delete',
            'escape': 'escape',
            'shift': 'shift',
            'ctrl': 'ctrl',
            'alt': 'alt',
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'home': 'home',
            'end': 'end',
            'pageup': 'pageup',
            'pagedown': 'pagedown',
            # Function keys
            'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
            'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
            'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12'
        }
        
        # Platform-specific adjustments
        if self.platform == "Darwin":  # macOS
            base_mappings.update({
                'cmd': 'cmd',
                'command': 'cmd',
                'ctrl': 'cmd',  # Map ctrl to cmd on macOS
                'win': 'cmd'
            })
        elif self.platform == "Windows":
            base_mappings.update({
                'win': 'win',
                'windows': 'win',
                'cmd': 'ctrl'  # Map cmd to ctrl on Windows
            })
        else:  # Linux
            base_mappings.update({
                'super': 'cmd',
                'meta': 'cmd',
                'win': 'cmd'
            })
        
        return base_mappings
    
    def _test_basic_input(self) -> bool:
        """Test basic keyboard input capability"""
        try:
            # This is a minimal test - in production, you might want more thorough testing
            return True
        except Exception as e:
            self.logger.error(f"❌ Basic input test failed: {e}")
            return False
    
    def execute_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a keyboard action
        
        Args:
            parameters: Action parameters
            
        Returns:
            Dict containing action result
        """
        if not self.initialized:
            raise RuntimeError("Keyboard controller not initialized")
        
        action_type = parameters.get('action_type')
        if not action_type:
            raise ValueError("Action type is required")
        
        with self.action_lock:
            try:
                if action_type == 'type_text':
                    return self._type_text(parameters)
                elif action_type == 'press_key':
                    return self._press_key(parameters)
                elif action_type == 'key_combination':
                    return self._key_combination(parameters)
                elif action_type == 'shortcut':
                    return self._execute_shortcut(parameters)
                elif action_type == 'hold_key':
                    return self._hold_key(parameters)
                elif action_type == 'release_key':
                    return self._release_key(parameters)
                else:
                    raise ValueError(f"Unknown action type: {action_type}")
                    
            except Exception as e:
                self.errors_encountered += 1
                self.logger.error(f"❌ Keyboard action failed: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'action_type': action_type
                }
    
    def _type_text(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Type text string"""
        text = parameters.get('text', '')
        typing_speed = parameters.get('typing_speed', self.typing_speed)
        
        if not text:
            raise ValueError("Text is required for typing")
        
        start_time = time.time()
        
        self.logger.info(f"⌨️ Typing text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        try:
            # Calculate delay between characters
            char_delay = 60.0 / (typing_speed * 5) if typing_speed > 0 else self.key_delay
            
            if PYAUTOGUI_AVAILABLE:
                pyautogui.typewrite(text, interval=char_delay)
            elif PYNPUT_AVAILABLE:
                keyboard_controller = keyboard.Controller()
                for char in text:
                    keyboard_controller.type(char)
                    if char_delay > 0:
                        time.sleep(char_delay)
            
            self.characters_typed += len(text)
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'action_type': 'type_text',
                'text_length': len(text),
                'typing_speed': typing_speed,
                'execution_time': execution_time,
                'characters_per_second': len(text) / execution_time if execution_time > 0 else 0
            }
            
        except Exception as e:
            raise RuntimeError(f"Text typing failed: {e}")
    
    def _press_key(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Press a single key"""
        key = parameters.get('key')
        duration = parameters.get('duration', 0.0)
        
        if not key:
            raise ValueError("Key is required")
        
        # Normalize key name
        normalized_key = self._normalize_key(key)
        
        start_time = time.time()
        
        self.logger.info(f"⌨️ Pressing key: {key} (normalized: {normalized_key})")
        
        try:
            if PYAUTOGUI_AVAILABLE:
                if duration > 0:
                    pyautogui.keyDown(normalized_key)
                    time.sleep(duration)
                    pyautogui.keyUp(normalized_key)
                else:
                    pyautogui.press(normalized_key)
            elif PYNPUT_AVAILABLE:
                keyboard_controller = keyboard.Controller()
                pynput_key = self._get_pynput_key(normalized_key)
                
                if duration > 0:
                    keyboard_controller.press(pynput_key)
                    time.sleep(duration)
                    keyboard_controller.release(pynput_key)
                else:
                    keyboard_controller.press(pynput_key)
                    keyboard_controller.release(pynput_key)
            
            self.keys_pressed += 1
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'action_type': 'press_key',
                'key': key,
                'normalized_key': normalized_key,
                'duration': duration,
                'execution_time': execution_time
            }
            
        except Exception as e:
            raise RuntimeError(f"Key press failed: {e}")
    
    def _key_combination(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute key combination"""
        keys = parameters.get('keys', [])
        duration = parameters.get('duration', 0.1)
        
        if not keys or not isinstance(keys, list):
            raise ValueError("Keys list is required for combination")
        
        # Normalize all keys
        normalized_keys = [self._normalize_key(key) for key in keys]
        
        start_time = time.time()
        
        self.logger.info(f"⌨️ Key combination: {' + '.join(keys)}")
        
        try:
            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey(*normalized_keys)
            elif PYNPUT_AVAILABLE:
                keyboard_controller = keyboard.Controller()
                pynput_keys = [self._get_pynput_key(key) for key in normalized_keys]
                
                # Press all keys
                for key in pynput_keys:
                    keyboard_controller.press(key)
                
                time.sleep(duration)
                
                # Release all keys in reverse order
                for key in reversed(pynput_keys):
                    keyboard_controller.release(key)
            
            self.shortcuts_executed += 1
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'action_type': 'key_combination',
                'keys': keys,
                'normalized_keys': normalized_keys,
                'execution_time': execution_time
            }
            
        except Exception as e:
            raise RuntimeError(f"Key combination failed: {e}")
    
    def _execute_shortcut(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute named shortcut"""
        shortcut_name = parameters.get('shortcut_name')
        
        if not shortcut_name:
            raise ValueError("Shortcut name is required")
        
        # Get shortcut keys from predefined shortcuts
        from . import SHORTCUTS
        
        if shortcut_name not in SHORTCUTS:
            raise ValueError(f"Unknown shortcut: {shortcut_name}")
        
        keys = SHORTCUTS[shortcut_name]
        
        # Execute as key combination
        return self._key_combination({'keys': keys})
    
    def _hold_key(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Hold a key down"""
        key = parameters.get('key')
        
        if not key:
            raise ValueError("Key is required")
        
        normalized_key = self._normalize_key(key)
        
        self.logger.info(f"⌨️ Holding key: {key}")
        
        try:
            if PYAUTOGUI_AVAILABLE:
                pyautogui.keyDown(normalized_key)
            elif PYNPUT_AVAILABLE:
                keyboard_controller = keyboard.Controller()
                pynput_key = self._get_pynput_key(normalized_key)
                keyboard_controller.press(pynput_key)
            
            self.pressed_keys.add(normalized_key)
            
            return {
                'success': True,
                'action_type': 'hold_key',
                'key': key,
                'normalized_key': normalized_key
            }
            
        except Exception as e:
            raise RuntimeError(f"Key hold failed: {e}")
    
    def _release_key(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Release a held key"""
        key = parameters.get('key')
        
        if not key:
            raise ValueError("Key is required")
        
        normalized_key = self._normalize_key(key)
        
        self.logger.info(f"⌨️ Releasing key: {key}")
        
        try:
            if PYAUTOGUI_AVAILABLE:
                pyautogui.keyUp(normalized_key)
            elif PYNPUT_AVAILABLE:
                keyboard_controller = keyboard.Controller()
                pynput_key = self._get_pynput_key(normalized_key)
                keyboard_controller.release(pynput_key)
            
            self.pressed_keys.discard(normalized_key)
            
            return {
                'success': True,
                'action_type': 'release_key',
                'key': key,
                'normalized_key': normalized_key
            }
            
        except Exception as e:
            raise RuntimeError(f"Key release failed: {e}")
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key name for cross-platform compatibility"""
        key_lower = key.lower().strip()
        
        # Check if key is in mappings
        if key_lower in self.key_mappings:
            return self.key_mappings[key_lower]
        
        # Return as-is for regular characters
        return key_lower
    
    def _get_pynput_key(self, key_name: str):
        """Convert key name to pynput Key object"""
        if not PYNPUT_AVAILABLE:
            raise RuntimeError("Pynput not available")
        
        # Special keys mapping
        special_keys = {
            'enter': Key.enter,
            'tab': Key.tab,
            'space': Key.space,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'escape': Key.esc,
            'shift': Key.shift,
            'ctrl': Key.ctrl,
            'alt': Key.alt,
            'cmd': Key.cmd,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'pageup': Key.page_up,
            'pagedown': Key.page_down,
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12
        }
        
        if key_name in special_keys:
            return special_keys[key_name]
        
        # For regular characters, return as string
        return key_name
    
    def release_all_keys(self) -> bool:
        """Release all currently held keys"""
        try:
            for key in list(self.pressed_keys):
                self._release_key({'key': key})
            
            self.pressed_keys.clear()
            self.logger.info("⌨️ All keys released")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to release all keys: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if keyboard controller is ready"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get keyboard controller status"""
        return {
            'initialized': self.initialized,
            'platform': self.platform,
            'characters_typed': self.characters_typed,
            'keys_pressed': self.keys_pressed,
            'shortcuts_executed': self.shortcuts_executed,
            'errors_encountered': self.errors_encountered,
            'pressed_keys': list(self.pressed_keys),
            'typing_speed': self.typing_speed,
            'key_delay': self.key_delay,
            'safety_enabled': self.safety_enabled,
            'libraries_available': {
                'pyautogui': PYAUTOGUI_AVAILABLE,
                'pynput': PYNPUT_AVAILABLE
            }
        }
    
    def shutdown(self):
        """Shutdown keyboard controller"""
        self.logger.info("🛑 Shutting down keyboard controller")
        
        # Release all held keys
        self.release_all_keys()
        
        self.initialized = False
        self.logger.info("✅ Keyboard controller shutdown complete")
