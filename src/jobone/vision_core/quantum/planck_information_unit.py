"""
🔬 Planck Information Quantization Unit (ℏI) - Q1.1 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 1
"""

# Import core components from modular design
from .planck_information_core import (
    InformationUnitType,
    InformationQuality,
    PlanckInformationUnit
)

# Import manager component
from .planck_information_manager import PlanckInformationManager

# Import utility functions
from .planck_information_utils import create_planck_information_manager, test_planck_information_unit

# Export all components for backward compatibility
__all__ = [
    'InformationUnitType',
    'InformationQuality',
    'PlanckInformationUnit',
    'PlanckInformationManager',
    'create_planck_information_manager',
    'test_planck_information_unit'
]

if __name__ == "__main__":
    test_planck_information_unit()
