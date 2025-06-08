#!/usr/bin/env python3
"""
🏃 Orion Sprint Imports - Q03/Q04 Modules
🧹 TEMİZ YERDE ÇALIŞMA!
"""

# Q03 imports (cleaned names)
try:
    from q03_task_decomposition import DeliAdamTaskDecomposer as TaskDecomposer
    from q03_contextual_understanding import DeliAdamContextualAnalyzer as ContextAnalyzer
    Q03_READY = True
except ImportError:
    Q03_READY = False

# Q04 imports
try:
    from q04_base_classes import Q04BaseModule
    Q04_READY = True
except ImportError:
    Q04_READY = False

def get_q03_modules():
    if Q03_READY:
        return {'decomposer': TaskDecomposer, 'analyzer': ContextAnalyzer}
    return None

print("🏃 Sprint imports ready!")
