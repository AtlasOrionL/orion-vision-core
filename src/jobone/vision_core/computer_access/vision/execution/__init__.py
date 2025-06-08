#!/usr/bin/env python3
"""
📝 Orion Vision Core - Execution Modules Package
💖 DUYGULANDIK! SEN YAPARSIN! EXECUTION POWER!

Bu paket tüm görev yürütme modüllerini içerir.

Author: Orion Vision Core Team
Status: 🚀 ACTIVE DEVELOPMENT
"""

# Execution module imports
try:
    from .tasks.task_execution_engine import TaskExecutionEngine
    from .tasks.advanced_task_executor import AdvancedTaskExecutor
except ImportError as e:
    print(f"⚠️ Task execution import warning: {e}")

try:
    from .chat.simple_chat_executor import SimpleChatExecutor
except ImportError as e:
    print(f"⚠️ Chat executor import warning: {e}")

__all__ = [
    'TaskExecutionEngine',
    'AdvancedTaskExecutor',
    'SimpleChatExecutor'
]

__version__ = "1.0.0"
__author__ = "Orion Vision Core Team"
