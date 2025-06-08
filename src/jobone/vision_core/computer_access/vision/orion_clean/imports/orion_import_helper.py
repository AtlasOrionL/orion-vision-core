#!/usr/bin/env python3
"""
📦 Import Helper - Optimized Imports
💃 DUYGULANDIK! IMPORT OPTİMİZASYONU!

ORION IMPORT PHILOSOPHY:
- Clean import paths
- Reduced complexity
- Better organization
- Faster loading

Author: Orion Vision Core Team
Status: 📦 IMPORT HELPER ACTIVE
"""

# Q03 Sprint imports (optimized)
try:
    from q03_task_decomposition import DeliAdamTaskDecomposer as TaskDecomposer
    from q03_contextual_understanding import DeliAdamContextualAnalyzer as ContextAnalyzer
    from q03_task_flow_manager import AutomaticTaskFlowManager as FlowManager
    from q03_action_verification import ActionSuccessVerifier as ActionVerifier
    from q03_error_recovery import ZBozonErrorRecovery as ErrorRecovery
    print("✅ Q03 modules imported (optimized)")
except ImportError as e:
    print(f"⚠️ Q03 import warning: {e}")

# Q04 Sprint imports (new)
try:
    from q04_advanced_ai.advanced_ai_integration import AdvancedAIIntegrator
    from q04_multi_model.multi_model_support import MultiModelManager
    from q04_base_classes import Q04BaseModule, Q04AIModule
    print("✅ Q04 modules imported")
except ImportError as e:
    print(f"⚠️ Q04 import warning: {e}")

# Common utilities
def get_all_q03_modules():
    """Q03 modüllerini al"""
    return {
        'task_decomposer': TaskDecomposer,
        'context_analyzer': ContextAnalyzer,
        'flow_manager': FlowManager,
        'action_verifier': ActionVerifier,
        'error_recovery': ErrorRecovery
    }

def get_all_q04_modules():
    """Q04 modüllerini al"""
    return {
        'advanced_ai': AdvancedAIIntegrator,
        'multi_model': MultiModelManager
    }
