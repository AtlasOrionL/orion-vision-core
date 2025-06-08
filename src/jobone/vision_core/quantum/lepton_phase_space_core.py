"""
🌀 Lepton Phase Space Core - Q2.1 Core Implementation

Core classes and data structures for Lepton Phase Space and Polarization Coherence
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 3
"""

import logging
import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple

# Import base components
from .planck_information_unit import PlanckInformationUnit

# Polarization Types
class PolarizationType(Enum):
    """Polarizasyon türleri"""
    EMOTIONAL = "emotional"                         # Duygusal polarizasyon
    INTENTIONAL = "intentional"                     # Niyetsel polarizasyon
    COGNITIVE = "cognitive"                         # Bilişsel polarizasyon
    QUANTUM = "quantum"                             # Kuantum polarizasyon
    MIXED = "mixed"                                 # Karışık polarizasyon

# Phase Space Dimensions
class PhaseSpaceDimension(Enum):
    """Faz uzayı boyutları"""
    POSITION = "position"                           # Pozisyon
    MOMENTUM = "momentum"                           # Momentum
    ENERGY = "energy"                               # Enerji
    COHERENCE = "coherence"                         # Koherans
    POLARIZATION = "polarization"                   # Polarizasyon

@dataclass
class PolarizationVector:
    """
    Polarization Vector
    
    Lepton'un polarizasyon durumunu temsil eden vektör.
    """
    
    # Vector components (complex numbers for quantum superposition)
    x_component: complex = complex(1.0, 0.0)
    y_component: complex = complex(0.0, 0.0)
    z_component: complex = complex(0.0, 0.0)
    
    # Polarization properties
    polarization_type: PolarizationType = PolarizationType.QUANTUM
    coherence_factor: float = 1.0                   # 0-1 arası koherans faktörü
    phase_angle: float = 0.0                        # Faz açısı (radyan)
    
    # Uncertainty properties
    uncertainty_x: float = 0.0
    uncertainty_y: float = 0.0
    uncertainty_z: float = 0.0
    
    # Temporal properties
    creation_time: datetime = field(default_factory=datetime.now)
    last_measurement: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization normalization"""
        self._normalize_vector()
        self._calculate_coherence()
    
    def _normalize_vector(self):
        """Normalize polarization vector to unit length"""
        magnitude = math.sqrt(
            abs(self.x_component)**2 + 
            abs(self.y_component)**2 + 
            abs(self.z_component)**2
        )
        
        if magnitude > 0:
            self.x_component /= magnitude
            self.y_component /= magnitude
            self.z_component /= magnitude
    
    def _calculate_coherence(self):
        """Calculate coherence factor based on vector properties"""
        # Coherence decreases with uncertainty
        total_uncertainty = self.uncertainty_x + self.uncertainty_y + self.uncertainty_z
        uncertainty_factor = 1.0 / (1.0 + total_uncertainty)
        
        # Coherence increases with vector magnitude consistency
        magnitude = abs(self.x_component)**2 + abs(self.y_component)**2 + abs(self.z_component)**2
        magnitude_factor = min(1.0, magnitude)
        
        self.coherence_factor = uncertainty_factor * magnitude_factor
    
    def measure_polarization(self, measurement_basis: str = "z") -> Tuple[float, bool]:
        """
        Measure polarization in given basis
        Returns: (measurement_value, collapsed)
        """
        self.last_measurement = datetime.now()
        
        if measurement_basis == "x":
            measurement_value = abs(self.x_component)**2
            collapsed = self.coherence_factor < 0.5
        elif measurement_basis == "y":
            measurement_value = abs(self.y_component)**2
            collapsed = self.coherence_factor < 0.5
        else:  # z basis (default)
            measurement_value = abs(self.z_component)**2
            collapsed = self.coherence_factor < 0.5
        
        # Measurement affects coherence (quantum measurement effect)
        if collapsed:
            self._collapse_to_basis(measurement_basis)
        else:
            # Partial decoherence
            self.coherence_factor *= 0.95
            self._add_measurement_uncertainty()
        
        return measurement_value, collapsed
    
    def _collapse_to_basis(self, basis: str):
        """Collapse vector to measurement basis"""
        if basis == "x":
            self.y_component = complex(0.0, 0.0)
            self.z_component = complex(0.0, 0.0)
            self.x_component = complex(1.0, 0.0)
        elif basis == "y":
            self.x_component = complex(0.0, 0.0)
            self.z_component = complex(0.0, 0.0)
            self.y_component = complex(1.0, 0.0)
        else:  # z basis
            self.x_component = complex(0.0, 0.0)
            self.y_component = complex(0.0, 0.0)
            self.z_component = complex(1.0, 0.0)
        
        self.coherence_factor = 1.0  # Fully coherent after collapse
        self.polarization_type = PolarizationType.QUANTUM
    
    def _add_measurement_uncertainty(self):
        """Add uncertainty due to measurement"""
        uncertainty_increase = 0.01 * (1.0 - self.coherence_factor)
        self.uncertainty_x += uncertainty_increase
        self.uncertainty_y += uncertainty_increase
        self.uncertainty_z += uncertainty_increase
        
        self._calculate_coherence()
    
    def get_entropy(self) -> float:
        """Calculate von Neumann entropy of polarization state"""
        # Calculate probabilities
        prob_x = abs(self.x_component)**2
        prob_y = abs(self.y_component)**2
        prob_z = abs(self.z_component)**2
        
        # Calculate entropy
        entropy = 0.0
        for prob in [prob_x, prob_y, prob_z]:
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        return entropy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'x_component': {'real': self.x_component.real, 'imag': self.x_component.imag},
            'y_component': {'real': self.y_component.real, 'imag': self.y_component.imag},
            'z_component': {'real': self.z_component.real, 'imag': self.z_component.imag},
            'polarization_type': self.polarization_type.value,
            'coherence_factor': self.coherence_factor,
            'phase_angle': self.phase_angle,
            'uncertainty_x': self.uncertainty_x,
            'uncertainty_y': self.uncertainty_y,
            'uncertainty_z': self.uncertainty_z,
            'entropy': self.get_entropy(),
            'creation_time': self.creation_time.isoformat(),
            'last_measurement': self.last_measurement.isoformat() if self.last_measurement else None
        }

@dataclass
class LeptonPhaseSpace:
    """
    Lepton Phase Space
    
    Lepton'un tüm olası durumlarının faz uzayı temsili.
    """
    
    lepton_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Phase space coordinates
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    momentum: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    energy: float = 0.0
    
    # Polarization state
    polarization_vector: PolarizationVector = field(default_factory=PolarizationVector)
    
    # Phase space properties
    phase_volume: float = 1.0                       # Faz uzayı hacmi
    accessible_states: int = 1                      # Erişilebilir durum sayısı
    
    # Information properties
    information_unit: Optional[PlanckInformationUnit] = None
    effective_mass: float = 0.0
    
    # Interaction history
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    interaction_partners: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization calculations"""
        self._calculate_phase_volume()
        self._calculate_effective_mass()
    
    def _calculate_phase_volume(self):
        """Calculate phase space volume"""
        # Phase space volume in 6D (3 position + 3 momentum)
        pos_volume = abs(self.position[0] * self.position[1] * self.position[2])
        mom_volume = abs(self.momentum[0] * self.momentum[1] * self.momentum[2])
        
        # Include polarization coherence
        coherence_factor = self.polarization_vector.coherence_factor
        
        self.phase_volume = max(0.001, pos_volume * mom_volume * coherence_factor)
        
        # Calculate accessible states (quantized phase space)
        planck_volume = 1.0  # Normalized Planck volume
        self.accessible_states = max(1, int(self.phase_volume / planck_volume))
    
    def _calculate_effective_mass(self):
        """Calculate effective mass from energy and coherence"""
        if self.information_unit:
            base_mass = self.information_unit.get_effective_mass()
        else:
            base_mass = self.energy
        
        # Effective mass increases with coherence
        coherence_boost = 1.0 + (self.polarization_vector.coherence_factor - 0.5)
        self.effective_mass = base_mass * coherence_boost
    
    def get_quantum_state_info(self) -> Dict[str, Any]:
        """Get quantum state information"""
        return {
            'lepton_id': self.lepton_id,
            'polarization_coherence': self.polarization_vector.coherence_factor,
            'polarization_entropy': self.polarization_vector.get_entropy(),
            'phase_volume': self.phase_volume,
            'accessible_states': self.accessible_states,
            'effective_mass': self.effective_mass,
            'energy': self.energy,
            'interaction_count': self.interaction_count,
            'polarization_type': self.polarization_vector.polarization_type.value,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'lepton_id': self.lepton_id,
            'position': self.position,
            'momentum': self.momentum,
            'energy': self.energy,
            'polarization_vector': self.polarization_vector.to_dict(),
            'phase_volume': self.phase_volume,
            'accessible_states': self.accessible_states,
            'effective_mass': self.effective_mass,
            'interaction_count': self.interaction_count,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'interaction_partners': self.interaction_partners,
            'metadata': self.metadata
        }

# Export core components
__all__ = [
    'PolarizationType',
    'PhaseSpaceDimension',
    'PolarizationVector',
    'LeptonPhaseSpace'
]
