"""
🔮 Probability Amplitude Calculator - Q05.1.2 Component

Kuantum olasılık genlik hesaplamaları ve analizi.
ALT_LAS Quantum Mind OS ile entegre çalışır.

Bu modül Q05.1.2 görevinin üçüncü parçasıdır:
- Probability amplitude calculations ✅
- Born rule implementations
- Interference pattern analysis
- Quantum probability distributions

Author: Orion Vision Core Team
Sprint: Q05.1.2 - Kuantum Süperpozisyon Yönetimi
Status: IN_PROGRESS
"""

import logging
import threading
import math
import cmath
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Callable
import uuid

from .qfd_base import QFDBase, QFDConfig, QuantumEntity, EntityType, QFDException
from .quantum_field import QuantumState, QuantumField, FieldType

# Probability Calculation Types
class ProbabilityType(Enum):
    """Olasılık hesaplama türleri"""
    BORN_RULE = "born_rule"                    # Born kuralı
    CONDITIONAL = "conditional"                # Koşullu olasılık
    JOINT = "joint"                           # Birleşik olasılık
    MARGINAL = "marginal"                     # Marjinal olasılık
    INTERFERENCE = "interference"              # Girişim deseni
    ENTANGLEMENT = "entanglement"             # Dolaşıklık olasılığı
    ALT_LAS_WEIGHTED = "alt_las_weighted"     # ALT_LAS ağırlıklı

# Analysis Methods
class AnalysisMethod(Enum):
    """Analiz yöntemleri"""
    STATISTICAL = "statistical"               # İstatistiksel analiz
    BAYESIAN = "bayesian"                     # Bayesian analiz
    MAXIMUM_LIKELIHOOD = "maximum_likelihood"  # Maksimum olabilirlik
    QUANTUM_FISHER = "quantum_fisher"         # Quantum Fisher bilgisi
    FIDELITY_BASED = "fidelity_based"        # Fidelity tabanlı
    ALT_LAS_CONSCIOUSNESS = "alt_las_consciousness" # ALT_LAS bilinç

@dataclass
class ProbabilityResult:
    """Olasılık hesaplama sonucu"""
    
    calculation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    probability_type: ProbabilityType = ProbabilityType.BORN_RULE
    analysis_method: AnalysisMethod = AnalysisMethod.STATISTICAL
    
    # Calculation details
    timestamp: datetime = field(default_factory=datetime.now)
    computation_time: float = 0.0
    
    # Results
    probabilities: List[float] = field(default_factory=list)
    amplitudes: List[complex] = field(default_factory=list)
    phases: List[float] = field(default_factory=list)
    
    # Statistical measures
    mean_probability: float = 0.0
    variance: float = 0.0
    entropy: float = 0.0
    purity: float = 0.0
    
    # Quantum measures
    coherence: float = 0.0
    entanglement_measure: float = 0.0
    quantum_fidelity: float = 0.0
    
    # Interference analysis
    interference_visibility: float = 0.0
    interference_pattern: List[float] = field(default_factory=list)
    
    # ALT_LAS integration
    consciousness_weight: float = 0.0
    alt_las_seed: Optional[str] = None
    
    # Metadata
    basis_states: List[str] = field(default_factory=list)
    measurement_basis: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_statistics(self):
        """Calculate statistical measures"""
        if not self.probabilities:
            return
        
        # Mean and variance
        self.mean_probability = sum(self.probabilities) / len(self.probabilities)
        self.variance = sum((p - self.mean_probability)**2 for p in self.probabilities) / len(self.probabilities)
        
        # Entropy (Shannon)
        self.entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in self.probabilities)
        
        # Purity
        self.purity = sum(p**2 for p in self.probabilities)
        
        # Coherence (from amplitudes)
        if self.amplitudes:
            coherence_sum = 0.0
            for i in range(len(self.amplitudes)):
                for j in range(i+1, len(self.amplitudes)):
                    coherence_sum += abs(self.amplitudes[i] * self.amplitudes[j].conjugate())
            self.coherence = coherence_sum / (len(self.amplitudes) * (len(self.amplitudes) - 1) / 2) if len(self.amplitudes) > 1 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'calculation_id': self.calculation_id,
            'probability_type': self.probability_type.value,
            'analysis_method': self.analysis_method.value,
            'timestamp': self.timestamp.isoformat(),
            'computation_time': self.computation_time,
            'probabilities': self.probabilities,
            'mean_probability': self.mean_probability,
            'variance': self.variance,
            'entropy': self.entropy,
            'purity': self.purity,
            'coherence': self.coherence,
            'entanglement_measure': self.entanglement_measure,
            'quantum_fidelity': self.quantum_fidelity,
            'interference_visibility': self.interference_visibility,
            'consciousness_weight': self.consciousness_weight,
            'basis_states': self.basis_states,
            'measurement_basis': self.measurement_basis,
            'metadata': self.metadata
        }

class ProbabilityCalculator(QFDBase):
    """
    Kuantum olasılık genlik hesaplayıcısı
    
    Q05.1.2 görevinin üçüncü bileşeni. Kuantum durumlarının
    olasılık genliklerini hesaplar, Born kuralını uygular ve
    ALT_LAS bilinç sistemi ile entegre çalışır.
    """
    
    def __init__(self, config: Optional[QFDConfig] = None):
        super().__init__(config)
        
        # Calculation management
        self.calculation_history: List[ProbabilityResult] = []
        self.active_calculations: Dict[str, ProbabilityResult] = {}
        
        # Calculation methods
        self.probability_methods: Dict[ProbabilityType, Callable] = {}
        self.analysis_methods: Dict[AnalysisMethod, Callable] = {}
        
        # Precision settings
        self.calculation_precision = 1e-10
        self.normalization_tolerance = 1e-8
        self.phase_precision = 1e-6
        
        # Performance tracking
        self.total_calculations = 0
        self.successful_calculations = 0
        self.failed_calculations = 0
        self.average_calculation_time = 0.0
        
        # ALT_LAS integration
        self.alt_las_integration_active = False
        self.consciousness_weighting_enabled = False
        
        # Threading
        self._calc_lock = threading.Lock()
        self._history_lock = threading.Lock()
        
        self.logger.info("🔮 ProbabilityCalculator initialized")
    
    def initialize(self) -> bool:
        """Initialize probability calculator"""
        try:
            # Validate configuration
            if not self.validate_config():
                return False
            
            # Register calculation methods
            self._register_probability_methods()
            self._register_analysis_methods()
            
            # Setup ALT_LAS integration
            if self.config.alt_las_integration:
                self._setup_alt_las_integration()
            
            self.initialized = True
            self.active = True
            
            self.logger.info("✅ ProbabilityCalculator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ProbabilityCalculator initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown probability calculator"""
        try:
            self.active = False
            
            # Clear active calculations
            with self._calc_lock:
                self.active_calculations.clear()
            
            self.logger.info("🔴 ProbabilityCalculator shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ProbabilityCalculator shutdown failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get calculator status"""
        with self._calc_lock, self._history_lock:
            return {
                'initialized': self.initialized,
                'active': self.active,
                'total_calculations': self.total_calculations,
                'successful_calculations': self.successful_calculations,
                'failed_calculations': self.failed_calculations,
                'success_rate': (self.successful_calculations / max(1, self.total_calculations)) * 100,
                'average_calculation_time': self.average_calculation_time,
                'active_calculations': len(self.active_calculations),
                'calculation_history_size': len(self.calculation_history),
                'available_probability_methods': list(self.probability_methods.keys()),
                'available_analysis_methods': list(self.analysis_methods.keys()),
                'calculation_precision': self.calculation_precision,
                'alt_las_integration': self.alt_las_integration_active,
                'consciousness_weighting': self.consciousness_weighting_enabled
            }
    
    def calculate_probabilities(self, quantum_state: QuantumState,
                              probability_type: ProbabilityType = ProbabilityType.BORN_RULE,
                              analysis_method: AnalysisMethod = AnalysisMethod.STATISTICAL,
                              measurement_basis: Optional[str] = None) -> Optional[ProbabilityResult]:
        """Calculate quantum probabilities"""
        try:
            start_time = datetime.now()
            
            # Create result object
            result = ProbabilityResult(
                probability_type=probability_type,
                analysis_method=analysis_method,
                measurement_basis=measurement_basis,
                basis_states=getattr(quantum_state, 'basis_states', []),
                alt_las_seed=getattr(quantum_state, 'alt_las_seed', None)
            )
            
            # Add to active calculations
            with self._calc_lock:
                self.active_calculations[result.calculation_id] = result
            
            # Execute probability calculation
            if probability_type in self.probability_methods:
                prob_method = self.probability_methods[probability_type]
                success = prob_method(quantum_state, result)
            else:
                success = self._born_rule_calculation(quantum_state, result)
            
            if not success:
                raise QFDException(f"Probability calculation failed: {probability_type.value}")
            
            # Execute analysis
            if analysis_method in self.analysis_methods:
                analysis_func = self.analysis_methods[analysis_method]
                analysis_func(result)
            else:
                self._statistical_analysis(result)
            
            # Calculate statistics
            result.calculate_statistics()
            
            # Complete calculation
            end_time = datetime.now()
            result.computation_time = (end_time - start_time).total_seconds()
            
            # Update statistics
            self._update_calculation_stats(result.computation_time, True)
            
            # Move to history
            with self._calc_lock:
                if result.calculation_id in self.active_calculations:
                    del self.active_calculations[result.calculation_id]
            
            with self._history_lock:
                self.calculation_history.append(result)
                # Keep history manageable
                if len(self.calculation_history) > 1000:
                    self.calculation_history = self.calculation_history[-500:]
            
            self.logger.info(f"✅ Probability calculation completed: {probability_type.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Probability calculation failed: {e}")
            self._update_calculation_stats(0.0, False)
            return None
    
    def _register_probability_methods(self):
        """Register probability calculation methods"""
        self.probability_methods[ProbabilityType.BORN_RULE] = self._born_rule_calculation
        self.probability_methods[ProbabilityType.CONDITIONAL] = self._conditional_probability
        self.probability_methods[ProbabilityType.JOINT] = self._conditional_probability  # Simplified
        self.probability_methods[ProbabilityType.MARGINAL] = self._conditional_probability  # Simplified
        self.probability_methods[ProbabilityType.INTERFERENCE] = self._interference_probability
        self.probability_methods[ProbabilityType.ENTANGLEMENT] = self._entanglement_probability
        self.probability_methods[ProbabilityType.ALT_LAS_WEIGHTED] = self._alt_las_weighted_probability
        
        self.logger.info(f"📋 Registered {len(self.probability_methods)} probability methods")
    
    def _register_analysis_methods(self):
        """Register analysis methods"""
        self.analysis_methods[AnalysisMethod.STATISTICAL] = self._statistical_analysis
        self.analysis_methods[AnalysisMethod.BAYESIAN] = self._bayesian_analysis
        self.analysis_methods[AnalysisMethod.MAXIMUM_LIKELIHOOD] = self._maximum_likelihood_analysis
        self.analysis_methods[AnalysisMethod.QUANTUM_FISHER] = self._quantum_fisher_analysis
        self.analysis_methods[AnalysisMethod.FIDELITY_BASED] = self._fidelity_based_analysis
        self.analysis_methods[AnalysisMethod.ALT_LAS_CONSCIOUSNESS] = self._alt_las_consciousness_analysis
        
        self.logger.info(f"📋 Registered {len(self.analysis_methods)} analysis methods")
    
    def _born_rule_calculation(self, quantum_state: QuantumState, result: ProbabilityResult) -> bool:
        """Born rule probability calculation"""
        try:
            if not quantum_state.amplitudes:
                return False
            
            # Calculate probabilities using Born rule: P(i) = |ψ_i|²
            result.amplitudes = quantum_state.amplitudes.copy()
            result.probabilities = [abs(amp)**2 for amp in quantum_state.amplitudes]
            result.phases = [cmath.phase(amp) for amp in quantum_state.amplitudes]
            
            # Verify normalization
            total_prob = sum(result.probabilities)
            if abs(total_prob - 1.0) > self.normalization_tolerance:
                self.logger.warning(f"⚠️ Probability normalization error: {total_prob}")
                # Renormalize
                result.probabilities = [p / total_prob for p in result.probabilities]
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Born rule calculation failed: {e}")
            return False
    
    def _conditional_probability(self, quantum_state: QuantumState, result: ProbabilityResult) -> bool:
        """Conditional probability calculation"""
        try:
            # P(A|B) calculation - simplified implementation
            if not self._born_rule_calculation(quantum_state, result):
                return False
            
            # Apply conditional weighting (example implementation)
            condition_weight = result.metadata.get('condition_weight', 0.5)
            weighted_probs = []
            
            for i, prob in enumerate(result.probabilities):
                if i % 2 == 0:  # Even indices as condition
                    weighted_probs.append(prob * condition_weight)
                else:
                    weighted_probs.append(prob * (1.0 - condition_weight))
            
            # Renormalize
            total = sum(weighted_probs)
            result.probabilities = [p / total for p in weighted_probs]
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Conditional probability calculation failed: {e}")
            return False
    
    def _interference_probability(self, quantum_state: QuantumState, result: ProbabilityResult) -> bool:
        """Interference pattern probability calculation"""
        try:
            if not self._born_rule_calculation(quantum_state, result):
                return False
            
            # Calculate interference terms
            interference_pattern = []
            n = len(quantum_state.amplitudes)
            
            for k in range(n * 2):  # Extended pattern
                interference_value = 0.0
                for i in range(n):
                    for j in range(n):
                        if i != j:
                            phase_diff = cmath.phase(quantum_state.amplitudes[i]) - cmath.phase(quantum_state.amplitudes[j])
                            interference_value += abs(quantum_state.amplitudes[i]) * abs(quantum_state.amplitudes[j]) * math.cos(phase_diff + k * math.pi / n)
                
                interference_pattern.append(interference_value)
            
            result.interference_pattern = interference_pattern
            
            # Calculate visibility
            if interference_pattern:
                max_val = max(interference_pattern)
                min_val = min(interference_pattern)
                result.interference_visibility = (max_val - min_val) / (max_val + min_val) if (max_val + min_val) > 0 else 0.0
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Interference probability calculation failed: {e}")
            return False
    
    def _alt_las_weighted_probability(self, quantum_state: QuantumState, result: ProbabilityResult) -> bool:
        """ALT_LAS consciousness-weighted probability calculation"""
        try:
            if not self.alt_las_integration_active:
                return self._born_rule_calculation(quantum_state, result)
            
            # Start with Born rule
            if not self._born_rule_calculation(quantum_state, result):
                return False
            
            # Apply consciousness weighting
            consciousness_level = getattr(quantum_state, 'consciousness_level', 0.5)
            result.consciousness_weight = consciousness_level
            
            # Weight probabilities based on consciousness
            weighted_probs = []
            for i, prob in enumerate(result.probabilities):
                # Higher consciousness favors higher-index states (more complex)
                consciousness_factor = 1.0 + consciousness_level * (i / len(result.probabilities))
                weighted_probs.append(prob * consciousness_factor)
            
            # Renormalize
            total = sum(weighted_probs)
            result.probabilities = [p / total for p in weighted_probs]
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ALT_LAS weighted probability calculation failed: {e}")
            return False
    
    def _statistical_analysis(self, result: ProbabilityResult):
        """Statistical analysis of probabilities"""
        if not result.probabilities:
            return
        
        # Already calculated in calculate_statistics()
        # Additional statistical measures can be added here
        pass
    
    def _quantum_fisher_analysis(self, result: ProbabilityResult):
        """Quantum Fisher information analysis"""
        if not result.amplitudes or len(result.amplitudes) < 2:
            return
        
        # Simplified quantum Fisher information calculation
        fisher_info = 0.0
        for i in range(len(result.amplitudes)):
            prob = result.probabilities[i]
            if prob > 0:
                # Derivative approximation
                derivative = abs(result.amplitudes[i]) * 2  # Simplified
                fisher_info += (derivative**2) / prob
        
        result.metadata['quantum_fisher_information'] = fisher_info
    
    def _alt_las_consciousness_analysis(self, result: ProbabilityResult):
        """ALT_LAS consciousness-based analysis"""
        if not self.alt_las_integration_active:
            return
        
        # Consciousness coherence measure
        consciousness_coherence = result.consciousness_weight * result.coherence
        result.metadata['consciousness_coherence'] = consciousness_coherence
        
        # Consciousness entropy
        if result.probabilities:
            consciousness_entropy = -sum(p * math.log2(p) * result.consciousness_weight if p > 0 else 0 
                                        for p in result.probabilities)
            result.metadata['consciousness_entropy'] = consciousness_entropy
    
    def _setup_alt_las_integration(self):
        """Setup ALT_LAS integration"""
        try:
            from ..computer_access.vision.q02_quantum_seed_integration import QuantumSeedManager
            self.alt_las_integration_active = True
            self.consciousness_weighting_enabled = True
            self.logger.info("🔗 ALT_LAS integration activated for probability calculations")
        except ImportError:
            self.logger.warning("⚠️ ALT_LAS integration not available")
    
    def _update_calculation_stats(self, duration: float, success: bool):
        """Update calculation statistics"""
        self.total_calculations += 1
        if success:
            self.successful_calculations += 1
        else:
            self.failed_calculations += 1
        
        # Update average time
        total = self.total_calculations
        current_avg = self.average_calculation_time
        self.average_calculation_time = (current_avg * (total - 1) + duration) / total

# Utility functions
def create_probability_calculator(config: Optional[QFDConfig] = None) -> ProbabilityCalculator:
    """Create probability calculator"""
    return ProbabilityCalculator(config)

def test_probability_calculator():
    """Test probability calculator"""
    print("🔮 Testing Probability Calculator...")
    
    # Create calculator
    calculator = create_probability_calculator()
    print("✅ Probability calculator created")
    
    # Initialize
    if calculator.initialize():
        print("✅ Calculator initialized successfully")
    
    # Create test quantum state
    from .quantum_field import QuantumState
    test_state = QuantumState(
        amplitudes=[0.6 + 0.3j, 0.7 - 0.2j, 0.1 + 0.1j],
        basis_states=['|0⟩', '|1⟩', '|2⟩']
    )
    print(f"✅ Test quantum state created: {len(test_state.amplitudes)} amplitudes")
    
    # Test different probability calculations
    prob_types = [
        ProbabilityType.BORN_RULE,
        ProbabilityType.INTERFERENCE,
        ProbabilityType.ALT_LAS_WEIGHTED
    ]
    
    for prob_type in prob_types:
        result = calculator.calculate_probabilities(
            test_state,
            prob_type,
            AnalysisMethod.STATISTICAL
        )
        
        if result:
            print(f"✅ {prob_type.value}: entropy={result.entropy:.3f}, coherence={result.coherence:.3f}")
    
    # Get status
    status = calculator.get_status()
    print(f"✅ Calculator status: {status['successful_calculations']} successful calculations")
    
    print("🚀 Probability Calculator test completed!")

if __name__ == "__main__":
    test_probability_calculator()
