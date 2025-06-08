#!/usr/bin/env python3
"""
Shortcut Map - Keyboard shortcut mappings
"""

# Basic shortcuts with high success rate
BASIC_SHORTCUTS = {
    'copy': ['ctrl', 'c'],
    'paste': ['ctrl', 'v'],
    'cut': ['ctrl', 'x'],
    'save': ['ctrl', 's'],
    'undo': ['ctrl', 'z'],
    'redo': ['ctrl', 'y'],
    'select_all': ['ctrl', 'a'],
    'find': ['ctrl', 'f'],
    'new': ['ctrl', 'n'],
    'open': ['ctrl', 'o'],
    'close': ['ctrl', 'w'],
    'refresh': ['f5']
}

# Advanced shortcuts (may have lower success rate)
ADVANCED_SHORTCUTS = {
    'save_as': ['ctrl', 'shift', 's'],
    'find_replace': ['ctrl', 'h'],
    'go_to_line': ['ctrl', 'g'],
    'new_tab': ['ctrl', 't'],
    'close_tab': ['ctrl', 'w'],
    'reopen_tab': ['ctrl', 'shift', 't'],
    'next_tab': ['ctrl', 'tab'],
    'prev_tab': ['ctrl', 'shift', 'tab'],
    'developer_tools': ['f12'],
    'task_manager': ['ctrl', 'shift', 'esc']
}

# System shortcuts
SYSTEM_SHORTCUTS = {
    'alt_tab': ['alt', 'tab'],
    'run_dialog': ['win', 'r'],
    'desktop': ['win', 'd'],
    'lock_screen': ['win', 'l'],
    'screenshot': ['win', 'shift', 's']
}

# All shortcuts combined
ALL_SHORTCUTS = {**BASIC_SHORTCUTS, **ADVANCED_SHORTCUTS, **SYSTEM_SHORTCUTS}

def get_shortcut_keys(name):
    """Get key combination for shortcut"""
    return ALL_SHORTCUTS.get(name, [])

def get_basic_shortcuts():
    """Get basic shortcuts (high success rate)"""
    return BASIC_SHORTCUTS

def get_advanced_shortcuts():
    """Get advanced shortcuts"""
    return ADVANCED_SHORTCUTS

def get_system_shortcuts():
    """Get system shortcuts"""
    return SYSTEM_SHORTCUTS

def is_basic_shortcut(name):
    """Check if shortcut is basic (high success rate)"""
    return name in BASIC_SHORTCUTS
