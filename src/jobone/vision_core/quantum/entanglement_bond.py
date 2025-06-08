"""
🔗 Entanglement Bond - Q3.1 Bond Component

Entanglement bond implementation for quantum entanglement tracking
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q3.1 Information Entanglement Unit
Priority: CRITICAL - Modular Design Refactoring Phase 4
"""

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Set

# Entanglement Types
class EntanglementType(Enum):
    """Dolanıklık türleri"""
    QUANTUM_ENTANGLEMENT = "quantum_entanglement"     # Kuantum dolanıklığı
    INFORMATION_CORRELATION = "information_correlation" # Bilgi korelasyonu
    CAUSAL_ENTANGLEMENT = "causal_entanglement"       # Nedensel dolanıklık
    TEMPORAL_ENTANGLEMENT = "temporal_entanglement"   # Zamansal dolanıklık

# Entanglement States
class EntanglementState(Enum):
    """Dolanıklık durumları"""
    MAXIMALLY_ENTANGLED = "maximally_entangled"       # Maksimal dolanık
    PARTIALLY_ENTANGLED = "partially_entangled"       # Kısmi dolanık
    SEPARABLE = "separable"                           # Ayrılabilir
    DECOHERENT = "decoherent"                         # Dekohaerent

@dataclass
class EntanglementBond:
    """
    Entanglement Bond
    
    İki veya daha fazla Lepton/QCB arasındaki dolanıklık bağı.
    """
    
    bond_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entanglement_type: EntanglementType = EntanglementType.QUANTUM_ENTANGLEMENT
    
    # Entangled partners
    partner_ids: Set[str] = field(default_factory=set)
    partner_count: int = 0
    
    # Entanglement metrics
    entanglement_strength: float = 1.0              # 0-1 arası dolanıklık gücü
    coherence_correlation: float = 1.0              # Koherans korelasyonu
    phase_correlation: float = 1.0                  # Faz korelasyonu
    
    # Bell state properties
    bell_state_fidelity: float = 1.0                # Bell durumu sadakati
    concurrence: float = 1.0                        # Concurrence (dolanıklık ölçüsü)
    
    # Temporal properties
    creation_time: datetime = field(default_factory=datetime.now)
    last_measurement: Optional[datetime] = None
    decoherence_time: Optional[datetime] = None
    
    # Decoherence tracking
    decoherence_events: List[str] = field(default_factory=list)
    measurement_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization calculations"""
        self.partner_count = len(self.partner_ids)
        self._calculate_entanglement_metrics()
    
    def _calculate_entanglement_metrics(self):
        """Calculate entanglement metrics"""
        # Entanglement strength decreases with partner count (multipartite entanglement)
        if self.partner_count > 2:
            multipartite_factor = 1.0 / math.sqrt(self.partner_count)
            self.entanglement_strength *= multipartite_factor
        
        # Calculate concurrence (simplified)
        self.concurrence = self.entanglement_strength * self.coherence_correlation
        
        # Bell state fidelity
        self.bell_state_fidelity = (self.phase_correlation + self.coherence_correlation) / 2.0
    
    def add_partner(self, partner_id: str):
        """Add entanglement partner"""
        self.partner_ids.add(partner_id)
        self.partner_count = len(self.partner_ids)
        self._calculate_entanglement_metrics()
    
    def remove_partner(self, partner_id: str):
        """Remove entanglement partner (decoherence)"""
        if partner_id in self.partner_ids:
            self.partner_ids.remove(partner_id)
            self.partner_count = len(self.partner_ids)
            self.decoherence_events.append(f"partner_removed_{partner_id[:8]}")
            self._calculate_entanglement_metrics()
    
    def measure_entanglement(self) -> Tuple[float, bool]:
        """
        Measure entanglement strength
        Returns: (measurement_value, decoherence_occurred)
        """
        self.last_measurement = datetime.now()
        self.measurement_count += 1
        
        # Measurement affects entanglement (quantum measurement effect)
        measurement_effect = 0.95 ** self.measurement_count  # Exponential decay
        
        current_strength = self.entanglement_strength * measurement_effect
        
        # Check for decoherence
        decoherence_threshold = 0.3
        decoherence_occurred = current_strength < decoherence_threshold
        
        if decoherence_occurred and not self.decoherence_time:
            self.decoherence_time = datetime.now()
            self.decoherence_events.append("measurement_induced_decoherence")
        
        # Update strength
        self.entanglement_strength = current_strength
        self._calculate_entanglement_metrics()
        
        return current_strength, decoherence_occurred
    
    def get_entanglement_state(self) -> EntanglementState:
        """Get current entanglement state"""
        if self.decoherence_time:
            return EntanglementState.DECOHERENT
        elif self.entanglement_strength >= 0.9:
            return EntanglementState.MAXIMALLY_ENTANGLED
        elif self.entanglement_strength >= 0.5:
            return EntanglementState.PARTIALLY_ENTANGLED
        else:
            return EntanglementState.SEPARABLE
    
    def calculate_von_neumann_entropy(self) -> float:
        """Calculate von Neumann entropy of entangled state"""
        # Simplified calculation for bipartite entanglement
        if self.partner_count != 2:
            return 0.0  # Only for bipartite systems
        
        # Calculate reduced density matrix eigenvalues
        lambda1 = (1 + self.concurrence) / 2
        lambda2 = (1 - self.concurrence) / 2
        
        # von Neumann entropy
        entropy = 0.0
        for eigenvalue in [lambda1, lambda2]:
            if eigenvalue > 0:
                entropy -= eigenvalue * math.log2(eigenvalue)
        
        return entropy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'bond_id': self.bond_id,
            'entanglement_type': self.entanglement_type.value,
            'partner_count': self.partner_count,
            'entanglement_strength': self.entanglement_strength,
            'coherence_correlation': self.coherence_correlation,
            'phase_correlation': self.phase_correlation,
            'bell_state_fidelity': self.bell_state_fidelity,
            'concurrence': self.concurrence,
            'entanglement_state': self.get_entanglement_state().value,
            'von_neumann_entropy': self.calculate_von_neumann_entropy(),
            'creation_time': self.creation_time.isoformat(),
            'measurement_count': self.measurement_count,
            'decoherence_events': len(self.decoherence_events)
        }

# Export bond components
__all__ = [
    'EntanglementType',
    'EntanglementState',
    'EntanglementBond'
]
