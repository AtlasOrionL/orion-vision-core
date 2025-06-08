"""
🔬 Core Modules - Fundamental Quantum Components

Core data structures and base classes for quantum operations
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Priority: CRITICAL - Core Foundation
"""

# Import existing core modules that are already modularized
try:
    # Q1 Components
    from ...planck_information_unit import *
    from ...information_conservation_law import *

    # Q2 Components
    from ...lepton_phase_space import *
    from ...information_entanglement_unit import *

    # Q3 Components
    from ...redundant_information_encoding import *

    # Q4 Components
    from ...non_demolitional_measurement import *
    from ...measurement_induced_evolution import *

    # Q5 Components
    from ...computational_vacuum_state import *
    from ...information_thermodynamics_optimizer import *

except ImportError as e:
    print(f"⚠️ Core module import warning: {e}")

__all__ = [
    # Q1 - Information Foundation
    'PlanckInformationUnit',
    'InformationConservationLaw',
    
    # Q2 - Lepton Phase Space
    'LeptonPhaseSpace',
    'InformationEntanglementUnit',
    
    # Q3 - Redundant Information
    'RedundantInformationEncoding',
    
    # Q4 - Measurement Systems
    'NonDemolitionalMeasurement',
    'MeasurementInducedEvolution',
    
    # Q5 - Vacuum & Thermodynamics
    'ComputationalVacuumState',
    'InformationThermodynamicsOptimizer'
]
