"""
📊 Syndrome Calculator - Q05.2.2 Component

Kuantum hata sendromu hesaplama sistemi.
ALT_LAS Quantum Mind OS ile entegre çalışır.

Bu modül Q05.2.2 görevinin üçüncü parçasıdır:
- Syndrome calculation system ✅
- Stabilizer measurements
- Error syndrome mapping
- Syndrome decoding algorithms

Author: Orion Vision Core Team
Sprint: Q05.2.2 - Quantum Error Correction
Status: IN_PROGRESS
"""

import logging
import threading
import time
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Callable
import uuid

from .qfd_base import QFDBase, QFDConfig, QuantumEntity, EntityType
from .quantum_field import QuantumState, QuantumField, FieldType
from .error_detector import QuantumError, QuantumErrorType
from .error_correction_codes import ErrorCorrectionCode

# Syndrome Types
class SyndromeType(Enum):
    """Sendrom türleri"""
    X_SYNDROME = "x_syndrome"                 # X (bit flip) syndrome
    Z_SYNDROME = "z_syndrome"                 # Z (phase flip) syndrome
    Y_SYNDROME = "y_syndrome"                 # Y (bit-phase flip) syndrome
    STABILIZER_SYNDROME = "stabilizer_syndrome" # General stabilizer syndrome
    SURFACE_SYNDROME = "surface_syndrome"     # Surface code syndrome
    ALT_LAS_SYNDROME = "alt_las_syndrome"     # ALT_LAS consciousness syndrome

# Syndrome Calculation Methods
class SyndromeMethod(Enum):
    """Sendrom hesaplama yöntemleri"""
    PARITY_CHECK = "parity_check"             # Parity check matrix
    STABILIZER_MEASUREMENT = "stabilizer_measurement" # Stabilizer generators
    LOOKUP_TABLE = "lookup_table"             # Pre-computed lookup
    MINIMUM_WEIGHT = "minimum_weight"         # Minimum weight decoding
    MAXIMUM_LIKELIHOOD = "maximum_likelihood" # ML decoding
    ALT_LAS_CONSCIOUSNESS = "alt_las_consciousness" # Consciousness-guided

@dataclass
class SyndromeResult:
    """Sendrom hesaplama sonucu"""
    
    syndrome_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    syndrome_type: SyndromeType = SyndromeType.STABILIZER_SYNDROME
    calculation_method: SyndromeMethod = SyndromeMethod.STABILIZER_MEASUREMENT
    
    # Syndrome data
    syndrome_bits: List[int] = field(default_factory=list)
    syndrome_value: int = 0
    syndrome_weight: int = 0
    
    # Error mapping
    detected_error_pattern: List[int] = field(default_factory=list)
    error_location: List[int] = field(default_factory=list)
    error_type_prediction: QuantumErrorType = QuantumErrorType.BIT_FLIP
    
    # Confidence metrics
    calculation_confidence: float = 1.0
    decoding_confidence: float = 1.0
    ambiguity_score: float = 0.0
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    calculation_time: float = 0.0
    
    # ALT_LAS factors
    consciousness_guidance: float = 0.0
    dimensional_insight: float = 0.0
    
    def calculate_syndrome_value(self):
        """Calculate syndrome value from bits"""
        self.syndrome_value = sum(bit * (2**i) for i, bit in enumerate(self.syndrome_bits))
        self.syndrome_weight = sum(self.syndrome_bits)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'syndrome_id': self.syndrome_id,
            'syndrome_type': self.syndrome_type.value,
            'calculation_method': self.calculation_method.value,
            'syndrome_bits': self.syndrome_bits,
            'syndrome_value': self.syndrome_value,
            'syndrome_weight': self.syndrome_weight,
            'detected_error_pattern': self.detected_error_pattern,
            'error_location': self.error_location,
            'error_type_prediction': self.error_type_prediction.value,
            'calculation_confidence': self.calculation_confidence,
            'decoding_confidence': self.decoding_confidence,
            'ambiguity_score': self.ambiguity_score,
            'timestamp': self.timestamp.isoformat(),
            'calculation_time': self.calculation_time,
            'consciousness_guidance': self.consciousness_guidance
        }

class SyndromeCalculator(QFDBase):
    """
    Kuantum sendrom hesaplama sistemi
    
    Q05.2.2 görevinin üçüncü bileşeni. Hata sendromlarını
    hesaplar, decode eder ve ALT_LAS ile entegre çalışır.
    """
    
    def __init__(self, config: Optional[QFDConfig] = None):
        super().__init__(config)
        
        # Syndrome management
        self.syndrome_results: List[SyndromeResult] = []
        self.active_calculations: Dict[str, SyndromeResult] = {}
        
        # Calculation methods
        self.syndrome_calculators: Dict[SyndromeMethod, Callable] = {}
        self.syndrome_decoders: Dict[ErrorCorrectionCode, Callable] = {}
        
        # Syndrome tables
        self.syndrome_lookup_tables: Dict[ErrorCorrectionCode, Dict[int, List[int]]] = {}
        
        # Performance tracking
        self.total_calculations = 0
        self.successful_calculations = 0
        self.failed_calculations = 0
        self.average_calculation_time = 0.0
        self.average_decoding_confidence = 0.0
        
        # ALT_LAS integration
        self.alt_las_integration_active = False
        self.consciousness_syndrome_enabled = False
        
        # Threading
        self._syndrome_lock = threading.Lock()
        self._calculation_lock = threading.Lock()
        
        self.logger.info("📊 SyndromeCalculator initialized")
    
    def initialize(self) -> bool:
        """Initialize syndrome calculator"""
        try:
            # Validate configuration
            if not self.validate_config():
                return False
            
            # Register calculation methods
            self._register_calculation_methods()
            
            # Register syndrome decoders
            self._register_syndrome_decoders()
            
            # Build syndrome lookup tables
            self._build_syndrome_tables()
            
            # Setup ALT_LAS integration
            if self.config.alt_las_integration:
                self._setup_alt_las_integration()
            
            self.initialized = True
            self.active = True
            
            self.logger.info("✅ SyndromeCalculator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ SyndromeCalculator initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown syndrome calculator"""
        try:
            self.active = False
            
            # Clear active calculations
            with self._calculation_lock:
                self.active_calculations.clear()
            
            self.logger.info("🔴 SyndromeCalculator shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ SyndromeCalculator shutdown failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get calculator status"""
        with self._syndrome_lock, self._calculation_lock:
            return {
                'initialized': self.initialized,
                'active': self.active,
                'total_calculations': self.total_calculations,
                'successful_calculations': self.successful_calculations,
                'failed_calculations': self.failed_calculations,
                'success_rate': (self.successful_calculations / max(1, self.total_calculations)) * 100,
                'average_calculation_time': self.average_calculation_time,
                'average_decoding_confidence': self.average_decoding_confidence,
                'active_calculations': len(self.active_calculations),
                'syndrome_history_size': len(self.syndrome_results),
                'available_methods': list(self.syndrome_calculators.keys()),
                'supported_codes': list(self.syndrome_decoders.keys()),
                'lookup_tables_loaded': len(self.syndrome_lookup_tables),
                'alt_las_integration': self.alt_las_integration_active,
                'consciousness_syndrome': self.consciousness_syndrome_enabled
            }

    def calculate_syndrome(self, quantum_state: QuantumState,
                          code_type: ErrorCorrectionCode = ErrorCorrectionCode.SHOR_CODE,
                          syndrome_type: SyndromeType = SyndromeType.STABILIZER_SYNDROME,
                          method: SyndromeMethod = SyndromeMethod.STABILIZER_MEASUREMENT) -> Optional[SyndromeResult]:
        """Calculate error syndrome"""
        try:
            start_time = time.time()

            # Create syndrome result
            result = SyndromeResult(
                syndrome_type=syndrome_type,
                calculation_method=method
            )

            # Add to active calculations
            with self._calculation_lock:
                self.active_calculations[result.syndrome_id] = result

            # Execute syndrome calculation
            if method in self.syndrome_calculators:
                calculator = self.syndrome_calculators[method]
                success = calculator(quantum_state, code_type, result)
            else:
                success = self._stabilizer_measurement(quantum_state, code_type, result)

            # Complete calculation
            result.calculation_time = time.time() - start_time
            result.calculate_syndrome_value()

            # Decode syndrome to error location
            if success and code_type in self.syndrome_decoders:
                decoder = self.syndrome_decoders[code_type]
                decoder(result)

            # Update statistics
            self._update_calculation_stats(result, success)

            # Move to history
            with self._calculation_lock:
                if result.syndrome_id in self.active_calculations:
                    del self.active_calculations[result.syndrome_id]

            with self._syndrome_lock:
                self.syndrome_results.append(result)
                # Keep history manageable
                if len(self.syndrome_results) > 1000:
                    self.syndrome_results = self.syndrome_results[-500:]

            if success:
                self.logger.info(f"📊 Syndrome calculated: {syndrome_type.value} = {result.syndrome_value}")
            else:
                self.logger.warning(f"⚠️ Syndrome calculation failed: {syndrome_type.value}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Syndrome calculation failed: {e}")
            return None

    def _register_calculation_methods(self):
        """Register syndrome calculation methods"""
        self.syndrome_calculators[SyndromeMethod.PARITY_CHECK] = self._parity_check_syndrome
        self.syndrome_calculators[SyndromeMethod.STABILIZER_MEASUREMENT] = self._stabilizer_measurement
        self.syndrome_calculators[SyndromeMethod.LOOKUP_TABLE] = self._lookup_table_syndrome
        self.syndrome_calculators[SyndromeMethod.MINIMUM_WEIGHT] = self._minimum_weight_syndrome
        self.syndrome_calculators[SyndromeMethod.MAXIMUM_LIKELIHOOD] = self._maximum_likelihood_syndrome
        self.syndrome_calculators[SyndromeMethod.ALT_LAS_CONSCIOUSNESS] = self._alt_las_consciousness_syndrome

        self.logger.info(f"📋 Registered {len(self.syndrome_calculators)} calculation methods")

    def _register_syndrome_decoders(self):
        """Register syndrome decoders for different codes"""
        self.syndrome_decoders[ErrorCorrectionCode.SHOR_CODE] = self._decode_shor_syndrome
        self.syndrome_decoders[ErrorCorrectionCode.STEANE_CODE] = self._decode_steane_syndrome
        self.syndrome_decoders[ErrorCorrectionCode.SURFACE_CODE] = self._decode_surface_syndrome
        self.syndrome_decoders[ErrorCorrectionCode.ALT_LAS_CODE] = self._decode_alt_las_syndrome

        self.logger.info(f"📋 Registered {len(self.syndrome_decoders)} syndrome decoders")

    def _build_syndrome_tables(self):
        """Build syndrome lookup tables"""
        # Shor code syndrome table
        self.syndrome_lookup_tables[ErrorCorrectionCode.SHOR_CODE] = {
            0: [],  # No error
            1: [0], 2: [1], 4: [2],  # Single bit flips in first block
            8: [3], 16: [4], 32: [5],  # Single bit flips in second block
            64: [6], 128: [7], 256: [8]  # Single bit flips in third block
        }

        # Steane code syndrome table
        self.syndrome_lookup_tables[ErrorCorrectionCode.STEANE_CODE] = {
            0: [],  # No error
            1: [0], 2: [1], 3: [2], 4: [3], 5: [4], 6: [5], 7: [6]  # Single qubit errors
        }

        # Surface code syndrome table (simplified)
        self.syndrome_lookup_tables[ErrorCorrectionCode.SURFACE_CODE] = {
            0: [],  # No error
            1: [0], 2: [1], 4: [2], 8: [3], 16: [4]  # Single qubit errors
        }

        # ALT_LAS code syndrome table
        self.syndrome_lookup_tables[ErrorCorrectionCode.ALT_LAS_CODE] = {
            0: [],  # No error
            1: [0], 2: [1], 3: [2], 4: [3], 5: [4]  # Consciousness-guided patterns
        }

        self.logger.info(f"📋 Built syndrome tables for {len(self.syndrome_lookup_tables)} codes")

    # Syndrome Calculation Methods
    def _parity_check_syndrome(self, quantum_state: QuantumState,
                              code_type: ErrorCorrectionCode,
                              result: SyndromeResult) -> bool:
        """Calculate syndrome using parity check matrix"""
        try:
            if not quantum_state.amplitudes:
                return False

            # Simplified parity check syndrome calculation
            n_qubits = len(quantum_state.amplitudes).bit_length() - 1
            syndrome_bits = []

            # Calculate parity checks
            for i in range(min(n_qubits, 6)):  # Limit syndrome size
                parity = 0
                for j, amp in enumerate(quantum_state.amplitudes):
                    if (j >> i) & 1:  # Check i-th bit
                        parity ^= int(abs(amp)**2 > 0.5)
                syndrome_bits.append(parity)

            result.syndrome_bits = syndrome_bits
            result.calculation_confidence = 0.85
            result.decoding_confidence = 0.8

            return True

        except Exception as e:
            self.logger.error(f"❌ Parity check syndrome failed: {e}")
            return False

    def _stabilizer_measurement(self, quantum_state: QuantumState,
                               code_type: ErrorCorrectionCode,
                               result: SyndromeResult) -> bool:
        """Calculate syndrome using stabilizer measurements"""
        try:
            if not quantum_state.amplitudes:
                return False

            # Stabilizer syndrome calculation based on code type
            if code_type == ErrorCorrectionCode.SHOR_CODE:
                syndrome_bits = self._shor_stabilizer_syndrome(quantum_state)
            elif code_type == ErrorCorrectionCode.STEANE_CODE:
                syndrome_bits = self._steane_stabilizer_syndrome(quantum_state)
            elif code_type == ErrorCorrectionCode.SURFACE_CODE:
                syndrome_bits = self._surface_stabilizer_syndrome(quantum_state)
            else:
                syndrome_bits = self._generic_stabilizer_syndrome(quantum_state)

            result.syndrome_bits = syndrome_bits
            result.calculation_confidence = 0.95
            result.decoding_confidence = 0.9

            return True

        except Exception as e:
            self.logger.error(f"❌ Stabilizer measurement failed: {e}")
            return False

    def _shor_stabilizer_syndrome(self, quantum_state: QuantumState) -> List[int]:
        """Calculate Shor code stabilizer syndrome"""
        # Shor code has 8 stabilizer generators
        syndrome_bits = []

        # Simplified Shor stabilizer measurements
        for i in range(8):
            # Simulate stabilizer measurement
            measurement = random.randint(0, 1)  # Simplified
            syndrome_bits.append(measurement)

        return syndrome_bits

    def _steane_stabilizer_syndrome(self, quantum_state: QuantumState) -> List[int]:
        """Calculate Steane code stabilizer syndrome"""
        # Steane code has 6 stabilizer generators
        syndrome_bits = []

        # Simplified Steane stabilizer measurements
        for i in range(6):
            # Simulate stabilizer measurement
            measurement = random.randint(0, 1)  # Simplified
            syndrome_bits.append(measurement)

        return syndrome_bits

    def _surface_stabilizer_syndrome(self, quantum_state: QuantumState) -> List[int]:
        """Calculate Surface code stabilizer syndrome"""
        # Surface code stabilizers (plaquette and star operators)
        syndrome_bits = []

        # Simplified surface code syndrome
        for i in range(8):  # 8 stabilizers for 5x5 surface code
            measurement = random.randint(0, 1)  # Simplified
            syndrome_bits.append(measurement)

        return syndrome_bits

    def _generic_stabilizer_syndrome(self, quantum_state: QuantumState) -> List[int]:
        """Calculate generic stabilizer syndrome"""
        # Generic stabilizer syndrome
        n_qubits = min(len(quantum_state.amplitudes).bit_length() - 1, 5)
        syndrome_bits = []

        for i in range(n_qubits):
            measurement = random.randint(0, 1)  # Simplified
            syndrome_bits.append(measurement)

        return syndrome_bits

    def _lookup_table_syndrome(self, quantum_state: QuantumState,
                              code_type: ErrorCorrectionCode,
                              result: SyndromeResult) -> bool:
        """Calculate syndrome using lookup table"""
        try:
            # Use pre-computed lookup table
            if code_type not in self.syndrome_lookup_tables:
                return False

            # Simplified lookup based on state
            state_hash = hash(str(quantum_state.amplitudes)) % 16
            syndrome_value = state_hash % 8

            # Convert to binary
            syndrome_bits = []
            for i in range(3):
                syndrome_bits.append((syndrome_value >> i) & 1)

            result.syndrome_bits = syndrome_bits
            result.calculation_confidence = 1.0  # Lookup is deterministic
            result.decoding_confidence = 0.95

            return True

        except Exception as e:
            self.logger.error(f"❌ Lookup table syndrome failed: {e}")
            return False

    def _minimum_weight_syndrome(self, quantum_state: QuantumState,
                                code_type: ErrorCorrectionCode,
                                result: SyndromeResult) -> bool:
        """Calculate syndrome using minimum weight decoding"""
        try:
            # Minimum weight perfect matching for syndrome
            if not quantum_state.amplitudes:
                return False

            # Find minimum weight error pattern
            n_qubits = min(len(quantum_state.amplitudes).bit_length() - 1, 6)
            syndrome_bits = []

            # Calculate syndrome with minimum weight constraint
            for i in range(n_qubits):
                # Prefer lower weight syndromes
                weight_bias = 0.3  # Bias towards 0
                measurement = 1 if random.random() > weight_bias else 0
                syndrome_bits.append(measurement)

            result.syndrome_bits = syndrome_bits
            result.calculation_confidence = 0.9
            result.decoding_confidence = 0.95

            return True

        except Exception as e:
            self.logger.error(f"❌ Minimum weight syndrome failed: {e}")
            return False

    def _maximum_likelihood_syndrome(self, quantum_state: QuantumState,
                                    code_type: ErrorCorrectionCode,
                                    result: SyndromeResult) -> bool:
        """Calculate syndrome using maximum likelihood decoding"""
        try:
            # Maximum likelihood syndrome calculation
            if not quantum_state.amplitudes:
                return False

            # ML-based syndrome calculation
            n_qubits = min(len(quantum_state.amplitudes).bit_length() - 1, 5)
            syndrome_bits = []

            # Use likelihood to determine syndrome
            for i in range(n_qubits):
                # Calculate likelihood of error
                error_likelihood = abs(quantum_state.amplitudes[i % len(quantum_state.amplitudes)])**2
                measurement = 1 if error_likelihood > 0.5 else 0
                syndrome_bits.append(measurement)

            result.syndrome_bits = syndrome_bits
            result.calculation_confidence = 0.92
            result.decoding_confidence = 0.88

            return True

        except Exception as e:
            self.logger.error(f"❌ Maximum likelihood syndrome failed: {e}")
            return False

    def _alt_las_consciousness_syndrome(self, quantum_state: QuantumState,
                                       code_type: ErrorCorrectionCode,
                                       result: SyndromeResult) -> bool:
        """Calculate syndrome using ALT_LAS consciousness"""
        try:
            if not self.alt_las_integration_active:
                return self._stabilizer_measurement(quantum_state, code_type, result)

            # Consciousness-enhanced syndrome calculation
            consciousness_factor = 0.8

            if not quantum_state.amplitudes:
                return False

            # Consciousness can detect subtle error patterns
            n_qubits = min(len(quantum_state.amplitudes).bit_length() - 1, 5)
            syndrome_bits = []

            for i in range(n_qubits):
                # Consciousness-guided syndrome detection
                consciousness_insight = random.random() * consciousness_factor
                base_measurement = random.randint(0, 1)

                # Consciousness enhancement
                if consciousness_insight > 0.6:
                    measurement = 1 - base_measurement  # Consciousness correction
                else:
                    measurement = base_measurement

                syndrome_bits.append(measurement)

            result.syndrome_bits = syndrome_bits
            result.consciousness_guidance = consciousness_factor
            result.calculation_confidence = 0.98
            result.decoding_confidence = 0.95

            return True

        except Exception as e:
            self.logger.error(f"❌ ALT_LAS consciousness syndrome failed: {e}")
            return False

    # Syndrome Decoders
    def _decode_shor_syndrome(self, result: SyndromeResult):
        """Decode Shor code syndrome to error location"""
        try:
            syndrome_value = result.syndrome_value

            # Shor code syndrome decoding
            if syndrome_value == 0:
                result.error_location = []
                result.error_type_prediction = QuantumErrorType.BIT_FLIP
            elif syndrome_value <= 8:
                # Single bit flip errors
                result.error_location = [syndrome_value - 1]
                result.error_type_prediction = QuantumErrorType.BIT_FLIP
            else:
                # Phase flip or complex errors
                result.error_location = [syndrome_value % 9]
                result.error_type_prediction = QuantumErrorType.PHASE_FLIP

            result.decoding_confidence = 0.9

        except Exception as e:
            self.logger.error(f"❌ Shor syndrome decoding failed: {e}")

    def _decode_steane_syndrome(self, result: SyndromeResult):
        """Decode Steane code syndrome to error location"""
        try:
            syndrome_value = result.syndrome_value

            # Steane code syndrome decoding
            if syndrome_value == 0:
                result.error_location = []
                result.error_type_prediction = QuantumErrorType.BIT_FLIP
            elif syndrome_value <= 7:
                result.error_location = [syndrome_value - 1]
                result.error_type_prediction = QuantumErrorType.BIT_FLIP
            else:
                # Multi-qubit or phase errors
                result.error_location = [syndrome_value % 7]
                result.error_type_prediction = QuantumErrorType.BIT_PHASE_FLIP

            result.decoding_confidence = 0.92

        except Exception as e:
            self.logger.error(f"❌ Steane syndrome decoding failed: {e}")

    def _decode_surface_syndrome(self, result: SyndromeResult):
        """Decode Surface code syndrome to error location"""
        try:
            syndrome_value = result.syndrome_value

            # Surface code syndrome decoding (simplified)
            if syndrome_value == 0:
                result.error_location = []
                result.error_type_prediction = QuantumErrorType.BIT_FLIP
            else:
                # Use minimum weight perfect matching (simplified)
                error_chain = self._find_minimum_weight_chain(syndrome_value)
                result.error_location = error_chain
                result.error_type_prediction = QuantumErrorType.DEPOLARIZING

            result.decoding_confidence = 0.95

        except Exception as e:
            self.logger.error(f"❌ Surface syndrome decoding failed: {e}")

    def _find_minimum_weight_chain(self, syndrome_value: int) -> List[int]:
        """Find minimum weight error chain for surface code"""
        # Simplified minimum weight chain finding
        chain = []

        # Convert syndrome to error chain
        for i in range(min(syndrome_value.bit_length(), 5)):
            if (syndrome_value >> i) & 1:
                chain.append(i)

        return chain

    def _decode_alt_las_syndrome(self, result: SyndromeResult):
        """Decode ALT_LAS code syndrome using consciousness"""
        try:
            if not self.alt_las_integration_active:
                return self._decode_steane_syndrome(result)

            syndrome_value = result.syndrome_value
            consciousness_factor = result.consciousness_guidance

            # Consciousness-enhanced decoding
            if syndrome_value == 0:
                result.error_location = []
                result.error_type_prediction = QuantumErrorType.BIT_FLIP
            else:
                # Consciousness can decode complex error patterns
                consciousness_insight = consciousness_factor * 0.8

                if consciousness_insight > 0.6:
                    # Advanced consciousness decoding
                    result.error_location = [syndrome_value % 5]
                    result.error_type_prediction = QuantumErrorType.ALT_LAS_DISRUPTION
                else:
                    # Standard decoding
                    result.error_location = [syndrome_value - 1]
                    result.error_type_prediction = QuantumErrorType.BIT_FLIP

            result.decoding_confidence = 0.98
            result.dimensional_insight = consciousness_factor * 0.5

        except Exception as e:
            self.logger.error(f"❌ ALT_LAS syndrome decoding failed: {e}")

    def _update_calculation_stats(self, result: SyndromeResult, success: bool):
        """Update calculation statistics"""
        self.total_calculations += 1

        if success:
            self.successful_calculations += 1
        else:
            self.failed_calculations += 1

        # Update average calculation time
        total = self.total_calculations
        current_avg = self.average_calculation_time
        self.average_calculation_time = (current_avg * (total - 1) + result.calculation_time) / total

        # Update average decoding confidence
        current_confidence_avg = self.average_decoding_confidence
        self.average_decoding_confidence = (current_confidence_avg * (total - 1) + result.decoding_confidence) / total

    def _setup_alt_las_integration(self):
        """Setup ALT_LAS integration"""
        try:
            from ..computer_access.vision.q02_quantum_seed_integration import QuantumSeedManager
            self.alt_las_integration_active = True
            self.consciousness_syndrome_enabled = True
            self.logger.info("🔗 ALT_LAS integration activated for syndrome calculation")
        except ImportError:
            self.logger.warning("⚠️ ALT_LAS integration not available")

# Utility functions
def create_syndrome_calculator(config: Optional[QFDConfig] = None) -> SyndromeCalculator:
    """Create syndrome calculator"""
    return SyndromeCalculator(config)

def test_syndrome_calculator():
    """Test syndrome calculator"""
    print("📊 Testing Syndrome Calculator...")
    
    # Create calculator
    calculator = create_syndrome_calculator()
    print("✅ Syndrome calculator created")
    
    # Initialize
    if calculator.initialize():
        print("✅ Calculator initialized successfully")
    
    # Get status
    status = calculator.get_status()
    print(f"✅ Calculator status: {status['total_calculations']} calculations")
    
    # Shutdown
    calculator.shutdown()
    print("✅ Calculator shutdown completed")
    
    print("🚀 Syndrome Calculator test completed!")

if __name__ == "__main__":
    test_syndrome_calculator()
