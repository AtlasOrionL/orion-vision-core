"""
🧠 Evolution Core - Q4.2 Core Implementation

Core classes and data structures for Measurement Induced Evolution
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q4.2 Measurement Induced Evolution & Quantum Learning Rate
Priority: CRITICAL - Modular Design Refactoring Phase 7
"""

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional

# Import measurement components
from .measurement_core import MeasurementResult

# Evolution Types
class EvolutionType(Enum):
    """Evrim türleri"""
    MEASUREMENT_INDUCED = "measurement_induced"     # Ölçüm kaynaklı evrim
    SPONTANEOUS = "spontaneous"                     # Kendiliğinden evrim
    INTERACTION_DRIVEN = "interaction_driven"       # Etkileşim kaynaklı evrim
    LEARNING_BASED = "learning_based"               # Öğrenme bazlı evrim

# Learning Modes
class LearningMode(Enum):
    """Öğrenme modları"""
    QUANTUM_REINFORCEMENT = "quantum_reinforcement" # Kuantum pekiştirmeli öğrenme
    COHERENCE_OPTIMIZATION = "coherence_optimization" # Koherans optimizasyonu
    INFORMATION_INTEGRATION = "information_integration" # Bilgi entegrasyonu
    ADAPTIVE_EVOLUTION = "adaptive_evolution"       # Adaptif evrim

# Memory Update Types
class MemoryUpdateType(Enum):
    """Hafıza güncelleme türleri"""
    INCREMENTAL = "incremental"                     # Artırımsal güncelleme
    BATCH = "batch"                                 # Toplu güncelleme
    SELECTIVE = "selective"                         # Seçici güncelleme
    GLOBAL = "global"                               # Global güncelleme

@dataclass
class EvolutionEvent:
    """
    Evolution Event
    
    Ölçüm kaynaklı evrim olayı kaydı.
    """
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evolution_type: EvolutionType = EvolutionType.MEASUREMENT_INDUCED
    
    # Source measurement
    measurement_id: str = ""                        # Kaynak ölçüm ID
    measurement_result: Optional[MeasurementResult] = None
    
    # Target information
    target_id: str = ""                             # Hedef Lepton/QCB ID
    target_type: str = ""                           # Hedef türü
    
    # Evolution metrics
    coherence_change: float = 0.0                   # Koherans değişimi
    information_gain: float = 0.0                   # Bilgi kazancı
    learning_strength: float = 0.0                  # Öğrenme gücü
    evolution_magnitude: float = 0.0                # Evrim büyüklüğü
    
    # Learning parameters
    quantum_learning_rate: float = 0.1              # Kuantum öğrenme oranı
    coherence_weight: float = 1.0                   # Koherans ağırlığı
    information_weight: float = 1.0                 # Bilgi ağırlığı
    
    # System impact
    atlas_memory_updated: bool = False              # ATLAS hafızası güncellendi mi?
    bozon_interactions_modified: bool = False       # Bozon etkileşimleri değişti mi?
    system_state_changed: bool = False              # Sistem durumu değişti mi?
    
    # Temporal properties
    evolution_time: datetime = field(default_factory=datetime.now)
    evolution_duration: float = 0.0                 # Evrim süresi (saniye)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_evolution_impact(self) -> float:
        """Calculate overall evolution impact"""
        # Impact factors
        coherence_impact = abs(self.coherence_change) * self.coherence_weight
        information_impact = self.information_gain * self.information_weight
        learning_impact = self.learning_strength * self.quantum_learning_rate
        
        # Overall impact (weighted sum)
        total_impact = (coherence_impact + information_impact + learning_impact) / 3.0
        
        return min(1.0, total_impact)
    
    def get_impact_grade(self) -> str:
        """Get impact grade based on evolution impact"""
        impact = self.calculate_evolution_impact()
        
        if impact >= 0.8:
            return "High"
        elif impact >= 0.5:
            return "Medium"
        elif impact >= 0.2:
            return "Low"
        else:
            return "Minimal"
    
    def is_significant_evolution(self) -> bool:
        """Check if evolution is significant"""
        return (self.learning_strength > 0.3 and 
                self.calculate_evolution_impact() > 0.4)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get evolution summary"""
        return {
            'event_id': self.event_id[:8] + "...",
            'evolution_type': self.evolution_type.value,
            'target_type': self.target_type,
            'learning_strength': self.learning_strength,
            'coherence_change': self.coherence_change,
            'information_gain': self.information_gain,
            'impact': self.calculate_evolution_impact(),
            'impact_grade': self.get_impact_grade(),
            'significant': self.is_significant_evolution(),
            'duration_ms': self.evolution_duration * 1000
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'evolution_type': self.evolution_type.value,
            'measurement_id': self.measurement_id,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'coherence_change': self.coherence_change,
            'information_gain': self.information_gain,
            'learning_strength': self.learning_strength,
            'evolution_magnitude': self.evolution_magnitude,
            'quantum_learning_rate': self.quantum_learning_rate,
            'coherence_weight': self.coherence_weight,
            'information_weight': self.information_weight,
            'atlas_memory_updated': self.atlas_memory_updated,
            'bozon_interactions_modified': self.bozon_interactions_modified,
            'system_state_changed': self.system_state_changed,
            'evolution_impact': self.calculate_evolution_impact(),
            'impact_grade': self.get_impact_grade(),
            'significant': self.is_significant_evolution(),
            'evolution_time': self.evolution_time.isoformat(),
            'evolution_duration': self.evolution_duration,
            'metadata': self.metadata
        }

@dataclass
class QuantumLearningParameters:
    """
    Quantum Learning Parameters
    
    Kuantum öğrenme parametreleri.
    """
    
    # Base learning rates
    base_learning_rate: float = 0.1                 # Temel öğrenme oranı
    coherence_learning_rate: float = 0.05           # Koherans öğrenme oranı
    information_learning_rate: float = 0.15         # Bilgi öğrenme oranı
    
    # Dynamic adjustment factors
    coherence_threshold: float = 0.7                # Koherans eşiği
    information_threshold: float = 1.0              # Bilgi eşiği
    learning_decay: float = 0.95                    # Öğrenme azalması
    
    # Memory integration
    memory_integration_rate: float = 0.2            # Hafıza entegrasyon oranı
    atlas_update_threshold: float = 0.5             # ATLAS güncelleme eşiği
    
    # Adaptation parameters
    adaptation_speed: float = 0.1                   # Adaptasyon hızı
    stability_factor: float = 0.9                   # Kararlılık faktörü
    
    def calculate_dynamic_learning_rate(self, 
                                       coherence_factor: float,
                                       information_content: float) -> float:
        """Calculate dynamic learning rate based on coherence and information"""
        
        # Coherence-based adjustment
        if coherence_factor >= self.coherence_threshold:
            coherence_boost = 1.0 + (coherence_factor - self.coherence_threshold) * 2.0
        else:
            coherence_boost = coherence_factor / self.coherence_threshold
        
        # Information-based adjustment
        if information_content >= self.information_threshold:
            information_boost = 1.0 + math.log(information_content / self.information_threshold + 1)
        else:
            information_boost = information_content / self.information_threshold
        
        # Dynamic learning rate
        dynamic_rate = (self.base_learning_rate * 
                       coherence_boost * 
                       information_boost * 
                       self.stability_factor)
        
        return min(1.0, dynamic_rate)

# Utility functions
def create_evolution_event(measurement_result: MeasurementResult,
                          evolution_type: EvolutionType = EvolutionType.MEASUREMENT_INDUCED) -> EvolutionEvent:
    """Create evolution event from measurement result"""
    return EvolutionEvent(
        evolution_type=evolution_type,
        measurement_id=measurement_result.measurement_id,
        measurement_result=measurement_result,
        target_id=measurement_result.target_id,
        target_type=measurement_result.target_type
    )

def create_quantum_learning_parameters(base_rate: float = 0.1,
                                     coherence_threshold: float = 0.7,
                                     stability_factor: float = 0.9) -> QuantumLearningParameters:
    """Create quantum learning parameters with custom values"""
    return QuantumLearningParameters(
        base_learning_rate=base_rate,
        coherence_threshold=coherence_threshold,
        stability_factor=stability_factor
    )

# Export core components
__all__ = [
    'EvolutionType',
    'LearningMode',
    'MemoryUpdateType',
    'EvolutionEvent',
    'QuantumLearningParameters',
    'create_evolution_event',
    'create_quantum_learning_parameters'
]
