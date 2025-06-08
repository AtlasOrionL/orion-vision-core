#!/usr/bin/env python3
"""
Keyboard Mappings - Special character and shortcut mappings for enhanced keyboard control
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class KeyDifficulty(Enum):
    """Key combination difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class KeyCategory(Enum):
    """Keyboard shortcut categories"""
    FILE = "file"
    EDIT = "edit"
    NAVIGATION = "navigation"
    SYSTEM = "system"
    BROWSER = "browser"

@dataclass
class SpecialCharMapping:
    """Special character mapping definition"""
    char: str
    keys: List[str]
    difficulty: KeyDifficulty
    description: str = ""

@dataclass
class ShortcutMapping:
    """Keyboard shortcut mapping definition"""
    name: str
    keys: List[str]
    category: KeyCategory
    priority: str
    description: str = ""

class KeyboardMappings:
    """
    Centralized keyboard mappings for special characters and shortcuts
    """
    
    def __init__(self):
        self.special_chars = self._initialize_special_chars()
        self.shortcuts = self._initialize_shortcuts()
        self.sequences = self._initialize_sequences()
    
    def _initialize_special_chars(self) -> Dict[str, SpecialCharMapping]:
        """Initialize special character mappings"""
        mappings = {}
        
        # Basic punctuation (easy)
        basic_punct = [
            ('!', ['shift', '1'], 'Exclamation mark'),
            ('@', ['shift', '2'], 'At symbol'),
            ('#', ['shift', '3'], 'Hash/pound'),
            ('$', ['shift', '4'], 'Dollar sign'),
            ('%', ['shift', '5'], 'Percent'),
            ('&', ['shift', '7'], 'Ampersand'),
            ('*', ['shift', '8'], 'Asterisk'),
            ('(', ['shift', '9'], 'Left parenthesis'),
            (')', ['shift', '0'], 'Right parenthesis'),
            ('?', ['shift', '/'], 'Question mark')
        ]
        
        for char, keys, desc in basic_punct:
            mappings[char] = SpecialCharMapping(
                char=char,
                keys=keys,
                difficulty=KeyDifficulty.EASY,
                description=desc
            )
        
        # Medium difficulty characters
        medium_chars = [
            ('^', ['shift', '6'], 'Caret'),
            ('_', ['shift', '-'], 'Underscore'),
            ('+', ['shift', '='], 'Plus sign'),
            (':', ['shift', ';'], 'Colon'),
            ('"', ['shift', "'"], 'Double quote'),
            ('<', ['shift', ','], 'Less than'),
            ('>', ['shift', '.'], 'Greater than'),
            ('{', ['shift', '['], 'Left brace'),
            ('}', ['shift', ']'], 'Right brace')
        ]
        
        for char, keys, desc in medium_chars:
            mappings[char] = SpecialCharMapping(
                char=char,
                keys=keys,
                difficulty=KeyDifficulty.MEDIUM,
                description=desc
            )
        
        # Hard difficulty characters
        hard_chars = [
            ('|', ['shift', '\\'], 'Pipe/vertical bar'),
            ('~', ['shift', '`'], 'Tilde'),
            ('`', ['`'], 'Backtick'),
            ('\\', ['\\'], 'Backslash')
        ]
        
        for char, keys, desc in hard_chars:
            mappings[char] = SpecialCharMapping(
                char=char,
                keys=keys,
                difficulty=KeyDifficulty.HARD,
                description=desc
            )
        
        return mappings
    
    def _initialize_shortcuts(self) -> Dict[str, ShortcutMapping]:
        """Initialize keyboard shortcut mappings"""
        shortcuts = {}
        
        # File operations
        file_shortcuts = [
            ('new_file', ['ctrl', 'n'], 'high', 'Create new file'),
            ('open_file', ['ctrl', 'o'], 'high', 'Open file'),
            ('save_file', ['ctrl', 's'], 'high', 'Save file'),
            ('save_as', ['ctrl', 'shift', 's'], 'medium', 'Save as'),
            ('close_file', ['ctrl', 'w'], 'high', 'Close file'),
            ('print', ['ctrl', 'p'], 'medium', 'Print document'),
            ('quit', ['ctrl', 'q'], 'medium', 'Quit application')
        ]
        
        for name, keys, priority, desc in file_shortcuts:
            shortcuts[name] = ShortcutMapping(
                name=name,
                keys=keys,
                category=KeyCategory.FILE,
                priority=priority,
                description=desc
            )
        
        # Edit operations
        edit_shortcuts = [
            ('copy', ['ctrl', 'c'], 'high', 'Copy selection'),
            ('cut', ['ctrl', 'x'], 'high', 'Cut selection'),
            ('paste', ['ctrl', 'v'], 'high', 'Paste clipboard'),
            ('undo', ['ctrl', 'z'], 'high', 'Undo last action'),
            ('redo', ['ctrl', 'y'], 'high', 'Redo last action'),
            ('select_all', ['ctrl', 'a'], 'high', 'Select all'),
            ('find', ['ctrl', 'f'], 'high', 'Find text'),
            ('replace', ['ctrl', 'h'], 'medium', 'Find and replace'),
            ('find_next', ['f3'], 'medium', 'Find next occurrence')
        ]
        
        for name, keys, priority, desc in edit_shortcuts:
            shortcuts[name] = ShortcutMapping(
                name=name,
                keys=keys,
                category=KeyCategory.EDIT,
                priority=priority,
                description=desc
            )
        
        # Navigation shortcuts
        nav_shortcuts = [
            ('home', ['home'], 'medium', 'Go to beginning'),
            ('end', ['end'], 'medium', 'Go to end'),
            ('page_up', ['pageup'], 'medium', 'Page up'),
            ('page_down', ['pagedown'], 'medium', 'Page down'),
            ('go_to_line', ['ctrl', 'g'], 'low', 'Go to line number'),
            ('word_left', ['ctrl', 'left'], 'medium', 'Move word left'),
            ('word_right', ['ctrl', 'right'], 'medium', 'Move word right')
        ]
        
        for name, keys, priority, desc in nav_shortcuts:
            shortcuts[name] = ShortcutMapping(
                name=name,
                keys=keys,
                category=KeyCategory.NAVIGATION,
                priority=priority,
                description=desc
            )
        
        # System shortcuts
        system_shortcuts = [
            ('alt_tab', ['alt', 'tab'], 'high', 'Switch applications'),
            ('task_manager', ['ctrl', 'shift', 'esc'], 'low', 'Open task manager'),
            ('run_dialog', ['win', 'r'], 'medium', 'Open run dialog'),
            ('desktop', ['win', 'd'], 'medium', 'Show desktop'),
            ('lock_screen', ['win', 'l'], 'low', 'Lock screen'),
            ('screenshot', ['win', 'shift', 's'], 'medium', 'Take screenshot')
        ]
        
        for name, keys, priority, desc in system_shortcuts:
            shortcuts[name] = ShortcutMapping(
                name=name,
                keys=keys,
                category=KeyCategory.SYSTEM,
                priority=priority,
                description=desc
            )
        
        # Browser shortcuts
        browser_shortcuts = [
            ('new_tab', ['ctrl', 't'], 'high', 'New browser tab'),
            ('close_tab', ['ctrl', 'w'], 'high', 'Close current tab'),
            ('reopen_tab', ['ctrl', 'shift', 't'], 'medium', 'Reopen closed tab'),
            ('refresh', ['f5'], 'high', 'Refresh page'),
            ('hard_refresh', ['ctrl', 'f5'], 'medium', 'Hard refresh'),
            ('address_bar', ['ctrl', 'l'], 'medium', 'Focus address bar'),
            ('developer_tools', ['f12'], 'low', 'Open developer tools'),
            ('next_tab', ['ctrl', 'tab'], 'medium', 'Switch to next tab'),
            ('prev_tab', ['ctrl', 'shift', 'tab'], 'medium', 'Switch to previous tab')
        ]
        
        for name, keys, priority, desc in browser_shortcuts:
            shortcuts[name] = ShortcutMapping(
                name=name,
                keys=keys,
                category=KeyCategory.BROWSER,
                priority=priority,
                description=desc
            )
        
        return shortcuts
    
    def _initialize_sequences(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize complex key sequences"""
        return {
            'select_word': [
                {'action': 'key_combination', 'keys': ['ctrl', 'right'], 'description': 'Move to word end'},
                {'action': 'key_combination', 'keys': ['ctrl', 'shift', 'left'], 'description': 'Select word'}
            ],
            'select_line': [
                {'action': 'press_key', 'key': 'home', 'description': 'Go to line start'},
                {'action': 'key_combination', 'keys': ['shift', 'end'], 'description': 'Select to line end'}
            ],
            'duplicate_line': [
                {'action': 'press_key', 'key': 'home', 'description': 'Go to line start'},
                {'action': 'key_combination', 'keys': ['shift', 'end'], 'description': 'Select line'},
                {'action': 'key_combination', 'keys': ['ctrl', 'c'], 'description': 'Copy line'},
                {'action': 'press_key', 'key': 'end', 'description': 'Go to line end'},
                {'action': 'press_key', 'key': 'enter', 'description': 'New line'},
                {'action': 'key_combination', 'keys': ['ctrl', 'v'], 'description': 'Paste line'}
            ],
            'comment_line': [
                {'action': 'press_key', 'key': 'home', 'description': 'Go to line start'},
                {'action': 'type_text', 'text': '// ', 'description': 'Add comment prefix'}
            ],
            'indent_block': [
                {'action': 'key_combination', 'keys': ['ctrl', 'a'], 'description': 'Select all'},
                {'action': 'press_key', 'key': 'tab', 'description': 'Indent selection'}
            ]
        }
    
    def get_special_char(self, char: str) -> SpecialCharMapping:
        """Get special character mapping"""
        return self.special_chars.get(char)
    
    def get_shortcut(self, name: str) -> ShortcutMapping:
        """Get shortcut mapping"""
        return self.shortcuts.get(name)
    
    def get_sequence(self, name: str) -> List[Dict[str, Any]]:
        """Get key sequence"""
        return self.sequences.get(name, [])
    
    def get_shortcuts_by_category(self, category: KeyCategory) -> Dict[str, ShortcutMapping]:
        """Get shortcuts filtered by category"""
        return {
            name: mapping for name, mapping in self.shortcuts.items()
            if mapping.category == category
        }
    
    def get_shortcuts_by_priority(self, priority: str) -> Dict[str, ShortcutMapping]:
        """Get shortcuts filtered by priority"""
        return {
            name: mapping for name, mapping in self.shortcuts.items()
            if mapping.priority == priority
        }
    
    def get_chars_by_difficulty(self, difficulty: KeyDifficulty) -> Dict[str, SpecialCharMapping]:
        """Get special characters filtered by difficulty"""
        return {
            char: mapping for char, mapping in self.special_chars.items()
            if mapping.difficulty == difficulty
        }
    
    def get_mapping_stats(self) -> Dict[str, Any]:
        """Get mapping statistics"""
        return {
            'total_special_chars': len(self.special_chars),
            'total_shortcuts': len(self.shortcuts),
            'total_sequences': len(self.sequences),
            'difficulty_distribution': {
                'easy': len(self.get_chars_by_difficulty(KeyDifficulty.EASY)),
                'medium': len(self.get_chars_by_difficulty(KeyDifficulty.MEDIUM)),
                'hard': len(self.get_chars_by_difficulty(KeyDifficulty.HARD))
            },
            'category_distribution': {
                'file': len(self.get_shortcuts_by_category(KeyCategory.FILE)),
                'edit': len(self.get_shortcuts_by_category(KeyCategory.EDIT)),
                'navigation': len(self.get_shortcuts_by_category(KeyCategory.NAVIGATION)),
                'system': len(self.get_shortcuts_by_category(KeyCategory.SYSTEM)),
                'browser': len(self.get_shortcuts_by_category(KeyCategory.BROWSER))
            },
            'priority_distribution': {
                'high': len(self.get_shortcuts_by_priority('high')),
                'medium': len(self.get_shortcuts_by_priority('medium')),
                'low': len(self.get_shortcuts_by_priority('low'))
            }
        }
    
    def validate_mappings(self) -> Dict[str, Any]:
        """Validate all mappings for consistency"""
        issues = []
        
        # Check for duplicate key combinations in shortcuts
        key_combinations = {}
        for name, mapping in self.shortcuts.items():
            key_combo = '+'.join(mapping.keys)
            if key_combo in key_combinations:
                issues.append(f"Duplicate key combination '{key_combo}': {name} and {key_combinations[key_combo]}")
            else:
                key_combinations[key_combo] = name
        
        # Check for empty descriptions
        for char, mapping in self.special_chars.items():
            if not mapping.description:
                issues.append(f"Special character '{char}' missing description")
        
        for name, mapping in self.shortcuts.items():
            if not mapping.description:
                issues.append(f"Shortcut '{name}' missing description")
        
        # Check sequence validity
        for seq_name, sequence in self.sequences.items():
            if not sequence:
                issues.append(f"Empty sequence: {seq_name}")
            
            for step in sequence:
                if 'action' not in step:
                    issues.append(f"Sequence '{seq_name}' has step without action")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_mappings': len(self.special_chars) + len(self.shortcuts) + len(self.sequences)
        }

# Global instance
keyboard_mappings = KeyboardMappings()

def get_keyboard_mappings() -> KeyboardMappings:
    """Get global keyboard mappings instance"""
    return keyboard_mappings
