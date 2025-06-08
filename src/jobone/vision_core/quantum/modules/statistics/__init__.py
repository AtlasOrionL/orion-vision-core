"""
📊 Statistics Modules - Analysis & Metrics

Statistical analysis and performance metrics for quantum systems
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Priority: MEDIUM - Statistics Domain
"""

# Import existing statistics modules
try:
    from ...vacuum_statistics import *
    from ...optimizer_statistics import *
    from ...evolution_statistics import *
    from ...measurement_statistics import *
except ImportError as e:
    print(f"⚠️ Statistics module import warning: {e}")

__all__ = [
    # Existing statistics modules
    'VacuumStatistics',
    'OptimizerStatistics', 
    'EvolutionStatistics',
    'MeasurementStatistics',
    
    # Future statistics modules
    'ErrorCorrectionStatistics',
    'FieldDynamicsStatistics',
    'EntanglementStatistics',
    'PerformanceStatistics'
]
