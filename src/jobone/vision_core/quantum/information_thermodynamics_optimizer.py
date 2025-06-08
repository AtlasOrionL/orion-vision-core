"""
🔥 Information Thermodynamics Optimizer - Q5.2 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 9
"""

# Import core components from modular design
from .thermodynamics_core import (
    OptimizationStrategy,
    ThermodynamicProcess,
    OptimizationPhase,
    ThermodynamicState,
    OptimizationResult,
    create_thermodynamic_state,
    create_optimization_result
)

# Import engine component
from .optimizer_engine import (
    InformationThermodynamicsOptimizer
)

# Import statistics component
from .optimizer_statistics import (
    OptimizerStatistics,
    get_optimizer_statistics,
    create_optimizer_statistics,
    analyze_optimization_batch,
    get_optimization_summary,
    get_thermodynamic_summary
)

# Import base components for compatibility
from .planck_information_unit import PlanckInformationUnit

# Enhanced Optimizer with statistics
class EnhancedThermodynamicsOptimizer(InformationThermodynamicsOptimizer):
    """Enhanced Thermodynamics Optimizer with integrated statistics"""
    
    def __init__(self, 
                 default_strategy: OptimizationStrategy = OptimizationStrategy.ENTROPY_MINIMIZATION,
                 convergence_threshold: float = 0.001):
        super().__init__(default_strategy, convergence_threshold)
        self.statistics = create_optimizer_statistics()
    
    def optimize_system(self, *args, **kwargs) -> OptimizationResult:
        """Enhanced optimization with statistics tracking"""
        result = super().optimize_system(*args, **kwargs)
        self.statistics.add_optimization_result(result)
        return result
    
    def get_thermodynamics_statistics(self):
        """Get comprehensive thermodynamics statistics"""
        return self.statistics.get_comprehensive_statistics()

# Utility functions
def create_information_thermodynamics_optimizer(
    default_strategy: OptimizationStrategy = OptimizationStrategy.ENTROPY_MINIMIZATION,
    convergence_threshold: float = 0.001,
    enhanced: bool = True) -> InformationThermodynamicsOptimizer:
    """Create Information Thermodynamics Optimizer"""
    if enhanced:
        return EnhancedThermodynamicsOptimizer(default_strategy, convergence_threshold)
    else:
        return InformationThermodynamicsOptimizer(default_strategy, convergence_threshold)

def test_information_thermodynamics_optimizer():
    """Test Information Thermodynamics Optimizer system"""
    print("🔥 Testing Information Thermodynamics Optimizer...")
    
    # Create optimizer
    optimizer = create_information_thermodynamics_optimizer(
        default_strategy=OptimizationStrategy.ENTROPY_MINIMIZATION,
        convergence_threshold=0.001
    )
    print("✅ Optimizer created")
    
    # Create test information units
    from .planck_information_unit import create_planck_information_manager
    
    planck_manager = create_planck_information_manager()
    information_units = []
    
    for i in range(5):
        unit = planck_manager.create_unit(coherence_factor=0.6 + i * 0.05)
        information_units.append(unit)
    
    print(f"✅ Created {len(information_units)} test information units")
    
    # Test different optimization strategies
    strategies = [
        OptimizationStrategy.ENTROPY_MINIMIZATION,
        OptimizationStrategy.INFORMATION_MAXIMIZATION,
        OptimizationStrategy.COHERENCE_OPTIMIZATION,
        OptimizationStrategy.ENERGY_EFFICIENCY
    ]
    
    results = []
    for strategy in strategies:
        result = optimizer.optimize_system(
            information_units=information_units,
            strategy=strategy
        )
        results.append(result)
        
        print(f"✅ {strategy.value} optimization:")
        print(f"    - Overall improvement: {result.calculate_overall_improvement():.3f}")
        print(f"    - Grade: {result.get_improvement_grade()}")
        print(f"    - Entropy reduction: {result.entropy_reduction:+.3f}")
        print(f"    - Information gain: {result.information_gain:+.3f}")
        print(f"    - Coherence improvement: {result.coherence_improvement:+.3f}")
        print(f"    - Convergence: {result.convergence_achieved}")
    
    # Test thermodynamic state measurement
    state = optimizer.measure_thermodynamic_state(information_units)
    
    print(f"✅ Thermodynamic state:")
    print(f"    - Temperature: {state.temperature:.3f}")
    print(f"    - Entropy: {state.entropy:.3f}")
    print(f"    - Information density: {state.information_density:.3f}")
    print(f"    - Coherence factor: {state.coherence_factor:.3f}")
    print(f"    - Efficiency: {state.calculate_information_efficiency():.3f}")
    print(f"    - Grade: {state.get_efficiency_grade()}")
    
    # Get comprehensive statistics
    stats = optimizer.get_thermodynamics_statistics()
    
    print(f"✅ Optimizer Statistics:")
    print(f"    - Total optimizations: {stats['total_optimizations']}")
    print(f"    - Success rate: {stats['success_rate']:.1%}")
    print(f"    - Convergence rate: {stats['convergence_rate']:.1%}")
    print(f"    - Average improvement: {stats['average_improvement']:.3f}")
    
    # Test batch analysis
    batch_stats = analyze_optimization_batch(results)
    print(f"✅ Batch analysis:")
    print(f"    - Strategy distribution: {batch_stats['strategy_statistics']}")
    
    print("🚀 Information Thermodynamics Optimizer test completed!")

# Export all components for backward compatibility
__all__ = [
    'OptimizationStrategy',
    'ThermodynamicProcess',
    'OptimizationPhase',
    'ThermodynamicState',
    'OptimizationResult',
    'InformationThermodynamicsOptimizer',
    'EnhancedThermodynamicsOptimizer',
    'OptimizerStatistics',
    'create_thermodynamic_state',
    'create_optimization_result',
    'create_information_thermodynamics_optimizer',
    'get_optimizer_statistics',
    'create_optimizer_statistics',
    'analyze_optimization_batch',
    'get_optimization_summary',
    'get_thermodynamic_summary',
    'test_information_thermodynamics_optimizer'
]

if __name__ == "__main__":
    test_information_thermodynamics_optimizer()
