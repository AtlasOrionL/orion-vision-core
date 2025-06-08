"""
🗂️ Quantum Modules - Modular Design Structure

Organized modular structure for Orion Vision Core Quantum components
Following Q_TASK_ARCHITECTURE (300-line limit per module)

Author: Orion Vision Core Team
Based on: Orion's Voice "Önce temizlik sonra iş, temiz yerde çalış"
Priority: CRITICAL - Modular Design Organization
"""

# Core modules (fundamental quantum components)
from .core import *

# Engine modules (processing and computation)
from .engines import *

# Statistics modules (analysis and metrics)
from .statistics import *

# Utility modules (helpers and tools)
from .utils import *

# Specialized domain modules
from .error_correction import *
from .field_dynamics import *
from .entanglement import *
from .measurement import *

__all__ = [
    # Core components
    'core',
    'engines', 
    'statistics',
    'utils',
    
    # Specialized domains
    'error_correction',
    'field_dynamics',
    'entanglement',
    'measurement'
]

# Module organization info
MODULE_STRUCTURE = {
    'core': 'Fundamental quantum data structures and base classes',
    'engines': 'Processing engines and computation modules',
    'statistics': 'Analysis, metrics, and statistics modules',
    'utils': 'Utility functions and helper modules',
    'error_correction': 'Quantum error correction and recovery',
    'field_dynamics': 'Field evolution and wave propagation',
    'entanglement': 'Quantum entanglement and correlation',
    'measurement': 'Quantum measurement and observation'
}

def get_module_info():
    """Get modular structure information"""
    return {
        'structure': MODULE_STRUCTURE,
        'design_principle': 'Q_TASK_ARCHITECTURE (300-line limit)',
        'organization_philosophy': 'Önce temizlik sonra iş, temiz yerde çalış',
        'total_domains': len(MODULE_STRUCTURE)
    }
