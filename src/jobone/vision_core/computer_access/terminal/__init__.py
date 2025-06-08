#!/usr/bin/env python3
"""
Terminal Control Module - Autonomous terminal command execution
"""

__version__ = "1.0.0"
__author__ = "Atlas-orion"

# Terminal module imports
from .terminal_controller import TerminalController
from .command_executor import CommandExecutor
from .output_parser import OutputParser
from .session_manager import SessionManager

__all__ = [
    "TerminalController",
    "CommandExecutor", 
    "OutputParser",
    "SessionManager"
]

# Terminal module constants
DEFAULT_TIMEOUT = 30.0
DEFAULT_ENCODING = 'utf-8'
MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB
COMMAND_HISTORY_SIZE = 1000

# Supported shells
SUPPORTED_SHELLS = {
    'Windows': ['cmd', 'powershell', 'pwsh'],
    'Linux': ['bash', 'sh', 'zsh', 'fish'],
    'Darwin': ['bash', 'sh', 'zsh', 'fish']
}

def get_terminal_info():
    """Get terminal module information"""
    return {
        'module': 'computer_access.terminal',
        'version': __version__,
        'author': __author__,
        'components': {
            'TerminalController': 'Main terminal control interface',
            'CommandExecutor': 'Command execution engine',
            'OutputParser': 'Output analysis and parsing',
            'SessionManager': 'Terminal session management'
        },
        'capabilities': [
            'Cross-platform command execution',
            'Real-time output streaming',
            'Interactive session management',
            'Command history tracking',
            'Error detection and handling',
            'Timeout management',
            'Output parsing and analysis'
        ],
        'supported_shells': SUPPORTED_SHELLS,
        'performance_targets': {
            'command_execution': '<100ms startup',
            'output_parsing': '<50ms per KB',
            'session_management': '<10ms overhead'
        }
    }
