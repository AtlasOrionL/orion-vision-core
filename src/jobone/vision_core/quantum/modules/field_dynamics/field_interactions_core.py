"""
⚛️ Field Interactions Core - Q05.3.1 Core Implementation

Core classes and data structures for Field Interaction Modeling
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q05.3.1 Field Interaction Modeling
Priority: CRITICAL - Modular Design Refactoring Phase 12
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

# Interaction Types
class InteractionType(Enum):
    """Etkileşim türleri"""
    LINEAR_COUPLING = "linear_coupling"       # Linear coupling
    NONLINEAR_COUPLING = "nonlinear_coupling" # Nonlinear coupling
    INTERFERENCE = "interference"             # Quantum interference
    ENTANGLEMENT = "entanglement"            # Field entanglement
    RESONANCE = "resonance"                  # Resonant coupling
    ALT_LAS_CONSCIOUSNESS = "alt_las_consciousness" # Consciousness interaction

# Coupling Mechanisms
class CouplingMechanism(Enum):
    """Bağlaşım mekanizmaları"""
    DIRECT_COUPLING = "direct_coupling"       # Direct field coupling
    EXCHANGE_COUPLING = "exchange_coupling"   # Exchange interaction
    DIPOLE_COUPLING = "dipole_coupling"       # Dipole-dipole
    SPIN_ORBIT = "spin_orbit"                # Spin-orbit coupling
    HYPERFINE = "hyperfine"                  # Hyperfine interaction
    ALT_LAS_BRIDGE = "alt_las_bridge"        # ALT_LAS consciousness bridge

@dataclass
class InteractionParameters:
    """Etkileşim parametreleri"""
    
    interaction_type: InteractionType = InteractionType.LINEAR_COUPLING
    coupling_mechanism: CouplingMechanism = CouplingMechanism.DIRECT_COUPLING
    
    # Coupling parameters
    coupling_strength: float = 1.0           # Coupling strength
    coupling_range: float = 1.0              # Interaction range
    coupling_frequency: float = 1.0          # Coupling frequency
    
    # Field parameters
    field_count: int = 2                     # Number of interacting fields
    field_dimensions: List[int] = field(default_factory=lambda: [2, 2])
    
    # Interaction dynamics
    interaction_time: float = 1.0            # Interaction duration
    time_steps: int = 100                    # Time steps
    
    # Nonlinear parameters
    nonlinearity_strength: float = 0.0       # Nonlinear coupling strength
    self_interaction: float = 0.0            # Self-interaction strength
    
    # ALT_LAS parameters
    consciousness_mediation: float = 0.0      # Consciousness-mediated interaction
    dimensional_bridging: float = 0.0        # Cross-dimensional coupling
    alt_las_seed: Optional[str] = None
    
    def get_coupling_efficiency_estimate(self) -> float:
        """Estimate coupling efficiency based on parameters"""
        base_efficiency = 1.0
        
        # Reduce efficiency for nonlinear interactions
        if self.nonlinearity_strength > 0:
            base_efficiency *= (1.0 - self.nonlinearity_strength * 0.2)
        
        # Enhance efficiency with consciousness mediation
        if self.consciousness_mediation > 0:
            base_efficiency *= (1.0 + self.consciousness_mediation * 0.1)
        
        return min(1.0, max(0.0, base_efficiency))
    
    def get_interaction_complexity(self) -> int:
        """Get interaction complexity score (1-5)"""
        complexity = 1
        
        if self.interaction_type == InteractionType.NONLINEAR_COUPLING:
            complexity += 2
        elif self.interaction_type == InteractionType.ENTANGLEMENT:
            complexity += 3
        elif self.interaction_type == InteractionType.ALT_LAS_CONSCIOUSNESS:
            complexity += 4
        
        if self.nonlinearity_strength > 0.5:
            complexity += 1
        
        if self.consciousness_mediation > 0.5:
            complexity += 1
        
        return min(5, complexity)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get interaction parameters summary"""
        return {
            'interaction_type': self.interaction_type.value,
            'coupling_mechanism': self.coupling_mechanism.value,
            'coupling_strength': self.coupling_strength,
            'field_count': self.field_count,
            'time_steps': self.time_steps,
            'nonlinearity_strength': self.nonlinearity_strength,
            'consciousness_mediation': self.consciousness_mediation,
            'efficiency_estimate': self.get_coupling_efficiency_estimate(),
            'complexity': self.get_interaction_complexity()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'interaction_type': self.interaction_type.value,
            'coupling_mechanism': self.coupling_mechanism.value,
            'coupling_strength': self.coupling_strength,
            'coupling_range': self.coupling_range,
            'coupling_frequency': self.coupling_frequency,
            'field_count': self.field_count,
            'field_dimensions': self.field_dimensions,
            'interaction_time': self.interaction_time,
            'time_steps': self.time_steps,
            'nonlinearity_strength': self.nonlinearity_strength,
            'self_interaction': self.self_interaction,
            'consciousness_mediation': self.consciousness_mediation,
            'dimensional_bridging': self.dimensional_bridging,
            'alt_las_seed': self.alt_las_seed,
            'efficiency_estimate': self.get_coupling_efficiency_estimate(),
            'complexity': self.get_interaction_complexity()
        }

@dataclass
class InteractionResult:
    """Etkileşim sonucu"""
    
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    interaction_type: InteractionType = InteractionType.LINEAR_COUPLING
    
    # Field states (simplified for core)
    initial_field_count: int = 0
    final_field_count: int = 0
    interaction_steps: int = 0
    
    # Interaction metrics
    coupling_efficiency: float = 1.0         # How efficiently fields couple
    energy_transfer: float = 0.0             # Energy transferred between fields
    entanglement_generation: float = 0.0     # Generated entanglement
    coherence_preservation: float = 1.0      # Coherence preservation
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    interaction_time: float = 0.0
    computation_time: float = 0.0
    
    # ALT_LAS factors
    consciousness_enhancement: float = 0.0
    dimensional_transcendence: float = 0.0
    
    # Success metrics
    interaction_successful: bool = True
    error_message: str = ""
    
    def get_interaction_quality(self) -> float:
        """Calculate overall interaction quality (0-1)"""
        quality_factors = [
            self.coupling_efficiency,
            self.coherence_preservation,
            1.0 - abs(self.energy_transfer) * 0.1,  # Penalize excessive energy transfer
            self.entanglement_generation * 0.5      # Bonus for entanglement
        ]
        
        # Add consciousness enhancement bonus
        if self.consciousness_enhancement > 0:
            quality_factors.append(1.0 + self.consciousness_enhancement * 0.2)
        
        return min(1.0, sum(quality_factors) / len(quality_factors))
    
    def get_interaction_grade(self) -> str:
        """Get interaction quality grade"""
        quality = self.get_interaction_quality()
        
        if quality >= 0.9:
            return "Excellent"
        elif quality >= 0.7:
            return "Good"
        elif quality >= 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def get_performance_score(self) -> float:
        """Get performance score considering time and quality"""
        quality = self.get_interaction_quality()
        
        # Penalize long computation times
        time_penalty = min(1.0, self.computation_time / 10.0)  # 10s reference
        performance = quality * (1.0 - time_penalty * 0.3)
        
        return max(0.0, performance)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get interaction result summary"""
        return {
            'result_id': self.result_id[:8] + "...",
            'type': self.interaction_type.value,
            'successful': self.interaction_successful,
            'coupling_efficiency': self.coupling_efficiency,
            'energy_transfer': self.energy_transfer,
            'entanglement_generation': self.entanglement_generation,
            'coherence_preservation': self.coherence_preservation,
            'quality': self.get_interaction_quality(),
            'grade': self.get_interaction_grade(),
            'performance_score': self.get_performance_score(),
            'computation_time_ms': self.computation_time * 1000,
            'consciousness_enhanced': self.consciousness_enhancement > 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'result_id': self.result_id,
            'interaction_type': self.interaction_type.value,
            'initial_field_count': self.initial_field_count,
            'final_field_count': self.final_field_count,
            'interaction_steps': self.interaction_steps,
            'coupling_efficiency': self.coupling_efficiency,
            'energy_transfer': self.energy_transfer,
            'entanglement_generation': self.entanglement_generation,
            'coherence_preservation': self.coherence_preservation,
            'interaction_quality': self.get_interaction_quality(),
            'interaction_grade': self.get_interaction_grade(),
            'performance_score': self.get_performance_score(),
            'timestamp': self.timestamp.isoformat(),
            'interaction_time': self.interaction_time,
            'computation_time': self.computation_time,
            'consciousness_enhancement': self.consciousness_enhancement,
            'dimensional_transcendence': self.dimensional_transcendence,
            'interaction_successful': self.interaction_successful,
            'error_message': self.error_message
        }

# Utility functions
def create_interaction_parameters(interaction_type: InteractionType = InteractionType.LINEAR_COUPLING,
                                coupling_strength: float = 1.0,
                                field_count: int = 2) -> InteractionParameters:
    """Create interaction parameters with default values"""
    return InteractionParameters(
        interaction_type=interaction_type,
        coupling_strength=coupling_strength,
        field_count=field_count
    )

def create_interaction_result(interaction_type: InteractionType = InteractionType.LINEAR_COUPLING) -> InteractionResult:
    """Create interaction result"""
    return InteractionResult(interaction_type=interaction_type)

def estimate_interaction_time(parameters: InteractionParameters) -> float:
    """Estimate interaction computation time"""
    base_time = 0.1  # Base time in seconds
    
    # Scale with time steps
    time_factor = parameters.time_steps / 100.0
    
    # Scale with field count
    field_factor = parameters.field_count / 2.0
    
    # Scale with complexity
    complexity_factor = parameters.get_interaction_complexity() / 3.0
    
    estimated_time = base_time * time_factor * field_factor * complexity_factor
    
    return estimated_time

# Export core components
__all__ = [
    'InteractionType',
    'CouplingMechanism',
    'InteractionParameters',
    'InteractionResult',
    'create_interaction_parameters',
    'create_interaction_result',
    'estimate_interaction_time'
]
