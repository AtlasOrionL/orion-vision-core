"""
🔗 Decoherence Detection System - Q3.1 Detector Component

Decoherence detection and Z Boson triggering for Information Entanglement Units
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q3.1 Information Entanglement Unit & Decoherence Detection
Priority: CRITICAL - Modular Design Refactoring Phase 4
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import core components
from .entanglement_core import InformationEntanglementUnit
from .information_conservation_law import ZBosonTrigger
from .planck_information_unit import PlanckInformationUnit

class DecoherenceDetectionSystem:
    """
    Decoherence Detection System
    
    IEU'ların dekohaerans durumunu izler ve Z_Bozon tetikler.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # IEU registry
        self.ieus: Dict[str, InformationEntanglementUnit] = {}
        
        # Decoherence tracking
        self.decoherence_events: List[Dict[str, Any]] = []
        self.total_decoherence_count = 0
        
        # Z Boson trigger system
        self.z_boson_trigger = ZBosonTrigger()
        
        # Detection parameters
        self.monitoring_interval = 1.0                  # Monitoring interval (seconds)
        self.decoherence_threshold = 0.3               # Global decoherence threshold
        
        self.logger.info("🔗 DecoherenceDetectionSystem initialized - Q3.1 Implementation")
    
    def register_ieu(self, ieu: InformationEntanglementUnit) -> bool:
        """Register IEU for monitoring"""
        try:
            self.ieus[ieu.ieu_id] = ieu
            self.logger.debug(f"🔗 Registered IEU: {ieu.ieu_id[:8]}... "
                            f"({len(ieu.lepton_ids)} leptons)")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to register IEU: {e}")
            return False
    
    def unregister_ieu(self, ieu_id: str) -> bool:
        """Unregister IEU from monitoring"""
        try:
            if ieu_id in self.ieus:
                del self.ieus[ieu_id]
                self.logger.debug(f"🔗 Unregistered IEU: {ieu_id[:8]}...")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to unregister IEU: {e}")
            return False
    
    def monitor_all_ieus(self) -> List[str]:
        """Monitor all registered IEUs for decoherence"""
        decoherent_ieus = []
        
        for ieu_id, ieu in self.ieus.items():
            if self._check_ieu_decoherence(ieu):
                decoherent_ieus.append(ieu_id)
        
        return decoherent_ieus
    
    def _check_ieu_decoherence(self, ieu: InformationEntanglementUnit) -> bool:
        """Check specific IEU for decoherence"""
        try:
            # Perform decoherence check
            decoherence_detected = ieu._check_decoherence()
            
            if decoherence_detected and not ieu.decoherence_detected:
                # New decoherence event
                self._handle_decoherence_event(ieu)
                return True
            
            return decoherence_detected
            
        except Exception as e:
            self.logger.error(f"❌ Decoherence check failed for IEU {ieu.ieu_id}: {e}")
            return False
    
    def _handle_decoherence_event(self, ieu: InformationEntanglementUnit):
        """Handle decoherence event"""
        try:
            # Create decoherence event record
            decoherence_event = {
                'event_id': str(uuid.uuid4()),
                'ieu_id': ieu.ieu_id,
                'timestamp': datetime.now().isoformat(),
                'entanglement_strength': ieu.entanglement_bond.entanglement_strength,
                'collective_coherence': ieu.collective_coherence,
                'lepton_count': len(ieu.lepton_ids),
                'decoherence_type': 'entanglement_loss'
            }
            
            self.decoherence_events.append(decoherence_event)
            self.total_decoherence_count += 1
            
            # Create mock conservation event for Z Boson trigger compatibility
            from .conservation_law_core import ConservationEvent, ConservationEventType
            mock_event = ConservationEvent(
                event_type=ConservationEventType.DECAY,
                process_name="entanglement_decoherence",
                process_id=ieu.ieu_id
            )
            mock_event.conservation_error = 1.0 - ieu.entanglement_bond.entanglement_strength
            
            # Trigger Z Boson
            z_boson_id = self.z_boson_trigger.trigger_decoherence_signal(
                conservation_event=mock_event,
                severity="medium"
            )
            
            self.logger.warning(f"🔗 Decoherence detected in IEU {ieu.ieu_id[:8]}... "
                              f"(strength: {ieu.entanglement_bond.entanglement_strength:.3f}, "
                              f"Z Boson: {z_boson_id[:8]}...)")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle decoherence event: {e}")
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get decoherence detection statistics"""
        if not self.ieus:
            return {
                'total_ieus': 0,
                'decoherent_ieus': 0,
                'decoherence_rate': 0.0,
                'total_decoherence_events': self.total_decoherence_count
            }
        
        # Count decoherent IEUs
        decoherent_count = sum(1 for ieu in self.ieus.values() if ieu.decoherence_detected)
        decoherence_rate = decoherent_count / len(self.ieus)
        
        # Average entanglement strength
        total_strength = sum(ieu.entanglement_bond.entanglement_strength for ieu in self.ieus.values())
        avg_strength = total_strength / len(self.ieus)
        
        # Recent events (last hour)
        recent_time = datetime.now().timestamp() - 3600
        recent_events = [
            e for e in self.decoherence_events 
            if datetime.fromisoformat(e['timestamp']).timestamp() > recent_time
        ]
        
        return {
            'total_ieus': len(self.ieus),
            'decoherent_ieus': decoherent_count,
            'decoherence_rate': decoherence_rate,
            'average_entanglement_strength': avg_strength,
            'total_decoherence_events': self.total_decoherence_count,
            'recent_decoherence_events': len(recent_events),
            'z_boson_stats': self.z_boson_trigger.get_trigger_statistics()
        }
    
    def simulate_entanglement_measurement(self, ieu_id: str) -> bool:
        """Simulate entanglement measurement on specific IEU"""
        if ieu_id not in self.ieus:
            self.logger.error(f"❌ IEU not found: {ieu_id}")
            return False
        
        ieu = self.ieus[ieu_id]
        
        try:
            # Perform measurement
            strength, decoherence_occurred = ieu.measure_entanglement_strength()
            
            if decoherence_occurred:
                self._handle_decoherence_event(ieu)
            
            self.logger.debug(f"🔗 Entanglement measurement: {ieu_id[:8]}... "
                            f"(strength: {strength:.3f}, decoherence: {decoherence_occurred})")
            
            return not decoherence_occurred
            
        except Exception as e:
            self.logger.error(f"❌ Entanglement measurement failed: {e}")
            return False
    
    def get_ieu_by_id(self, ieu_id: str) -> Optional[InformationEntanglementUnit]:
        """Get IEU by ID"""
        return self.ieus.get(ieu_id)
    
    def get_healthy_ieus(self) -> List[InformationEntanglementUnit]:
        """Get list of healthy (non-decoherent) IEUs"""
        return [ieu for ieu in self.ieus.values() if not ieu.decoherence_detected]
    
    def get_decoherent_ieus(self) -> List[InformationEntanglementUnit]:
        """Get list of decoherent IEUs"""
        return [ieu for ieu in self.ieus.values() if ieu.decoherence_detected]

# Utility functions
def create_information_entanglement_unit(lepton_ids: List[str], 
                                        information_units: Optional[List[PlanckInformationUnit]] = None) -> InformationEntanglementUnit:
    """Create Information Entanglement Unit"""
    ieu = InformationEntanglementUnit()
    
    for i, lepton_id in enumerate(lepton_ids):
        info_unit = information_units[i] if information_units and i < len(information_units) else None
        ieu.add_lepton(lepton_id, info_unit)
    
    return ieu

def create_decoherence_detection_system() -> DecoherenceDetectionSystem:
    """Create Decoherence Detection System"""
    return DecoherenceDetectionSystem()

# Test function
def test_information_entanglement_unit():
    """Test Information Entanglement Unit system"""
    print("🔗 Testing Information Entanglement Unit (IEU) & Decoherence Detection System...")
    
    # Create detection system
    detector = create_decoherence_detection_system()
    print("✅ Decoherence Detection System created")
    
    # Create test IEUs
    from .planck_information_unit import create_planck_information_manager
    
    planck_manager = create_planck_information_manager()
    
    # Create information units
    info_units = [
        planck_manager.create_unit(coherence_factor=0.9),
        planck_manager.create_unit(coherence_factor=0.8)
    ]
    
    # Create IEU with entangled leptons
    lepton_ids = ["lepton_001", "lepton_002"]
    ieu1 = create_information_entanglement_unit(lepton_ids, info_units)
    
    print(f"✅ Created IEU with {len(ieu1.lepton_ids)} entangled leptons")
    print(f"    - Entanglement strength: {ieu1.entanglement_bond.entanglement_strength:.3f}")
    print(f"    - Collective coherence: {ieu1.collective_coherence:.3f}")
    
    # Register IEU for monitoring
    detector.register_ieu(ieu1)
    print("✅ IEU registered for decoherence monitoring")
    
    # Test entanglement measurement
    success = detector.simulate_entanglement_measurement(ieu1.ieu_id)
    print(f"✅ Entanglement measurement: {'Success' if success else 'Decoherence detected'}")
    
    # Test decoherence by removing lepton
    ieu1.remove_lepton("lepton_001")
    print("✅ Lepton removed (simulating decoherence)")
    
    # Monitor for decoherence
    decoherent_ieus = detector.monitor_all_ieus()
    print(f"✅ Decoherence monitoring: {len(decoherent_ieus)} decoherent IEUs detected")
    
    # Get statistics
    stats = detector.get_detection_statistics()
    print(f"✅ Detection statistics:")
    print(f"    - Total IEUs: {stats['total_ieus']}")
    print(f"    - Decoherent IEUs: {stats['decoherent_ieus']}")
    print(f"    - Decoherence rate: {stats['decoherence_rate']:.1%}")
    print(f"    - Z Boson triggers: {stats['z_boson_stats']['total_triggers']}")
    
    print("🚀 Information Entanglement Unit test completed!")

# Export detector components
__all__ = [
    'DecoherenceDetectionSystem',
    'create_information_entanglement_unit',
    'create_decoherence_detection_system',
    'test_information_entanglement_unit'
]
