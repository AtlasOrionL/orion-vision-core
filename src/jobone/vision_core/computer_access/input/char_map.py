#!/usr/bin/env python3
"""
Character Map - Basic special character mappings
"""

# Special character to key combination mappings
SPECIAL_CHARS = {
    # Easy characters (high success rate expected)
    '!': ['shift', '1'],
    '@': ['shift', '2'], 
    '#': ['shift', '3'],
    '$': ['shift', '4'],
    '%': ['shift', '5'],
    '&': ['shift', '7'],
    '*': ['shift', '8'],
    '(': ['shift', '9'],
    ')': ['shift', '0'],
    
    # Medium difficulty
    '^': ['shift', '6'],
    '_': ['shift', '-'],
    '+': ['shift', '='],
    ':': ['shift', ';'],
    '"': ['shift', "'"],
    '<': ['shift', ','],
    '>': ['shift', '.'],
    '?': ['shift', '/'],
    
    # Brackets
    '{': ['shift', '['],
    '}': ['shift', ']'],
    '[': ['['],
    ']': [']'],
    
    # Hard characters
    '|': ['shift', '\\'],
    '~': ['shift', '`'],
    '`': ['`'],
    '\\': ['\\']
}

# Character difficulty levels
CHAR_DIFFICULTY = {
    'easy': ['!', '@', '#', '$', '%', '&', '*', '(', ')'],
    'medium': ['^', '_', '+', ':', '"', '<', '>', '?', '{', '}', '[', ']'],
    'hard': ['|', '~', '`', '\\']
}

def get_char_keys(char):
    """Get key combination for character"""
    return SPECIAL_CHARS.get(char, [char])

def get_char_difficulty(char):
    """Get difficulty level for character"""
    for level, chars in CHAR_DIFFICULTY.items():
        if char in chars:
            return level
    return 'easy'

def get_chars_by_difficulty(level):
    """Get characters by difficulty level"""
    return CHAR_DIFFICULTY.get(level, [])
