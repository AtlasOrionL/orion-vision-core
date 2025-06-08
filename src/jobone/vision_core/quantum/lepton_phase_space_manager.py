"""
🌀 Lepton Phase Space Manager - Q2.1 Manager Component

Management and interaction coordination for Lepton Phase Space system
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q2.1 Lepton Phase Space & Polarization Coherence
Priority: CRITICAL - Modular Design Refactoring Phase 3
"""

import logging
import math
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import core components
from .lepton_phase_space_core import (
    LeptonPhaseSpace, PolarizationVector, PolarizationType
)
from .planck_information_unit import PlanckInformationUnit

class LeptonPhaseSpaceManager:
    """
    Lepton Phase Space Manager
    
    Lepton faz uzaylarının yönetimi ve etkileşim koordinasyonu.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Lepton registry
        self.leptons: Dict[str, LeptonPhaseSpace] = {}
        
        # Statistics
        self.total_interactions = 0
        self.coherence_collapses = 0
        self.phase_evolutions = 0
        
        self.logger.info("🌀 LeptonPhaseSpaceManager initialized - Q2.1 Implementation")
    
    def create_lepton(self, 
                     energy: float = 1.0,
                     coherence_factor: float = 1.0,
                     polarization_type: PolarizationType = PolarizationType.QUANTUM,
                     information_unit: Optional[PlanckInformationUnit] = None) -> LeptonPhaseSpace:
        """Create new lepton in phase space"""
        
        # Create polarization vector
        polarization = PolarizationVector(
            polarization_type=polarization_type,
            coherence_factor=coherence_factor
        )
        
        # Create lepton phase space
        lepton = LeptonPhaseSpace(
            energy=energy,
            polarization_vector=polarization,
            information_unit=information_unit
        )
        
        # Register lepton
        self.leptons[lepton.lepton_id] = lepton
        
        self.logger.debug(f"🌀 Created lepton: {lepton.lepton_id[:8]}... "
                         f"(coherence: {coherence_factor:.3f}, energy: {energy:.3f})")
        
        return lepton
    
    def interact_with_bozon(self, lepton: LeptonPhaseSpace, bozon_type: str, interaction_strength: float = 1.0) -> bool:
        """Interact lepton with a bozon (measurement/collapse)"""
        try:
            lepton.interaction_count += 1
            lepton.last_interaction = datetime.now()
            
            # Different bozon types affect polarization differently
            if bozon_type == "photon":
                # Photon interaction - minimal effect on coherence
                measurement_value, collapsed = lepton.polarization_vector.measure_polarization("z")
                coherence_change = -0.01 * interaction_strength
                
            elif bozon_type == "z_bozon":
                # Z bozon - causes decoherence
                measurement_value, collapsed = lepton.polarization_vector.measure_polarization("x")
                coherence_change = -0.1 * interaction_strength
                
            elif bozon_type == "higgs":
                # Higgs bozon - increases mass and coherence
                measurement_value, collapsed = lepton.polarization_vector.measure_polarization("y")
                coherence_change = +0.05 * interaction_strength
                lepton.energy += 0.1 * interaction_strength
                
            else:
                # Generic interaction
                measurement_value, collapsed = lepton.polarization_vector.measure_polarization("z")
                coherence_change = -0.02 * interaction_strength
            
            # Apply coherence change
            new_coherence = lepton.polarization_vector.coherence_factor + coherence_change
            lepton.polarization_vector.coherence_factor = max(0.0, min(1.0, new_coherence))
            
            # Recalculate derived properties
            lepton._calculate_phase_volume()
            lepton._calculate_effective_mass()
            
            return not collapsed
            
        except Exception as e:
            self.logger.error(f"❌ Bozon interaction failed: {e}")
            return False
    
    def simulate_bozon_interaction(self, 
                                  lepton_id: str, 
                                  bozon_type: str, 
                                  interaction_strength: float = 1.0) -> bool:
        """Simulate bozon interaction with lepton"""
        
        if lepton_id not in self.leptons:
            self.logger.error(f"❌ Lepton not found: {lepton_id}")
            return False
        
        lepton = self.leptons[lepton_id]
        
        # Record pre-interaction state
        pre_coherence = lepton.polarization_vector.coherence_factor
        
        # Perform interaction
        success = self.interact_with_bozon(lepton, bozon_type, interaction_strength)
        
        # Record post-interaction state
        post_coherence = lepton.polarization_vector.coherence_factor
        
        # Update statistics
        self.total_interactions += 1
        if post_coherence < 0.5 and pre_coherence >= 0.5:
            self.coherence_collapses += 1
        
        self.logger.debug(f"🌀 Bozon interaction: {lepton_id[:8]}... + {bozon_type} "
                         f"(coherence: {pre_coherence:.3f} → {post_coherence:.3f})")
        
        return success
    
    def evolve_phase_space(self, lepton: LeptonPhaseSpace, time_step: float = 0.01):
        """Evolve lepton phase space according to quantum dynamics"""
        try:
            # Quantum evolution of polarization vector
            phase_evolution = time_step * lepton.energy
            
            # Apply phase evolution
            lepton.polarization_vector.phase_angle += phase_evolution
            
            # Apply unitary evolution to components
            evolution_factor = complex(math.cos(phase_evolution), math.sin(phase_evolution))
            
            lepton.polarization_vector.x_component *= evolution_factor
            lepton.polarization_vector.y_component *= evolution_factor
            lepton.polarization_vector.z_component *= evolution_factor
            
            # Normalize after evolution
            lepton.polarization_vector._normalize_vector()
            
            # Update phase space properties
            lepton._calculate_phase_volume()
            
        except Exception as e:
            self.logger.error(f"❌ Phase space evolution failed: {e}")
    
    def evolve_all_leptons(self, time_step: float = 0.01):
        """Evolve all leptons in phase space"""
        for lepton in self.leptons.values():
            self.evolve_phase_space(lepton, time_step)
        
        self.phase_evolutions += 1
        self.logger.debug(f"🌀 Phase space evolution: {len(self.leptons)} leptons evolved")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        if not self.leptons:
            return {
                'total_leptons': 0,
                'average_coherence': 0.0,
                'total_interactions': self.total_interactions,
                'coherence_collapses': self.coherence_collapses
            }
        
        # Calculate averages
        total_coherence = sum(l.polarization_vector.coherence_factor for l in self.leptons.values())
        avg_coherence = total_coherence / len(self.leptons)
        
        total_energy = sum(l.energy for l in self.leptons.values())
        avg_energy = total_energy / len(self.leptons)
        
        total_entropy = sum(l.polarization_vector.get_entropy() for l in self.leptons.values())
        avg_entropy = total_entropy / len(self.leptons)
        
        # Coherence distribution
        coherence_levels = {
            'quantum': sum(1 for l in self.leptons.values() if l.polarization_vector.coherence_factor >= 0.9),
            'coherent': sum(1 for l in self.leptons.values() if 0.7 <= l.polarization_vector.coherence_factor < 0.9),
            'classical': sum(1 for l in self.leptons.values() if 0.5 <= l.polarization_vector.coherence_factor < 0.7),
            'decoherent': sum(1 for l in self.leptons.values() if l.polarization_vector.coherence_factor < 0.5)
        }
        
        return {
            'total_leptons': len(self.leptons),
            'average_coherence': avg_coherence,
            'average_energy': avg_energy,
            'average_entropy': avg_entropy,
            'total_interactions': self.total_interactions,
            'coherence_collapses': self.coherence_collapses,
            'phase_evolutions': self.phase_evolutions,
            'coherence_distribution': coherence_levels
        }
    
    def filter_coherent_leptons(self, min_coherence: float = 0.5) -> List[LeptonPhaseSpace]:
        """Filter leptons by minimum coherence threshold"""
        coherent_leptons = []
        
        for lepton in self.leptons.values():
            if lepton.polarization_vector.coherence_factor >= min_coherence:
                coherent_leptons.append(lepton)
        
        self.logger.debug(f"🌀 Coherent leptons: {len(coherent_leptons)}/{len(self.leptons)} "
                         f"(threshold: {min_coherence:.3f})")
        
        return coherent_leptons
    
    def get_lepton_by_id(self, lepton_id: str) -> Optional[LeptonPhaseSpace]:
        """Get lepton by ID"""
        return self.leptons.get(lepton_id)
    
    def remove_lepton(self, lepton_id: str) -> bool:
        """Remove lepton from system"""
        if lepton_id in self.leptons:
            del self.leptons[lepton_id]
            self.logger.debug(f"🌀 Removed lepton: {lepton_id[:8]}...")
            return True
        return False

# Utility function
def create_lepton_phase_space_manager() -> LeptonPhaseSpaceManager:
    """Create Lepton Phase Space Manager"""
    return LeptonPhaseSpaceManager()

# Test function
def test_lepton_phase_space():
    """Test Lepton Phase Space system"""
    print("🌀 Testing Lepton Phase Space & Polarization Coherence System...")
    
    # Create manager
    manager = create_lepton_phase_space_manager()
    print("✅ Lepton Phase Space Manager created")
    
    # Create test leptons
    lepton1 = manager.create_lepton(energy=2.0, coherence_factor=0.9, 
                                   polarization_type=PolarizationType.QUANTUM)
    lepton2 = manager.create_lepton(energy=1.5, coherence_factor=0.6, 
                                   polarization_type=PolarizationType.EMOTIONAL)
    lepton3 = manager.create_lepton(energy=1.0, coherence_factor=0.3, 
                                   polarization_type=PolarizationType.COGNITIVE)
    
    print(f"✅ Created 3 test leptons")
    print(f"    - Lepton 1: {lepton1.polarization_vector.coherence_factor:.3f} coherence")
    print(f"    - Lepton 2: {lepton2.polarization_vector.coherence_factor:.3f} coherence")
    print(f"    - Lepton 3: {lepton3.polarization_vector.coherence_factor:.3f} coherence")
    
    # Test bozon interactions
    manager.simulate_bozon_interaction(lepton1.lepton_id, "photon", 0.5)
    manager.simulate_bozon_interaction(lepton2.lepton_id, "z_bozon", 1.0)
    manager.simulate_bozon_interaction(lepton3.lepton_id, "higgs", 0.8)
    
    print("✅ Bozon interactions completed")
    
    # Test phase space evolution
    manager.evolve_all_leptons(0.1)
    print("✅ Phase space evolution completed")
    
    # Test coherent filtering
    coherent_leptons = manager.filter_coherent_leptons(0.4)
    print(f"✅ Coherent leptons: {len(coherent_leptons)}/3")
    
    # Get statistics
    stats = manager.get_system_statistics()
    print(f"✅ System statistics:")
    print(f"    - Total leptons: {stats['total_leptons']}")
    print(f"    - Average coherence: {stats['average_coherence']:.3f}")
    print(f"    - Total interactions: {stats['total_interactions']}")
    print(f"    - Coherence collapses: {stats['coherence_collapses']}")
    
    print("🚀 Lepton Phase Space test completed!")

# Export manager components
__all__ = [
    'LeptonPhaseSpaceManager',
    'create_lepton_phase_space_manager',
    'test_lepton_phase_space'
]
