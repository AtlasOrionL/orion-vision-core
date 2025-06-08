#!/usr/bin/env python3
"""
Enhanced Keyboard Controller - Main controller combining all modules
"""

import time
import logging
from typing import Dict, Any

from .typing_engine import TypingEngine
from .shortcut_engine import ShortcutEngine
from .char_map import get_char_keys, get_chars_by_difficulty
from .shortcut_map import get_basic_shortcuts, get_advanced_shortcuts

class EnhancedKeyboardController:
    """
    Enhanced keyboard controller using modular engines
    """
    
    def __init__(self):
        self.logger = logging.getLogger('enhanced_keyboard')
        
        # Initialize engines
        self.typing_engine = TypingEngine()
        self.shortcut_engine = ShortcutEngine()
        
        # Statistics
        self.stats = {
            'texts_typed': 0,
            'shortcuts_executed': 0,
            'special_chars_typed': 0,
            'total_characters': 0,
            'successful_operations': 0,
            'failed_operations': 0
        }
        
        self.initialized = False
        
    def initialize(self):
        """Initialize the enhanced controller"""
        try:
            self.logger.info("🚀 Initializing Enhanced Keyboard Controller")
            
            # Test basic functionality
            test_result = self._run_initialization_test()
            
            if test_result['success']:
                self.initialized = True
                self.logger.info("✅ Enhanced Keyboard Controller initialized successfully")
                return True
            else:
                self.logger.error(f"❌ Initialization test failed: {test_result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def _run_initialization_test(self):
        """Run basic initialization test"""
        try:
            # Test typing engine
            typing_result = self.typing_engine.type_text("test")
            if not typing_result['success']:
                return {'success': False, 'error': 'Typing engine test failed'}
            
            # Test shortcut engine
            shortcut_result = self.shortcut_engine.execute_shortcut('copy')
            if not shortcut_result['success']:
                return {'success': False, 'error': 'Shortcut engine test failed'}
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def type_text_enhanced(self, text, **options):
        """Enhanced text typing"""
        if not self.initialized:
            return {'success': False, 'error': 'Controller not initialized'}
        
        try:
            # Get optimized speed
            speed = options.get('speed', self.typing_engine.get_optimized_speed(text))
            
            # Execute typing
            result = self.typing_engine.type_text(text, speed)
            
            # Update statistics
            self.stats['texts_typed'] += 1
            self.stats['total_characters'] += result['text_length']
            self.stats['special_chars_typed'] += result['special_chars_handled']
            
            if result['success']:
                self.stats['successful_operations'] += 1
            else:
                self.stats['failed_operations'] += 1
            
            result['action_type'] = 'enhanced_typing'
            return result
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            return {'success': False, 'error': str(e), 'action_type': 'enhanced_typing'}
    
    def execute_shortcut_enhanced(self, shortcut_name):
        """Enhanced shortcut execution"""
        if not self.initialized:
            return {'success': False, 'error': 'Controller not initialized'}
        
        try:
            result = self.shortcut_engine.execute_shortcut(shortcut_name)
            
            # Update statistics
            self.stats['shortcuts_executed'] += 1
            
            if result['success']:
                self.stats['successful_operations'] += 1
            else:
                self.stats['failed_operations'] += 1
            
            result['action_type'] = 'enhanced_shortcut'
            return result
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            return {'success': False, 'error': str(e), 'action_type': 'enhanced_shortcut'}
    
    def type_special_character(self, char):
        """Type a specific special character"""
        if not self.initialized:
            return {'success': False, 'error': 'Controller not initialized'}
        
        try:
            result = self.typing_engine.type_special_char(char)
            
            # Update statistics
            if result['success']:
                self.stats['special_chars_typed'] += 1
                self.stats['successful_operations'] += 1
            else:
                self.stats['failed_operations'] += 1
            
            result['action_type'] = 'special_character'
            return result
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            return {'success': False, 'error': str(e), 'action_type': 'special_character'}
    
    def execute_key_combination(self, keys):
        """Execute custom key combination"""
        if not self.initialized:
            return {'success': False, 'error': 'Controller not initialized'}
        
        try:
            result = self.shortcut_engine.execute_key_combination(keys)
            
            # Update statistics
            if result['success']:
                self.stats['successful_operations'] += 1
            else:
                self.stats['failed_operations'] += 1
            
            result['action_type'] = 'key_combination'
            return result
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            return {'success': False, 'error': str(e), 'action_type': 'key_combination'}
    
    def get_enhanced_status(self):
        """Get enhanced controller status"""
        total_ops = self.stats['successful_operations'] + self.stats['failed_operations']
        success_rate = (self.stats['successful_operations'] / total_ops * 100) if total_ops > 0 else 0
        
        return {
            'initialized': self.initialized,
            'statistics': self.stats.copy(),
            'success_rate': success_rate,
            'typing_engine_stats': self.typing_engine.get_stats(),
            'shortcut_engine_stats': self.shortcut_engine.get_stats(),
            'available_features': {
                'enhanced_typing': True,
                'special_characters': True,
                'enhanced_shortcuts': True,
                'key_combinations': True
            }
        }
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all features"""
        if not self.initialized:
            return {'success': False, 'error': 'Controller not initialized'}
        
        test_results = {
            'enhanced_typing': [],
            'special_characters': [],
            'shortcuts': [],
            'key_combinations': []
        }
        
        # Test enhanced typing
        test_texts = ["Hello World", "Test @#$%", "Complex text with symbols!"]
        for text in test_texts:
            result = self.type_text_enhanced(text)
            test_results['enhanced_typing'].append(result)
        
        # Test special characters
        test_chars = ['@', '#', '$', '%', '&', '*']
        for char in test_chars:
            result = self.type_special_character(char)
            test_results['special_characters'].append(result)
        
        # Test shortcuts
        test_shortcuts = ['copy', 'paste', 'save', 'undo', 'find']
        for shortcut in test_shortcuts:
            result = self.execute_shortcut_enhanced(shortcut)
            test_results['shortcuts'].append(result)
        
        # Test key combinations
        test_combinations = [['ctrl', 'c'], ['alt', 'tab'], ['ctrl', 'shift', 's']]
        for combo in test_combinations:
            result = self.execute_key_combination(combo)
            test_results['key_combinations'].append(result)
        
        # Calculate overall success
        all_results = []
        for category in test_results.values():
            all_results.extend(category)
        
        successful = sum(1 for r in all_results if r.get('success', False))
        total = len(all_results)
        overall_success_rate = (successful / total * 100) if total > 0 else 0
        
        return {
            'success': overall_success_rate >= 80,
            'overall_success_rate': overall_success_rate,
            'successful_tests': successful,
            'total_tests': total,
            'detailed_results': test_results
        }
    
    def shutdown(self):
        """Shutdown the enhanced controller"""
        self.logger.info("🛑 Shutting down Enhanced Keyboard Controller")
        self.initialized = False
        self.logger.info("✅ Enhanced Keyboard Controller shutdown complete")
