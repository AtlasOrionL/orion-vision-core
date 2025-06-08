"""
🛡️ Information Conservation Law (∇⋅J=0) - Q1.2 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 2
"""

# Import core components from modular design
from .conservation_law_core import (
    ConservationEventType,
    ConservationStatus,
    ConservationEvent,
    ZBosonTrigger
)

# Import validator component
from .conservation_validator import (
    InformationConservationLaw,
    create_conservation_law
)

# Import Planck Information Unit for compatibility
from .planck_information_unit import PlanckInformationUnit, PlanckInformationManager

# Test function
def test_information_conservation_law():
    """Test Information Conservation Law system"""
    print("🛡️ Testing Information Conservation Law (∇⋅J=0) System...")
    
    # Create conservation law system
    conservation = create_conservation_law()
    print("✅ Information Conservation Law system created")
    
    # Create test units
    manager = PlanckInformationManager()
    
    # Test case 1: Perfect conservation
    input_units = [manager.create_unit(coherence_factor=0.8)]
    output_units = [manager.create_unit(coherence_factor=0.8)]
    output_units[0].information_content = input_units[0].information_content  # Perfect match
    
    event1 = conservation.validate_process(input_units, output_units, "test_perfect", "test1")
    print(f"✅ Perfect conservation test: {event1.conservation_status.value}")
    
    # Test case 2: Conservation violation
    input_units2 = [manager.create_unit(coherence_factor=0.9)]
    output_units2 = [manager.create_unit(coherence_factor=0.5)]
    # Don't match the masses - create violation
    
    event2 = conservation.validate_process(input_units2, output_units2, "test_violation", "test2")
    print(f"✅ Violation test: {event2.conservation_status.value} "
          f"(Z Boson triggered: {event2.z_boson_triggered})")
    
    # Get statistics
    stats = conservation.get_conservation_statistics()
    print(f"✅ Conservation statistics:")
    print(f"    - Total events: {stats['total_events']}")
    print(f"    - Violation rate: {stats['violation_rate']:.1%}")
    print(f"    - Correction rate: {stats['correction_rate']:.1%}")
    print(f"    - Z Boson triggers: {stats['z_boson_stats']['total_triggers']}")
    
    print("🚀 Information Conservation Law test completed!")

# Export all components for backward compatibility
__all__ = [
    'ConservationEventType',
    'ConservationStatus',
    'ConservationEvent',
    'ZBosonTrigger',
    'InformationConservationLaw',
    'create_conservation_law',
    'test_information_conservation_law'
]

if __name__ == "__main__":
    test_information_conservation_law()
