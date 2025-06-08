"""
🔬 Planck Information Manager - Q1.1 Manager Component

Manager component for Planck Information Unit system
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q1.1 Planck Information Quantization Unit
Priority: CRITICAL - Modular Design Refactoring Phase 1
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from .planck_information_core import PlanckInformationUnit, InformationQuality

class PlanckInformationManager:
    """
    Planck Information Manager
    
    Manages collection of Planck Information Units with conservation laws,
    noise filtering, and system-wide optimization.
    """
    
    def __init__(self, planck_constant: float = 1.0):
        self.logger = logging.getLogger(__name__)
        self.planck_constant = planck_constant
        
        # Unit storage
        self.units: Dict[str, PlanckInformationUnit] = {}
        
        # System statistics
        self.total_units_created = 0
        self.noise_filtered_count = 0
        self.conservation_violations = 0
        
        # Noise threshold for filtering
        self.noise_threshold = 0.1
        
        self.logger.info(f"🔬 PlanckInformationManager initialized - Q1.1 Implementation")
    
    def create_unit(self, coherence_factor: float = 0.5) -> PlanckInformationUnit:
        """Create new Planck Information Unit"""
        unit = PlanckInformationUnit(
            coherence_factor=coherence_factor,
            planck_constant=self.planck_constant
        )
        
        self.units[unit.unit_id] = unit
        self.total_units_created += 1
        
        self.logger.debug(f"🔬 Created Planck unit: {unit.unit_id[:8]}... "
                         f"(quality: {unit.quality.value}, content: {unit.information_content:.3f})")
        
        return unit
    
    def get_unit(self, unit_id: str) -> Optional[PlanckInformationUnit]:
        """Get unit by ID"""
        return self.units.get(unit_id)
    
    def remove_unit(self, unit_id: str) -> bool:
        """Remove unit by ID"""
        if unit_id in self.units:
            del self.units[unit_id]
            return True
        return False
    
    def filter_noise_units(self, units: List[PlanckInformationUnit]) -> List[PlanckInformationUnit]:
        """Filter out noise units below threshold"""
        filtered_units = []
        
        for unit in units:
            if unit.information_content >= self.noise_threshold:
                filtered_units.append(unit)
            else:
                self.noise_filtered_count += 1
                self.logger.debug(f"🔬 Filtered noise unit: {unit.unit_id[:8]}... "
                                f"(content: {unit.information_content:.3f} < threshold: {self.noise_threshold})")
        
        return filtered_units
    
    def validate_conservation_law(self, input_units: List[PlanckInformationUnit],
                                 output_units: List[PlanckInformationUnit],
                                 tolerance: float = 0.01) -> bool:
        """Validate information conservation law"""
        
        # Calculate total input information
        total_input = sum(unit.information_content for unit in input_units)
        
        # Calculate total output information
        total_output = sum(unit.information_content for unit in output_units)
        
        # Check conservation within tolerance
        conservation_error = abs(total_input - total_output)
        is_conserved = conservation_error <= tolerance
        
        if not is_conserved:
            self.conservation_violations += 1
            self.logger.warning(f"🔬 Conservation law violation: "
                              f"input={total_input:.3f}, output={total_output:.3f}, "
                              f"error={conservation_error:.3f}")
        
        return is_conserved
    
    def optimize_unit_collection(self, target_quality: InformationQuality = InformationQuality.QUANTUM) -> List[PlanckInformationUnit]:
        """Optimize collection for target quality"""
        
        # Filter units by quality
        quality_units = [unit for unit in self.units.values() if unit.quality == target_quality]
        
        # Sort by information content (descending)
        quality_units.sort(key=lambda u: u.information_content, reverse=True)
        
        self.logger.info(f"🔬 Optimized collection: {len(quality_units)} units with {target_quality.value} quality")
        
        return quality_units
    
    def merge_units(self, unit1_id: str, unit2_id: str) -> Optional[PlanckInformationUnit]:
        """Merge two units into one"""
        unit1 = self.get_unit(unit1_id)
        unit2 = self.get_unit(unit2_id)
        
        if not unit1 or not unit2:
            return None
        
        # Calculate merged coherence (average)
        merged_coherence = (unit1.coherence_factor + unit2.coherence_factor) / 2
        
        # Create merged unit
        merged_unit = self.create_unit(coherence_factor=merged_coherence)
        
        # Add merge metadata
        merged_unit.metadata['merged_from'] = [unit1_id, unit2_id]
        merged_unit.metadata['merge_timestamp'] = datetime.now().isoformat()
        
        # Remove original units
        self.remove_unit(unit1_id)
        self.remove_unit(unit2_id)
        
        self.logger.info(f"🔬 Merged units {unit1_id[:8]}... and {unit2_id[:8]}... "
                        f"into {merged_unit.unit_id[:8]}...")
        
        return merged_unit
    
    def get_quality_distribution(self) -> Dict[str, int]:
        """Get distribution of units by quality"""
        distribution = {}
        
        for unit in self.units.values():
            quality = unit.quality.value
            distribution[quality] = distribution.get(quality, 0) + 1
        
        return distribution
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        
        if not self.units:
            return {
                'total_units': 0,
                'total_units_created': self.total_units_created,
                'noise_filtered_count': self.noise_filtered_count,
                'conservation_violations': self.conservation_violations,
                'quality_distribution': {},
                'average_information_content': 0.0,
                'average_coherence': 0.0,
                'planck_constant': self.planck_constant,
                'above_threshold_units': 0
            }
        
        # Calculate averages
        total_content = sum(unit.information_content for unit in self.units.values())
        total_coherence = sum(unit.coherence_factor for unit in self.units.values())
        
        avg_content = total_content / len(self.units)
        avg_coherence = total_coherence / len(self.units)
        
        return {
            'total_units': len(self.units),
            'total_units_created': self.total_units_created,
            'noise_filtered_count': self.noise_filtered_count,
            'conservation_violations': self.conservation_violations,
            'quality_distribution': self.get_quality_distribution(),
            'average_information_content': avg_content,
            'average_coherence': avg_coherence,
            'planck_constant': self.planck_constant,
            'above_threshold_units': sum(1 for unit in self.units.values() 
                                       if unit.is_above_planck_threshold())
        }
    
    def export_units(self) -> Dict[str, Any]:
        """Export all units for persistence"""
        export_data = {
            'metadata': {
                'total_units': len(self.units),
                'planck_constant': self.planck_constant,
                'export_timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            },
            'statistics': self.get_system_statistics(),
            'units': []
        }
        
        for unit in self.units.values():
            unit_data = {
                'unit_id': unit.unit_id,
                'information_content': unit.information_content,
                'coherence_factor': unit.coherence_factor,
                'quality': unit.quality.value,
                'planck_constant': unit.planck_constant,
                'creation_time': unit.creation_time.isoformat(),
                'metadata': unit.metadata
            }
            export_data['units'].append(unit_data)
        
        return export_data
    
    def import_units(self, data: Dict[str, Any]) -> int:
        """Import units from exported data"""
        imported_count = 0
        
        for unit_data in data.get('units', []):
            try:
                # Create unit with imported coherence
                unit = self.create_unit(coherence_factor=unit_data['coherence_factor'])
                
                # Restore metadata
                unit.metadata.update(unit_data.get('metadata', {}))
                unit.metadata['imported'] = True
                unit.metadata['original_id'] = unit_data['unit_id']
                
                imported_count += 1
                
            except Exception as e:
                self.logger.error(f"🔬 Failed to import unit: {e}")
        
        self.logger.info(f"🔬 Imported {imported_count} units")
        return imported_count
    
    def cleanup_old_units(self, max_age_hours: int = 24):
        """Clean up old units beyond max age"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        old_units = []
        
        for unit_id, unit in self.units.items():
            if unit.creation_time.timestamp() < cutoff_time:
                old_units.append(unit_id)
        
        # Remove old units
        for unit_id in old_units:
            self.remove_unit(unit_id)
        
        if old_units:
            self.logger.info(f"🔬 Cleaned up {len(old_units)} old units")
        
        return len(old_units)
    
    def reset_system(self):
        """Reset the entire system"""
        self.units.clear()
        self.total_units_created = 0
        self.noise_filtered_count = 0
        self.conservation_violations = 0
        
        self.logger.info("🔬 System reset completed")

# Utility function
def create_planck_information_manager(planck_constant: float = 1.0) -> PlanckInformationManager:
    """Create Planck Information Manager"""
    return PlanckInformationManager(planck_constant)
