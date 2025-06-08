"""
🛡️ Redundant Information Encoder - Q3.2 Encoder Component

Redundant encoding and distributed storage for information units
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q3.2 Redundant Information Encoding
Priority: CRITICAL - Modular Design Refactoring Phase 5
"""

import logging
from typing import Dict, List, Any, Optional, Set

# Import core components
from .redundant_copy_core import (
    EncodingType, RedundancyLevel, RedundantCopy, create_redundant_copy
)
from .planck_information_unit import PlanckInformationUnit

class RedundantInformationEncoder:
    """
    Redundant Information Encoder
    
    Bilgi birimlerinin yedekli kodlanması ve dağıtık depolanması.
    """
    
    def __init__(self, 
                 encoding_type: EncodingType = EncodingType.REPETITION_CODE,
                 redundancy_level: RedundancyLevel = RedundancyLevel.MEDIUM):
        self.logger = logging.getLogger(__name__)
        self.encoding_type = encoding_type
        self.redundancy_level = redundancy_level
        
        # Storage registry
        self.encoded_units: Dict[str, List[RedundantCopy]] = {}
        self.storage_locations: Set[str] = set()
        
        # Redundancy configuration
        self.redundancy_counts = {
            RedundancyLevel.LOW: 3,
            RedundancyLevel.MEDIUM: 5,
            RedundancyLevel.HIGH: 7,
            RedundancyLevel.CRITICAL: 9
        }
        
        # Statistics
        self.total_encoded = 0
        self.corruption_detected_count = 0
        self.recovery_success_count = 0
        
        self.logger.info(f"🛡️ RedundantInformationEncoder initialized - Q3.2 Implementation "
                        f"({encoding_type.value}, {redundancy_level.value})")
    
    def encode_information_unit(self, 
                               information_unit: PlanckInformationUnit,
                               storage_locations: Optional[List[str]] = None) -> List[RedundantCopy]:
        """Encode information unit with redundancy"""
        try:
            redundancy_count = self.redundancy_counts[self.redundancy_level]
            
            # Generate storage locations if not provided
            if not storage_locations:
                storage_locations = [f"shard_{i}" for i in range(redundancy_count)]
            
            # Ensure we have enough storage locations
            while len(storage_locations) < redundancy_count:
                storage_locations.append(f"shard_{len(storage_locations)}")
            
            # Create redundant copies
            copies = []
            for i in range(redundancy_count):
                copy = create_redundant_copy(
                    information_unit=information_unit,
                    storage_location=storage_locations[i % len(storage_locations)],
                    shard_index=i
                )
                copies.append(copy)
                self.storage_locations.add(copy.storage_location)
            
            # Store copies
            self.encoded_units[information_unit.unit_id] = copies
            self.total_encoded += 1
            
            self.logger.debug(f"🛡️ Encoded unit {information_unit.unit_id[:8]}... "
                            f"with {len(copies)} redundant copies")
            
            return copies
            
        except Exception as e:
            self.logger.error(f"❌ Failed to encode information unit: {e}")
            return []
    
    def verify_all_copies(self, unit_id: str) -> Dict[str, bool]:
        """Verify integrity of all copies for a unit"""
        if unit_id not in self.encoded_units:
            return {}
        
        verification_results = {}
        
        for copy in self.encoded_units[unit_id]:
            result = copy.verify_integrity()
            verification_results[copy.copy_id] = result
            
            if not result:
                self.corruption_detected_count += 1
                self.logger.warning(f"🛡️ Corruption detected in copy {copy.copy_id[:8]}... "
                                  f"of unit {unit_id[:8]}...")
        
        return verification_results
    
    def get_valid_copies(self, unit_id: str) -> List[RedundantCopy]:
        """Get all valid (non-corrupted) copies of a unit"""
        if unit_id not in self.encoded_units:
            return []
        
        valid_copies = []
        
        for copy in self.encoded_units[unit_id]:
            if copy.verify_integrity():
                valid_copies.append(copy)
        
        return valid_copies
    
    def recover_corrupted_unit(self, unit_id: str) -> Optional[PlanckInformationUnit]:
        """Recover information unit from valid copies"""
        try:
            valid_copies = self.get_valid_copies(unit_id)
            
            if not valid_copies:
                self.logger.error(f"❌ No valid copies found for unit {unit_id[:8]}...")
                return None
            
            # Use the first valid copy for recovery
            recovered_unit = valid_copies[0].information_unit
            
            if recovered_unit:
                self.recovery_success_count += 1
                self.logger.info(f"🛡️ Successfully recovered unit {unit_id[:8]}... "
                               f"from {len(valid_copies)} valid copies")
            
            return recovered_unit
            
        except Exception as e:
            self.logger.error(f"❌ Failed to recover unit {unit_id}: {e}")
            return None
    
    def simulate_corruption(self, unit_id: str, copy_index: int = 0) -> bool:
        """Simulate corruption in a specific copy (for testing)"""
        try:
            if unit_id not in self.encoded_units:
                return False
            
            copies = self.encoded_units[unit_id]
            if copy_index >= len(copies):
                return False
            
            # Simulate corruption by modifying the hash
            copy = copies[copy_index]
            copy.data_hash = "corrupted_hash"
            copy.corruption_detected = True
            copy.integrity_verified = False
            
            self.logger.debug(f"🛡️ Simulated corruption in copy {copy.copy_id[:8]}... "
                            f"of unit {unit_id[:8]}...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to simulate corruption: {e}")
            return False
    
    def get_copies_by_unit(self, unit_id: str) -> List[RedundantCopy]:
        """Get all copies for a specific unit"""
        return self.encoded_units.get(unit_id, [])
    
    def remove_unit(self, unit_id: str) -> bool:
        """Remove all copies of a unit"""
        if unit_id in self.encoded_units:
            del self.encoded_units[unit_id]
            self.logger.debug(f"🛡️ Removed all copies of unit {unit_id[:8]}...")
            return True
        return False
    
    def get_encoding_statistics(self) -> Dict[str, Any]:
        """Get encoding statistics"""
        total_copies = sum(len(copies) for copies in self.encoded_units.values())
        
        # Count corrupted copies
        corrupted_copies = 0
        for copies in self.encoded_units.values():
            for copy in copies:
                if copy.corruption_detected:
                    corrupted_copies += 1
        
        corruption_rate = corrupted_copies / max(1, total_copies)
        recovery_rate = self.recovery_success_count / max(1, self.corruption_detected_count)
        
        return {
            'total_encoded_units': self.total_encoded,
            'total_copies': total_copies,
            'corrupted_copies': corrupted_copies,
            'corruption_rate': corruption_rate,
            'recovery_success_count': self.recovery_success_count,
            'recovery_rate': recovery_rate,
            'storage_locations': len(self.storage_locations),
            'encoding_type': self.encoding_type.value,
            'redundancy_level': self.redundancy_level.value
        }

# Utility function
def create_redundant_information_encoder(encoding_type: EncodingType = EncodingType.REPETITION_CODE,
                                        redundancy_level: RedundancyLevel = RedundancyLevel.MEDIUM) -> RedundantInformationEncoder:
    """Create Redundant Information Encoder"""
    return RedundantInformationEncoder(encoding_type, redundancy_level)

# Export encoder components
__all__ = [
    'RedundantInformationEncoder',
    'create_redundant_information_encoder'
]
