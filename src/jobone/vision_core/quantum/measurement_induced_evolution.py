"""
🧠 Measurement Induced Evolution & Quantum Learning Rate - Q4.2 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 7
"""

# Import core components from modular design
from .evolution_core import (
    EvolutionType,
    LearningMode,
    MemoryUpdateType,
    EvolutionEvent,
    QuantumLearningParameters,
    create_evolution_event,
    create_quantum_learning_parameters
)

# Import engine component
from .learning_engine import (
    MeasurementInducedEvolution
)

# Import statistics component
from .evolution_statistics import (
    EvolutionStatistics,
    create_evolution_statistics,
    analyze_evolution_batch,
    get_evolution_summary
)

# Import base components for compatibility
from .measurement_core import MeasurementResult
from .planck_information_unit import PlanckInformationUnit
from .lepton_phase_space import LeptonPhaseSpace

# Enhanced Evolution System with statistics
class EnhancedEvolutionSystem(MeasurementInducedEvolution):
    """Enhanced Evolution System with integrated statistics"""
    
    def __init__(self, 
                 learning_mode: LearningMode = LearningMode.QUANTUM_REINFORCEMENT,
                 memory_update_type: MemoryUpdateType = MemoryUpdateType.INCREMENTAL):
        super().__init__(learning_mode, memory_update_type)
        self.statistics = create_evolution_statistics()
    
    def process_measurement_evolution(self, *args, **kwargs) -> EvolutionEvent:
        """Enhanced evolution processing with statistics tracking"""
        event = super().process_measurement_evolution(*args, **kwargs)
        self.statistics.add_evolution_event(event)
        return event
    
    def get_evolution_statistics(self):
        """Get comprehensive evolution statistics"""
        return self.statistics.get_comprehensive_statistics()

# Utility functions
def create_measurement_induced_evolution(
    learning_mode: LearningMode = LearningMode.QUANTUM_REINFORCEMENT,
    memory_update_type: MemoryUpdateType = MemoryUpdateType.INCREMENTAL,
    enhanced: bool = True) -> MeasurementInducedEvolution:
    """Create Measurement Induced Evolution system"""
    if enhanced:
        return EnhancedEvolutionSystem(learning_mode, memory_update_type)
    else:
        return MeasurementInducedEvolution(learning_mode, memory_update_type)

def test_measurement_induced_evolution():
    """Test Measurement Induced Evolution system"""
    print("🧠 Testing Measurement Induced Evolution & Quantum Learning...")
    
    # Create evolution system
    evolution_system = create_measurement_induced_evolution(
        learning_mode=LearningMode.QUANTUM_REINFORCEMENT,
        memory_update_type=MemoryUpdateType.INCREMENTAL
    )
    print("✅ Evolution system created")
    
    # Create test measurement result
    from .measurement_core import create_measurement_result, MeasurementType, MeasurementMode, ObserverType
    
    measurement_result = create_measurement_result(
        target_id="test_unit_001",
        target_type="PlanckInformationUnit",
        measurement_type=MeasurementType.NON_DEMOLITIONAL,
        measurement_mode=MeasurementMode.COPY_ONLY,
        observer_id="test_observer",
        observer_type=ObserverType.S_EHP
    )
    measurement_result.measurement_confidence = 0.9
    measurement_result.state_disturbance = 0.01
    
    print(f"✅ Test measurement result created: quality {measurement_result.calculate_measurement_quality():.3f}")
    
    # Create test information unit
    from .planck_information_unit import create_planck_information_manager
    
    planck_manager = create_planck_information_manager()
    info_unit = planck_manager.create_unit(coherence_factor=0.8)
    
    # Test different learning modes
    modes = [
        LearningMode.QUANTUM_REINFORCEMENT,
        LearningMode.COHERENCE_OPTIMIZATION,
        LearningMode.INFORMATION_INTEGRATION,
        LearningMode.ADAPTIVE_EVOLUTION
    ]
    
    events = []
    for mode in modes:
        # Create system for each mode
        mode_system = create_measurement_induced_evolution(learning_mode=mode)
        
        # Process evolution
        event = mode_system.process_measurement_evolution(
            measurement_result=measurement_result,
            target_unit=info_unit
        )
        events.append(event)
        
        print(f"✅ {mode.value} evolution:")
        print(f"    - Learning strength: {event.learning_strength:.3f}")
        print(f"    - Impact grade: {event.get_impact_grade()}")
        print(f"    - Significant: {event.is_significant_evolution()}")
        print(f"    - Coherence change: {event.coherence_change:+.3f}")
        print(f"    - Information gain: {event.information_gain:.3f}")
    
    # Test lepton evolution
    from .lepton_phase_space import create_lepton_phase_space_manager
    
    lepton_manager = create_lepton_phase_space_manager()
    lepton = lepton_manager.create_lepton(coherence_factor=0.9)
    
    lepton_event = evolution_system.process_measurement_evolution(
        measurement_result=measurement_result,
        target_lepton=lepton
    )
    
    print(f"✅ Lepton evolution:")
    print(f"    - Learning strength: {lepton_event.learning_strength:.3f}")
    print(f"    - Impact: {lepton_event.calculate_evolution_impact():.3f}")
    print(f"    - ATLAS memory updated: {lepton_event.atlas_memory_updated}")
    
    # Get comprehensive statistics
    stats = evolution_system.get_evolution_statistics()
    
    print(f"✅ Evolution Statistics:")
    print(f"    - Total evolutions: {stats['total_evolutions']}")
    print(f"    - Significance rate: {stats['significance_rate']:.1%}")
    print(f"    - Average learning strength: {stats['average_learning_strength']:.3f}")
    print(f"    - Average impact: {stats['average_impact']:.3f}")
    
    # Test batch analysis
    batch_stats = analyze_evolution_batch(events)
    print(f"✅ Batch analysis:")
    print(f"    - Impact distribution: {batch_stats['impact_distribution']}")
    
    print("🚀 Measurement Induced Evolution test completed!")

# Export all components for backward compatibility
__all__ = [
    'EvolutionType',
    'LearningMode',
    'MemoryUpdateType',
    'EvolutionEvent',
    'QuantumLearningParameters',
    'MeasurementInducedEvolution',
    'EnhancedEvolutionSystem',
    'EvolutionStatistics',
    'create_evolution_event',
    'create_quantum_learning_parameters',
    'create_measurement_induced_evolution',
    'create_evolution_statistics',
    'analyze_evolution_batch',
    'get_evolution_summary',
    'test_measurement_induced_evolution'
]

if __name__ == "__main__":
    test_measurement_induced_evolution()
