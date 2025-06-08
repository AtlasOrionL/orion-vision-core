"""
🔗 Information Entanglement Core - Q3.1 Core Implementation

Core classes and data structures for Information Entanglement Unit (IEU)
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 4
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set

# Import bond components
from .entanglement_bond import EntanglementType, EntanglementState, EntanglementBond

# Import base components
from .planck_information_unit import PlanckInformationUnit

@dataclass
class InformationEntanglementUnit:
    """
    Information Entanglement Unit (IEU)
    
    Dolanık Lepton çiftleri/QCB'lerin yönetimi ve korunması.
    """
    
    ieu_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Entangled components
    lepton_ids: Set[str] = field(default_factory=set)
    information_units: List[PlanckInformationUnit] = field(default_factory=list)
    
    # Entanglement bond
    entanglement_bond: EntanglementBond = field(default_factory=EntanglementBond)
    
    # IEU properties
    total_information_content: float = 0.0
    collective_coherence: float = 1.0
    entanglement_entropy: float = 0.0
    
    # Decoherence detection
    decoherence_detected: bool = False
    decoherence_threshold: float = 0.3
    
    # Temporal properties
    creation_time: datetime = field(default_factory=datetime.now)
    last_check: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization calculations"""
        self._calculate_collective_properties()
        self._setup_entanglement_bond()
    
    def _calculate_collective_properties(self):
        """Calculate collective properties of entangled system"""
        if not self.information_units:
            return
        
        # Total information content
        self.total_information_content = sum(
            unit.information_content for unit in self.information_units
        )
        
        # Collective coherence (geometric mean)
        coherence_product = 1.0
        for unit in self.information_units:
            coherence_product *= unit.coherence_factor
        
        self.collective_coherence = coherence_product ** (1.0 / len(self.information_units))
        
        # Entanglement entropy
        self.entanglement_entropy = self.entanglement_bond.calculate_von_neumann_entropy()
    
    def _setup_entanglement_bond(self):
        """Setup entanglement bond with lepton IDs"""
        for lepton_id in self.lepton_ids:
            self.entanglement_bond.add_partner(lepton_id)
        
        # Set correlations based on collective properties
        self.entanglement_bond.coherence_correlation = self.collective_coherence
        self.entanglement_bond.phase_correlation = min(1.0, self.collective_coherence * 1.1)
    
    def add_lepton(self, lepton_id: str, information_unit: Optional[PlanckInformationUnit] = None):
        """Add lepton to entanglement unit"""
        self.lepton_ids.add(lepton_id)
        
        if information_unit:
            self.information_units.append(information_unit)
        
        self.entanglement_bond.add_partner(lepton_id)
        self._calculate_collective_properties()
    
    def remove_lepton(self, lepton_id: str) -> bool:
        """Remove lepton from entanglement unit (causes decoherence)"""
        if lepton_id not in self.lepton_ids:
            return False
        
        self.lepton_ids.remove(lepton_id)
        self.entanglement_bond.remove_partner(lepton_id)
        
        # Remove corresponding information unit
        # (simplified - in practice would need better matching)
        if self.information_units:
            self.information_units.pop()
        
        self._calculate_collective_properties()
        self._check_decoherence()
        
        return True
    
    def _check_decoherence(self) -> bool:
        """Check for decoherence conditions"""
        self.last_check = datetime.now()
        
        # Check entanglement strength
        if self.entanglement_bond.entanglement_strength < self.decoherence_threshold:
            self.decoherence_detected = True
            return True
        
        # Check collective coherence
        if self.collective_coherence < self.decoherence_threshold:
            self.decoherence_detected = True
            return True
        
        # Check minimum partner count
        if len(self.lepton_ids) < 2:
            self.decoherence_detected = True
            return True
        
        return False
    
    def measure_entanglement_strength(self) -> Tuple[float, bool]:
        """Measure entanglement strength and check for decoherence"""
        strength, decoherence_occurred = self.entanglement_bond.measure_entanglement()
        
        if decoherence_occurred:
            self.decoherence_detected = True
        
        self._calculate_collective_properties()
        return strength, decoherence_occurred
    
    def get_ieu_status(self) -> Dict[str, Any]:
        """Get IEU status information"""
        return {
            'ieu_id': self.ieu_id,
            'lepton_count': len(self.lepton_ids),
            'entanglement_state': self.entanglement_bond.get_entanglement_state().value,
            'entanglement_strength': self.entanglement_bond.entanglement_strength,
            'collective_coherence': self.collective_coherence,
            'decoherence_detected': self.decoherence_detected
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'ieu_id': self.ieu_id,
            'lepton_count': len(self.lepton_ids),
            'entanglement_strength': self.entanglement_bond.entanglement_strength,
            'collective_coherence': self.collective_coherence,
            'decoherence_detected': self.decoherence_detected,
            'creation_time': self.creation_time.isoformat()
        }

# Export core components
__all__ = [
    'EntanglementType',
    'EntanglementState',
    'EntanglementBond',
    'InformationEntanglementUnit'
]
