"""
🔬 Planck Information Unit Utilities - Q1.1 Utilities

Utility functions for Planck Information Unit system
Separated to maintain 300-line modular design limit

Author: Orion Vision Core Team
Based on: Q1.1 Planck Information Quantization Unit
Priority: HIGH - Quantum Foundation
"""

import logging
from typing import List, Dict, Any
from .planck_information_core import PlanckInformationUnit
from .planck_information_manager import PlanckInformationManager

def test_planck_information_unit():
    """Test Planck Information Unit system"""
    print("🔬 Testing Planck Information Unit (ℏI) System...")
    
    # Create manager
    manager = PlanckInformationManager()
    print("✅ Planck Information Manager created")
    
    # Create test units
    unit1 = manager.create_unit(coherence_factor=0.9)
    unit2 = manager.create_unit(coherence_factor=0.5)
    unit3 = manager.create_unit(coherence_factor=0.2)
    
    print(f"✅ Created 3 test units")
    print(f"    - Unit 1: {unit1.quality.value} (content: {unit1.information_content:.2f})")
    print(f"    - Unit 2: {unit2.quality.value} (content: {unit2.information_content:.2f})")
    print(f"    - Unit 3: {unit3.quality.value} (content: {unit3.information_content:.2f})")
    
    # Test noise filtering
    all_units = [unit1, unit2, unit3]
    filtered_units = manager.filter_noise_units(all_units)
    print(f"✅ Noise filtering: {len(filtered_units)}/{len(all_units)} units passed")
    
    # Test conservation law
    input_units = [unit1]
    output_units = [unit2, unit3]
    conservation_ok = manager.validate_conservation_law(input_units, output_units)
    print(f"✅ Conservation law test: {'PASSED' if conservation_ok else 'FAILED'}")
    
    # Get statistics
    stats = manager.get_system_statistics()
    print(f"✅ System statistics:")
    print(f"    - Total units: {stats['total_units']}")
    print(f"    - Average content: {stats['average_information_content']:.3f}")
    print(f"    - Quality distribution: {stats['quality_distribution']}")
    
    print("🚀 Planck Information Unit test completed!")

def create_batch_planck_units(manager: PlanckInformationManager, 
                             count: int = 10,
                             coherence_range: tuple = (0.1, 1.0)) -> List[PlanckInformationUnit]:
    """Create batch of Planck information units with varying coherence"""
    import random
    
    units = []
    for i in range(count):
        coherence = random.uniform(coherence_range[0], coherence_range[1])
        unit = manager.create_unit(coherence_factor=coherence)
        units.append(unit)
    
    return units

def analyze_planck_unit_distribution(units: List[PlanckInformationUnit]) -> Dict[str, Any]:
    """Analyze distribution of Planck information units"""
    if not units:
        return {}
    
    # Quality distribution
    quality_counts = {}
    for unit in units:
        quality = unit.quality.value
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
    
    # Content statistics
    contents = [unit.information_content for unit in units]
    avg_content = sum(contents) / len(contents)
    min_content = min(contents)
    max_content = max(contents)
    
    # Coherence statistics
    coherences = [unit.coherence_factor for unit in units]
    avg_coherence = sum(coherences) / len(coherences)
    
    return {
        'total_units': len(units),
        'quality_distribution': quality_counts,
        'average_content': avg_content,
        'min_content': min_content,
        'max_content': max_content,
        'average_coherence': avg_coherence,
        'content_range': max_content - min_content
    }

def optimize_planck_unit_collection(units: List[PlanckInformationUnit],
                                   target_quality: str = "QUANTUM") -> List[PlanckInformationUnit]:
    """Optimize collection of Planck units for target quality"""
    from .planck_information_core import InformationQuality

    # Filter by target quality
    if target_quality == "QUANTUM":
        target_qualities = [InformationQuality.QUANTUM]
    elif target_quality == "COHERENT":
        target_qualities = [InformationQuality.QUANTUM, InformationQuality.COHERENT]
    elif target_quality == "CLASSICAL":
        target_qualities = [InformationQuality.QUANTUM, InformationQuality.COHERENT, InformationQuality.CLASSICAL]
    else:
        target_qualities = list(InformationQuality)
    
    optimized_units = [unit for unit in units if unit.quality in target_qualities]
    
    # Sort by information content (descending)
    optimized_units.sort(key=lambda u: u.information_content, reverse=True)
    
    return optimized_units

def validate_planck_unit_integrity(unit: PlanckInformationUnit) -> Dict[str, bool]:
    """Validate integrity of a Planck information unit"""
    validations = {}
    
    # Check basic properties
    validations['valid_id'] = bool(unit.unit_id)
    validations['valid_content'] = unit.information_content >= 0
    validations['valid_coherence'] = 0 <= unit.coherence_factor <= 1
    validations['valid_timestamp'] = unit.creation_time is not None
    
    # Check quantum properties
    validations['above_planck_threshold'] = unit.is_above_planck_threshold()
    validations['valid_quality'] = unit.quality is not None
    
    # Check consistency
    expected_content = unit.coherence_factor * unit.planck_constant
    content_tolerance = 0.01
    validations['content_consistency'] = abs(unit.information_content - expected_content) < content_tolerance
    
    # Overall integrity
    validations['overall_integrity'] = all(validations.values())
    
    return validations

def merge_planck_units(unit1: PlanckInformationUnit, 
                      unit2: PlanckInformationUnit,
                      manager: PlanckInformationManager) -> PlanckInformationUnit:
    """Merge two Planck information units"""
    # Calculate merged properties
    merged_coherence = (unit1.coherence_factor + unit2.coherence_factor) / 2
    
    # Create merged unit
    merged_unit = manager.create_unit(coherence_factor=merged_coherence)
    
    # Update metadata
    merged_unit.metadata['merged_from'] = [unit1.unit_id, unit2.unit_id]
    merged_unit.metadata['merge_timestamp'] = merged_unit.creation_time
    
    return merged_unit

def export_planck_units_data(units: List[PlanckInformationUnit]) -> Dict[str, Any]:
    """Export Planck units data for analysis"""
    export_data = {
        'metadata': {
            'total_units': len(units),
            'export_timestamp': units[0].creation_time.isoformat() if units else None,
            'version': '1.0.0'
        },
        'units': []
    }
    
    for unit in units:
        unit_data = {
            'unit_id': unit.unit_id,
            'information_content': unit.information_content,
            'coherence_factor': unit.coherence_factor,
            'quality': unit.quality.value,
            'planck_constant': unit.planck_constant,
            'creation_time': unit.creation_time.isoformat(),
            'above_threshold': unit.is_above_planck_threshold(),
            'metadata': unit.metadata
        }
        export_data['units'].append(unit_data)
    
    return export_data

def import_planck_units_data(data: Dict[str, Any], 
                            manager: PlanckInformationManager) -> List[PlanckInformationUnit]:
    """Import Planck units data"""
    units = []
    
    for unit_data in data.get('units', []):
        # Create unit with imported coherence
        unit = manager.create_unit(coherence_factor=unit_data['coherence_factor'])
        
        # Restore metadata
        unit.metadata.update(unit_data.get('metadata', {}))
        unit.metadata['imported'] = True
        unit.metadata['original_id'] = unit_data['unit_id']
        
        units.append(unit)
    
    return units

if __name__ == "__main__":
    test_planck_information_unit()
