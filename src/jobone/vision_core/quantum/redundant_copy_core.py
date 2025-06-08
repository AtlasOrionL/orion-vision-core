"""
🛡️ Redundant Copy Core - Q3.2 Core Implementation

Core classes for redundant information encoding and copy management
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 5
"""

import hashlib
import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

# Import base components
from .planck_information_unit import PlanckInformationUnit

# Encoding Types
class EncodingType(Enum):
    """Kodlama türleri"""
    REPETITION_CODE = "repetition_code"             # Tekrarlama kodu
    HAMMING_CODE = "hamming_code"                   # Hamming kodu
    QUANTUM_ERROR_CORRECTION = "quantum_error_correction"  # Kuantum hata düzeltme
    DISTRIBUTED_STORAGE = "distributed_storage"     # Dağıtık depolama

# Redundancy Levels
class RedundancyLevel(Enum):
    """Yedeklilik seviyeleri"""
    LOW = "low"                                     # Düşük (3 kopya)
    MEDIUM = "medium"                               # Orta (5 kopya)
    HIGH = "high"                                   # Yüksek (7 kopya)
    CRITICAL = "critical"                           # Kritik (9 kopya)

# Quorum Decision Types
class QuorumDecision(Enum):
    """Quorum karar türleri"""
    UNANIMOUS = "unanimous"                         # Oybirliği
    MAJORITY = "majority"                           # Çoğunluk
    SUPERMAJORITY = "supermajority"                 # Süper çoğunluk
    CONSENSUS = "consensus"                         # Konsensüs

@dataclass
class RedundantCopy:
    """
    Redundant Copy
    
    Bilgi biriminin yedekli kopyası.
    """
    
    copy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_id: str = ""
    
    # Copy data
    information_unit: Optional[PlanckInformationUnit] = None
    data_hash: str = ""
    checksum: str = ""
    
    # Storage location
    storage_location: str = ""                      # Depolama konumu
    shard_index: int = 0                           # Shard indeksi
    
    # Integrity tracking
    integrity_verified: bool = True
    last_verification: Optional[datetime] = None
    corruption_detected: bool = False
    
    # Temporal properties
    creation_time: datetime = field(default_factory=datetime.now)
    last_access: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization calculations"""
        if self.information_unit and not self.data_hash:
            self._calculate_hashes()
    
    def _calculate_hashes(self):
        """Calculate data hash and checksum"""
        if not self.information_unit:
            return
        
        # Create data representation
        data_repr = json.dumps({
            'unit_id': self.information_unit.unit_id,
            'information_content': self.information_unit.information_content,
            'seed_value': self.information_unit.seed_value,
            'coherence_factor': self.information_unit.coherence_factor
        }, sort_keys=True)
        
        # Calculate hash
        self.data_hash = hashlib.sha256(data_repr.encode('utf-8')).hexdigest()
        
        # Calculate checksum (simpler hash for quick verification)
        self.checksum = hashlib.md5(data_repr.encode('utf-8')).hexdigest()[:16]
    
    def verify_integrity(self) -> bool:
        """Verify copy integrity"""
        self.last_verification = datetime.now()
        self.last_access = datetime.now()
        
        if not self.information_unit:
            self.corruption_detected = True
            self.integrity_verified = False
            return False
        
        # Recalculate hash
        old_hash = self.data_hash
        self._calculate_hashes()
        
        # Check integrity
        if self.data_hash != old_hash:
            self.corruption_detected = True
            self.integrity_verified = False
            return False
        
        self.integrity_verified = True
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'copy_id': self.copy_id,
            'original_id': self.original_id,
            'data_hash': self.data_hash,
            'checksum': self.checksum,
            'storage_location': self.storage_location,
            'shard_index': self.shard_index,
            'integrity_verified': self.integrity_verified,
            'corruption_detected': self.corruption_detected,
            'creation_time': self.creation_time.isoformat(),
            'last_verification': self.last_verification.isoformat() if self.last_verification else None,
            'last_access': self.last_access.isoformat() if self.last_access else None,
            'metadata': self.metadata
        }

@dataclass
class QuorumVote:
    """
    Quorum Vote
    
    Quorum sensing için oy verme sistemi.
    """
    
    vote_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    voter_id: str = ""                              # Oy veren kopya ID'si
    
    # Vote data
    candidate_hash: str = ""                        # Aday hash
    confidence_score: float = 1.0                   # Güven skoru (0-1)
    verification_result: bool = True                # Doğrulama sonucu
    
    # Vote metadata
    vote_weight: float = 1.0                        # Oy ağırlığı
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'vote_id': self.vote_id,
            'voter_id': self.voter_id,
            'candidate_hash': self.candidate_hash,
            'confidence_score': self.confidence_score,
            'verification_result': self.verification_result,
            'vote_weight': self.vote_weight,
            'timestamp': self.timestamp.isoformat()
        }

# Utility functions
def create_redundant_copy(information_unit: PlanckInformationUnit, 
                         storage_location: str = "default",
                         shard_index: int = 0) -> RedundantCopy:
    """Create redundant copy of information unit"""
    return RedundantCopy(
        original_id=information_unit.unit_id,
        information_unit=information_unit,
        storage_location=storage_location,
        shard_index=shard_index
    )

def verify_copy_integrity(copy: RedundantCopy) -> bool:
    """Verify integrity of redundant copy"""
    return copy.verify_integrity()

# Export core components
__all__ = [
    'EncodingType',
    'RedundancyLevel',
    'QuorumDecision',
    'RedundantCopy',
    'QuorumVote',
    'create_redundant_copy',
    'verify_copy_integrity'
]
