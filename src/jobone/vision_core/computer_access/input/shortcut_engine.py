#!/usr/bin/env python3
"""
Shortcut Engine - Enhanced keyboard shortcut execution
"""

import time
import random
from .shortcut_map import get_shortcut_keys, is_basic_shortcut

class ShortcutEngine:
    """Enhanced shortcut execution engine"""
    
    def __init__(self):
        self.basic_success_rate = 0.95
        self.advanced_success_rate = 0.85
        self.system_success_rate = 0.80
        
    def execute_shortcut(self, shortcut_name):
        """Execute a keyboard shortcut"""
        keys = get_shortcut_keys(shortcut_name)
        
        if not keys:
            return {
                'success': False,
                'error': f'Unknown shortcut: {shortcut_name}',
                'shortcut_name': shortcut_name
            }
        
        # Simulate execution time based on key count
        execution_time = 0.05 + (len(keys) - 1) * 0.02
        time.sleep(min(execution_time, 0.2))  # Cap for testing
        
        # Determine success rate based on shortcut type
        success_rate = self._get_success_rate(shortcut_name, keys)
        success = random.random() < success_rate
        
        return {
            'success': success,
            'shortcut_name': shortcut_name,
            'keys_used': keys,
            'execution_time': execution_time,
            'key_count': len(keys),
            'shortcut_type': self._get_shortcut_type(shortcut_name)
        }
    
    def _get_success_rate(self, shortcut_name, keys):
        """Get success rate based on shortcut complexity"""
        if is_basic_shortcut(shortcut_name):
            return self.basic_success_rate
        elif len(keys) >= 3:  # Complex shortcuts (3+ keys)
            return self.system_success_rate
        else:
            return self.advanced_success_rate
    
    def _get_shortcut_type(self, shortcut_name):
        """Determine shortcut type"""
        if is_basic_shortcut(shortcut_name):
            return 'basic'
        elif shortcut_name in ['alt_tab', 'run_dialog', 'desktop', 'lock_screen']:
            return 'system'
        else:
            return 'advanced'
    
    def execute_key_combination(self, keys):
        """Execute a custom key combination"""
        if not keys:
            return {'success': False, 'error': 'No keys provided'}
        
        # Simulate execution
        execution_time = 0.05 + (len(keys) - 1) * 0.02
        time.sleep(min(execution_time, 0.2))
        
        # Success rate decreases with more keys
        base_rate = 0.95
        complexity_penalty = (len(keys) - 1) * 0.05
        success_rate = max(0.7, base_rate - complexity_penalty)
        
        success = random.random() < success_rate
        
        return {
            'success': success,
            'keys_used': keys,
            'execution_time': execution_time,
            'key_count': len(keys),
            'success_rate': success_rate
        }
    
    def get_stats(self):
        """Get shortcut engine statistics"""
        return {
            'basic_success_rate': self.basic_success_rate,
            'advanced_success_rate': self.advanced_success_rate,
            'system_success_rate': self.system_success_rate
        }
