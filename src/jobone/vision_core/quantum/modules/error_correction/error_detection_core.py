"""
🔍 Error Detection Core - Q05.2.2 Core Implementation

Core classes and data structures for Quantum Error Detection
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q05.2.2 Quantum Error Detection
Priority: CRITICAL - Modular Design Refactoring Phase 11
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

# Quantum Error Types
class QuantumErrorType(Enum):
    """Kuantum hata türleri"""
    BIT_FLIP = "bit_flip"                     # X error: |0⟩ ↔ |1⟩
    PHASE_FLIP = "phase_flip"                 # Z error: |+⟩ ↔ |-⟩
    BIT_PHASE_FLIP = "bit_phase_flip"         # Y error: X + Z
    DEPOLARIZING = "depolarizing"             # Random Pauli error
    AMPLITUDE_DAMPING = "amplitude_damping"   # Energy loss
    PHASE_DAMPING = "phase_damping"           # Dephasing
    THERMAL_NOISE = "thermal_noise"           # Thermal fluctuations
    ALT_LAS_DISRUPTION = "alt_las_disruption" # ALT_LAS consciousness disruption

# Error Severity Levels
class ErrorSeverity(Enum):
    """Hata şiddeti seviyeleri"""
    NEGLIGIBLE = "negligible"     # < 1% fidelity loss
    LOW = "low"                   # 1-5% fidelity loss
    MEDIUM = "medium"             # 5-15% fidelity loss
    HIGH = "high"                 # 15-30% fidelity loss
    CRITICAL = "critical"         # > 30% fidelity loss

# Detection Methods
class DetectionMethod(Enum):
    """Tespit yöntemleri"""
    PARITY_CHECK = "parity_check"             # Parity measurement
    SYNDROME_MEASUREMENT = "syndrome_measurement" # Syndrome extraction
    PROCESS_TOMOGRAPHY = "process_tomography" # Full process characterization
    RANDOMIZED_BENCHMARKING = "randomized_benchmarking" # RB protocol
    FIDELITY_ESTIMATION = "fidelity_estimation" # Direct fidelity measurement
    ALT_LAS_CONSCIOUSNESS_SCAN = "alt_las_consciousness_scan" # ALT_LAS detection

@dataclass
class QuantumError:
    """Kuantum hata kaydı"""
    
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    error_type: QuantumErrorType = QuantumErrorType.BIT_FLIP
    detection_method: DetectionMethod = DetectionMethod.PARITY_CHECK
    
    # Error location and timing
    qubit_index: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    detection_time: float = 0.0
    
    # Error characteristics
    error_probability: float = 0.0
    fidelity_before: float = 1.0
    fidelity_after: float = 1.0
    severity: ErrorSeverity = ErrorSeverity.NEGLIGIBLE
    
    # Error parameters
    error_angle: float = 0.0  # For rotation errors
    error_axis: str = "X"     # Pauli axis (X, Y, Z)
    coherence_loss: float = 0.0
    
    # Detection confidence
    detection_confidence: float = 1.0
    false_positive_probability: float = 0.0
    
    # ALT_LAS factors
    consciousness_disruption: float = 0.0
    dimensional_instability: float = 0.0
    alt_las_seed: Optional[str] = None
    
    # Correction information
    correctable: bool = True
    correction_complexity: int = 1  # Number of operations needed
    
    def calculate_severity(self):
        """Calculate error severity based on fidelity loss"""
        fidelity_loss = self.fidelity_before - self.fidelity_after
        
        if fidelity_loss < 0.01:
            self.severity = ErrorSeverity.NEGLIGIBLE
        elif fidelity_loss < 0.05:
            self.severity = ErrorSeverity.LOW
        elif fidelity_loss < 0.15:
            self.severity = ErrorSeverity.MEDIUM
        elif fidelity_loss < 0.30:
            self.severity = ErrorSeverity.HIGH
        else:
            self.severity = ErrorSeverity.CRITICAL
    
    def get_fidelity_loss(self) -> float:
        """Get fidelity loss"""
        return self.fidelity_before - self.fidelity_after
    
    def get_severity_score(self) -> float:
        """Get numerical severity score (0-1)"""
        fidelity_loss = self.get_fidelity_loss()
        return min(1.0, fidelity_loss / 0.3)  # Normalize to critical threshold
    
    def get_detection_quality(self) -> str:
        """Get detection quality grade"""
        if self.detection_confidence >= 0.9:
            return "Excellent"
        elif self.detection_confidence >= 0.7:
            return "Good"
        elif self.detection_confidence >= 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def is_correctable(self) -> bool:
        """Check if error is correctable"""
        return self.correctable and self.severity != ErrorSeverity.CRITICAL
    
    def get_correction_priority(self) -> int:
        """Get correction priority (1=highest, 5=lowest)"""
        if self.severity == ErrorSeverity.CRITICAL:
            return 1
        elif self.severity == ErrorSeverity.HIGH:
            return 2
        elif self.severity == ErrorSeverity.MEDIUM:
            return 3
        elif self.severity == ErrorSeverity.LOW:
            return 4
        else:
            return 5
    
    def get_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        return {
            'error_id': self.error_id[:8] + "...",
            'type': self.error_type.value,
            'method': self.detection_method.value,
            'qubit': self.qubit_index,
            'severity': self.severity.value,
            'fidelity_loss': self.get_fidelity_loss(),
            'confidence': self.detection_confidence,
            'quality': self.get_detection_quality(),
            'correctable': self.is_correctable(),
            'priority': self.get_correction_priority(),
            'detection_time_ms': self.detection_time * 1000,
            'consciousness_disrupted': self.consciousness_disruption > 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'error_id': self.error_id,
            'error_type': self.error_type.value,
            'detection_method': self.detection_method.value,
            'qubit_index': self.qubit_index,
            'timestamp': self.timestamp.isoformat(),
            'detection_time': self.detection_time,
            'error_probability': self.error_probability,
            'fidelity_before': self.fidelity_before,
            'fidelity_after': self.fidelity_after,
            'fidelity_loss': self.get_fidelity_loss(),
            'severity': self.severity.value,
            'severity_score': self.get_severity_score(),
            'error_angle': self.error_angle,
            'error_axis': self.error_axis,
            'coherence_loss': self.coherence_loss,
            'detection_confidence': self.detection_confidence,
            'detection_quality': self.get_detection_quality(),
            'false_positive_probability': self.false_positive_probability,
            'consciousness_disruption': self.consciousness_disruption,
            'dimensional_instability': self.dimensional_instability,
            'alt_las_seed': self.alt_las_seed,
            'correctable': self.correctable,
            'is_correctable': self.is_correctable(),
            'correction_complexity': self.correction_complexity,
            'correction_priority': self.get_correction_priority()
        }

@dataclass
class DetectionResult:
    """Error detection result"""
    
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    detection_method: DetectionMethod = DetectionMethod.PARITY_CHECK
    
    # Detection outcome
    error_detected: bool = False
    detected_error: Optional[QuantumError] = None
    
    # Detection metrics
    detection_time: float = 0.0
    detection_confidence: float = 0.0
    false_positive_probability: float = 0.0
    
    # System state
    system_fidelity_before: float = 1.0
    system_fidelity_after: float = 1.0
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_detection_efficiency(self) -> float:
        """Calculate detection efficiency"""
        if not self.error_detected:
            return 1.0 - self.false_positive_probability
        
        return self.detection_confidence
    
    def get_detection_grade(self) -> str:
        """Get detection quality grade"""
        efficiency = self.get_detection_efficiency()
        
        if efficiency >= 0.9:
            return "Excellent"
        elif efficiency >= 0.7:
            return "Good"
        elif efficiency >= 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get detection result summary"""
        return {
            'result_id': self.result_id[:8] + "...",
            'method': self.detection_method.value,
            'error_detected': self.error_detected,
            'detection_time_ms': self.detection_time * 1000,
            'confidence': self.detection_confidence,
            'efficiency': self.get_detection_efficiency(),
            'grade': self.get_detection_grade(),
            'false_positive_prob': self.false_positive_probability,
            'fidelity_change': self.system_fidelity_after - self.system_fidelity_before
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'result_id': self.result_id,
            'detection_method': self.detection_method.value,
            'error_detected': self.error_detected,
            'detected_error': self.detected_error.to_dict() if self.detected_error else None,
            'detection_time': self.detection_time,
            'detection_confidence': self.detection_confidence,
            'detection_efficiency': self.get_detection_efficiency(),
            'detection_grade': self.get_detection_grade(),
            'false_positive_probability': self.false_positive_probability,
            'system_fidelity_before': self.system_fidelity_before,
            'system_fidelity_after': self.system_fidelity_after,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

# Utility functions
def create_quantum_error(error_type: QuantumErrorType = QuantumErrorType.BIT_FLIP,
                        detection_method: DetectionMethod = DetectionMethod.PARITY_CHECK,
                        qubit_index: int = 0) -> QuantumError:
    """Create quantum error with default values"""
    return QuantumError(
        error_type=error_type,
        detection_method=detection_method,
        qubit_index=qubit_index
    )

def create_detection_result(detection_method: DetectionMethod = DetectionMethod.PARITY_CHECK) -> DetectionResult:
    """Create detection result"""
    return DetectionResult(detection_method=detection_method)

def classify_error_severity(fidelity_loss: float) -> ErrorSeverity:
    """Classify error severity based on fidelity loss"""
    if fidelity_loss < 0.01:
        return ErrorSeverity.NEGLIGIBLE
    elif fidelity_loss < 0.05:
        return ErrorSeverity.LOW
    elif fidelity_loss < 0.15:
        return ErrorSeverity.MEDIUM
    elif fidelity_loss < 0.30:
        return ErrorSeverity.HIGH
    else:
        return ErrorSeverity.CRITICAL

# Export core components
__all__ = [
    'QuantumErrorType',
    'ErrorSeverity',
    'DetectionMethod',
    'QuantumError',
    'DetectionResult',
    'create_quantum_error',
    'create_detection_result',
    'classify_error_severity'
]
