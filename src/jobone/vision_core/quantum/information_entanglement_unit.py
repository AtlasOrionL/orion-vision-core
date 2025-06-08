"""
🔗 Information Entanglement Unit (IEU) & Decoherence Detection - Q3.1 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 4
"""

# Import core components from modular design
from .entanglement_core import (
    EntanglementType,
    EntanglementState,
    EntanglementBond,
    InformationEntanglementUnit
)

# Import detector component
from .decoherence_detector import (
    DecoherenceDetectionSystem,
    create_information_entanglement_unit,
    create_decoherence_detection_system,
    test_information_entanglement_unit
)

# Import base components for compatibility
from .planck_information_unit import PlanckInformationUnit
from .lepton_phase_space import LeptonPhaseSpace
from .information_conservation_law import ZBosonTrigger

# Export all components for backward compatibility
__all__ = [
    'EntanglementType',
    'EntanglementState',
    'EntanglementBond',
    'InformationEntanglementUnit',
    'DecoherenceDetectionSystem',
    'create_information_entanglement_unit',
    'create_decoherence_detection_system',
    'test_information_entanglement_unit'
]

if __name__ == "__main__":
    test_information_entanglement_unit()
