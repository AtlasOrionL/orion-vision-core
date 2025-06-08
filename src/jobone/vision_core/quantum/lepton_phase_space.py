"""
🌀 Lepton Phase Space ve Polarization Coherence - Q2.1 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 3
"""

# Import core components from modular design
from .lepton_phase_space_core import (
    PolarizationType,
    PhaseSpaceDimension,
    PolarizationVector,
    LeptonPhaseSpace
)

# Import manager component
from .lepton_phase_space_manager import (
    LeptonPhaseSpaceManager,
    create_lepton_phase_space_manager,
    test_lepton_phase_space
)

# Import base components for compatibility
from .planck_information_unit import PlanckInformationUnit

# Export all components for backward compatibility
__all__ = [
    'PolarizationType',
    'PhaseSpaceDimension',
    'PolarizationVector',
    'LeptonPhaseSpace',
    'LeptonPhaseSpaceManager',
    'create_lepton_phase_space_manager',
    'test_lepton_phase_space'
]

if __name__ == "__main__":
    test_lepton_phase_space()
