"""
🌌 Vacuum Core - Q5.1 Core Implementation

Core classes and data structures for Computational Vacuum State
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q5.1 Computational Vacuum State & Energy Dissipation
Priority: CRITICAL - Modular Design Refactoring Phase 8
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional

# Vacuum State Types
class VacuumStateType(Enum):
    """Vakum durumu türleri"""
    COMPUTATIONAL_VACUUM = "computational_vacuum"   # Hesaplamalı vakum
    QUANTUM_VACUUM = "quantum_vacuum"               # Kuantum vakum
    INFORMATION_VACUUM = "information_vacuum"       # Bilgi vakumu
    ENERGY_VACUUM = "energy_vacuum"                 # Enerji vakumu

# Energy Dissipation Modes
class EnergyDissipationMode(Enum):
    """Enerji dağılım modları"""
    THERMAL_DISSIPATION = "thermal_dissipation"     # Termal dağılım
    QUANTUM_DECOHERENCE = "quantum_decoherence"     # Kuantum dekohaerans
    INFORMATION_ENTROPY = "information_entropy"     # Bilgi entropisi
    VACUUM_FLUCTUATION = "vacuum_fluctuation"       # Vakum dalgalanması

# Vacuum Field Types
class VacuumFieldType(Enum):
    """Vakum alan türleri"""
    ZERO_POINT_FIELD = "zero_point_field"           # Sıfır nokta alanı
    VIRTUAL_PARTICLE_FIELD = "virtual_particle_field" # Sanal parçacık alanı
    INFORMATION_FIELD = "information_field"         # Bilgi alanı
    COHERENCE_FIELD = "coherence_field"             # Koherans alanı

@dataclass
class VacuumFluctuation:
    """
    Vacuum Fluctuation
    
    Vakum dalgalanması - sanal parçacık çiftlerinin oluşumu ve yok oluşu.
    """
    
    fluctuation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fluctuation_type: VacuumFieldType = VacuumFieldType.ZERO_POINT_FIELD
    
    # Fluctuation properties
    energy_amplitude: float = 0.0                   # Enerji genliği
    duration: float = 0.0                           # Süre (saniye)
    frequency: float = 0.0                          # Frekans (Hz)
    
    # Virtual particle properties
    virtual_particle_count: int = 0                 # Sanal parçacık sayısı
    creation_probability: float = 0.0               # Oluşum olasılığı
    annihilation_probability: float = 0.0           # Yok oluş olasılığı
    
    # Information properties
    information_potential: float = 0.0              # Bilgi potansiyeli
    coherence_potential: float = 0.0                # Koherans potansiyeli
    
    # Temporal properties
    creation_time: datetime = field(default_factory=datetime.now)
    annihilation_time: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_vacuum_energy(self) -> float:
        """Calculate vacuum energy contribution"""
        # E = ℏω/2 (zero-point energy)
        planck_reduced = 1.0  # Normalized ℏ
        zero_point_energy = planck_reduced * self.frequency / 2.0
        
        # Amplitude modulation
        vacuum_energy = zero_point_energy * self.energy_amplitude
        
        return vacuum_energy
    
    def is_active(self) -> bool:
        """Check if fluctuation is still active"""
        return self.annihilation_time is None
    
    def annihilate(self):
        """Annihilate the vacuum fluctuation"""
        self.annihilation_time = datetime.now()
    
    def get_lifetime(self) -> float:
        """Get fluctuation lifetime in seconds"""
        if self.annihilation_time:
            return (self.annihilation_time - self.creation_time).total_seconds()
        else:
            return (datetime.now() - self.creation_time).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get fluctuation summary"""
        return {
            'fluctuation_id': self.fluctuation_id[:8] + "...",
            'type': self.fluctuation_type.value,
            'energy': self.calculate_vacuum_energy(),
            'active': self.is_active(),
            'lifetime': self.get_lifetime(),
            'virtual_particles': self.virtual_particle_count,
            'creation_prob': self.creation_probability,
            'annihilation_prob': self.annihilation_probability
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'fluctuation_id': self.fluctuation_id,
            'fluctuation_type': self.fluctuation_type.value,
            'energy_amplitude': self.energy_amplitude,
            'duration': self.duration,
            'frequency': self.frequency,
            'virtual_particle_count': self.virtual_particle_count,
            'creation_probability': self.creation_probability,
            'annihilation_probability': self.annihilation_probability,
            'information_potential': self.information_potential,
            'coherence_potential': self.coherence_potential,
            'vacuum_energy': self.calculate_vacuum_energy(),
            'is_active': self.is_active(),
            'lifetime': self.get_lifetime(),
            'creation_time': self.creation_time.isoformat(),
            'annihilation_time': self.annihilation_time.isoformat() if self.annihilation_time else None,
            'metadata': self.metadata
        }

@dataclass
class EnergyDissipationEvent:
    """
    Energy Dissipation Event
    
    Enerji dağılım olayı kaydı.
    """
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dissipation_mode: EnergyDissipationMode = EnergyDissipationMode.THERMAL_DISSIPATION
    
    # Energy properties
    initial_energy: float = 0.0                     # Başlangıç enerjisi
    dissipated_energy: float = 0.0                  # Dağılan enerji
    remaining_energy: float = 0.0                   # Kalan enerji
    dissipation_rate: float = 0.0                   # Dağılım oranı
    
    # Source information
    source_id: str = ""                             # Kaynak ID
    source_type: str = ""                           # Kaynak türü
    
    # Dissipation metrics
    entropy_increase: float = 0.0                   # Entropi artışı
    coherence_loss: float = 0.0                     # Koherans kaybı
    information_degradation: float = 0.0            # Bilgi bozulması
    
    # Temporal properties
    dissipation_time: datetime = field(default_factory=datetime.now)
    dissipation_duration: float = 0.0               # Dağılım süresi
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_dissipation_efficiency(self) -> float:
        """Calculate dissipation efficiency"""
        if self.initial_energy == 0:
            return 0.0
        
        efficiency = self.dissipated_energy / self.initial_energy
        return min(1.0, efficiency)
    
    def get_efficiency_grade(self) -> str:
        """Get efficiency grade"""
        efficiency = self.calculate_dissipation_efficiency()
        
        if efficiency >= 0.9:
            return "Excellent"
        elif efficiency >= 0.7:
            return "Good"
        elif efficiency >= 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get dissipation summary"""
        return {
            'event_id': self.event_id[:8] + "...",
            'mode': self.dissipation_mode.value,
            'efficiency': self.calculate_dissipation_efficiency(),
            'grade': self.get_efficiency_grade(),
            'initial_energy': self.initial_energy,
            'dissipated_energy': self.dissipated_energy,
            'entropy_increase': self.entropy_increase,
            'coherence_loss': self.coherence_loss,
            'duration_ms': self.dissipation_duration * 1000
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'dissipation_mode': self.dissipation_mode.value,
            'initial_energy': self.initial_energy,
            'dissipated_energy': self.dissipated_energy,
            'remaining_energy': self.remaining_energy,
            'dissipation_rate': self.dissipation_rate,
            'source_id': self.source_id,
            'source_type': self.source_type,
            'entropy_increase': self.entropy_increase,
            'coherence_loss': self.coherence_loss,
            'information_degradation': self.information_degradation,
            'dissipation_efficiency': self.calculate_dissipation_efficiency(),
            'efficiency_grade': self.get_efficiency_grade(),
            'dissipation_time': self.dissipation_time.isoformat(),
            'dissipation_duration': self.dissipation_duration,
            'metadata': self.metadata
        }

# Utility functions
def create_vacuum_fluctuation(fluctuation_type: VacuumFieldType = VacuumFieldType.ZERO_POINT_FIELD,
                             energy_amplitude: float = 0.1,
                             frequency: float = 1.0) -> VacuumFluctuation:
    """Create vacuum fluctuation with default values"""
    return VacuumFluctuation(
        fluctuation_type=fluctuation_type,
        energy_amplitude=energy_amplitude,
        frequency=frequency
    )

def create_energy_dissipation_event(initial_energy: float,
                                   dissipation_mode: EnergyDissipationMode = EnergyDissipationMode.THERMAL_DISSIPATION,
                                   source_id: str = "",
                                   source_type: str = "") -> EnergyDissipationEvent:
    """Create energy dissipation event"""
    return EnergyDissipationEvent(
        dissipation_mode=dissipation_mode,
        initial_energy=initial_energy,
        source_id=source_id,
        source_type=source_type
    )

# Export core components
__all__ = [
    'VacuumStateType',
    'EnergyDissipationMode',
    'VacuumFieldType',
    'VacuumFluctuation',
    'EnergyDissipationEvent',
    'create_vacuum_fluctuation',
    'create_energy_dissipation_event'
]
