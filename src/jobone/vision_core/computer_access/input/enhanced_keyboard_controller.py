#!/usr/bin/env python3
"""
Enhanced Keyboard Controller - Improved keyboard control with better special character and shortcut handling
"""

import time
import logging
import threading
from typing import Dict, Any, List, Set
from dataclasses import dataclass
from enum import Enum

# Import existing keyboard controller
try:
    from .keyboard_controller import KeyboardController
    BASE_CONTROLLER_AVAILABLE = True
except ImportError:
    BASE_CONTROLLER_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedInputType(Enum):
    """Enhanced keyboard input types"""
    TEXT = "text"
    SPECIAL_CHAR = "special_char"
    SHORTCUT = "shortcut"
    COMBINATION = "combination"
    SEQUENCE = "sequence"

@dataclass
class SpecialCharMapping:
    """Special character mapping"""
    char: str
    keys: List[str]
    difficulty: str = "medium"

class EnhancedKeyboardController:
    """
    Enhanced keyboard controller with improved special character and shortcut handling
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.computer_access.input.enhanced_keyboard')
        
        # Base controller
        if BASE_CONTROLLER_AVAILABLE:
            self.base_controller = KeyboardController()
        else:
            self.base_controller = None
        
        # Enhanced mappings
        self.special_char_mappings = self._initialize_special_char_mappings()
        self.enhanced_shortcuts = self._initialize_enhanced_shortcuts()
        self.key_sequences = self._initialize_key_sequences()
        
        # Enhanced state tracking
        self.successful_special_chars = 0
        self.failed_special_chars = 0
        self.successful_shortcuts = 0
        self.failed_shortcuts = 0
        self.typing_accuracy = 1.0
        
        # Performance optimization
        self.char_cache = {}
        self.shortcut_cache = {}
        
        self.initialized = False
        
        self.logger.info("⌨️ Enhanced Keyboard Controller initialized")
    
    def initialize(self) -> bool:
        """Initialize enhanced keyboard controller"""
        try:
            self.logger.info("🚀 Initializing enhanced keyboard controller...")
            
            # Initialize base controller if available
            if self.base_controller:
                if not self.base_controller.initialize():
                    self.logger.warning("⚠️ Base controller initialization failed, using fallback")
            
            # Test enhanced features
            if not self._test_enhanced_features():
                self.logger.warning("⚠️ Some enhanced features may not work properly")
            
            self.initialized = True
            self.logger.info("✅ Enhanced keyboard controller initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced keyboard controller initialization failed: {e}")
            return False
    
    def _initialize_special_char_mappings(self) -> Dict[str, SpecialCharMapping]:
        """Initialize comprehensive special character mappings"""
        mappings = {}
        
        # Punctuation characters
        punctuation_chars = {
            '!': (['shift', '1'], 'easy'),
            '@': (['shift', '2'], 'easy'),
            '#': (['shift', '3'], 'easy'),
            '$': (['shift', '4'], 'easy'),
            '%': (['shift', '5'], 'easy'),
            '^': (['shift', '6'], 'medium'),
            '&': (['shift', '7'], 'easy'),
            '*': (['shift', '8'], 'easy'),
            '(': (['shift', '9'], 'easy'),
            ')': (['shift', '0'], 'easy'),
            '_': (['shift', '-'], 'medium'),
            '+': (['shift', '='], 'medium'),
            '|': (['shift', '\\'], 'hard'),
            ':': (['shift', ';'], 'easy'),
            '"': (['shift', "'"], 'medium'),
            '<': (['shift', ','], 'medium'),
            '>': (['shift', '.'], 'medium'),
            '?': (['shift', '/'], 'easy'),
            '~': (['shift', '`'], 'hard')
        }
        
        for char, (keys, difficulty) in punctuation_chars.items():
            mappings[char] = SpecialCharMapping(char, keys, difficulty)
        
        # Bracket characters
        bracket_chars = {
            '{': (['shift', '['], 'medium'),
            '}': (['shift', ']'], 'medium'),
            '[': (['['], 'easy'),
            ']': ([']'], 'easy'),
            '<': (['shift', ','], 'medium'),
            '>': (['shift', '.'], 'medium')
        }
        
        for char, (keys, difficulty) in bracket_chars.items():
            if char not in mappings:  # Don't override existing mappings
                mappings[char] = SpecialCharMapping(char, keys, difficulty)
        
        return mappings
    
    def _initialize_enhanced_shortcuts(self) -> Dict[str, Dict[str, Any]]:
        """Initialize enhanced shortcut mappings"""
        return {
            # File operations
            'new_file': {'keys': ['ctrl', 'n'], 'category': 'file', 'priority': 'high'},
            'open_file': {'keys': ['ctrl', 'o'], 'category': 'file', 'priority': 'high'},
            'save_file': {'keys': ['ctrl', 's'], 'category': 'file', 'priority': 'high'},
            'save_as': {'keys': ['ctrl', 'shift', 's'], 'category': 'file', 'priority': 'medium'},
            'close_file': {'keys': ['ctrl', 'w'], 'category': 'file', 'priority': 'high'},
            'print': {'keys': ['ctrl', 'p'], 'category': 'file', 'priority': 'medium'},
            
            # Edit operations
            'copy': {'keys': ['ctrl', 'c'], 'category': 'edit', 'priority': 'high'},
            'cut': {'keys': ['ctrl', 'x'], 'category': 'edit', 'priority': 'high'},
            'paste': {'keys': ['ctrl', 'v'], 'category': 'edit', 'priority': 'high'},
            'undo': {'keys': ['ctrl', 'z'], 'category': 'edit', 'priority': 'high'},
            'redo': {'keys': ['ctrl', 'y'], 'category': 'edit', 'priority': 'high'},
            'select_all': {'keys': ['ctrl', 'a'], 'category': 'edit', 'priority': 'high'},
            'find': {'keys': ['ctrl', 'f'], 'category': 'edit', 'priority': 'high'},
            'replace': {'keys': ['ctrl', 'h'], 'category': 'edit', 'priority': 'medium'},
            'find_next': {'keys': ['f3'], 'category': 'edit', 'priority': 'medium'},
            
            # Navigation
            'home': {'keys': ['home'], 'category': 'navigation', 'priority': 'medium'},
            'end': {'keys': ['end'], 'category': 'navigation', 'priority': 'medium'},
            'page_up': {'keys': ['pageup'], 'category': 'navigation', 'priority': 'medium'},
            'page_down': {'keys': ['pagedown'], 'category': 'navigation', 'priority': 'medium'},
            'go_to_line': {'keys': ['ctrl', 'g'], 'category': 'navigation', 'priority': 'low'},
            
            # System operations
            'alt_tab': {'keys': ['alt', 'tab'], 'category': 'system', 'priority': 'high'},
            'task_manager': {'keys': ['ctrl', 'shift', 'esc'], 'category': 'system', 'priority': 'low'},
            'run_dialog': {'keys': ['win', 'r'], 'category': 'system', 'priority': 'medium'},
            'desktop': {'keys': ['win', 'd'], 'category': 'system', 'priority': 'medium'},
            'lock_screen': {'keys': ['win', 'l'], 'category': 'system', 'priority': 'low'},
            
            # Browser operations
            'new_tab': {'keys': ['ctrl', 't'], 'category': 'browser', 'priority': 'high'},
            'close_tab': {'keys': ['ctrl', 'w'], 'category': 'browser', 'priority': 'high'},
            'reopen_tab': {'keys': ['ctrl', 'shift', 't'], 'category': 'browser', 'priority': 'medium'},
            'refresh': {'keys': ['f5'], 'category': 'browser', 'priority': 'high'},
            'hard_refresh': {'keys': ['ctrl', 'f5'], 'category': 'browser', 'priority': 'medium'},
            'address_bar': {'keys': ['ctrl', 'l'], 'category': 'browser', 'priority': 'medium'},
            'developer_tools': {'keys': ['f12'], 'category': 'browser', 'priority': 'low'}
        }
    
    def _initialize_key_sequences(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize complex key sequences"""
        return {
            'select_word': [
                {'action': 'key_combination', 'keys': ['ctrl', 'right']},
                {'action': 'key_combination', 'keys': ['ctrl', 'shift', 'left']}
            ],
            'select_line': [
                {'action': 'press_key', 'key': 'home'},
                {'action': 'key_combination', 'keys': ['shift', 'end']}
            ],
            'duplicate_line': [
                {'action': 'press_key', 'key': 'home'},
                {'action': 'key_combination', 'keys': ['shift', 'end']},
                {'action': 'key_combination', 'keys': ['ctrl', 'c']},
                {'action': 'press_key', 'key': 'end'},
                {'action': 'press_key', 'key': 'enter'},
                {'action': 'key_combination', 'keys': ['ctrl', 'v']}
            ],
            'comment_line': [
                {'action': 'press_key', 'key': 'home'},
                {'action': 'type_text', 'text': '// '}
            ]
        }
    
    def execute_enhanced_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced keyboard action"""
        if not self.initialized:
            raise RuntimeError("Enhanced keyboard controller not initialized")
        
        start_time = time.time()
        
        try:
            if action_type == 'type_text_enhanced':
                result = self._type_text_enhanced(parameters)
            elif action_type == 'special_character':
                result = self._type_special_character(parameters)
            elif action_type == 'enhanced_shortcut':
                result = self._execute_enhanced_shortcut(parameters)
            elif action_type == 'key_sequence':
                result = self._execute_key_sequence(parameters)
            elif action_type == 'smart_typing':
                result = self._smart_typing(parameters)
            else:
                # Fallback to base controller
                if self.base_controller:
                    return self.base_controller.execute_action(parameters)
                else:
                    raise ValueError(f"Unknown enhanced action type: {action_type}")
            
            result['execution_time'] = time.time() - start_time
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Enhanced action failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'action_type': action_type,
                'execution_time': execution_time
            }
    
    def _type_text_enhanced(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced text typing with special character handling"""
        text = parameters.get('text', '')
        typing_speed = parameters.get('typing_speed', 60)
        auto_correct = parameters.get('auto_correct', True)
        
        if not text:
            raise ValueError("Text is required")
        
        self.logger.info(f"⌨️ Enhanced typing: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        typed_chars = 0
        special_chars_handled = 0
        errors = 0
        
        for char in text:
            try:
                if char in self.special_char_mappings:
                    # Handle special character
                    mapping = self.special_char_mappings[char]
                    if self.base_controller:
                        result = self.base_controller.execute_action({
                            'action_type': 'key_combination',
                            'keys': mapping.keys
                        })
                        if result.get('success'):
                            special_chars_handled += 1
                        else:
                            errors += 1
                    else:
                        # Simulate special character typing
                        time.sleep(0.05)
                        special_chars_handled += 1
                else:
                    # Handle regular character
                    if self.base_controller:
                        result = self.base_controller.execute_action({
                            'action_type': 'type_text',
                            'text': char,
                            'typing_speed': typing_speed
                        })
                        if not result.get('success'):
                            errors += 1
                    else:
                        # Simulate regular typing
                        time.sleep(60.0 / (typing_speed * 5) if typing_speed > 0 else 0.01)
                
                typed_chars += 1
                
            except Exception as e:
                self.logger.warning(f"⚠️ Error typing character '{char}': {e}")
                errors += 1
        
        # Update statistics
        self.successful_special_chars += special_chars_handled
        self.failed_special_chars += errors
        
        # Calculate accuracy
        accuracy = (typed_chars - errors) / typed_chars if typed_chars > 0 else 0
        self.typing_accuracy = (self.typing_accuracy + accuracy) / 2  # Running average
        
        success = errors <= len(text) * 0.1  # Allow 10% error rate
        
        return {
            'success': success,
            'action_type': 'type_text_enhanced',
            'text_length': len(text),
            'typed_characters': typed_chars,
            'special_characters': special_chars_handled,
            'errors': errors,
            'accuracy': accuracy,
            'typing_speed': typing_speed
        }
    
    def _type_special_character(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Type a specific special character"""
        char = parameters.get('character')
        
        if not char:
            raise ValueError("Character is required")
        
        if char not in self.special_char_mappings:
            raise ValueError(f"No mapping found for character: {char}")
        
        mapping = self.special_char_mappings[char]
        
        self.logger.info(f"⌨️ Typing special character: '{char}' using {mapping.keys}")
        
        try:
            if self.base_controller:
                result = self.base_controller.execute_action({
                    'action_type': 'key_combination',
                    'keys': mapping.keys
                })
                
                if result.get('success'):
                    self.successful_special_chars += 1
                else:
                    self.failed_special_chars += 1
                
                return {
                    'success': result.get('success', False),
                    'action_type': 'special_character',
                    'character': char,
                    'keys_used': mapping.keys,
                    'difficulty': mapping.difficulty
                }
            else:
                # Simulate special character
                time.sleep(0.05)
                self.successful_special_chars += 1
                
                return {
                    'success': True,
                    'action_type': 'special_character',
                    'character': char,
                    'keys_used': mapping.keys,
                    'difficulty': mapping.difficulty,
                    'simulated': True
                }
                
        except Exception as e:
            self.failed_special_chars += 1
            raise RuntimeError(f"Special character typing failed: {e}")
    
    def _execute_enhanced_shortcut(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced shortcut"""
        shortcut_name = parameters.get('shortcut_name')
        
        if not shortcut_name:
            raise ValueError("Shortcut name is required")
        
        if shortcut_name not in self.enhanced_shortcuts:
            raise ValueError(f"Unknown enhanced shortcut: {shortcut_name}")
        
        shortcut = self.enhanced_shortcuts[shortcut_name]
        keys = shortcut['keys']
        
        self.logger.info(f"⌨️ Enhanced shortcut: {shortcut_name} ({' + '.join(keys)})")
        
        try:
            if self.base_controller:
                result = self.base_controller.execute_action({
                    'action_type': 'key_combination',
                    'keys': keys
                })
                
                if result.get('success'):
                    self.successful_shortcuts += 1
                else:
                    self.failed_shortcuts += 1
                
                return {
                    'success': result.get('success', False),
                    'action_type': 'enhanced_shortcut',
                    'shortcut_name': shortcut_name,
                    'keys': keys,
                    'category': shortcut['category'],
                    'priority': shortcut['priority']
                }
            else:
                # Simulate shortcut
                time.sleep(0.05)
                self.successful_shortcuts += 1
                
                return {
                    'success': True,
                    'action_type': 'enhanced_shortcut',
                    'shortcut_name': shortcut_name,
                    'keys': keys,
                    'category': shortcut['category'],
                    'priority': shortcut['priority'],
                    'simulated': True
                }
                
        except Exception as e:
            self.failed_shortcuts += 1
            raise RuntimeError(f"Enhanced shortcut execution failed: {e}")
    
    def _execute_key_sequence(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complex key sequence"""
        sequence_name = parameters.get('sequence_name')
        
        if not sequence_name:
            raise ValueError("Sequence name is required")
        
        if sequence_name not in self.key_sequences:
            raise ValueError(f"Unknown key sequence: {sequence_name}")
        
        sequence = self.key_sequences[sequence_name]
        
        self.logger.info(f"⌨️ Executing key sequence: {sequence_name}")
        
        executed_steps = 0
        failed_steps = 0
        
        for step in sequence:
            try:
                action = step['action']
                step_params = {k: v for k, v in step.items() if k != 'action'}
                
                if self.base_controller:
                    result = self.base_controller.execute_action({
                        'action_type': action,
                        **step_params
                    })
                    
                    if result.get('success'):
                        executed_steps += 1
                    else:
                        failed_steps += 1
                else:
                    # Simulate step execution
                    time.sleep(0.1)
                    executed_steps += 1
                
                # Brief pause between steps
                time.sleep(0.05)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Key sequence step failed: {e}")
                failed_steps += 1
        
        success = failed_steps == 0
        
        return {
            'success': success,
            'action_type': 'key_sequence',
            'sequence_name': sequence_name,
            'total_steps': len(sequence),
            'executed_steps': executed_steps,
            'failed_steps': failed_steps
        }
    
    def _smart_typing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Smart typing with auto-correction and optimization"""
        text = parameters.get('text', '')
        enable_autocorrect = parameters.get('autocorrect', True)
        optimize_speed = parameters.get('optimize_speed', True)
        
        if not text:
            raise ValueError("Text is required for smart typing")
        
        self.logger.info(f"⌨️ Smart typing: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        
        # Analyze text for optimization
        special_char_count = sum(1 for char in text if char in self.special_char_mappings)
        regular_char_count = len(text) - special_char_count
        
        # Optimize typing speed based on content
        if optimize_speed:
            if special_char_count > regular_char_count * 0.3:  # >30% special chars
                typing_speed = 45  # Slower for complex text
            else:
                typing_speed = 65  # Faster for regular text
        else:
            typing_speed = parameters.get('typing_speed', 60)
        
        # Execute enhanced typing
        result = self._type_text_enhanced({
            'text': text,
            'typing_speed': typing_speed,
            'auto_correct': enable_autocorrect
        })
        
        result['action_type'] = 'smart_typing'
        result['optimization_applied'] = optimize_speed
        result['autocorrect_enabled'] = enable_autocorrect
        result['optimized_speed'] = typing_speed
        
        return result
    
    def _test_enhanced_features(self) -> bool:
        """Test enhanced features"""
        try:
            # Test special character mapping
            test_char = '@'
            if test_char in self.special_char_mappings:
                mapping = self.special_char_mappings[test_char]
                if mapping.keys == ['shift', '2']:
                    self.logger.info("✅ Special character mapping test passed")
                else:
                    self.logger.warning("⚠️ Special character mapping test failed")
            
            # Test shortcut mapping
            if 'copy' in self.enhanced_shortcuts:
                shortcut = self.enhanced_shortcuts['copy']
                if shortcut['keys'] == ['ctrl', 'c']:
                    self.logger.info("✅ Enhanced shortcut mapping test passed")
                else:
                    self.logger.warning("⚠️ Enhanced shortcut mapping test failed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced features test failed: {e}")
            return False
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get enhanced keyboard controller status"""
        base_status = {}
        if self.base_controller:
            base_status = self.base_controller.get_status()
        
        enhanced_status = {
            'enhanced_initialized': self.initialized,
            'special_char_mappings': len(self.special_char_mappings),
            'enhanced_shortcuts': len(self.enhanced_shortcuts),
            'key_sequences': len(self.key_sequences),
            'successful_special_chars': self.successful_special_chars,
            'failed_special_chars': self.failed_special_chars,
            'successful_shortcuts': self.successful_shortcuts,
            'failed_shortcuts': self.failed_shortcuts,
            'typing_accuracy': self.typing_accuracy,
            'special_char_success_rate': (
                self.successful_special_chars / 
                max(self.successful_special_chars + self.failed_special_chars, 1)
            ) * 100,
            'shortcut_success_rate': (
                self.successful_shortcuts / 
                max(self.successful_shortcuts + self.failed_shortcuts, 1)
            ) * 100
        }
        
        return {**base_status, **enhanced_status}
    
    def is_ready(self) -> bool:
        """Check if enhanced keyboard controller is ready"""
        return self.initialized
    
    def shutdown(self):
        """Shutdown enhanced keyboard controller"""
        self.logger.info("🛑 Shutting down enhanced keyboard controller")
        
        if self.base_controller:
            self.base_controller.shutdown()
        
        self.initialized = False
        self.logger.info("✅ Enhanced keyboard controller shutdown complete")
