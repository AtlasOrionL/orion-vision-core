#!/usr/bin/env python3
"""
Typing Engine - Enhanced text typing with special character support
"""

import time
import random
from .char_map import get_char_keys, get_char_difficulty

class TypingEngine:
    """Enhanced typing engine with special character support"""
    
    def __init__(self):
        self.base_wpm = 60
        self.accuracy_rate = 0.95
        self.special_char_success_rate = 0.90
        
    def type_text(self, text, speed_wpm=None):
        """Type text with enhanced special character handling"""
        if speed_wpm is None:
            speed_wpm = self.base_wpm
            
        results = {
            'success': True,
            'text_length': len(text),
            'characters_typed': 0,
            'special_chars_handled': 0,
            'errors': 0,
            'typing_speed': speed_wpm,
            'accuracy': 0.0
        }
        
        for char in text:
            char_result = self._type_single_char(char, speed_wpm)
            
            if char_result['success']:
                results['characters_typed'] += 1
                if char_result['is_special']:
                    results['special_chars_handled'] += 1
            else:
                results['errors'] += 1
        
        # Calculate accuracy
        if results['text_length'] > 0:
            results['accuracy'] = (results['characters_typed'] - results['errors']) / results['text_length']
        
        # Overall success if accuracy > 80%
        results['success'] = results['accuracy'] >= 0.8
        
        return results
    
    def _type_single_char(self, char, speed_wpm):
        """Type a single character"""
        # Simulate typing delay
        char_delay = 60.0 / (speed_wpm * 5) if speed_wpm > 0 else 0.01
        time.sleep(min(char_delay, 0.1))  # Cap delay for testing
        
        is_special = char in get_char_keys(char) and len(get_char_keys(char)) > 1
        
        if is_special:
            # Special character handling
            difficulty = get_char_difficulty(char)
            success_rate = self._get_success_rate_for_difficulty(difficulty)
            success = random.random() < success_rate
        else:
            # Regular character
            success = random.random() < self.accuracy_rate
        
        return {
            'success': success,
            'character': char,
            'is_special': is_special,
            'keys_used': get_char_keys(char)
        }
    
    def _get_success_rate_for_difficulty(self, difficulty):
        """Get success rate based on character difficulty"""
        rates = {
            'easy': 0.95,
            'medium': 0.85,
            'hard': 0.75
        }
        return rates.get(difficulty, 0.90)
    
    def type_special_char(self, char):
        """Type a specific special character"""
        keys = get_char_keys(char)
        difficulty = get_char_difficulty(char)
        
        # Simulate special character typing
        time.sleep(0.05)  # Slightly longer for special chars
        
        success_rate = self._get_success_rate_for_difficulty(difficulty)
        success = random.random() < success_rate
        
        return {
            'success': success,
            'character': char,
            'keys_used': keys,
            'difficulty': difficulty
        }
    
    def get_optimized_speed(self, text):
        """Get optimized typing speed based on text complexity"""
        special_char_count = sum(1 for char in text if len(get_char_keys(char)) > 1)
        special_char_ratio = special_char_count / len(text) if text else 0
        
        # Reduce speed for complex text
        if special_char_ratio > 0.3:  # >30% special chars
            return max(40, self.base_wpm - 20)
        elif special_char_ratio > 0.1:  # >10% special chars
            return max(50, self.base_wpm - 10)
        else:
            return self.base_wpm
    
    def get_stats(self):
        """Get typing engine statistics"""
        return {
            'base_wpm': self.base_wpm,
            'accuracy_rate': self.accuracy_rate,
            'special_char_success_rate': self.special_char_success_rate
        }
