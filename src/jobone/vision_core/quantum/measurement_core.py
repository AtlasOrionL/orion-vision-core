"""
👁️ Measurement Core - Q4.1 Core Implementation

Core classes and data structures for Non-Demolitional Measurement Units (NDMU)
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q4.1 Non-Demolitional Measurement Units
Priority: CRITICAL - Modular Design Refactoring Phase 6
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any

# Measurement Types
class MeasurementType(Enum):
    """Ölçüm türleri"""
    NON_DEMOLITIONAL = "non_demolitional"          # Yıkıcı olmayan ölçüm
    WEAK_MEASUREMENT = "weak_measurement"           # Zayıf ölçüm
    QUANTUM_NON_DEMOLITION = "quantum_non_demolition"  # Kuantum yıkıcı olmayan
    CLASSICAL_OBSERVATION = "classical_observation" # Klasik gözlem

# Measurement Modes
class MeasurementMode(Enum):
    """Ölçüm modları"""
    COPY_ONLY = "copy_only"                        # Sadece kopya işleme
    SHADOW_MEASUREMENT = "shadow_measurement"       # Gölge ölçümü
    ENTANGLED_PROBE = "entangled_probe"            # Dolanık prob
    INDIRECT_INFERENCE = "indirect_inference"       # Dolaylı çıkarım

# Observer Types
class ObserverType(Enum):
    """Gözlemci türleri"""
    S_EHP = "s_ehp"                                # S-EHP gözlemcisi
    OBSERVER_AI = "observer_ai"                     # ObserverAI
    QUANTUM_SENSOR = "quantum_sensor"               # Kuantum sensör
    CLASSICAL_MONITOR = "classical_monitor"         # Klasik monitör

@dataclass
class MeasurementResult:
    """
    Measurement Result
    
    Non-demolitional ölçüm sonucu.
    """
    
    measurement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    measurement_type: MeasurementType = MeasurementType.NON_DEMOLITIONAL
    measurement_mode: MeasurementMode = MeasurementMode.COPY_ONLY
    
    # Target information
    target_id: str = ""                             # Hedef Lepton/QCB ID
    target_type: str = ""                           # Hedef türü
    
    # Measurement data
    measured_value: Any = None                      # Ölçülen değer
    measurement_uncertainty: float = 0.0            # Ölçüm belirsizliği
    measurement_confidence: float = 1.0             # Ölçüm güveni
    
    # State preservation
    original_state_preserved: bool = True           # Orijinal durum korundu mu?
    state_disturbance: float = 0.0                  # Durum bozulması (0-1)
    coherence_loss: float = 0.0                     # Koherans kaybı
    
    # Observer information
    observer_id: str = ""                           # Gözlemci ID
    observer_type: ObserverType = ObserverType.S_EHP
    
    # Temporal properties
    measurement_time: datetime = field(default_factory=datetime.now)
    measurement_duration: float = 0.0               # Ölçüm süresi (saniye)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_measurement_quality(self) -> float:
        """Calculate overall measurement quality"""
        # Quality factors
        preservation_factor = 1.0 if self.original_state_preserved else 0.5
        disturbance_factor = 1.0 - self.state_disturbance
        coherence_factor = 1.0 - self.coherence_loss
        confidence_factor = self.measurement_confidence
        
        # Overall quality (geometric mean)
        quality = (preservation_factor * disturbance_factor * 
                  coherence_factor * confidence_factor) ** 0.25
        
        return quality
    
    def get_quality_grade(self) -> str:
        """Get quality grade based on measurement quality"""
        quality = self.calculate_measurement_quality()
        
        if quality >= 0.9:
            return "A+"
        elif quality >= 0.8:
            return "A"
        elif quality >= 0.7:
            return "B"
        elif quality >= 0.6:
            return "C"
        else:
            return "D"
    
    def is_non_demolitional(self) -> bool:
        """Check if measurement was truly non-demolitional"""
        return (self.original_state_preserved and 
                self.state_disturbance < 0.05 and 
                self.coherence_loss < 0.1)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get measurement summary"""
        return {
            'measurement_id': self.measurement_id[:8] + "...",
            'target_type': self.target_type,
            'mode': self.measurement_mode.value,
            'quality': self.calculate_measurement_quality(),
            'grade': self.get_quality_grade(),
            'non_demolitional': self.is_non_demolitional(),
            'state_preserved': self.original_state_preserved,
            'disturbance': self.state_disturbance,
            'confidence': self.measurement_confidence,
            'duration_ms': self.measurement_duration * 1000
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'measurement_id': self.measurement_id,
            'measurement_type': self.measurement_type.value,
            'measurement_mode': self.measurement_mode.value,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'measured_value': self.measured_value,
            'measurement_uncertainty': self.measurement_uncertainty,
            'measurement_confidence': self.measurement_confidence,
            'original_state_preserved': self.original_state_preserved,
            'state_disturbance': self.state_disturbance,
            'coherence_loss': self.coherence_loss,
            'observer_id': self.observer_id,
            'observer_type': self.observer_type.value,
            'measurement_quality': self.calculate_measurement_quality(),
            'quality_grade': self.get_quality_grade(),
            'non_demolitional': self.is_non_demolitional(),
            'measurement_time': self.measurement_time.isoformat(),
            'measurement_duration': self.measurement_duration,
            'metadata': self.metadata
        }

# Utility functions
def create_measurement_result(target_id: str, 
                            target_type: str,
                            measurement_type: MeasurementType = MeasurementType.NON_DEMOLITIONAL,
                            measurement_mode: MeasurementMode = MeasurementMode.COPY_ONLY,
                            observer_id: str = "",
                            observer_type: ObserverType = ObserverType.S_EHP) -> MeasurementResult:
    """Create measurement result with default values"""
    return MeasurementResult(
        measurement_type=measurement_type,
        measurement_mode=measurement_mode,
        target_id=target_id,
        target_type=target_type,
        observer_id=observer_id,
        observer_type=observer_type
    )

def calculate_measurement_uncertainty(base_precision: float, 
                                    mode: MeasurementMode,
                                    coherence_factor: float = 1.0) -> float:
    """Calculate measurement uncertainty based on mode and coherence"""
    mode_factors = {
        MeasurementMode.COPY_ONLY: 1.0,
        MeasurementMode.SHADOW_MEASUREMENT: 2.0,
        MeasurementMode.ENTANGLED_PROBE: 0.5,
        MeasurementMode.INDIRECT_INFERENCE: 3.0
    }
    
    mode_factor = mode_factors.get(mode, 1.0)
    coherence_factor = max(0.1, coherence_factor)  # Avoid division by zero
    
    return (base_precision * mode_factor) / coherence_factor

def calculate_measurement_confidence(disturbance: float) -> float:
    """Calculate measurement confidence based on disturbance"""
    confidence = 1.0 - disturbance
    
    # Boost confidence for very low disturbance measurements
    if disturbance < 0.01:
        confidence = min(1.0, confidence * 1.1)
    
    return max(0.0, confidence)

# Export core components
__all__ = [
    'MeasurementType',
    'MeasurementMode',
    'ObserverType',
    'MeasurementResult',
    'create_measurement_result',
    'calculate_measurement_uncertainty',
    'calculate_measurement_confidence'
]
