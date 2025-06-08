"""
👁️ Non-Demolitional Measurement Units (NDMU) - Q4.1 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 6
"""

# Import core components from modular design
from .measurement_core import (
    MeasurementType,
    MeasurementMode,
    ObserverType,
    MeasurementResult,
    create_measurement_result,
    calculate_measurement_uncertainty,
    calculate_measurement_confidence
)

# Import engine component
from .measurement_engine import (
    NonDemolitionalMeasurementUnit
)

# Import statistics component
from .measurement_statistics import (
    MeasurementStatistics,
    create_measurement_statistics,
    analyze_measurement_batch,
    get_measurement_summary
)

# Import base components for compatibility
from .planck_information_unit import PlanckInformationUnit
from .lepton_phase_space import LeptonPhaseSpace

# Enhanced NDMU with statistics
class EnhancedNDMU(NonDemolitionalMeasurementUnit):
    """Enhanced NDMU with integrated statistics"""
    
    def __init__(self, 
                 measurement_type: MeasurementType = MeasurementType.NON_DEMOLITIONAL,
                 default_mode: MeasurementMode = MeasurementMode.COPY_ONLY):
        super().__init__(measurement_type, default_mode)
        self.statistics = create_measurement_statistics()
    
    def measure_information_unit(self, *args, **kwargs) -> MeasurementResult:
        """Enhanced measurement with statistics tracking"""
        result = super().measure_information_unit(*args, **kwargs)
        self.statistics.add_measurement(result)
        return result
    
    def measure_lepton_phase_space(self, *args, **kwargs) -> MeasurementResult:
        """Enhanced lepton measurement with statistics tracking"""
        result = super().measure_lepton_phase_space(*args, **kwargs)
        self.statistics.add_measurement(result)
        return result
    
    def get_ndmu_statistics(self):
        """Get comprehensive NDMU statistics"""
        return self.statistics.get_comprehensive_statistics()

# Utility functions
def create_non_demolitional_measurement_unit(
    measurement_type: MeasurementType = MeasurementType.NON_DEMOLITIONAL,
    default_mode: MeasurementMode = MeasurementMode.COPY_ONLY,
    enhanced: bool = True) -> NonDemolitionalMeasurementUnit:
    """Create Non-Demolitional Measurement Unit"""
    if enhanced:
        return EnhancedNDMU(measurement_type, default_mode)
    else:
        return NonDemolitionalMeasurementUnit(measurement_type, default_mode)

def test_non_demolitional_measurement():
    """Test Non-Demolitional Measurement system"""
    print("👁️ Testing Non-Demolitional Measurement Units (NDMU)...")
    
    # Create NDMU
    ndmu = create_non_demolitional_measurement_unit(
        measurement_type=MeasurementType.NON_DEMOLITIONAL,
        default_mode=MeasurementMode.COPY_ONLY
    )
    print("✅ NDMU created")
    
    # Create test information unit
    from .planck_information_unit import create_planck_information_manager
    
    planck_manager = create_planck_information_manager()
    info_unit = planck_manager.create_unit(coherence_factor=0.8)
    
    print(f"✅ Test information unit created: {info_unit.quality.value}")
    
    # Test different measurement modes
    modes = [
        MeasurementMode.COPY_ONLY,
        MeasurementMode.SHADOW_MEASUREMENT,
        MeasurementMode.ENTANGLED_PROBE
    ]
    
    results = []
    for mode in modes:
        result = ndmu.measure_information_unit(
            info_unit,
            observer_id="test_observer",
            observer_type=ObserverType.S_EHP,
            measurement_mode=mode
        )
        results.append(result)
        
        print(f"✅ {mode.value} measurement:")
        print(f"    - Quality: {result.calculate_measurement_quality():.3f}")
        print(f"    - Grade: {result.get_quality_grade()}")
        print(f"    - NDM: {result.is_non_demolitional()}")
        print(f"    - Disturbance: {result.state_disturbance:.3f}")
    
    # Test lepton measurement
    from .lepton_phase_space import create_lepton_phase_space_manager
    
    lepton_manager = create_lepton_phase_space_manager()
    lepton = lepton_manager.create_lepton(coherence_factor=0.9)
    
    lepton_result = ndmu.measure_lepton_phase_space(
        lepton,
        observer_id="lepton_observer",
        observer_type=ObserverType.OBSERVER_AI
    )
    
    print(f"✅ Lepton measurement:")
    print(f"    - Quality: {lepton_result.calculate_measurement_quality():.3f}")
    print(f"    - NDM: {lepton_result.is_non_demolitional()}")
    print(f"    - State preserved: {lepton_result.original_state_preserved}")
    
    # Get comprehensive statistics
    stats = ndmu.get_ndmu_statistics()
    
    print(f"✅ NDMU Statistics:")
    print(f"    - Total measurements: {stats['total_measurements']}")
    print(f"    - NDM success rate: {stats['ndm_success_rate']:.1%}")
    print(f"    - Average quality: {stats['average_quality']:.3f}")
    print(f"    - State preservation rate: {stats['state_preservation_rate']:.1%}")
    
    # Test batch analysis
    batch_stats = analyze_measurement_batch(results)
    print(f"✅ Batch analysis:")
    print(f"    - Quality distribution: {batch_stats['quality_distribution']}")
    
    print("🚀 Non-Demolitional Measurement test completed!")

# Export all components for backward compatibility
__all__ = [
    'MeasurementType',
    'MeasurementMode',
    'ObserverType',
    'MeasurementResult',
    'NonDemolitionalMeasurementUnit',
    'EnhancedNDMU',
    'MeasurementStatistics',
    'create_measurement_result',
    'calculate_measurement_uncertainty',
    'calculate_measurement_confidence',
    'create_non_demolitional_measurement_unit',
    'create_measurement_statistics',
    'analyze_measurement_batch',
    'get_measurement_summary',
    'test_non_demolitional_measurement'
]

if __name__ == "__main__":
    test_non_demolitional_measurement()
