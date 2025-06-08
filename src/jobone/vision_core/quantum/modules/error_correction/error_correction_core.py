"""
🛡️ Error Correction Core - Q05.2.2 Core Implementation

Core classes and data structures for Quantum Error Correction
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q05.2.2 Quantum Error Correction Codes
Priority: CRITICAL - Modular Design Refactoring Phase 10
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

# Error Correction Code Types
class ErrorCorrectionCode(Enum):
    """Hata düzeltme kodu türleri"""
    SHOR_CODE = "shor_code"               # 9-qubit Shor code
    STEANE_CODE = "steane_code"           # 7-qubit Steane code
    SURFACE_CODE = "surface_code"         # Surface code (topological)
    REPETITION_CODE = "repetition_code"   # Simple repetition code
    HAMMING_CODE = "hamming_code"         # Classical Hamming code adapted
    CSS_CODE = "css_code"                 # Calderbank-Shor-Steane code
    ALT_LAS_CODE = "alt_las_code"         # ALT_LAS consciousness-enhanced code

# Code Parameters
class CodeParameters(Enum):
    """Kod parametreleri"""
    DISTANCE_3 = "distance_3"             # Distance 3 codes
    DISTANCE_5 = "distance_5"             # Distance 5 codes
    DISTANCE_7 = "distance_7"             # Distance 7 codes
    ADAPTIVE = "adaptive"                 # Adaptive distance

@dataclass
class CorrectionCode:
    """Hata düzeltme kodu tanımı"""
    
    code_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    code_type: ErrorCorrectionCode = ErrorCorrectionCode.SHOR_CODE
    code_parameters: CodeParameters = CodeParameters.DISTANCE_3
    
    # Code properties
    n_physical_qubits: int = 9            # Total physical qubits
    n_logical_qubits: int = 1             # Logical qubits encoded
    code_distance: int = 3                # Minimum distance
    
    # Error correction capabilities
    correctable_errors: List[str] = field(default_factory=list)
    max_correctable_errors: int = 1       # Maximum correctable errors
    
    # Encoding/decoding
    encoding_circuit: List[str] = field(default_factory=list)
    decoding_circuit: List[str] = field(default_factory=list)
    stabilizer_generators: List[str] = field(default_factory=list)
    
    # Performance metrics
    encoding_fidelity: float = 1.0
    correction_success_rate: float = 1.0
    logical_error_rate: float = 0.0
    
    # ALT_LAS integration
    consciousness_enhancement: float = 0.0
    alt_las_seed: Optional[str] = None
    
    def get_efficiency_score(self) -> float:
        """Calculate code efficiency score"""
        # Efficiency = (logical qubits / physical qubits) * correction_success_rate
        efficiency = (self.n_logical_qubits / max(1, self.n_physical_qubits)) * self.correction_success_rate
        return efficiency
    
    def get_code_grade(self) -> str:
        """Get code quality grade"""
        score = self.get_efficiency_score()
        
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Poor"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get correction code summary"""
        return {
            'code_id': self.code_id[:8] + "...",
            'type': self.code_type.value,
            'parameters': self.code_parameters.value,
            'physical_qubits': self.n_physical_qubits,
            'logical_qubits': self.n_logical_qubits,
            'distance': self.code_distance,
            'max_correctable': self.max_correctable_errors,
            'success_rate': self.correction_success_rate,
            'efficiency_score': self.get_efficiency_score(),
            'grade': self.get_code_grade(),
            'consciousness_enhanced': self.consciousness_enhancement > 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'code_id': self.code_id,
            'code_type': self.code_type.value,
            'code_parameters': self.code_parameters.value,
            'n_physical_qubits': self.n_physical_qubits,
            'n_logical_qubits': self.n_logical_qubits,
            'code_distance': self.code_distance,
            'correctable_errors': self.correctable_errors,
            'max_correctable_errors': self.max_correctable_errors,
            'encoding_circuit': self.encoding_circuit,
            'decoding_circuit': self.decoding_circuit,
            'stabilizer_generators': self.stabilizer_generators,
            'encoding_fidelity': self.encoding_fidelity,
            'correction_success_rate': self.correction_success_rate,
            'logical_error_rate': self.logical_error_rate,
            'consciousness_enhancement': self.consciousness_enhancement,
            'alt_las_seed': self.alt_las_seed,
            'efficiency_score': self.get_efficiency_score(),
            'grade': self.get_code_grade()
        }

@dataclass
class CorrectionResult:
    """Hata düzeltme sonucu"""
    
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correction_code: ErrorCorrectionCode = ErrorCorrectionCode.SHOR_CODE
    
    # Correction details
    detected_errors: List[Any] = field(default_factory=list)
    corrected_errors: List[Any] = field(default_factory=list)
    uncorrectable_errors: List[Any] = field(default_factory=list)
    
    # Success metrics
    correction_successful: bool = True
    fidelity_before: float = 1.0
    fidelity_after: float = 1.0
    fidelity_improvement: float = 0.0
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    correction_time: float = 0.0
    
    # ALT_LAS factors
    consciousness_assistance: float = 0.0
    
    def calculate_improvement(self):
        """Calculate fidelity improvement"""
        self.fidelity_improvement = self.fidelity_after - self.fidelity_before
    
    def get_correction_efficiency(self) -> float:
        """Calculate correction efficiency"""
        total_errors = len(self.detected_errors)
        corrected_errors = len(self.corrected_errors)
        
        if total_errors == 0:
            return 1.0
        
        return corrected_errors / total_errors
    
    def get_correction_grade(self) -> str:
        """Get correction quality grade"""
        efficiency = self.get_correction_efficiency()
        
        if efficiency >= 0.9:
            return "Excellent"
        elif efficiency >= 0.7:
            return "Good"
        elif efficiency >= 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get correction result summary"""
        return {
            'result_id': self.result_id[:8] + "...",
            'code': self.correction_code.value,
            'successful': self.correction_successful,
            'detected_errors': len(self.detected_errors),
            'corrected_errors': len(self.corrected_errors),
            'uncorrectable_errors': len(self.uncorrectable_errors),
            'efficiency': self.get_correction_efficiency(),
            'grade': self.get_correction_grade(),
            'fidelity_improvement': self.fidelity_improvement,
            'correction_time_ms': self.correction_time * 1000,
            'consciousness_assisted': self.consciousness_assistance > 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'result_id': self.result_id,
            'correction_code': self.correction_code.value,
            'detected_errors_count': len(self.detected_errors),
            'corrected_errors_count': len(self.corrected_errors),
            'uncorrectable_errors_count': len(self.uncorrectable_errors),
            'correction_successful': self.correction_successful,
            'fidelity_before': self.fidelity_before,
            'fidelity_after': self.fidelity_after,
            'fidelity_improvement': self.fidelity_improvement,
            'correction_efficiency': self.get_correction_efficiency(),
            'correction_grade': self.get_correction_grade(),
            'timestamp': self.timestamp.isoformat(),
            'correction_time': self.correction_time,
            'consciousness_assistance': self.consciousness_assistance
        }

# Utility functions
def create_correction_code(code_type: ErrorCorrectionCode = ErrorCorrectionCode.SHOR_CODE,
                          n_physical: int = 9,
                          n_logical: int = 1,
                          distance: int = 3) -> CorrectionCode:
    """Create correction code with default values"""
    return CorrectionCode(
        code_type=code_type,
        n_physical_qubits=n_physical,
        n_logical_qubits=n_logical,
        code_distance=distance
    )

def create_correction_result(code_type: ErrorCorrectionCode = ErrorCorrectionCode.SHOR_CODE) -> CorrectionResult:
    """Create correction result"""
    return CorrectionResult(correction_code=code_type)

def get_standard_codes() -> Dict[ErrorCorrectionCode, CorrectionCode]:
    """Get standard error correction codes"""
    codes = {}
    
    # Shor Code (9-qubit)
    codes[ErrorCorrectionCode.SHOR_CODE] = create_correction_code(
        ErrorCorrectionCode.SHOR_CODE, 9, 1, 3
    )
    
    # Steane Code (7-qubit)
    codes[ErrorCorrectionCode.STEANE_CODE] = create_correction_code(
        ErrorCorrectionCode.STEANE_CODE, 7, 1, 3
    )
    
    # Surface Code
    codes[ErrorCorrectionCode.SURFACE_CODE] = create_correction_code(
        ErrorCorrectionCode.SURFACE_CODE, 17, 1, 5
    )
    
    return codes

# Export core components
__all__ = [
    'ErrorCorrectionCode',
    'CodeParameters',
    'CorrectionCode',
    'CorrectionResult',
    'create_correction_code',
    'create_correction_result',
    'get_standard_codes'
]
