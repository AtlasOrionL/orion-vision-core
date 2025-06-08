"""
🔥 Thermodynamics Core - Q5.2 Core Implementation

Core classes and data structures for Information Thermodynamics Optimizer
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q5.2 Information Thermodynamics Optimizer
Priority: CRITICAL - Modular Design Refactoring Phase 9
"""

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional

# Optimization Strategies
class OptimizationStrategy(Enum):
    """Optimizasyon stratejileri"""
    ENTROPY_MINIMIZATION = "entropy_minimization"   # Entropi minimizasyonu
    INFORMATION_MAXIMIZATION = "information_maximization" # Bilgi maksimizasyonu
    COHERENCE_OPTIMIZATION = "coherence_optimization" # Koherans optimizasyonu
    ENERGY_EFFICIENCY = "energy_efficiency"         # Enerji verimliliği

# Thermodynamic Processes
class ThermodynamicProcess(Enum):
    """Termodinamik süreçler"""
    ISOTHERMAL = "isothermal"                       # İzotermal (sabit sıcaklık)
    ADIABATIC = "adiabatic"                         # Adyabatik (ısı alışverişi yok)
    ISOBARIC = "isobaric"                           # İzobarik (sabit basınç)
    ISOCHORIC = "isochoric"                         # İzokorik (sabit hacim)

# Optimization Phases
class OptimizationPhase(Enum):
    """Optimizasyon fazları"""
    ANALYSIS = "analysis"                           # Analiz fazı
    PLANNING = "planning"                           # Planlama fazı
    EXECUTION = "execution"                         # Uygulama fazı
    VALIDATION = "validation"                       # Doğrulama fazı

@dataclass
class ThermodynamicState:
    """
    Thermodynamic State
    
    Sistemin termodinamik durumu.
    """
    
    state_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Thermodynamic variables
    temperature: float = 1.0                        # Bilgi sıcaklığı
    pressure: float = 1.0                           # Bilgi basıncı
    volume: float = 1.0                             # Bilgi hacmi
    entropy: float = 0.0                            # Entropi
    
    # Information properties
    information_density: float = 0.0                # Bilgi yoğunluğu
    coherence_factor: float = 1.0                   # Koherans faktörü
    energy_content: float = 0.0                     # Enerji içeriği
    
    # System properties
    particle_count: int = 0                         # Parçacık sayısı (Lepton/QCB)
    interaction_strength: float = 1.0               # Etkileşim gücü
    
    # Temporal properties
    measurement_time: datetime = field(default_factory=datetime.now)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_free_energy(self) -> float:
        """Calculate Helmholtz free energy F = U - TS"""
        internal_energy = self.energy_content
        free_energy = internal_energy - (self.temperature * self.entropy)
        return free_energy
    
    def calculate_information_efficiency(self) -> float:
        """Calculate information efficiency"""
        if self.entropy == 0:
            return 1.0
        
        # Efficiency = Information / Entropy (higher info, lower entropy = better)
        efficiency = self.information_density / (self.entropy + 0.001)
        return min(1.0, efficiency)
    
    def get_efficiency_grade(self) -> str:
        """Get efficiency grade"""
        efficiency = self.calculate_information_efficiency()
        
        if efficiency >= 0.9:
            return "Excellent"
        elif efficiency >= 0.7:
            return "Good"
        elif efficiency >= 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get thermodynamic state summary"""
        return {
            'state_id': self.state_id[:8] + "...",
            'temperature': self.temperature,
            'entropy': self.entropy,
            'information_density': self.information_density,
            'coherence_factor': self.coherence_factor,
            'particle_count': self.particle_count,
            'free_energy': self.calculate_free_energy(),
            'efficiency': self.calculate_information_efficiency(),
            'efficiency_grade': self.get_efficiency_grade()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'state_id': self.state_id,
            'temperature': self.temperature,
            'pressure': self.pressure,
            'volume': self.volume,
            'entropy': self.entropy,
            'information_density': self.information_density,
            'coherence_factor': self.coherence_factor,
            'energy_content': self.energy_content,
            'particle_count': self.particle_count,
            'interaction_strength': self.interaction_strength,
            'free_energy': self.calculate_free_energy(),
            'information_efficiency': self.calculate_information_efficiency(),
            'efficiency_grade': self.get_efficiency_grade(),
            'measurement_time': self.measurement_time.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class OptimizationResult:
    """
    Optimization Result
    
    Optimizasyon sonucu.
    """
    
    optimization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy: OptimizationStrategy = OptimizationStrategy.ENTROPY_MINIMIZATION
    
    # Initial and final states
    initial_state: Optional[ThermodynamicState] = None
    final_state: Optional[ThermodynamicState] = None
    
    # Optimization metrics
    entropy_reduction: float = 0.0                  # Entropi azalması
    information_gain: float = 0.0                   # Bilgi kazancı
    coherence_improvement: float = 0.0              # Koherans iyileşmesi
    energy_efficiency_gain: float = 0.0             # Enerji verimliliği kazancı
    
    # Process information
    optimization_steps: int = 0                     # Optimizasyon adım sayısı
    convergence_achieved: bool = False              # Yakınsama sağlandı mı?
    optimization_time: float = 0.0                  # Optimizasyon süresi
    
    # Success metrics
    success_rate: float = 0.0                       # Başarı oranı
    improvement_factor: float = 1.0                 # İyileşme faktörü
    
    # Temporal properties
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_overall_improvement(self) -> float:
        """Calculate overall improvement score"""
        if not self.initial_state or not self.final_state:
            return 0.0
        
        # Weighted improvement score
        entropy_weight = 0.3
        information_weight = 0.3
        coherence_weight = 0.2
        efficiency_weight = 0.2
        
        # Normalize improvements
        entropy_improvement = max(0, -self.entropy_reduction)  # Negative reduction is good
        information_improvement = max(0, self.information_gain)
        coherence_improvement = max(0, self.coherence_improvement)
        efficiency_improvement = max(0, self.energy_efficiency_gain)
        
        overall_improvement = (
            entropy_improvement * entropy_weight +
            information_improvement * information_weight +
            coherence_improvement * coherence_weight +
            efficiency_improvement * efficiency_weight
        )
        
        return overall_improvement
    
    def get_improvement_grade(self) -> str:
        """Get improvement grade"""
        improvement = self.calculate_overall_improvement()
        
        if improvement >= 0.8:
            return "Excellent"
        elif improvement >= 0.6:
            return "Good"
        elif improvement >= 0.4:
            return "Fair"
        elif improvement >= 0.2:
            return "Poor"
        else:
            return "Failed"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get optimization result summary"""
        return {
            'optimization_id': self.optimization_id[:8] + "...",
            'strategy': self.strategy.value,
            'entropy_reduction': self.entropy_reduction,
            'information_gain': self.information_gain,
            'coherence_improvement': self.coherence_improvement,
            'overall_improvement': self.calculate_overall_improvement(),
            'improvement_grade': self.get_improvement_grade(),
            'convergence_achieved': self.convergence_achieved,
            'success_rate': self.success_rate,
            'optimization_time_ms': self.optimization_time * 1000
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'optimization_id': self.optimization_id,
            'strategy': self.strategy.value,
            'entropy_reduction': self.entropy_reduction,
            'information_gain': self.information_gain,
            'coherence_improvement': self.coherence_improvement,
            'energy_efficiency_gain': self.energy_efficiency_gain,
            'optimization_steps': self.optimization_steps,
            'convergence_achieved': self.convergence_achieved,
            'optimization_time': self.optimization_time,
            'success_rate': self.success_rate,
            'improvement_factor': self.improvement_factor,
            'overall_improvement': self.calculate_overall_improvement(),
            'improvement_grade': self.get_improvement_grade(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'metadata': self.metadata
        }

# Utility functions
def create_thermodynamic_state(temperature: float = 1.0,
                              entropy: float = 0.0,
                              information_density: float = 0.0,
                              coherence_factor: float = 1.0) -> ThermodynamicState:
    """Create thermodynamic state with default values"""
    return ThermodynamicState(
        temperature=temperature,
        entropy=entropy,
        information_density=information_density,
        coherence_factor=coherence_factor
    )

def create_optimization_result(strategy: OptimizationStrategy = OptimizationStrategy.ENTROPY_MINIMIZATION) -> OptimizationResult:
    """Create optimization result"""
    return OptimizationResult(strategy=strategy)

# Export core components
__all__ = [
    'OptimizationStrategy',
    'ThermodynamicProcess',
    'OptimizationPhase',
    'ThermodynamicState',
    'OptimizationResult',
    'create_thermodynamic_state',
    'create_optimization_result'
]
