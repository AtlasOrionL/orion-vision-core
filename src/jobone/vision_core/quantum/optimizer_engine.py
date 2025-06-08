"""
🔥 Optimizer Engine - Q5.2 Engine Component

Information Thermodynamics Optimizer engine implementation
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q5.2 Information Thermodynamics Optimizer
Priority: CRITICAL - Modular Design Refactoring Phase 9
"""

import logging
import math
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import core components
from .thermodynamics_core import (
    OptimizationStrategy, ThermodynamicState, OptimizationResult,
    create_thermodynamic_state, create_optimization_result
)
from .planck_information_unit import PlanckInformationUnit

class InformationThermodynamicsOptimizer:
    """
    Information Thermodynamics Optimizer (ITO)
    
    Bilgi termodinamiği optimizasyon motoru.
    """
    
    def __init__(self, 
                 default_strategy: OptimizationStrategy = OptimizationStrategy.ENTROPY_MINIMIZATION,
                 convergence_threshold: float = 0.001):
        self.logger = logging.getLogger(__name__)
        self.default_strategy = default_strategy
        self.convergence_threshold = convergence_threshold
        
        # Optimization parameters
        self.max_iterations = 100                    # Maksimum iterasyon
        self.learning_rate = 0.1                     # Öğrenme oranı
        self.temperature_scaling = 1.0               # Sıcaklık ölçekleme
        
        # System state tracking
        self.current_state: Optional[ThermodynamicState] = None
        self.state_history: List[ThermodynamicState] = []
        
        # Optimization tracking
        self.optimization_results: List[OptimizationResult] = []
        self.total_optimizations = 0
        self.successful_optimizations = 0
        
        # Thermodynamic constants
        self.boltzmann_constant = 1.0                # Normalized kB
        self.information_constant = 1.0              # Information scaling constant
        
        self.logger.info(f"🔥 InformationThermodynamicsOptimizer initialized - Q5.2 Implementation "
                        f"({default_strategy.value}, threshold: {convergence_threshold})")
    
    def measure_thermodynamic_state(self, 
                                   information_units: List[PlanckInformationUnit],
                                   vacuum_state=None) -> ThermodynamicState:
        """Measure current thermodynamic state of the system"""
        
        state = create_thermodynamic_state()
        
        if not information_units:
            return state
        
        try:
            # Calculate system properties
            total_information = sum(unit.information_content for unit in information_units)
            total_coherence = sum(unit.coherence_factor for unit in information_units)
            avg_coherence = total_coherence / len(information_units)
            
            # Calculate entropy (Shannon entropy of information distribution)
            total_entropy = 0.0
            for unit in information_units:
                if unit.information_content > 0:
                    prob = unit.information_content / total_information
                    total_entropy -= prob * math.log2(prob + 1e-10)
            
            # Calculate thermodynamic variables
            state.particle_count = len(information_units)
            state.information_density = total_information / max(1, state.particle_count)
            state.coherence_factor = avg_coherence
            state.entropy = total_entropy
            
            # Calculate temperature (related to information distribution)
            state.temperature = total_entropy / max(1, math.log2(state.particle_count + 1))
            
            # Calculate pressure (information pressure)
            state.pressure = state.information_density * state.temperature
            
            # Calculate volume (information space)
            state.volume = state.particle_count * self.information_constant
            
            # Calculate energy content
            state.energy_content = sum(unit.get_effective_mass() for unit in information_units)
            
            # Include vacuum state if provided
            if vacuum_state:
                state.energy_content += vacuum_state.vacuum_energy
                state.temperature *= (1.0 + vacuum_state.field_strength * 0.1)
            
            # Calculate interaction strength
            state.interaction_strength = avg_coherence * state.information_density / max(1, state.entropy)
            
            # Update current state
            self.current_state = state
            self.state_history.append(state)
            
            # Limit history size
            if len(self.state_history) > 1000:
                self.state_history = self.state_history[-500:]
            
        except Exception as e:
            self.logger.error(f"❌ Thermodynamic state measurement failed: {e}")
        
        return state
    
    def optimize_system(self,
                       information_units: List[PlanckInformationUnit],
                       strategy: Optional[OptimizationStrategy] = None,
                       vacuum_state=None) -> OptimizationResult:
        """Optimize system using thermodynamic principles"""
        
        start_time = time.time()
        optimization_strategy = strategy or self.default_strategy
        
        # Create optimization result
        result = create_optimization_result(optimization_strategy)
        result.start_time = datetime.now()
        
        try:
            # Measure initial state
            initial_state = self.measure_thermodynamic_state(information_units, vacuum_state)
            result.initial_state = initial_state
            
            # Perform optimization based on strategy
            if optimization_strategy == OptimizationStrategy.ENTROPY_MINIMIZATION:
                optimized_units = self._optimize_entropy_minimization(information_units)
                
            elif optimization_strategy == OptimizationStrategy.INFORMATION_MAXIMIZATION:
                optimized_units = self._optimize_information_maximization(information_units)
                
            elif optimization_strategy == OptimizationStrategy.COHERENCE_OPTIMIZATION:
                optimized_units = self._optimize_coherence(information_units)
                
            elif optimization_strategy == OptimizationStrategy.ENERGY_EFFICIENCY:
                optimized_units = self._optimize_energy_efficiency(information_units)
            
            else:
                optimized_units = information_units  # No optimization
            
            # Measure final state
            final_state = self.measure_thermodynamic_state(optimized_units, vacuum_state)
            result.final_state = final_state
            
            # Calculate improvements
            if initial_state and final_state:
                result.entropy_reduction = initial_state.entropy - final_state.entropy
                result.information_gain = final_state.information_density - initial_state.information_density
                result.coherence_improvement = final_state.coherence_factor - initial_state.coherence_factor
                result.energy_efficiency_gain = (final_state.calculate_information_efficiency() - 
                                                initial_state.calculate_information_efficiency())
            
            # Check convergence
            result.convergence_achieved = abs(result.entropy_reduction) < self.convergence_threshold
            result.success_rate = 1.0 if result.calculate_overall_improvement() > 0 else 0.0
            result.improvement_factor = 1.0 + result.calculate_overall_improvement()
            
            # Update statistics
            self.total_optimizations += 1
            if result.success_rate > 0.5:
                self.successful_optimizations += 1
            
        except Exception as e:
            self.logger.error(f"❌ System optimization failed: {e}")
            result.success_rate = 0.0
            result.convergence_achieved = False
        
        # Finalize result
        result.optimization_time = time.time() - start_time
        result.end_time = datetime.now()
        self.optimization_results.append(result)
        
        # Limit results history
        if len(self.optimization_results) > 1000:
            self.optimization_results = self.optimization_results[-500:]
        
        self.logger.debug(f"🔥 Optimization completed: {result.optimization_id[:8]}... "
                         f"(strategy: {optimization_strategy.value}, "
                         f"improvement: {result.calculate_overall_improvement():.3f})")
        
        return result
    
    def _optimize_entropy_minimization(self, information_units: List[PlanckInformationUnit]) -> List[PlanckInformationUnit]:
        """Optimize for entropy minimization"""
        optimized_units = []
        
        for unit in information_units:
            optimized_unit = PlanckInformationUnit(
                unit_id=unit.unit_id,
                information_content=unit.information_content,
                coherence_factor=unit.coherence_factor,
                seed_value=unit.seed_value
            )
            
            # Entropy minimization: increase coherence, reduce noise
            if unit.coherence_factor < 0.9:
                optimized_unit.coherence_factor = min(1.0, unit.coherence_factor * 1.1)
            
            # Concentrate information (reduce entropy)
            if unit.information_content > 0:
                optimized_unit.information_content *= 1.05
            
            # Recalculate derived properties
            optimized_unit._calculate_information_content()
            optimized_unit._determine_quality_level()
            
            optimized_units.append(optimized_unit)
        
        return optimized_units
    
    def _optimize_information_maximization(self, information_units: List[PlanckInformationUnit]) -> List[PlanckInformationUnit]:
        """Optimize for information maximization"""
        optimized_units = []
        
        for unit in information_units:
            optimized_unit = PlanckInformationUnit(
                unit_id=unit.unit_id,
                information_content=unit.information_content,
                coherence_factor=unit.coherence_factor,
                seed_value=unit.seed_value
            )
            
            # Information maximization: increase information content
            optimized_unit.information_content *= 1.2
            
            # Maintain coherence for quality
            if unit.coherence_factor > 0.5:
                optimized_unit.coherence_factor = min(1.0, unit.coherence_factor * 1.05)
            
            # Recalculate derived properties
            optimized_unit._calculate_information_content()
            optimized_unit._determine_quality_level()
            
            optimized_units.append(optimized_unit)
        
        return optimized_units
    
    def _optimize_coherence(self, information_units: List[PlanckInformationUnit]) -> List[PlanckInformationUnit]:
        """Optimize for coherence"""
        optimized_units = []
        
        for unit in information_units:
            optimized_unit = PlanckInformationUnit(
                unit_id=unit.unit_id,
                information_content=unit.information_content,
                coherence_factor=unit.coherence_factor,
                seed_value=unit.seed_value
            )
            
            # Coherence optimization: maximize coherence factor
            optimized_unit.coherence_factor = min(1.0, unit.coherence_factor * 1.15)
            
            # Adjust information content to maintain balance
            if optimized_unit.coherence_factor > 0.8:
                optimized_unit.information_content *= 1.1
            
            # Recalculate derived properties
            optimized_unit._calculate_information_content()
            optimized_unit._determine_quality_level()
            
            optimized_units.append(optimized_unit)
        
        return optimized_units
    
    def _optimize_energy_efficiency(self, information_units: List[PlanckInformationUnit]) -> List[PlanckInformationUnit]:
        """Optimize for energy efficiency"""
        optimized_units = []
        
        for unit in information_units:
            optimized_unit = PlanckInformationUnit(
                unit_id=unit.unit_id,
                information_content=unit.information_content,
                coherence_factor=unit.coherence_factor,
                seed_value=unit.seed_value
            )
            
            # Energy efficiency: maximize information per unit energy
            effective_mass = unit.get_effective_mass()
            if effective_mass > 0:
                efficiency_factor = unit.information_content / effective_mass
                
                # Improve efficiency
                if efficiency_factor < 2.0:
                    optimized_unit.information_content *= 1.1
                    optimized_unit.coherence_factor = min(1.0, unit.coherence_factor * 1.05)
            
            # Recalculate derived properties
            optimized_unit._calculate_information_content()
            optimized_unit._determine_quality_level()
            
            optimized_units.append(optimized_unit)
        
        return optimized_units

# Export engine components
__all__ = [
    'InformationThermodynamicsOptimizer'
]
