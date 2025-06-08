"""
🛡️ Quorum Sensing System - Q3.2 Quorum Component

Quorum sensing and consensus mechanism for redundant information validation
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q3.2 Redundant Information Encoding & Quorum Sensing
Priority: CRITICAL - Modular Design Refactoring Phase 5
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple

# Import core components
from .redundant_copy_core import QuorumDecision, QuorumVote, RedundantCopy
from .information_conservation_law import ZBosonTrigger

class QuorumSensingSystem:
    """
    Quorum Sensing System
    
    Oy çokluğu mekanizmasıyla doğru bilgiye ulaşma sistemi.
    """
    
    def __init__(self, 
                 decision_type: QuorumDecision = QuorumDecision.MAJORITY,
                 minimum_votes: int = 3):
        self.logger = logging.getLogger(__name__)
        self.decision_type = decision_type
        self.minimum_votes = minimum_votes
        
        # Voting registry
        self.active_votes: Dict[str, List[QuorumVote]] = {}
        self.completed_votes: Dict[str, Dict[str, Any]] = {}
        
        # Z Boson trigger for inconsistencies
        self.z_boson_trigger = ZBosonTrigger()
        
        # Decision thresholds
        self.decision_thresholds = {
            QuorumDecision.UNANIMOUS: 1.0,
            QuorumDecision.SUPERMAJORITY: 0.75,
            QuorumDecision.MAJORITY: 0.51,
            QuorumDecision.CONSENSUS: 0.67
        }
        
        self.logger.info(f"🛡️ QuorumSensingSystem initialized - Q3.2 Implementation "
                        f"({decision_type.value}, min_votes: {minimum_votes})")
    
    def initiate_quorum_vote(self, 
                            unit_id: str, 
                            copies: List[RedundantCopy]) -> str:
        """Initiate quorum vote for information unit"""
        vote_session_id = str(uuid.uuid4())
        
        # Create votes from copies
        votes = []
        for copy in copies:
            if copy.verify_integrity():
                vote = QuorumVote(
                    voter_id=copy.copy_id,
                    candidate_hash=copy.data_hash,
                    confidence_score=1.0 if copy.integrity_verified else 0.5,
                    verification_result=copy.integrity_verified,
                    vote_weight=1.0
                )
                votes.append(vote)
        
        self.active_votes[vote_session_id] = votes
        
        self.logger.debug(f"🛡️ Initiated quorum vote {vote_session_id[:8]}... "
                         f"for unit {unit_id[:8]}... with {len(votes)} votes")
        
        return vote_session_id
    
    def evaluate_quorum_decision(self, vote_session_id: str) -> Tuple[Optional[str], bool, Dict[str, Any]]:
        """
        Evaluate quorum decision
        Returns: (winning_hash, consensus_reached, decision_details)
        """
        if vote_session_id not in self.active_votes:
            return None, False, {}
        
        votes = self.active_votes[vote_session_id]
        
        if len(votes) < self.minimum_votes:
            return None, False, {'reason': 'insufficient_votes', 'vote_count': len(votes)}
        
        # Count votes by hash
        hash_votes = {}
        total_weight = 0.0
        
        for vote in votes:
            if vote.verification_result:  # Only count verified votes
                hash_key = vote.candidate_hash
                if hash_key not in hash_votes:
                    hash_votes[hash_key] = {
                        'votes': [],
                        'total_weight': 0.0,
                        'confidence_sum': 0.0
                    }
                
                hash_votes[hash_key]['votes'].append(vote)
                hash_votes[hash_key]['total_weight'] += vote.vote_weight
                hash_votes[hash_key]['confidence_sum'] += vote.confidence_score
                total_weight += vote.vote_weight
        
        if not hash_votes:
            return None, False, {'reason': 'no_verified_votes'}
        
        # Find winning hash
        winning_hash = None
        max_weight = 0.0
        decision_threshold = self.decision_thresholds[self.decision_type]
        
        for hash_key, vote_data in hash_votes.items():
            vote_ratio = vote_data['total_weight'] / total_weight
            
            if vote_ratio >= decision_threshold and vote_data['total_weight'] > max_weight:
                winning_hash = hash_key
                max_weight = vote_data['total_weight']
        
        # Check for consensus
        consensus_reached = winning_hash is not None
        
        # Detect inconsistencies
        if len(hash_votes) > 1:
            # Multiple different hashes - potential data inconsistency
            self._handle_data_inconsistency(vote_session_id, hash_votes)
        
        # Create decision details
        decision_details = {
            'vote_session_id': vote_session_id,
            'total_votes': len(votes),
            'verified_votes': sum(1 for v in votes if v.verification_result),
            'unique_hashes': len(hash_votes),
            'winning_hash': winning_hash,
            'winning_weight': max_weight,
            'total_weight': total_weight,
            'decision_threshold': decision_threshold,
            'consensus_reached': consensus_reached,
            'hash_distribution': {
                h: {
                    'vote_count': len(data['votes']),
                    'total_weight': data['total_weight'],
                    'average_confidence': data['confidence_sum'] / len(data['votes'])
                }
                for h, data in hash_votes.items()
            }
        }
        
        # Move to completed votes
        self.completed_votes[vote_session_id] = decision_details
        del self.active_votes[vote_session_id]
        
        self.logger.info(f"🛡️ Quorum decision: {vote_session_id[:8]}... "
                        f"consensus: {consensus_reached}, winner: {winning_hash[:8] if winning_hash else 'None'}...")
        
        return winning_hash, consensus_reached, decision_details
    
    def _handle_data_inconsistency(self, vote_session_id: str, hash_votes: Dict[str, Any]):
        """Handle data inconsistency detected by quorum"""
        try:
            # Create mock conservation event for Z Boson trigger compatibility
            from .conservation_law_core import ConservationEvent, ConservationEventType
            mock_event = ConservationEvent(
                event_type=ConservationEventType.DECAY,
                process_name="quorum_data_inconsistency",
                process_id=vote_session_id
            )
            mock_event.conservation_error = len(hash_votes) / 10.0  # Normalized inconsistency measure
            
            # Trigger Z Boson for data inconsistency
            trigger_id = self.z_boson_trigger.trigger_decoherence_signal(
                conservation_event=mock_event,
                severity="high"
            )
            
            self.logger.warning(f"🛡️ Data inconsistency detected in vote {vote_session_id[:8]}... "
                              f"({len(hash_votes)} different hashes, Z Boson: {trigger_id[:8]}...)")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle data inconsistency: {e}")
    
    def get_vote_session_details(self, vote_session_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a vote session"""
        if vote_session_id in self.completed_votes:
            return self.completed_votes[vote_session_id]
        elif vote_session_id in self.active_votes:
            votes = self.active_votes[vote_session_id]
            return {
                'vote_session_id': vote_session_id,
                'status': 'active',
                'total_votes': len(votes),
                'verified_votes': sum(1 for v in votes if v.verification_result)
            }
        return None
    
    def get_quorum_statistics(self) -> Dict[str, Any]:
        """Get quorum sensing statistics"""
        total_sessions = len(self.completed_votes) + len(self.active_votes)
        
        if not self.completed_votes:
            return {
                'total_sessions': total_sessions,
                'completed_sessions': 0,
                'consensus_rate': 0.0,
                'average_votes_per_session': 0.0,
                'z_boson_stats': self.z_boson_trigger.get_trigger_statistics()
            }
        
        # Calculate statistics
        consensus_count = sum(1 for details in self.completed_votes.values() 
                            if details.get('consensus_reached', False))
        consensus_rate = consensus_count / len(self.completed_votes)
        
        total_votes = sum(details.get('total_votes', 0) for details in self.completed_votes.values())
        avg_votes = total_votes / len(self.completed_votes)
        
        # Inconsistency detection
        inconsistency_count = sum(1 for details in self.completed_votes.values() 
                                if details.get('unique_hashes', 1) > 1)
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': len(self.completed_votes),
            'active_sessions': len(self.active_votes),
            'consensus_rate': consensus_rate,
            'average_votes_per_session': avg_votes,
            'inconsistency_detections': inconsistency_count,
            'decision_type': self.decision_type.value,
            'minimum_votes': self.minimum_votes,
            'z_boson_stats': self.z_boson_trigger.get_trigger_statistics()
        }

# Utility function
def create_quorum_sensing_system(decision_type: QuorumDecision = QuorumDecision.MAJORITY,
                                minimum_votes: int = 3) -> QuorumSensingSystem:
    """Create Quorum Sensing System"""
    return QuorumSensingSystem(decision_type, minimum_votes)

# Export quorum components
__all__ = [
    'QuorumSensingSystem',
    'create_quorum_sensing_system'
]
