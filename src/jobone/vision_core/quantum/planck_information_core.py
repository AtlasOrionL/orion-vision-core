"""
🔬 Planck Information Core - Q1.1 Core Implementation

Core classes and data structures for Planck Information Quantization Unit (ℏI)
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 1
"""

import logging
import hashlib
import time
import uuid
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

# Information Unit Types
class InformationUnitType(Enum):
    """Bilgi birimi türleri"""
    PLANCK_UNIT = "planck_unit"                     # Temel ℏI birimi
    COMPOSITE_UNIT = "composite_unit"               # Birleşik birim
    NOISE_UNIT = "noise_unit"                       # Gürültü birimi
    COHERENT_UNIT = "coherent_unit"                 # Koherent birim

# Information Quality Levels
class InformationQuality(Enum):
    """Bilgi kalitesi seviyeleri"""
    QUANTUM = "quantum"                             # Kuantum seviyesi (en yüksek)
    COHERENT = "coherent"                           # Koherent seviye
    CLASSICAL = "classical"                         # Klasik seviye
    NOISE = "noise"                                 # Gürültü seviyesi (en düşük)

@dataclass
class PlanckInformationUnit:
    """
    Planck Information Quantization Unit (ℏI)
    
    ALT_LAS'ın en temel bilgi birimi.
    Her Lepton ve QCB bu birimde seed taşır.
    """
    
    # Core properties
    unit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    unit_type: InformationUnitType = InformationUnitType.PLANCK_UNIT
    quality: InformationQuality = InformationQuality.CLASSICAL
    
    # Quantization properties
    planck_constant: float = 1.0                    # ℏI temel sabiti
    information_content: float = 0.0                # Bilgi içeriği
    entropy_level: float = 0.0                      # Entropi seviyesi
    
    # Seed properties
    seed_value: str = ""                            # Temel seed değeri
    seed_hash: str = ""                             # Seed hash'i
    causal_chain: List[str] = field(default_factory=list)  # Nedensel zincir
    
    # Temporal properties
    creation_time: datetime = field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None
    lifetime: float = 0.0                           # Yaşam süresi (saniye)
    
    # Coherence properties
    coherence_factor: float = 1.0                   # Koherans faktörü (0-1)
    phase_stability: float = 1.0                    # Faz kararlılığı
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing"""
        if not self.seed_value:
            self.seed_value = self._generate_quantum_seed()
        
        if not self.seed_hash:
            self.seed_hash = self._calculate_seed_hash()
        
        self._calculate_information_content()
        self._determine_quality_level()
    
    def _generate_quantum_seed(self) -> str:
        """Generate quantum-inspired seed"""
        # Combine multiple entropy sources
        timestamp = str(time.time_ns())
        random_uuid = str(uuid.uuid4())
        unit_id = self.unit_id
        
        # Create quantum-inspired seed
        combined = f"{timestamp}:{random_uuid}:{unit_id}"
        
        # Apply quantum-like transformation
        seed_bytes = combined.encode('utf-8')
        quantum_seed = hashlib.sha256(seed_bytes).hexdigest()
        
        return quantum_seed[:32]  # 32 character seed
    
    def _calculate_seed_hash(self) -> str:
        """Calculate seed hash for verification"""
        seed_data = f"{self.seed_value}:{self.unit_id}:{self.creation_time.isoformat()}"
        return hashlib.sha256(seed_data.encode('utf-8')).hexdigest()
    
    def _calculate_information_content(self):
        """Calculate information content based on seed entropy"""
        if not self.seed_value:
            self.information_content = 0.0
            return
        
        # Calculate Shannon entropy of seed
        seed_bytes = self.seed_value.encode('utf-8')
        byte_counts = {}
        
        for byte in seed_bytes:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        total_bytes = len(seed_bytes)
        entropy = 0.0
        
        for count in byte_counts.values():
            probability = count / total_bytes
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Normalize to ℏI units
        self.information_content = entropy * self.planck_constant
        
        # Calculate entropy level (inverse of information content)
        max_entropy = math.log2(256)  # Maximum entropy for byte data
        self.entropy_level = 1.0 - (entropy / max_entropy)
    
    def _determine_quality_level(self):
        """Determine information quality level"""
        if self.information_content >= 7.0 and self.coherence_factor >= 0.9:
            self.quality = InformationQuality.QUANTUM
        elif self.information_content >= 5.0 and self.coherence_factor >= 0.7:
            self.quality = InformationQuality.COHERENT
        elif self.information_content >= 3.0 and self.coherence_factor >= 0.5:
            self.quality = InformationQuality.CLASSICAL
        else:
            self.quality = InformationQuality.NOISE
    
    def is_above_planck_threshold(self) -> bool:
        """Check if unit is above Planck threshold (not noise)"""
        return (self.information_content >= self.planck_constant and 
                self.quality != InformationQuality.NOISE)
    
    def add_to_causal_chain(self, interaction_id: str):
        """Add interaction to causal chain"""
        self.causal_chain.append(interaction_id)
        self.last_interaction = datetime.now()
        
        # Limit causal chain length
        if len(self.causal_chain) > 100:
            self.causal_chain = self.causal_chain[-50:]
    
    def update_coherence(self, new_coherence: float):
        """Update coherence factor and recalculate quality"""
        self.coherence_factor = max(0.0, min(1.0, new_coherence))
        self._determine_quality_level()
    
    def get_effective_mass(self) -> float:
        """Calculate effective mass based on information content"""
        # E = mc² analog: Information = effective_mass * c²
        # where c is the "speed of information" (normalized to 1)
        return self.information_content * self.coherence_factor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'unit_id': self.unit_id,
            'unit_type': self.unit_type.value,
            'quality': self.quality.value,
            'planck_constant': self.planck_constant,
            'information_content': self.information_content,
            'entropy_level': self.entropy_level,
            'seed_value': self.seed_value,
            'seed_hash': self.seed_hash,
            'causal_chain': self.causal_chain,
            'creation_time': self.creation_time.isoformat(),
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'lifetime': self.lifetime,
            'coherence_factor': self.coherence_factor,
            'phase_stability': self.phase_stability,
            'effective_mass': self.get_effective_mass(),
            'above_threshold': self.is_above_planck_threshold(),
            'metadata': self.metadata
        }

# Export core components
__all__ = [
    'InformationUnitType',
    'InformationQuality', 
    'PlanckInformationUnit'
]
